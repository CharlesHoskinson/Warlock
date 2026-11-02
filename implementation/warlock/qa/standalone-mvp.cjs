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
const noReservation=state=>!state.launchPending&&!state.launchUncertain&&state.launchStatus==='Idle'&&state.jumpEntry===null&&!state.jumpOpening&&state.jumpExpected===null&&!state.windowChoiceReserved;
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
    check('catalog exposes pin and truthful app-only unavailable launch/jump details '+seed,r.frame.status==='Type to search applications.'&&r.frame.popup.some(c=>c.id==='pin:sample.desktop'&&c.enabled&&c.detail==='Add to taskbar')&&r.frame.popup.some(c=>c.id==='entry:sample.desktop'&&!c.enabled&&c.detail==='Opening unavailable in this session')&&r.frame.popup.some(c=>c.id==='jump:open:sample.desktop'&&!c.enabled&&c.detail==='Application actions unavailable in this session'),r.frame.popup);
    r=await send('search','sam');
    check('app-only matching query reports opening unavailable without native requests '+seed,r.applicationOnly&&r.query==='sam'&&r.frame.status==='Matching applications are shown, but opening is unavailable in this session.'&&r.frame.popup.some(c=>c.id==='entry:sample.desktop'&&!c.enabled&&c.detail==='Opening unavailable in this session')&&r.frame.popup.some(c=>c.id==='jump:open:sample.desktop'&&!c.enabled&&c.detail==='Application actions unavailable in this session')&&r.requests.length===0,r);
    r=await send('surface-action',{surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:r.frame.publication,lease:'1',id:'entry:sample.desktop'});
    check('app-only disabled entry Surface.resolve is rejected and emits zero requests while preserving query and reservation '+seed,!r.resolved&&r.applicationOnly&&r.open&&r.query==='sam'&&r.frame.popup.some(c=>c.id==='entry:sample.desktop'&&!c.enabled)&&r.requests.length===0&&noReservation(r),r);
    r=await send('surface-action',{surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:r.frame.publication,lease:'1',id:'jump:open:sample.desktop'});
    check('app-only disabled jump Surface.resolve is rejected and emits zero requests while preserving query and reservation '+seed,!r.resolved&&r.applicationOnly&&r.open&&r.query==='sam'&&r.frame.popup.some(c=>c.id==='jump:open:sample.desktop'&&!c.enabled)&&r.requests.length===0&&noReservation(r),r);
    r=await send('surface-action',{surfaceProtocol:2,kind:'surface-context',surface:'popup',publication:r.frame.publication,lease:'1',id:'entry:sample.desktop',trigger:'pointer',x:12,y:12});
    check('app-only entry context Surface.resolve is rejected and emits zero requests while preserving query and reservation '+seed,!r.resolved&&r.applicationOnly&&r.open&&r.query==='sam'&&r.frame.popup.some(c=>c.id==='entry:sample.desktop'&&!c.enabled)&&r.requests.length===0&&noReservation(r),r);
    r=await send('search','no-such-app');
    check('app-only non-matching query reports no matching applications '+seed,r.applicationOnly&&r.query==='no-such-app'&&r.frame.status==='No matching applications. Change your search or Refresh.'&&!r.frame.popup.some(c=>c.id.startsWith('entry:'))&&r.requests.length===0,r);
    const close=r.frame.popup.filter(c=>c.id==='control:close');
    check('close applications has honest label and accessible name '+seed,close.length===1&&close[0].label==='Close applications'&&close[0].ariaLabel==='Close applications and return to windows'&&close[0].enabled,r.frame.popup);
    const closeAction={surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:'1',lease:'1',id:'control:close'};
    r=await send('surface-action',{...closeAction,publication:'2'});
    check('future-publication close action cannot dismiss applications '+seed,!r.resolved&&r.open&&r.publication==='1'&&r.frame.publication==='1'&&r.requests.length===0,r);
    r=await send('advance-publication');
    check('checked publication advances to 2 while applications stay open '+seed,r.open&&r.publication==='2'&&r.frame.publication==='2'&&r.requests.length===0,r);
    r=await send('surface-action',{...closeAction,publication:'1'});
    check('stale prior-publication close action cannot dismiss applications '+seed,!r.resolved&&r.open&&r.publication==='2'&&r.frame.publication==='2'&&r.requests.length===0,r);
    r=await send('surface-action',{...closeAction,publication:'2'});
    check('current close action dismisses without native request '+seed,r.resolved&&!r.open&&r.pendingCatalog===null&&r.requests.length===0,r);
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
  r=await send('reset');
  check('reachable Desktop.initial negative control has Connecting status and disabled bar:reconnect',!r.applicationOnly&&r.frame.status==='Connecting…'&&r.frame.bar.some(c=>c.id==='bar:reconnect'&&!c.enabled)&&['bar:overview','bar:switcher','bar:notifications','bar:files','bar:system','bar:settings'].every(id=>r.frame.bar.some(c=>c.id===id&&!c.enabled)),r.frame);
  await send('native',a);r=await send('open');
  const pinCatReq=r.requests.find(x=>x.kind==='catalog-request');
  if(!pinCatReq)throw Error('app-only pin catalog request missing');
  r=await send('native',{protocolVersion:3,kind:'application-catalog',binding:b,requestId:pinCatReq.requestId,snapshot:{catalogProtocol:2,lifetime:b.lifetime,generation:'1',entries:[{id:'sample.desktop',name:'Sample',iconHint:'',wmclass:'',genericName:'',keywords:[]},{id:'second.desktop',name:'Second',iconHint:'',wmclass:'',genericName:'',keywords:[]}]},preferences:{revision:'1',identities:['sample.desktop','second.desktop']}});
  check('app-only pinned taskbar button explains opening unavailable and first pin-left is boundary-disabled while Pins writable',r.applicationOnly&&r.frame.bar.some(c=>c.id==='bar:pin:sample.desktop'&&!c.enabled&&c.detail==='Pinned · Opening unavailable in this session')&&r.frame.popup.some(c=>c.id==='pin-left:sample.desktop'&&!c.enabled&&c.detail==='Pin order')&&r.frame.popup.some(c=>c.id==='pin-right:sample.desktop'&&c.enabled&&c.detail==='Pin order'),r.frame);
  r=await send('search','sam');
  r=await send('surface-action',{surfaceProtocol:2,kind:'surface-action',surface:'bar',publication:r.frame.publication,lease:'1',id:'bar:pin:sample.desktop'});
  check('app-only disabled bar:pin Surface.resolve is rejected and emits zero requests while preserving query and reservation',!r.resolved&&r.applicationOnly&&r.open&&r.query==='sam'&&r.frame.bar.some(c=>c.id==='bar:pin:sample.desktop'&&!c.enabled)&&r.requests.length===0&&noReservation(r),r);
  r=await send('surface-action',{surfaceProtocol:2,kind:'surface-context',surface:'bar',publication:r.frame.publication,lease:'1',id:'bar:pin:sample.desktop',trigger:'pointer',x:8,y:8});
  check('app-only disabled bar:pin context Surface.resolve is rejected and emits zero requests while preserving query and reservation',!r.resolved&&r.applicationOnly&&r.open&&r.query==='sam'&&r.frame.bar.some(c=>c.id==='bar:pin:sample.desktop'&&!c.enabled)&&r.requests.length===0&&noReservation(r),r);
  r=await send('search','');
  r=await send('pin','sample.desktop');
  check('reachable Pins.Pending negative control emits Saving pin order status and disables pin actions',r.frame.status==='Saving pin order…'&&r.frame.popup.some(c=>c.id==='unpin:second.desktop'&&!c.enabled&&c.detail==='Pinned application')&&r.frame.popup.some(c=>c.id==='pin-left:second.desktop'&&!c.enabled&&c.detail==='Pin order'),r.frame);
  r=await send('native',{protocolVersion:3,kind:'host-disconnected'});
  check('reachable disconnected negative control exposes reconnect, retires cached pin controls, and keeps Applications unavailable guidance',!r.applicationOnly&&r.shell.phase==='Detached'&&r.shell.available===false&&r.shell.reconnecting===false&&r.shell.status==='Connection lost. Reconnect to continue.'&&r.frame.mode==='applications'&&r.frame.status==='Application list unavailable. Refresh to try again.'&&r.catalogIds.length===0&&r.pendingCatalog===null&&r.frame.bar.some(c=>c.id==='bar:reconnect'&&c.enabled)&&!r.frame.bar.some(c=>c.id.startsWith('bar:pin:'))&&r.requests.length===0,r);
  r=await send('reconnect');
  check('reachable Reconnecting negative control disables reconnect, reports Shell reconnecting state, and retains Applications unavailable guidance',!r.applicationOnly&&r.shell.phase==='Detached'&&r.shell.available===false&&r.shell.reconnecting===true&&r.shell.status==='Reconnecting…'&&r.frame.mode==='applications'&&r.frame.status==='Application list unavailable. Refresh to try again.'&&r.catalogIds.length===0&&r.pendingCatalog===null&&r.frame.bar.some(c=>c.id==='bar:reconnect'&&!c.enabled)&&!r.frame.bar.some(c=>c.id.startsWith('bar:pin:'))&&r.requests.length===0,r);
  const readyFullSession=async()=>{
   await send('reset');let state=await send('native',{protocolVersion:3,kind:'attached',binding:b});
   const projReq=state.requests.find(x=>x.kind==='projection-request');
   if(!projReq)throw Error('legacy projection request missing');
   state=await send('native',{protocolVersion:3,kind:'action-projection',binding:b,requestId:projReq.requestId,context:{lifetime:b.lifetime,epoch:b.frontend,output:'1',revision:'1'},scene:{revision:'1',focused:null,windows:[]}});
   await send('pointer-ready');state=await send('open');
   const catReq=state.requests.find(x=>x.kind==='catalog-request');
   if(!catReq)throw Error('legacy catalog request missing');
   state=await send('native',{protocolVersion:3,kind:'application-catalog',binding:b,requestId:catReq.requestId,snapshot:{catalogProtocol:2,lifetime:b.lifetime,generation:'1',entries:[{id:'sample.desktop',name:'Sample',iconHint:'',wmclass:'',genericName:'',keywords:[]}]},preferences:{revision:'1',identities:['sample.desktop']}});
   return send('search','sam');
  };
  await send('reset');r=await send('native',{protocolVersion:3,kind:'attached',binding:b});
  check('legacy native attach retains original reads',!r.applicationOnly&&['projection-request','catalog-request','shell-settings-request','motion-preferences-request','shortcut-preferences-request'].every(k=>kinds(r).includes(k)),r);
  check('legacy binding keeps utility admission unchanged and reconciling disables overview/switcher with Updating window information',['bar:notifications','bar:files','bar:system','bar:settings'].every(id=>r.frame.bar.some(c=>c.id===id&&c.enabled))&&r.frame.status==='Updating window information…'&&['bar:overview','bar:switcher'].every(id=>r.frame.bar.some(c=>c.id===id&&!c.enabled)),r.frame.bar);
  // QA prelude arranges a current idle native pointer observation + reconciled empty projection; no native input is run.
  r=await readyFullSession();
  check('full-session Shell.Ready match retains ordinary guidance and enables entry, jump, bar:pin, overview, and switcher',!r.applicationOnly&&r.shell.available&&r.query==='sam'&&noReservation(r)&&r.frame.status==='Choose a matching application.'&&r.frame.popup.some(c=>c.id==='entry:sample.desktop'&&c.enabled&&c.detail==='')&&r.frame.popup.some(c=>c.id==='jump:open:sample.desktop'&&c.enabled&&c.detail==='Application actions and recent files')&&r.frame.bar.some(c=>c.id==='bar:pin:sample.desktop'&&c.enabled&&c.detail==='Pinned launcher')&&['bar:overview','bar:switcher'].every(id=>r.frame.bar.some(c=>c.id===id&&c.enabled))&&r.requests.length===0,r);
  r=await send('surface-action',{surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:r.frame.publication,lease:'1',id:'jump:open:sample.desktop'});
  check('non-vacuity positive control 1: full-session jump:open surface-action resolves and emits jump-list-request',r.resolved&&r.jumpEntry==='sample.desktop'&&r.jumpExpected!==null&&r.frame.mode==='jump'&&r.frame.status==='Reading application actions…'&&r.requests.length===1&&r.requests[0].kind==='jump-list-request'&&r.requests[0].entry==='sample.desktop',r);
  r=await readyFullSession();
  r=await send('surface-action',{surfaceProtocol:2,kind:'surface-context',surface:'popup',publication:r.frame.publication,lease:'1',id:'entry:sample.desktop',trigger:'pointer',x:12,y:12});
  check('non-vacuity positive control 2: full-session popup entry surface-context resolves and emits jump-list-request',r.resolved&&r.jumpEntry==='sample.desktop'&&r.jumpExpected!==null&&r.frame.mode==='jump'&&r.requests.length===1&&r.requests[0].kind==='jump-list-request'&&r.requests[0].entry==='sample.desktop',r);
  r=await readyFullSession();
  r=await send('surface-action',{surfaceProtocol:2,kind:'surface-context',surface:'bar',publication:r.frame.publication,lease:'1',id:'bar:pin:sample.desktop',trigger:'pointer',x:8,y:8});
  check('non-vacuity positive control 3: full-session bar:pin surface-context resolves and emits jump-list-request',r.resolved&&r.jumpEntry==='sample.desktop'&&r.jumpExpected!==null&&r.frame.mode==='jump'&&r.requests.length===1&&r.requests[0].kind==='jump-list-request'&&r.requests[0].entry==='sample.desktop',r);
  r=await readyFullSession();
  r=await send('surface-action',{surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:r.frame.publication,lease:'1',id:'entry:sample.desktop'});
  const launchRequests=r.requests.filter(x=>x.kind==='application-launch');
  check('non-vacuity positive control 4: full-session entry surface-action resolves, emits exactly one application-launch, and disables entry with Opening application status',r.resolved&&!r.applicationOnly&&r.launchPending&&!r.launchUncertain&&r.launchStatus==='Pending'&&r.requests.length===1&&launchRequests.length===1&&r.frame.status==='Opening application…'&&r.frame.popup.some(c=>c.id==='entry:sample.desktop'&&!c.enabled&&c.detail===''),r);
  r=await send('surface-action',{surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:r.frame.publication,lease:'1',id:'entry:sample.desktop'});
  check('full-session Launch.Pending negative control rejects duplicate entry surface-action at Surface.resolve with zero extra requests',!r.resolved&&!r.applicationOnly&&r.launchPending&&!r.launchUncertain&&r.launchStatus==='Pending'&&r.query==='sam'&&r.requests.length===0,r);
  r=await send('surface-action',{surfaceProtocol:2,kind:'surface-action',surface:'bar',publication:r.frame.publication,lease:'1',id:'bar:pin:sample.desktop'});
  check('full-session Launch.Pending negative control refuses duplicate bar:pin launch at Launch.start with zero extra requests',!r.applicationOnly&&r.launchPending&&!r.launchUncertain&&r.launchStatus==='Pending'&&r.query==='sam'&&r.requests.length===0,r);
  r=await readyFullSession();
  r=await send('surface-action',{surfaceProtocol:2,kind:'surface-action',surface:'bar',publication:r.frame.publication,lease:'1',id:'bar:pin:sample.desktop'});
  check('non-vacuity positive control 5: full-session bar:pin surface-action resolves and emits exactly one application-launch',r.resolved&&!r.applicationOnly&&r.launchPending&&!r.launchUncertain&&r.launchStatus==='Pending'&&r.requests.length===1&&r.requests[0].kind==='application-launch'&&r.frame.status==='Opening application…',r);
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
