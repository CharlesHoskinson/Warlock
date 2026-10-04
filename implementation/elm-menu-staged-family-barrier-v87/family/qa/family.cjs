'use strict';
const fs=require('fs'),assert=require('assert/strict');
const app=require(process.argv[2]).Elm.MenuSurfaceReplay.init({flags:null});
const base=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),geo=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));
const copy=x=>JSON.parse(JSON.stringify(x)),native=frame=>({kind:'native',frame}),cases=[];
const baseline=[{kind:'owner',frame:base.owner},native(base.attached),native(base.projection),native({protocolVersion:3,kind:'host-geometry-negotiate'}),native(geo.attach),native(geo.facts)];
const timer=setTimeout(()=>{throw Error('Family CPU replay deadline')},30000);
function replay(events){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows)};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events)})}
const stage=require('./stage.cjs')(replay);
const context=(frame,application='org.a')=>({kind:'action',action:{surfaceProtocol:2,kind:'surface-context',surface:'bar',publication:frame.publication,lease:frame.lease,id:'bar:group:application:'+application,trigger:'pointer',x:40,y:20}});
const action=(frame,id)=>({kind:'action',action:{surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:frame.publication,lease:frame.lease,id}});
async function check(name,events,verify){let rows;try{rows=await replay(events);verify(rows,rows.at(-1));cases.push({name,passed:true,rows})}catch(error){cases.push({name,passed:false,error:String(error),rows});console.error(name,error.stack)}}
async function observed(events,revision='2',geometryRevision='102'){
 const last=(await replay(events)).at(-1),p=copy(base.projection),g=copy(geo.facts);
 p.requestId=last.requests.find(x=>x.kind==='projection-request').requestId;
 p.context.revision=p.scene.revision=revision;
 g.requestId=last.requests.find(x=>x.kind==='geometry-facts-request').requestId;
 g.revision=geometryRevision;g.sequence=geometryRevision;
 return [...events,native(p),native(g)];
}
async function unknown(operation,incarnation){
 const sent=[...baseline,{kind:'direct-native-begin',operation,incarnation}],row=(await replay(sent)).at(-1),command=row.requests[0];
 assert.equal(command.kind,'window-effect');assert.equal(command.intent.incarnation,incarnation);
 const receipt={...copy(command),kind:'effect-outcome',status:'Unknown',reason:'Synthetic transport uncertainty',revision:'102',outputGeneration:'1'};
 return {events:await observed([...sent,native(receipt)]),command};
}
async function open(events,application='org.a'){
 const frame=(await replay(events)).at(-1).frame,opened=[...events,context(frame,application)];
 return {events:opened,last:(await replay(opened)).at(-1)};
}
function blocked(command){return (rows,last)=>{
 assert.equal(last.requests.length,0,'no observations before family barrier');
 assert.equal(last.preparedToken,null);assert.equal(last.outstanding,0);assert.equal(last.registry,0);
 assert.equal(last.shell.effects.request,'1');assert.equal(last.shell.effects.generation,'1');
 assert.equal(last.unresolved.length,1);assert.equal(last.unresolved[0].status,'Unknown');
 assert.deepEqual(last.unresolved[0].intent,command.intent);
 assert.equal(last.menu.status,'ready','native barrier does not fabricate local Unknown receipt');
};}
(async()=>{
 const child=await unknown('activate','11'),a=await open(child.events);
 await check('child-target native Unknown blocks canonical root before any preparation',[...a.events,action(a.last.frame,'menu:1:2')],blocked(child.command));
 await check('same child family legacy Minimize cannot bypass native Unknown',[...a.events,action(a.last.frame,'menu:1:1')],blocked(child.command));
 const b=await open(child.events,'org.b'),bSent=await stage([...b.events,action(b.last.frame,'menu:1:2')]);
 await check('unrelated root may dispatch while old child full key remains Unknown',bSent,(_,last)=>{
  assert.equal(last.requests[0].intent.incarnation,'20');assert.equal(last.requests[0].intent.request,'2');assert.equal(last.registry,1);assert.equal(last.unresolved.length,2);
  assert.deepEqual(last.unresolved.find(x=>x.status==='Unknown').intent,child.command.intent);
 });
 const root=await unknown('maximize','10'),rootMenu=await open(root.events);
 await check('native effect2 Unknown blocks effect1 menu preparation',[...rootMenu.events,action(rootMenu.last.frame,'menu:1:1')],blocked(root.command));
 const lost=[...child.events,native({protocolVersion:3,kind:'host-disconnected'})],lostFrame=(await replay(lost)).at(-1).frame;
 async function rebound(lifetime){
  const binding={...base.binding,lifetime,session:'201',frontend:'301'};
  let events=[...lost,{kind:'action',action:{surfaceProtocol:2,kind:'surface-action',surface:'bar',publication:lostFrame.publication,lease:lostFrame.lease,id:'bar:reconnect'}},native({...copy(base.attached),binding})];
  let row=(await replay(events)).at(-1),p=copy(base.projection);p.binding=binding;p.context.lifetime=lifetime;p.context.epoch='301';p.context.revision=p.scene.revision='3';p.requestId=row.requests[0].requestId;events.push(native(p),native({protocolVersion:3,kind:'host-geometry-negotiate'}));
  row=(await replay(events)).at(-1);let attach=copy(geo.attach);attach.binding=binding;attach.requestId=row.requests[0].requestId;events.push(native(attach));
  row=(await replay(events)).at(-1);let g=copy(geo.facts);g.binding=binding;g.requestId=row.requests[0].requestId;g.revision=g.sequence='103';events.push(native(g));
  return events;
 }
 const reboundEvents=await rebound('100'),reboundA=await open(reboundEvents);
 await check('same lifetime child Unknown survives session and frontend replacement',[...reboundA.events,action(reboundA.last.frame,`menu:${reboundA.last.menu.id}:2`)],blocked(child.command));
 const newEvents=await rebound('101'),newA=await open(newEvents),newSent=await stage([...newA.events,action(newA.last.frame,`menu:${newA.last.menu.id}:2`)]);
 await check('different native lifetime does not alias old incarnation barrier',newSent,(_,last)=>{
  assert.equal(last.requests[0].intent.context.lifetime,'101');assert.equal(last.requests[0].intent.incarnation,'10');
  assert.equal(last.unresolved.length,2);assert.deepEqual(last.unresolved.find(x=>x.status==='Unknown').intent,child.command.intent);
 });
 const passed=cases.every(x=>x.passed);fs.writeFileSync(process.argv[5],JSON.stringify({passed,checks:cases.length,cases,scope:'Actual compiled Shell/MenuBridge family guard; synthetic native full receipts, no GUI'},null,2)+'\n');clearTimeout(timer);if(!passed)process.exitCode=1;
})().catch(error=>{fs.writeFileSync(process.argv[5],JSON.stringify({passed:false,checks:cases.length,cases,error:String(error)},null,2)+'\n');clearTimeout(timer);console.error(error.stack);process.exitCode=1});
