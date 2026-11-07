'use strict';
// Independent literal expectations; no native fixture, state injection or captured baseline.
const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path'),{isDeepStrictEqual:eq}=require('node:util');
if(process.argv.length!==4)throw Error('fixed compiled-worker/report arguments required');
const [compiled,output]=process.argv.slice(2),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const seeds=Array.from({length:16},(_,i)=>i),report={schema:1,seed:20261106,sequences:16,checks:[],failures:[],traces:[],imageSHA256:sha(compiled),scriptSHA256:sha(__filename),nativeAcceptance:false,originalAcceptance:false,guiAcceptance:false};
let app,waiting;const watchdog=setTimeout(()=>finish(Error('campaign deadline60000ms')),60000);
function check(name,passed,actual){const row={name,passed:passed===true,actual};report.checks.push(row);if(!row.passed)report.failures.push(row);}
function send(kind,value){return new Promise((resolve,reject)=>{if(waiting)return reject(Error('overlapping replay input'));const timer=setTimeout(()=>{waiting=null;reject(Error('response deadline2000ms '+kind));},2000);waiting=r=>{clearTimeout(timer);waiting=null;report.traces.push({input:{kind,value},output:r});resolve(r);};app.ports.incoming.send(value===undefined?{kind}:{kind,value});});}
const binding=i=>({lifetime:String(9007199254741001n+BigInt(i)*7n),session:String(9007199254741103n+BigInt(i)*11n),frontend:String(9007199254741207n+BigInt(i)*13n)});
const attach=(b,ops)=>Object.assign({protocolVersion:3,kind:'application-attached',binding:b,nativeOperations:[]},ops===undefined?{}:{applicationOperations:ops});
const action=id=>({surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:'1',lease:'1',id});
const launches=r=>r.requests.filter(x=>x.kind==='application-launch');
const noWindow=r=>!r.available&&r.pointerObservationAbsent&&r.requests.every(x=>['catalog-request','taskbar-pins-write','application-launch'].includes(x.kind));
const catalog=(b,request)=>({protocolVersion:3,kind:'application-catalog',binding:b,requestId:request,snapshot:{catalogProtocol:2,lifetime:b.lifetime,generation:'1',entries:[{id:'sample.desktop',name:'Sample',iconHint:'',wmclass:'',genericName:'',keywords:[]}]},preferences:{revision:'1',identities:[]}});
const outcome=(b,intent,status,reason)=>({protocolVersion:3,kind:'application-launch-outcome',binding:b,outcome:{catalogProtocol:1,kind:'launch-outcome',intent,status,reason}});
async function load(b){let r=await send('open');const req=r.requests.find(x=>x.kind==='catalog-request');return {r,req,response:catalog(b,req?req.requestId:'1')};}
function finish(error){clearTimeout(watchdog);if(error)report.error=String(error.stack||error);report.passed=!error&&report.failures.length===0;fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));process.exitCode=report.passed?0:1;}
(async()=>{try{app=require(path.resolve(compiled)).Elm.ApplicationAvailabilityReplay.init();app.ports.outgoing.subscribe(r=>{if(waiting)waiting(r);});
for(const seed of seeds){const b=binding(seed),tag='seed'+seed;await send('reset');let r=await send('native',attach(b,['application-launch']));
 check(tag+'/positive-capability-attach',r.applicationOnly&&eq(r.binding,b)&&r.shell.phase==='Reconciling'&&noWindow(r),r);
 let setup=await load(b);check(tag+'/positive-catalog-request',Boolean(setup.req)&&setup.r.open&&noWindow(setup.r),setup.r);
 r=await send('native',{...setup.response,binding:binding(seed+100)});check(tag+'/foreign-catalog-refused',r.catalogIds.length===0&&launches(r).length===0,r);
 r=await send('native',setup.response);check(tag+'/positive-current-catalog',eq(r.catalogIds,['sample.desktop'])&&r.pendingCatalog===null&&noWindow(r),r);
 r=await send('search','sam');check(tag+'/positive-query',r.query==='sam'&&noWindow(r),r);
 check(tag+'/positive-entry-enabled',r.frame.popup.some(c=>c.id==='entry:sample.desktop'&&c.enabled),r.frame);
 r=await send('surface',action('jump:open:sample.desktop'));check(tag+'/jump-guard',!r.resolved&&r.requests.length===0&&noWindow(r),r);
 r=await send('surface',{...action('entry:sample.desktop'),publication:'2'});check(tag+'/stale-surface-refused',!r.resolved&&launches(r).length===0,r);
 r=await send('surface',action('entry:sample.desktop'));const sent=launches(r),intent={request:'1',lifetime:b.lifetime,generation:'1',entry:'sample.desktop'};
 check(tag+'/positive-single-surface-start',r.resolved&&sent.length===1&&eq(sent[0].intent,intent)&&r.launchPending&&r.launchStatus==='Pending'&&eq(sent[0].binding,b)&&noWindow(r),r);
 r=await send('direct-start');check(tag+'/pending-duplicate-blocked',r.launchPending&&launches(r).length===0,r);
 r=await send('native',outcome(binding(seed+100),intent,'Submitted','native-submission-accepted'));check(tag+'/foreign-outcome-refused',r.launchPending&&launches(r).length===0,r);
 r=await send('native',outcome(b,{...intent,request:String(BigInt(intent.request)+1n)},'Submitted','native-submission-accepted'));check(tag+'/stale-outcome-refused',r.launchPending&&launches(r).length===0,r);
 r=await send('deadline');check(tag+'/pending-to-unknown',r.launchUnknown&&!r.launchPending&&r.launchStatus==='Unknown'&&launches(r).length===0,r);
 r=await send('direct-start');check(tag+'/unknown-duplicate-blocked',r.launchUnknown&&launches(r).length===0,r);
 r=await send('native',{protocolVersion:3,kind:'host-disconnected'});check(tag+'/disconnect-clears-authority',!r.applicationOnly&&eq(r.binding,b)&&r.shell.phase==='Detached'&&r.catalogIds.length===0&&launches(r).length===0&&noWindow(r),r);
 r=await send('native',setup.response);check(tag+'/late-catalog-after-disconnect',r.catalogIds.length===0&&launches(r).length===0,r);
 // A separate real attach/catalog route exercises direct Desktop.Start without Surface.
 await send('reset');await send('native',attach(b,['application-launch']));setup=await load(b);await send('native',setup.response);r=await send('direct-start');check(tag+'/positive-direct-start',r.selectionExists&&launches(r).length===1&&r.launchPending&&noWindow(r),r);r=await send('native',outcome(b,intent,'Submitted','native-submission-accepted'));check(tag+'/positive-current-outcome',!r.launchPending&&!r.launchUnknown&&r.launchStatus==='Submitted'&&r.requests.length===0&&noWindow(r),r);
 // Separate literal preference receipt exercises pinned launch on the same real public route.
 await send('reset');await send('native',attach(b,['application-launch']));setup=await load(b);
 r=await send('native',{...setup.response,preferences:{revision:'1',identities:['sample.desktop']}});
 check(tag+'/positive-app-pin-enabled',r.applicationOnly&&r.pointerObservationAbsent&&!r.available&&r.frame.bar.some(c=>c.id==='bar:pin:sample.desktop'&&c.enabled)&&r.requests.length===0,r);
 r=await send('surface',{...action('bar:pin:sample.desktop'),surface:'bar'});
 check(tag+'/positive-app-pin-single-start',r.resolved&&launches(r).length===1&&eq(launches(r)[0].intent,intent)&&r.launchPending&&r.pointerObservationAbsent&&noWindow(r),r);
 r=await send('surface',{...action('bar:pin:sample.desktop'),surface:'bar'});
 check(tag+'/positive-app-pin-pending-duplicate',launches(r).length===0&&r.launchPending&&r.pointerObservationAbsent,r);
 // Native attach is genuinely Reconciling: no injected pointer or Ready state.
 await send('reset');await send('native',{protocolVersion:3,kind:'attached',binding:b});setup=await load(b);
 r=await send('native',{...setup.response,preferences:{revision:'1',identities:['sample.desktop']}});
 check(tag+'/native-reconciling-pin-disabled',!r.applicationOnly&&!r.available&&r.shell.phase==='Reconciling'&&r.pointerObservationAbsent&&r.frame.bar.some(c=>c.id==='bar:pin:sample.desktop'&&!c.enabled),r);
 r=await send('surface',{...action('bar:pin:sample.desktop'),surface:'bar'});
 check(tag+'/native-reconciling-pin-no-effect',!r.resolved&&r.requests.length===0&&!r.launchPending&&!r.available&&r.pointerObservationAbsent,r);
 // Drive the native projection receipt through Incoming, then the public transport-refusal message.
 await send('reset');r=await send('native',{protocolVersion:3,kind:'attached',binding:b});const projection=r.requests.find(x=>x.kind==='projection-request');
 await send('native',{protocolVersion:3,kind:'action-projection',binding:b,requestId:projection?projection.requestId:'1',context:{lifetime:b.lifetime,epoch:b.frontend,output:'1',revision:'1'},scene:{revision:'1',focused:null,windows:[]}});
 setup=await load(b);await send('native',{...setup.response,preferences:{revision:'1',identities:['sample.desktop']}});
 r=await send('transport-refused');check(tag+'/native-transport-refused-pin-disabled',!r.applicationOnly&&r.transportRefused&&!r.available&&r.pointerObservationAbsent&&r.frame.bar.some(c=>c.id==='bar:pin:sample.desktop'&&!c.enabled),r);
 r=await send('surface',{...action('bar:pin:sample.desktop'),surface:'bar'});
 check(tag+'/native-transport-refused-pin-no-effect',!r.resolved&&r.requests.length===0&&!r.launchPending&&!r.available&&r.transportRefused&&r.pointerObservationAbsent,r);

}
const b=binding(0);for(const [name,ops] of [['legacy-absent',undefined],['explicit-empty',[]]]){await send('reset');let r=await send('native',attach(b,ops));check(name+'/attach',r.applicationOnly&&eq(r.binding,b)&&noWindow(r),r);const setup=await load(b);r=await send('native',setup.response);r=await send('surface',action('entry:sample.desktop'));check(name+'/surface-blocked',!r.resolved&&launches(r).length===0&&noWindow(r),r);r=await send('direct-start');check(name+'/direct-bypass-blocked',launches(r).length===0&&!r.launchPending&&!r.launchUnknown&&noWindow(r),r);}
for(const [name,ops] of [['null',null],['string','application-launch'],['unknown',['focus']],['duplicate',['application-launch','application-launch']]]){await send('reset');let r=await send('native',attach(b,ops));check('malformed-'+name+'/attachment-refused',!r.applicationOnly&&r.binding===null&&r.shell.phase==='Detached'&&r.requests.length===0&&noWindow(r),r);r=await send('direct-start');check('malformed-'+name+'/no-bypass',launches(r).length===0&&!r.launchPending,r);}
await send('reset');await send('native',attach(b,['application-launch']));let r=await send('native',attach(binding(99),['application-launch']));check('foreign-repeat-attachment-stutters',eq(r.binding,b)&&launches(r).length===0,r);r=await send('native',attach({...b,frontend:String(BigInt(b.frontend)-1n)},['application-launch']));check('stale-repeat-attachment-stutters',eq(r.binding,b)&&r.requests.length===0,r);r=await send('native',attach(b,[]));check('same-binding-repeat-stutters',eq(r.binding,b)&&r.requests.length===0,r);
for(const id of ['bar:notifications','bar:files','bar:system','bar:settings','bar:overview','bar:switcher']){r=await send('surface',{...action(id),surface:'bar'});check(id+'/native-utility-guard',!r.resolved&&r.requests.length===0&&noWindow(r),r);}
finish();}catch(e){finish(e);}})();
