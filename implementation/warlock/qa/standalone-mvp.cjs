'use strict';
// Root executes this QA-only harness against compiled StandaloneMvpReplay.
// Deterministic seeded source-route traces; no native or GUI acceptance.
const fs=require('node:fs'),crypto=require('node:crypto');
const [compiled,output]=process.argv.slice(2);
if(process.argv.length!==4) throw Error('usage: node standalone-mvp.cjs REPLAY.js REPORT.json');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const report={schema:1,seed:20261101,checks:[],failures:[],sourceHashes:{replay:sha(compiled),harness:sha(__filename)},nativeAcceptance:false,guiAcceptance:false};
let app;
let waiting=null;
function check(name,ok,detail){const row={name,passed:Boolean(ok)};if(!ok)row.detail=detail;report.checks.push(row);if(!ok)report.failures.push(row);}
async function send(kind,value){const result=new Promise((resolve,reject)=>{const timer=setTimeout(()=>{waiting=null;reject(Error('missing replay output: '+kind));},2000);waiting=reply=>{clearTimeout(timer);waiting=null;resolve(reply);};});app.ports.incoming.send(value===undefined?{kind}:{kind,value});return result;}
const binding=n=>({lifetime:String(9007199254741001n+BigInt(n)*7n),session:String(9007199254741103n+BigInt(n)*11n),frontend:String(9007199254741207n+BigInt(n)*13n)});
const attachment=b=>({protocolVersion:3,kind:'application-attached',binding:b,nativeOperations:[]});
const gateway=(kind,payload)=>({bridgeProtocol:1,kind,payload});
const kinds=r=>r.requests.map(x=>x.kind);
const forbidden=xs=>xs.some(x=>!['catalog-request','taskbar-pins-write'].includes(x));
(async()=>{
 try {
  app=require(require('node:path').resolve(compiled)).Elm.StandaloneMvpReplay.init();
  app.ports.outgoing.subscribe(value=>{if(waiting)waiting(value);});
  for(let seed=0;seed<32;seed++){
   await send('reset');const b=binding(seed),a=attachment(b);
   let r=await send('native',a);
   check('attach preserves app-only/no-native '+seed,r.applicationOnly&&JSON.stringify(r.binding)===JSON.stringify(b)&&!r.shell.available&&!forbidden(kinds(r)),r);
   const controls=r.frame.bar;
   check('application control enabled; unsupported utilities disabled '+seed,controls.some(c=>c.id==='bar:applications'&&c.enabled)&&['bar:notifications','bar:files','bar:system','bar:settings','bar:overview','bar:switcher'].every(id=>controls.some(c=>c.id===id&&!c.enabled)),controls);
   for(const command of ['refresh','supersede','geometry']){
    r=await send(command);check(command+' cannot request native work '+seed,r.applicationOnly&&!r.shell.available&&!forbidden(kinds(r)),r);
   }
   r=await send('open');const catalogs=r.requests.filter(x=>x.kind==='catalog-request');
   check('actual Desktop catalog route '+seed,r.open&&catalogs.length===1&&JSON.stringify(catalogs[0].binding)===JSON.stringify(b)&&!forbidden(kinds(r)),r);
   const catalog=catalogs[0];if(catalog){
    const snapshot={catalogProtocol:2,lifetime:b.lifetime,generation:'1',entries:[{id:'sample.desktop',name:'Sample',iconHint:'',wmclass:'',genericName:'',keywords:[]}]};
    const response={protocolVersion:3,kind:'application-catalog',binding:b,requestId:catalog.requestId,snapshot,preferences:{revision:'1',identities:[]}};
    const stale={...response,binding:{...b,frontend:String(BigInt(b.frontend)+1n)}};
    r=await send('native',stale);check('foreign receipt rejected '+seed,r.open&&r.pendingCatalog===catalog.requestId&&r.catalogIds.length===0&&!forbidden(kinds(r)),r);
    r=await send('native',response);check('current catalog response no native request '+seed,r.open&&r.applicationOnly&&r.pendingCatalog===null&&r.catalogIds.includes('sample.desktop')&&!forbidden(kinds(r)),r);
    check('catalog exposes pin but not unsupported launch or jump '+seed,r.frame.popup.some(c=>c.id==='pin:sample.desktop'&&c.enabled)&&r.frame.popup.some(c=>c.id==='entry:sample.desktop'&&!c.enabled)&&r.frame.popup.some(c=>c.id==='jump:open:sample.desktop'&&!c.enabled),r.frame.popup);
   }
  }
  const b=binding(0),a=attachment(b);
  for(const [label,bad] of [['version',{...a,protocolVersion:2}],['extra',{...a,extra:true}],['operations',{...a,nativeOperations:['focus']}],['missing binding',{...a,binding:{lifetime:b.lifetime,session:b.session}}],['zero',{...a,binding:{...b,frontend:'0'}}],['rounded number',{...a,binding:{...b,lifetime:9007199254741000}}]]){
   await send('reset');const r=await send('native',bad);check('invalid attachment '+label,!r.applicationOnly&&!r.binding&&!r.shell.available&&!forbidden(kinds(r)),r);
  }
  await send('reset');await send('native',a);let r=await send('open');
  const pending=r.requests.find(x=>x.kind==='catalog-request');
  await send('native',{protocolVersion:3,kind:'host-disconnected'});
  const late={protocolVersion:3,kind:'application-catalog',binding:b,requestId:pending.requestId,snapshot:{catalogProtocol:2,lifetime:b.lifetime,generation:'1',entries:[]},preferences:{revision:'1',identities:[]}};
  r=await send('native',late);check('late catalog after disconnect cannot replay',!r.applicationOnly&&r.catalogIds.length===0&&!forbidden(kinds(r)),r);
  await send('reconnect');r=await send('native',a);check('old binding cannot reattach',!r.applicationOnly&&!r.shell.available,r);
  const newer={...b,frontend:String(BigInt(b.frontend)+1n)};r=await send('native',attachment(newer));
  check('fresh binding reconnects without native work',r.applicationOnly&&JSON.stringify(r.binding)===JSON.stringify(newer)&&!forbidden(kinds(r)),r);
  await send('reset');r=await send('native',{protocolVersion:3,kind:'attached',binding:b});
  check('legacy native attach retains original reads',!r.applicationOnly&&['projection-request','catalog-request','shell-settings-request','motion-preferences-request','shortcut-preferences-request'].every(k=>kinds(r).includes(k)),r);
  check('legacy binding keeps utility admission unchanged',['bar:notifications','bar:files','bar:system','bar:settings'].every(id=>r.frame.bar.some(c=>c.id===id&&c.enabled)),r.frame.bar);
  await send('reset');
  const topology={viewProtocol:2,kind:'view-topology',revision:'1',views:[{id:'1',generation:'1'}],locations:[{scope:{id:'1',generation:'1'},box:[0,0,800,600]}]};
  r=await send('policy',gateway('view-topology',topology));
  check('first topology yields presentation-only commit',r.policyPackets.some(packet=>packet.kind==='view-commit'&&packet.viewProtocol===1&&packet.requests.length===0&&packet.projection.kind==='view-frame')&&!r.policyPackets.some(packet=>forbidden((packet.requests||[]).map(x=>x.kind))),r);
  r=await send('policy',gateway('native-event',a));
  check('actual HttpMain policy accepts scoped attach',r.policyApplicationOnly&&!r.policyPackets.some(packet=>forbidden((packet.requests||[]).map(x=>x.kind))),r);
  const moved={...topology,revision:'2',locations:[{scope:{id:'1',generation:'1'},box:[0,0,900,600]}]};
  r=await send('policy',gateway('view-topology',moved));
  check('actual policy topology emits no native requests',r.policyApplicationOnly&&!r.policyPackets.some(packet=>forbidden((packet.requests||[]).map(x=>x.kind))),r);
  const frame=r.policyFrame.frame;
  r=await send('policy',gateway('view-action',{viewProtocol:1,kind:'view-action',scope:{id:'1',generation:'1'},action:{surfaceProtocol:2,kind:'surface-action',surface:'bar',publication:frame.publication,lease:frame.lease,id:'bar:applications'}}));
  check('actual policy action emits catalog request',r.policyPackets.some(packet=>(packet.requests||[]).some(x=>x.kind==='catalog-request'))&&!r.policyPackets.some(packet=>forbidden((packet.requests||[]).map(x=>x.kind))),r);
  await send('reset');r=await send('policy',gateway('view-action',a));
  check('renderer gateway cannot claim attachment',!r.policyApplicationOnly,r);
 } catch(err){report.failures.push({name:'harness exception',message:String(err.stack||err)});}
 report.passed=report.failures.length===0;fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');if(!report.passed)process.exitCode=1;
})();
