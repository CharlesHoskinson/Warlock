'use strict';
const fs=require('fs'),assert=require('assert/strict');
const app=require(process.argv[2]).Elm.MenuSurfaceReplay.init({flags:null});
const base=JSON.parse(fs.readFileSync(process.argv[3],'utf8')), fixture=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));
const clone=x=>JSON.parse(JSON.stringify(x)),native=frame=>({kind:'native',frame});
const baseline=[{kind:'owner',frame:base.owner},native(base.attached),native(base.projection)];
const negotiated=[...baseline,native({protocolVersion:3,kind:'host-geometry-negotiate'}),native(fixture.attach),native(fixture.facts)];
const timer=setTimeout(()=>{throw Error('Geometry replay deadline');},20000);
function replay(events){return new Promise(resolve=>{const receive=value=>{app.ports.outgoing.unsubscribe(receive);resolve(value)};app.ports.outgoing.subscribe(receive);app.ports.incoming.send(events)});}
const cases=[];
async function check(name,events,verify){let rows;try{rows=await replay(events);verify(rows,rows.at(-1));cases.push({name,passed:true,rows})}catch(error){cases.push({name,passed:false,error:String(error),rows});console.error(name,error.stack)}}
const action=(frame,id,surface='popup')=>({kind:'action',action:{surfaceProtocol:2,kind:'surface-action',surface,publication:frame.publication,lease:frame.lease,id}});
const context=(frame,id='bar:group:application:org.a')=>({kind:'action',action:{surfaceProtocol:2,kind:'surface-context',surface:'bar',publication:frame.publication,lease:frame.lease,id,trigger:'pointer',x:40,y:20}});
const receipt=(command,status='Committed')=>({...clone(command),kind:'effect-outcome',status,reason:'',revision:'102',outputGeneration:'1'});
async function open(events,target){const frame=(await replay(events)).at(-1).frame;const next=[...events,context(frame,target)];return {events:next,last:(await replay(next)).at(-1)}}
async function observe(events,state,legacyRevision,geometryRevision){
 const last=(await replay(events)).at(-1);const projection=clone(base.projection),facts=clone(fixture.facts);
 const projectionRequest=last.requests.find(x=>x.kind==='projection-request'),geometryRequest=last.requests.find(x=>x.kind==='geometry-facts-request');
 assert(projectionRequest&&geometryRequest,'separate fresh observation requests');
 projection.requestId=projectionRequest.requestId;projection.context.revision=String(legacyRevision);projection.scene.revision=String(legacyRevision);
 for(const w of projection.scene.windows)if(['10','11'].includes(w.incarnation))w.minimized=state.minimized;
 facts.requestId=geometryRequest.requestId;facts.sequence=String(geometryRevision);facts.revision=String(geometryRevision);
 const w=facts.facts.windows.find(w=>w.incarnation==='10');w.nativeMode=w.clientMode=state.mode;w.minimized=state.minimized;w.geometryEligible=!state.minimized;
 w.ordinaryPlacementKnown=state.known;w.capabilities={maximize:state.mode==='ordinary'&&!state.minimized,restoreGeometry:state.mode==='maximized'&&!state.minimized&&state.known};
 w.logicalGeometry=w.visualGeometry=state.mode==='maximized'?[0,0,800,600]:[83,61,320,180];
 facts.facts.windows.find(w=>w.incarnation==='11').minimized=state.minimized;
 return [...events,native(projection),native(facts)];
}
(async()=>{
 const ready=(await replay(negotiated)).at(-1);
 await check('geometry observation separately admitted with independent revision',negotiated,(_,last)=>{assert.equal(last.geometry.revision,'101');assert.equal(last.shell.effects.request,'0');assert.equal(last.requests.length,0);assert.equal(last.shell.effects.windows[0].minimized,false)});
 const ordinary=await open(negotiated);
 await check('negotiated ordinary Restore disabled Maximize enabled frozen table',ordinary.events,(_,last)=>{assert.deepEqual(last.frame.popup.map(x=>[x.label,x.enabled]),[['Close',true],['Restore',false],['Minimize',true],['Maximize',true]])});
 const max=[...ordinary.events,action(ordinary.last.frame,'menu:1:2')];
 await check('Maximize uses actual shared allocator and geometry revision full key',max,(_,last)=>{assert.deepEqual(last.requests,[fixture.maxCommand]);assert.equal(last.registry,1);assert.equal(last.outstanding,1);assert.equal(last.frame.mode,'closed');assert.equal(last.geometry.windows[0].mode,'ordinary');assert.equal(last.shell.effects.windows[0].minimized,false)});
 await check('duplicate geometry callback cannot allocate again',[...max,action(ordinary.last.frame,'menu:1:2')],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.shell.effects.request,'1');assert.equal(last.registry,1)});
 const committed=[...max,native(receipt(fixture.maxCommand))];
 await check('geometry receipt never creates observed maximized state',committed,(_,last)=>{assert.equal(last.geometry.windows[0].mode,'ordinary');assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.equal(last.requests.length,2);assert.deepEqual(last.requests.map(x=>x.kind),['projection-request','geometry-facts-request'])});
 let sequence=await observe(committed,{mode:'maximized',minimized:false,known:true},2,102);
 const maximized=await open(sequence);
 await check('observed maximized supports RestoreGeometry and disabled Maximize',maximized.events,(_,last)=>{assert.deepEqual(last.frame.popup.map(x=>[x.label,x.enabled]),[['Close',true],['Restore',true],['Minimize',true],['Maximize',false]]);assert.equal(last.geometry.windows[0].mode,'maximized')});
 const min=[...maximized.events,action(maximized.last.frame,`menu:${maximized.last.menu.id}:1`)];
 const minCommand=clone(base.firstCommand);minCommand.intent.request='2';minCommand.intent.generation='2';minCommand.intent.context.revision='2';
 await check('Maximized Minimize uses legacy scene revision and next shared IDs',min,(_,last)=>{assert.deepEqual(last.requests,[minCommand]);assert.equal(last.geometry.windows[0].mode,'maximized')});
 sequence=await observe([...min,native(receipt(minCommand))],{mode:'maximized',minimized:true,known:true},3,103);
 const minimized=await open(sequence);
 await check('minimized saved Max keeps legacy Restore and disables Maximize',minimized.events,(_,last)=>{assert.deepEqual(last.frame.popup.map(x=>[x.label,x.enabled]),[['Close',true],['Restore',true],['Minimize',false],['Maximize',false]])});
 const restoreMin=[...minimized.events,action(minimized.last.frame,`menu:${minimized.last.menu.id}:0`)];
 const restoreMinCommand=clone(minCommand);restoreMinCommand.intent={...restoreMinCommand.intent,request:'3',generation:'3',operation:'restore',context:{...restoreMinCommand.intent.context,revision:'3'}};
 await check('Restore minimized remains effect1 restore with next shared IDs',restoreMin,(_,last)=>assert.deepEqual(last.requests,[restoreMinCommand]));
 sequence=await observe([...restoreMin,native(receipt(restoreMinCommand))],{mode:'maximized',minimized:false,known:true},4,104);
 const restoredMax=await open(sequence);
 await check('fresh restore observation retains Maximized mode',restoredMax.events,(_,last)=>{assert.equal(last.geometry.windows[0].mode,'maximized');assert.equal(last.geometry.windows[0].minimized,false)});
 const restoreGeo=[...restoredMax.events,action(restoredMax.last.frame,`menu:${restoredMax.last.menu.id}:0`)];
 const restoreGeoCommand=clone(fixture.maxCommand);restoreGeoCommand.intent={...restoreGeoCommand.intent,request:'4',generation:'4',operation:'restore-geometry',context:{...restoreGeoCommand.intent.context,revision:'104'}};
 await check('RestoreGeometry distinct effect2 uses fourth shared identity',restoreGeo,(_,last)=>assert.deepEqual(last.requests,[restoreGeoCommand]));
 const final=await observe([...restoreGeo,native(receipt(restoreGeoCommand))],{mode:'ordinary',minimized:false,known:false},5,105);
 await check('max min restoreMax restoreGeometry actual pure engine roundtrip',final,(_,last)=>{assert.equal(last.geometry.windows[0].mode,'ordinary');assert.equal(last.shell.effects.windows[0].minimized,false);assert.equal(last.shell.effects.request,'4');assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.deepEqual(last.unresolved,[])});
 const noSupport=clone(fixture.attach);noSupport.capabilities.effects=false;noSupport.capabilities.operations=[];
 const falseFacts=clone(fixture.facts);falseFacts.facts.windows.forEach(w=>w.capabilities={maximize:false,restoreGeometry:false});
 const unsupported=await open([...baseline,{kind:'geometry-attach'},native(noSupport),native(falseFacts)]);
 await check('unadvertised geometry operations absent preserve legacy two rows',unsupported.events,(_,last)=>assert.deepEqual(last.frame.popup.map(x=>x.label),['Close','Restore','Minimize']));
 for(const [name,change] of [['fixedSize',{fixedSize:true}],['constrainedSize',{constrainedSize:true,geometryEligible:false}],['current denied',{capabilities:{maximize:false,restoreGeometry:false}}]]){
  const f=clone(fixture.facts);Object.assign(f.facts.windows[0],change);const opened=await open([...baseline,{kind:'geometry-attach'},native(fixture.attach),native(f)]);
  await check('supported state disabled '+name,opened.events,(_,last)=>{assert.equal(last.frame.popup.find(x=>x.label==='Maximize').enabled,false);assert.equal(last.registry,0)});
 }
 for(const [name,mutate] of [['wrong effect version',r=>r.effectProtocol=1],['wrong binding',r=>r.binding.frontend='301'],['wrong request',r=>r.intent.request='2'],['wrong generation',r=>r.intent.generation='2'],['wrong geometry revision',r=>r.intent.context.revision='1'],['wrong operation',r=>r.intent.operation='restore-geometry']]){
  const bad=receipt(fixture.maxCommand);mutate(bad);await check('geometry full-key rejects '+name,[...max,native(bad)],(_,last)=>{assert.equal(last.registry,1);assert.equal(last.outstanding,1);assert.equal(last.requests.length,0);assert.equal(last.unresolved[0].status,'Pending')});
 }
 const unknown=[...max,native(receipt(fixture.maxCommand,'Unknown'))];
 await check('Unknown keeps both registry and shared native ledger',unknown,(_,last)=>{assert.equal(last.registry,1);assert.equal(last.outstanding,1);assert.equal(last.unresolved[0].status,'Unknown');assert.equal(last.geometry.windows[0].mode,'ordinary')});
 let unknownReady=await observe(unknown,{mode:'ordinary',minimized:false,known:false},2,102);
 const unknownMenu=await open(unknownReady);
 await check('Unknown blocks geometry retry and legacy Minimize same window',[...unknownMenu.events,action(unknownMenu.last.frame,`menu:${unknownMenu.last.menu.id}:1`)],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.registry,1);assert.equal(last.shell.effects.request,'1')});
 const unknownFrame=(await replay(unknownReady)).at(-1).frame;
 await check('Unknown blocks taskbar family activation namespace',[...unknownReady,action(unknownFrame,'bar:group:application:org.a','bar')],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.registry,1);assert.equal(last.shell.effects.request,'1')});
 const disconnected=[...unknownReady,native({protocolVersion:3,kind:'host-disconnected'})];
 const lost=(await replay(disconnected)).at(-1).frame;
 const binding={...base.binding,session:'201',frontend:'301'},projection=clone(base.projection);projection.binding=binding;projection.requestId='6';projection.context.epoch='301';projection.context.revision='3';projection.scene.revision='3';
 // Observation request IDs are read from actual generated reconnect command.
 let rebound=[...disconnected,action(lost,'bar:reconnect','bar'),native({...base.attached,binding})];
 projection.requestId=(await replay(rebound)).at(-1).requests.find(x=>x.kind==='projection-request').requestId;rebound.push(native(projection));
 let attach=clone(fixture.attach);attach.binding=binding;rebound.push({kind:'geometry-attach'});attach.requestId=(await replay(rebound)).at(-1).requests[0].requestId;rebound.push(native(attach));
 let facts=clone(fixture.facts);facts.binding=binding;facts.requestId=(await replay(rebound)).at(-1).requests[0].requestId;facts.revision='103';facts.sequence='103';rebound.push(native(facts));
 const reboundMenu=await open(rebound);
 await check('new session frontend cannot bypass native lifetime incarnation Unknown',reboundMenu.events,(_,last)=>{assert.equal(last.menu.status,'unknown');assert.equal(last.registry,1);assert.equal(last.outstanding,1)});
 await check('late original full key resolves ledger after session rebind',[...reboundMenu.events,native(receipt(fixture.maxCommand))],(_,last)=>{assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.deepEqual(last.unresolved,[]);assert.equal(last.requests.length,0)});
 for(const [name,change] of [['version',{geometryProtocol:2}],['stale request',{requestId:'999'}],['old binding',{binding:{...base.binding,frontend:'299'}}],['bad mode',null],['duplicate identity',null],['missing field',null]]){
  const bad=clone(fixture.facts);Object.assign(bad,change||{});if(name==='bad mode')bad.facts.windows[0].nativeMode='tiled';if(name==='duplicate identity')bad.facts.windows.push(clone(bad.facts.windows[0]));if(name==='missing field')delete bad.facts.windows[0].workAreaRevision;
  await check('strict geometry observation rejects '+name,[...baseline,{kind:'geometry-attach'},native(fixture.attach),native(bad)],(_,last)=>{assert.equal(last.geometry,null);assert.equal(last.requests.length,0);assert.equal(last.registry,0)});
 }

 const refreshing=[...ordinary.events,{kind:'geometry-refresh'}];const refreshFrame=(await replay(refreshing)).at(-1).frame;
 await check('fresh geometry pending disables mutations but keeps Close available',refreshing,(_,last)=>{assert(last.frame.popup.filter(x=>x.id.startsWith('menu:')).every(x=>!x.enabled));assert(last.frame.popup.find(x=>x.label==='Close').enabled)});
 await check('stale pre-refresh callback cannot dispatch during geometry pending',[...refreshing,action(ordinary.last.frame,'menu:1:2')],(_,last)=>{assert.equal(last.registry,0);assert.equal(last.requests.length,0);assert.equal(last.shell.effects.request,'0')});
 const other=await open(unknownReady,'bar:group:application:org.b');
 const otherEvents=[...other.events,action(other.last.frame,`menu:${other.last.menu.id}:2`)];
 const otherCommand=clone(fixture.maxCommand);otherCommand.intent={...otherCommand.intent,request:'2',generation:'2',incarnation:'20',context:{...otherCommand.intent.context,revision:'102'}};
 await check('unrelated geometry target still uses shared next IDs',otherEvents,(_,last)=>{assert.deepEqual(last.requests,[otherCommand]);assert.equal(last.registry,2);assert.equal(last.unresolved.length,2)});
 await check('B geometry receipt then delayed A receipt settles only full registered keys',[...otherEvents,native(receipt(otherCommand)),native(receipt(fixture.maxCommand))],(_,last)=>{assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.deepEqual(last.unresolved,[]);assert.deepEqual(last.shell.effects.transaction.intent,otherCommand.intent);assert.equal(last.shell.effects.transaction.status,'Committed');assert.equal(last.geometry.windows.find(w=>w.incarnation==='20').mode,'ordinary');assert.equal(last.requests.length,0)});
 const barFrame=(await replay(negotiated)).at(-1).frame;
 const barEvents=[...negotiated,action(barFrame,'bar:group:application:org.a','bar')];
 const barCommand=clone(base.firstCommand);barCommand.intent.operation='activate';
 await check('ordinary taskbar shares same allocator without menu registry',barEvents,(_,last)=>{assert.deepEqual(last.requests,[barCommand]);assert.equal(last.registry,0);assert.equal(last.unresolved.length,1)});
 const barUnknown=await observe([...barEvents,native(receipt(barCommand,'Unknown'))],{mode:'ordinary',minimized:false,known:false},2,102);
 const barUnknownFrame=(await replay(barUnknown)).at(-1).frame;
 await check('taskbar-origin Unknown prevents taskbar retry independent of menu ledger',[...barUnknown,action(barUnknownFrame,'bar:group:application:org.a','bar')],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.registry,0);assert.equal(last.shell.effects.request,'1');assert.equal(last.unresolved[0].status,'Unknown')});
 const barUnknownMenu=await open(barUnknown);
 await check('taskbar-origin Unknown prevents geometry namespace bypass',[...barUnknownMenu.events,action(barUnknownMenu.last.frame,`menu:${barUnknownMenu.last.menu.id}:2`)],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.registry,0);assert.equal(last.shell.effects.request,'1');assert.equal(last.unresolved[0].status,'Unknown')});
 const staleFacts=clone(fixture.facts);staleFacts.requestId='4';staleFacts.sequence='1';staleFacts.revision='100';
 await check('geometry revision cannot roll backward during fresh request',[...negotiated,{kind:'geometry-refresh'},native(staleFacts)],(_,last)=>{assert.equal(last.geometry.revision,'101');assert.equal(last.requests.length,0)});
 const disagreement=clone(fixture.facts);disagreement.facts.windows[0].minimized=true;disagreement.facts.windows[0].geometryEligible=false;disagreement.facts.windows[0].capabilities.maximize=false;
 const disagreeOpen=await open([...baseline,{kind:'geometry-attach'},native(fixture.attach),native(disagreement)]);
 await check('independent geometry legacy minimized disagreement cannot freeze actionable provider',disagreeOpen.events,(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.registry,0);assert.equal(last.requests.length,0)});

 const control={protocolVersion:3,kind:'host-geometry-negotiate'};
 const waiting=[...baseline,native(control)];
 await check('authenticated geometry negotiate control invokes explicit attach once',waiting,(_,last)=>{assert.deepEqual(last.requests,[{protocolVersion:3,kind:'geometry-attach',geometryProtocol:1,binding:base.binding,requestId:'2'}]);assert.equal(last.shell.available,false)});
 await check('repeated negotiation controls coalesce while pending',[...waiting,native(control),native(control)],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.shell.request,'2')});
 await check('repeated negotiation controls coalesce after successful negotiation',[...negotiated,native(control)],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.shell.request,'3')});
 const unavailable={protocolVersion:3,kind:'geometry-unavailable',binding:base.binding,requestId:'2',reason:'unsupported geometry observer'};
 await check('correlated attach refusal restores legacy UI without geometry inference',[...waiting,native(unavailable),native(control)],(_,last)=>{assert.equal(last.shell.available,true);assert.equal(last.requests.length,0);assert.equal(last.shell.request,'2');assert.equal(last.geometry,null)});
 for(const [name,change] of [['wrong request',{requestId:'3'}],['wrong binding',{binding:{...base.binding,frontend:'301'}}],['extra field',{exec:'x'}]]){
  await check('geometry refusal correlation rejects '+name,[...waiting,native({...unavailable,...change})],(_,last)=>{assert.equal(last.shell.available,false);assert.equal(last.shell.request,'2');assert.equal(last.requests.length,0)});
 }
 for(const [name,control] of [['bad version',{protocolVersion:2,kind:'host-geometry-negotiate'}],['extra field',{protocolVersion:3,kind:'host-geometry-negotiate',effects:true}]])
  await check('closed negotiation control rejects '+name,[...baseline,native(control)],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.shell.request,'1');assert.equal(last.shell.available,true)});
 await check('attach refusal never clears preexisting Unknown ledger',[...unknownReady,{kind:'geometry-attach'},native({...unavailable,requestId:'6'})],(_,last)=>{assert.equal(last.registry,1);assert.equal(last.outstanding,1);assert.equal(last.unresolved[0].status,'Unknown');assert.equal(last.requests.length,0)});

 const reordered=receipt(fixture.maxCommand);const originalIntent=reordered.intent;
 reordered.intent={context:{revision:originalIntent.context.revision,output:originalIntent.context.output,epoch:originalIntent.context.epoch,lifetime:originalIntent.context.lifetime},operation:originalIntent.operation,incarnation:originalIntent.incarnation,generation:originalIntent.generation,request:originalIntent.request};
 await check('full typed receipt key is independent of JSON property order',[...max,native(reordered)],(_,last)=>{assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.deepEqual(last.unresolved,[]);assert.equal(last.requests.length,2);assert.equal(last.geometry.windows[0].mode,'ordinary')});
 const passed=cases.every(x=>x.passed);fs.writeFileSync(process.argv[5],JSON.stringify({passed,checks:cases.length,cases,scope:'Compiled production Controller/Shell/Effects/Provider/MenuBridge/ReceiptRouter; synthetic geometry authority only'},null,2)+'\n');clearTimeout(timer);if(!passed)process.exitCode=1;
})().catch(error=>{clearTimeout(timer);console.error(error.stack);process.exitCode=1});
