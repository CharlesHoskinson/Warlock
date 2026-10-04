'use strict';
const fs=require('fs'),assert=require('assert/strict');
const app=require(process.argv[2]).Elm.MenuSurfaceReplay.init({flags:null});
const base=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),geo=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));
const clone=x=>JSON.parse(JSON.stringify(x)),native=frame=>({kind:'native',frame}),cases=[];
const baseline=[{kind:'owner',frame:base.owner},native(base.attached),native(base.projection),native({protocolVersion:3,kind:'host-geometry-negotiate'}),native(geo.attach),native(geo.facts)];
const timer=setTimeout(()=>{throw Error('Post-close CPU replay deadline')},30000);
function replay(events){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows)};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events)})}
async function check(name,events,verify){let rows;try{rows=await replay(events);verify(rows,rows.at(-1));cases.push({name,passed:true,rows})}catch(error){cases.push({name,passed:false,error:String(error),rows});console.error(name,error.stack)}}
const context=(frame,application='org.a')=>({kind:'action',action:{surfaceProtocol:2,kind:'surface-context',surface:'bar',publication:frame.publication,lease:frame.lease,id:'bar:group:application:'+application,trigger:'pointer',x:40,y:20}});
const action=(frame,id)=>({kind:'action',action:{surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:frame.publication,lease:frame.lease,id}});
const commands=rows=>rows.flatMap(row=>row.requests.filter(x=>x.kind==='window-effect'));
function noCommands(rows){assert.deepEqual(commands(rows),[])}
function observed(selection){
 const requests=selection.requests;const p=clone(base.projection),g=clone(geo.facts);
 p.requestId=requests.find(r=>r.kind==='projection-request').requestId;p.context.revision=p.scene.revision='2';p.scene.focused='20';
 g.requestId=requests.find(r=>r.kind==='geometry-facts-request').requestId;g.revision='102';g.sequence='2';g.facts.focused='20';return {p,g};
}
(async()=>{
 const ready=(await replay(baseline)).at(-1).frame,opened=[...baseline,context(ready)],menu=(await replay(opened)).at(-1);
 const selectMax=action(menu.frame,'menu:1:2'),selected=[...opened,selectMax],waiting=(await replay(selected)).at(-1),fresh=observed(waiting);
 await check('selection closes presentation and allocates only correlated observations',selected,(rows,last)=>{noCommands(rows);assert.equal(last.frame.mode,'closed');assert.deepEqual(last.requests.map(r=>r.kind),['projection-request','geometry-facts-request']);assert.equal(last.shell.effects.request,'0');assert.equal(last.shell.effects.generation,'0');assert.equal(last.registry,0);assert.equal(last.outstanding,1);assert(last.preparedToken)});
 await check('legacy response alone cannot produce native intent',[...selected,native(fresh.p)],(rows,last)=>{noCommands(rows);assert.equal(last.registry,0);assert.equal(last.shell.effects.request,'0');assert(last.preparedToken)});
 await check('geometry response alone cannot produce native intent',[...selected,native(fresh.g)],(rows,last)=>{noCommands(rows);assert.equal(last.registry,0);assert.equal(last.shell.effects.request,'0');assert(last.preparedToken)});
 const readyPair=[...selected,native(fresh.p),native(fresh.g)];
 await check('benign focus revision change permits exactly one fresh maximize intent',readyPair,(rows,last)=>{const sent=commands(rows);assert.equal(sent.length,1);assert.deepEqual(sent[0],{protocolVersion:3,kind:'window-effect',effectProtocol:2,binding:base.binding,intent:{request:'1',generation:'1',incarnation:'10',operation:'maximize',context:{lifetime:'100',epoch:'300',output:'1',revision:'102'}}});assert.equal(last.registry,1);assert.equal(last.outstanding,1);assert.equal(last.preparedToken,null);assert.equal(last.unresolved[0].status,'Pending')});
 await check('reverse dual-response order dispatches exactly once',[...selected,native(fresh.g),native(fresh.p)],rows=>{assert.equal(commands(rows).length,1);assert.equal(commands(rows)[0].intent.context.revision,'102')});
 await check('duplicate dual facts never replay prepared intent',[...readyPair,native(fresh.p),native(fresh.g),selectMax],rows=>assert.equal(commands(rows).length,1));
 await check('duplicate old scoped selection cannot replace reserved slot',[...selected,selectMax,selectMax],(rows,last)=>{noCommands(rows);assert.equal(last.preparedToken,waiting.preparedToken);assert.equal(last.outstanding,1);assert.equal(last.shell.request,waiting.shell.request)});

 await check('application opener cannot create competing popup while selection prepared',[...selected,{kind:'open'},native(fresh.p),native(fresh.g)],(rows,last)=>{assert.equal(rows[selected.length].frame.mode,'closed');assert.equal(commands(rows).length,1);assert.equal(last.frame.mode,'closed')});
 await check('partial legacy readiness flag is authentic stream only',[...selected,native(fresh.p)],(_,last)=>{assert.equal(last.prepared.legacyReady,true);assert.equal(last.prepared.geometryReady,false);assert.equal(last.prepared.legacyRequest,fresh.p.requestId);assert.equal(last.prepared.geometryRequest,fresh.g.requestId)});
 await check('partial geometry readiness flag is authentic stream only',[...selected,native(fresh.g)],(_,last)=>{assert.equal(last.prepared.legacyReady,false);assert.equal(last.prepared.geometryReady,true)});

 for(const field of ['outputId','providerId']){
  const owner=clone(base.owner);owner[field]='2';
  await check('conflicting registered '+field+' cancels unsent preparation',[...selected,{kind:'owner',frame:owner},native(fresh.p),native(fresh.g)],(rows,last)=>{noCommands(rows);assert.equal(last.preparedToken,null);assert.equal(last.outstanding,0);assert.equal(last.ownerExhausted,true)})
 }
 const pendingBarAction={kind:'action',action:{surfaceProtocol:2,kind:'surface-action',surface:'bar',publication:waiting.frame.publication,lease:waiting.frame.lease,id:'bar:group:application:org.b'}};
 await check('ordinary unrelated taskbar action cannot bypass prepared slot',[...selected,pendingBarAction],(rows,last)=>{noCommands(rows);assert.equal(last.preparedToken,waiting.preparedToken);assert.equal(last.shell.effects.request,'0')});
 // Unsupported geometry uses legacy observation only; the original deferred
 // target remains canonical even when its application has multiple families.
 const observeAttach=clone(geo.attach),observeGeometry=clone(geo.facts),observeProjection=clone(base.projection);
 observeAttach.capabilities.effects=false;observeAttach.capabilities.operations=[];
 observeGeometry.facts.windows.forEach(w=>w.capabilities={maximize:false,restoreGeometry:false});
 observeProjection.scene.windows.find(w=>w.incarnation==='20').application='org.a';
 const observeBaseline=[...baseline.slice(0,2),native(observeProjection),baseline[3],native(observeAttach),native(observeGeometry)],observeReady=(await replay(observeBaseline)).at(-1),observePicker=[...observeBaseline,context(observeReady.frame)],picker=(await replay(observePicker)).at(-1);
 const pickerContext={kind:'action',action:{surfaceProtocol:2,kind:'surface-context',surface:'popup',publication:picker.frame.publication,lease:picker.frame.lease,id:'family:10',trigger:'pointer',x:40,y:20}};
 const observeOpened=[...observePicker,pickerContext],observeMenu=(await replay(observeOpened)).at(-1),observeSelected=[...observeOpened,action(observeMenu.frame,'menu:1:1')],observeWaiting=(await replay(observeSelected)).at(-1);
 const op=clone(observeProjection);op.requestId=observeWaiting.requests.find(r=>r.kind==='projection-request').requestId;op.context.revision=op.scene.revision='2';
 const pickerAction={kind:'action',action:{surfaceProtocol:2,kind:'surface-action',surface:'bar',publication:observeWaiting.frame.publication,lease:observeWaiting.frame.lease,id:'bar:group:application:org.a'}};
 await check('unsupported geometry stages one legacy stream and no fabricated geometry wait',observeSelected,(rows,last)=>{noCommands(rows);assert.deepEqual(last.requests.map(x=>x.kind),['projection-request']);assert.equal(last.prepared.geometryRequest,null);assert.equal(last.prepared.geometryReady,true)});
 await check('multifamily application cannot open competing picker while prepared',[...observeSelected,pickerAction],(rows,last)=>{noCommands(rows);assert.equal(last.frame.mode,'closed');assert(last.preparedToken)});
 await check('unsupported geometry correlated legacy response dispatches one Minimize',[...observeSelected,pickerAction,native(op)],rows=>{const sent=commands(rows);assert.equal(sent.length,1);assert.equal(sent[0].effectProtocol,1);assert.equal(sent[0].intent.operation,'minimize');assert.equal(sent[0].intent.incarnation,'10');assert.equal(sent[0].intent.context.revision,'2')});
 const notification=native({protocolVersion:3,kind:'host-refresh'});
 await check('notifications preserve exact prepared observation IDs and one dirty bit',[...selected,...Array(20).fill(notification)],(rows,last)=>{noCommands(rows);assert.equal(last.shell.request,waiting.shell.request);assert.equal(last.preparedToken,waiting.preparedToken);assert.equal(last.shell.notificationQueued,true)});
 await check('notification burst then exact pair produces one effect',[...selected,...Array(20).fill(notification),native(fresh.p),native(fresh.g)],rows=>assert.equal(commands(rows).length,1));

 const selectMin=action(menu.frame,'menu:1:1'),waitingMin=[...opened,selectMin],minObservations=observed((await replay(waitingMin)).at(-1));
 await check('legacy Minimize stages and uses fresh legacy revision without geometry intent',[...waitingMin,native(minObservations.p),native(minObservations.g)],rows=>{const sent=commands(rows);assert.equal(sent.length,1);assert.equal(sent[0].effectProtocol,1);assert.equal(sent[0].intent.operation,'minimize');assert.equal(sent[0].intent.context.revision,'2');assert.equal(sent[0].intent.incarnation,'10')});
 const minProjection=clone(base.projection),minGeometry=clone(geo.facts);
 minProjection.scene.windows.filter(w=>['10','11'].includes(w.incarnation)).forEach(w=>w.minimized=true);
 minGeometry.facts.windows.filter(w=>['10','11'].includes(w.incarnation)).forEach(w=>{w.minimized=true;w.nativeMode=w.clientMode='maximized';w.geometryEligible=false;w.capabilities={maximize:false,restoreGeometry:false}});
 const minBaseline=[...baseline.slice(0,2),native(minProjection),...baseline.slice(3,5),native(minGeometry)];
 const minReady=(await replay(minBaseline)).at(-1),minOpen=[...minBaseline,context(minReady.frame)],minMenu=(await replay(minOpen)).at(-1),restoreSelected=[...minOpen,action(minMenu.frame,'menu:1:0')],restoreWaiting=(await replay(restoreSelected)).at(-1);
 const restoreProjection=clone(minProjection),restoreGeometry=clone(minGeometry);restoreProjection.requestId=restoreWaiting.requests.find(x=>x.kind==='projection-request').requestId;restoreProjection.context.revision=restoreProjection.scene.revision='2';restoreGeometry.requestId=restoreWaiting.requests.find(x=>x.kind==='geometry-facts-request').requestId;restoreGeometry.revision='102';restoreGeometry.sequence='2';
 await check('minimized MAX Restore remains legacy unminimize and observed MAX intact',[...restoreSelected,native(restoreProjection),native(restoreGeometry)],(rows,last)=>{const sent=commands(rows);assert.equal(sent.length,1);assert.equal(sent[0].effectProtocol,1);assert.equal(sent[0].intent.operation,'restore');assert.equal(last.geometry.windows[0].mode,'maximized');assert.equal(last.geometry.windows[0].minimized,true)});
 const wrongP=clone(fresh.p);wrongP.requestId='999';const wrongG=clone(fresh.g);wrongG.requestId='998';
 await check('wrong request IDs cannot admit prepared observations',[...selected,native(wrongP),native(wrongG)],(rows,last)=>{noCommands(rows);assert(last.preparedToken);assert.equal(last.registry,0)});
 for(const field of ['lifetime','session','frontend']){
  const p=clone(fresh.p),g=clone(fresh.g);p.binding[field]='999';g.binding[field]='999';
  await check('wrong '+field+' refuses preparation admission',[...selected,native(p),native(g)],rows=>noCommands(rows));
 }

 await check('wrong correlation followed by exact facts still dispatches once',[...selected,native(wrongP),native(wrongG),native(fresh.p),native(fresh.g)],rows=>assert.equal(commands(rows).length,1));

 for(const [name,change] of [['bool protocol',p=>p.protocolVersion=true],['missing window field',p=>delete p.scene.windows[0].available],['duplicate incarnation',p=>p.scene.windows.push(clone(p.scene.windows[0]))],['regressed legacy revision',p=>p.context.revision=p.scene.revision='0']]){
  const p=clone(fresh.p);change(p);await check(name+' cannot mark legacy stream ready',[...selected,native(p),native(fresh.g)],(rows,last)=>{noCommands(rows);assert.equal(last.prepared.legacyReady,false);assert.equal(last.prepared.geometryReady,true)})
 }
 for(const [name,change] of [['bool geometry protocol',g=>g.geometryProtocol=true],['missing geometry field',g=>delete g.facts.windows[0].workArea],['regressed geometry revision',g=>g.revision='100'],['regressed output generation',g=>g.outputGeneration='0']]){
  const g=clone(fresh.g);change(g);await check(name+' cannot mark geometry stream ready',[...selected,native(fresh.p),native(g)],(rows,last)=>{noCommands(rows);assert.equal(last.prepared.legacyReady,true);assert.equal(last.prepared.geometryReady,false)})
 }
 const mutations=[
  ['retired selected family',(p,g)=>{p.scene.windows=p.scene.windows.filter(w=>!['10','11'].includes(w.incarnation));g.facts.windows=g.facts.windows.filter(w=>!['10','11'].includes(w.incarnation))}],
  ['selected target replaced',(p,g)=>{p.scene.windows.filter(w=>w.incarnation==='10').forEach(w=>w.incarnation='99');p.scene.windows.filter(w=>w.owner==='10').forEach(w=>w.owner='99');g.facts.windows.filter(w=>w.incarnation==='10').forEach(w=>w.incarnation='99');g.facts.windows.filter(w=>w.owner==='10').forEach(w=>w.owner='99')}],
  ['changed family ownership',(p,g)=>{p.scene.windows.find(w=>w.incarnation==='11').owner='20';g.facts.windows.find(w=>w.incarnation==='11').owner='20'}],
  ['selected legacy availability',(p,g)=>{p.scene.windows.find(w=>w.incarnation==='10').available=false}],
  ['changed minimized state',(p,g)=>{p.scene.windows.filter(w=>['10','11'].includes(w.incarnation)).forEach(w=>w.minimized=true);g.facts.windows.filter(w=>['10','11'].includes(w.incarnation)).forEach(w=>w.minimized=true);g.facts.windows[0].geometryEligible=false;g.facts.windows[0].capabilities.maximize=false}],
  ['changed workspace',(p,g)=>{g.facts.windows.filter(w=>['10','11'].includes(w.incarnation)).forEach(w=>{w.workspace='-2';w.workspaceGeneration='51'})}],
  ['changed workspace ownership generation',(p,g)=>{g.facts.windows.forEach(w=>w.workspaceGeneration='51')}],
  ['changed output ownership',(p,g)=>{g.facts.windows.forEach(w=>w.outputOwnershipGeneration='61')}],
  ['changed workarea revision',(p,g)=>{g.facts.windows.forEach(w=>w.workAreaRevision='71')}],
  ['changed workarea geometry',(p,g)=>{g.facts.windows.forEach(w=>w.workArea=[0,0,700,600])}],
  ['changed logical placement',(p,g)=>{g.facts.windows[0].logicalGeometry=[84,61,320,180]}],
  ['changed visual placement',(p,g)=>{g.facts.windows[0].visualGeometry=[83,62,320,180]}],
  ['changed native mode',(p,g)=>{g.facts.windows[0].nativeMode=g.facts.windows[0].clientMode='maximized';g.facts.windows[0].capabilities.maximize=false}],
  ['revoked operation capability',(p,g)=>{g.facts.windows[0].capabilities.maximize=false}],
  ['changed fixed size',(p,g)=>{g.facts.windows[0].fixedSize=true;g.facts.windows[0].geometryEligible=false;g.facts.windows[0].capabilities.maximize=false}],
  ['new input blocker',(p,g)=>{g.facts.inputBlocked=true;g.facts.windows.forEach(w=>{w.geometryEligible=false;w.capabilities={maximize:false,restoreGeometry:false}})}],
  ['native output dependency change',(p,g)=>{p.context.output='2';g.outputGeneration='2'}]
 ];
 for(const [name,mutate] of mutations){const p=clone(fresh.p),g=clone(fresh.g);mutate(p,g);await check(name+' cannot retarget prepared operation',[...selected,native(p),native(g)],(rows,last)=>{noCommands(rows);assert.equal(last.geometry.revision,g.revision,'changed observation must actually be admitted');assert.equal(last.preparedToken,null,'valid incompatible observation must cancel')})}
 await check('exact preparation deadline removes local reservation without native allocation',[...selected,{kind:'prepared-deadline',token:waiting.preparedToken},native(fresh.p),native(fresh.g)],(rows,last)=>{noCommands(rows);assert.equal(last.preparedToken,null);assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.equal(last.shell.effects.request,'0')});

 await check('explicit matching cancel clears only unsent reservation',[...selected,{kind:'prepared-cancel',token:waiting.preparedToken},native(fresh.p),native(fresh.g)],(rows,last)=>{noCommands(rows);assert.equal(last.preparedToken,null);assert.equal(last.outstanding,0);assert.equal(last.registry,0)});
 await check('stale explicit cancellation cannot cancel current preparation',[...selected,{kind:'prepared-cancel',token:'999999'},native(fresh.p),native(fresh.g)],rows=>assert.equal(commands(rows).length,1));
 await check('stale preparation deadline cannot cancel current slot',[...selected,{kind:'prepared-deadline',token:'999999'},native(fresh.p),native(fresh.g)],rows=>assert.equal(commands(rows).length,1));
 await check('connection loss cancels unsent preparation without inventing Unknown execution',[...selected,native({protocolVersion:3,kind:'host-disconnected'}),native(fresh.p),native(fresh.g)],(rows,last)=>{noCommands(rows);assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.equal(last.preparedToken,null)});

 // Build an independently correlated sent/Unknown operation on B, then prepare A.
 const openedB=[...baseline,context(ready,'org.b')],menuB=(await replay(openedB)).at(-1);
 const selectedB=[...openedB,action(menuB.frame,'menu:1:2')],waitB=(await replay(selectedB)).at(-1),freshB=observed(waitB);
 const sentB=[...selectedB,native(freshB.p),native(freshB.g)],sentBRows=await replay(sentB),commandB=commands(sentBRows)[0];
 const unknownB={...clone(commandB),kind:'effect-outcome',status:'Unknown',reason:'QA synthetic delivery uncertainty',revision:'102',outputGeneration:'1'};
 const unknownEvents=[...sentB,native(unknownB)],unknownWaiting=(await replay(unknownEvents)).at(-1),unknownFacts=observed(unknownWaiting);
 unknownFacts.p.context.revision=unknownFacts.p.scene.revision='3';unknownFacts.g.sequence='3';
 const unknownReady=[...unknownEvents,native(unknownFacts.p),native(unknownFacts.g)],unknownState=(await replay(unknownReady)).at(-1);
 await check('observation cannot clear original Unknown key',unknownReady,(_,last)=>{assert.equal(last.registry,1);assert.equal(last.outstanding,1);assert.equal(last.unresolved[0].status,'Unknown');assert.deepEqual(last.unresolved[0].intent,commandB.intent)});
 const openedA=[...unknownReady,context(unknownState.frame)],menuA=(await replay(openedA)).at(-1);
 const reserveA=[...openedA,action(menuA.frame,'menu:2:2')],reservedA=(await replay(reserveA)).at(-1),freshA=observed(reservedA);
 freshA.p.context.revision=freshA.p.scene.revision='4';freshA.g.revision='103';freshA.g.sequence='4';
 await check('unrelated preparation preserves original sent Unknown registry',reserveA,(_,last)=>{assert(last.preparedToken);assert.equal(last.registry,1);assert.equal(last.outstanding,2);assert.deepEqual(last.unresolved[0].intent,commandB.intent);assert.equal(last.unresolved[0].status,'Unknown')});
 await check('cancel unrelated unsent slot preserves old Unknown exact key',[...reserveA,{kind:'prepared-deadline',token:reservedA.preparedToken}],(_,last)=>{assert.equal(last.preparedToken,null);assert.equal(last.registry,1);assert.equal(last.outstanding,1);assert.deepEqual(last.unresolved[0].intent,commandB.intent);assert.equal(last.unresolved[0].status,'Unknown')});
 await check('unrelated prepared intent dispatches fresh without clearing Unknown',[...reserveA,native(freshA.p),native(freshA.g)],(rows,last)=>{assert.equal(commands(rows).length,2);assert.equal(last.registry,2);assert.equal(last.outstanding,2);assert(last.unresolved.some(x=>x.status==='Unknown'&&JSON.stringify(x.intent)===JSON.stringify(commandB.intent)));assert.equal(commands(rows)[1].intent.request,'2');assert.equal(commands(rows)[1].intent.incarnation,'10')});
 const passed=cases.every(x=>x.passed);fs.writeFileSync(process.argv[5],JSON.stringify({passed,checks:cases.length,cases,scope:'Independent compiled actual post-close lifecycle with synthetic native observations; no GUI'},null,2)+'\n');clearTimeout(timer);if(!passed)process.exitCode=1;
})().catch(error=>{fs.writeFileSync(process.argv[5],JSON.stringify({passed:false,checks:cases.length,cases,error:String(error)},null,2)+'\n');clearTimeout(timer);console.error(error.stack);process.exitCode=1});
