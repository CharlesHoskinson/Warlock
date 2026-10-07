'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const {Elm}=require(process.argv[2]),fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const source=fixture.clientScope,frame=fixture.terminalReceipts[0].event.event.frame,binding=source.binding,id='family:'+source.scope.context.incarnation;
let checks=0;function check(v,m){assert(v,m);checks++;}function same(a,b,m){assert.deepEqual(a,b,m);checks++;}
function worker(){const app=Elm.RetainedPreviewPresenterReplay.init();let pending;app.ports.outgoing.subscribe(v=>{assert(pending);const p=pending;pending=null;p(v);});return (kind,value)=>new Promise((resolve,reject)=>{assert(!pending);const timer=setTimeout(()=>reject(Error('Original compiled Elm replay timeout')),3000);pending=v=>{clearTimeout(timer);resolve(v);};app.ports.incoming.send({kind,value});});}
const domain={binding,receiverEpoch:'1'},grant={...domain,capacity:1065};
const wrap=event=>({previewProtocol:3,kind:'native-preview-realm-event',...domain,event});
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[{id,domId:'window-'+id,label:'Window',ariaLabel:'Window',detail:'',enabled:true}]};
const sourceSeed={kind:'source-seed',publication:'1',lease:'1',identity:id,source,title:'Native source',application:'fixture'};
const trigger={...frame.job};delete trigger.request;
const kinds=r=>r.commands.entries.flatMap(row=>row.commands).map(v=>v.kind);
const intents=r=>r.realm.ingress.intents;
function ticket(row,ordinal='1',extra={}){return {previewProtocol:3,kind:'preview-control-ticket',...domain,controlOrdinal:ordinal,alreadyDelivered:false,wire:JSON.stringify({previewProtocol:3,kind:'preview-commands',...domain,controlOrdinal:ordinal,entries:[row]}),...extra};}
async function setup(capacity=1065){const send=worker();await send('grant',{...grant,capacity});await send('presentation',presentation);await send('native',wrap(sourceSeed));const result=await send('native',wrap({kind:'event',identity:id,event:{kind:'request',trigger}}));return {send,result};}
(async()=>{
 let {send,result:r}=await setup();same(kinds(r),['acquire']);same(r.realm.ingress.pending,1);const row=intents(r)[0],originalModels=structuredClone(r.models),fact=ticket(row);
 const changedWire=change=>{const packet=JSON.parse(fact.wire);change(packet);return {...fact,wire:JSON.stringify(packet)};};
 for(const bad of [null,{}, {...fact,extra:true},{...fact,receiverEpoch:'2'},{...fact,binding:{...binding,frontend:'9'}},{...fact,controlOrdinal:'2'},{...fact,controlOrdinal:1},{...fact,controlOrdinal:'0'},{...fact,alreadyDelivered:'true'},{...fact,wire:'not json'}, {...fact,wire:' '.repeat(4097)},changedWire(p=>p.extra=true),changedWire(p=>p.receiverEpoch='2'),changedWire(p=>p.binding.frontend='9'),changedWire(p=>p.entries[0].identity='family:foreign'),changedWire(p=>p.entries[0].commands[0].kind='foreign-purpose'),changedWire(p=>p.entries.push(row)),changedWire(p=>p.entries=[]),changedWire(p=>p.entries[0].commands=[null])]){
  r=await send('issued',bad);same(intents(r),[row],'Refused issued fact preserves exact original intent');same(r.models,originalModels,'Issuance never mutates the original window policy');
 }
 r=await send('retry',domain);same(r.commands.entries,[row],'Loss before issuance retries exact original intent');
 r=await send('retry',{...domain,receiverEpoch:'2'});same(kinds(r),[]);same(intents(r),[row]);
 r=await send('grant',grant);same(intents(r),[row],'Repeated original grant cannot erase retained work');
 r=await send('grant',{...grant,receiverEpoch:'2'});same(r.realm.epoch,'1');same(intents(r),[row]);
 // Object field order is incidental, original command values and domains are not.
 const reordered=JSON.parse(fact.wire);reordered.entries[0].commands[0]=Object.fromEntries(Object.entries(row.commands[0]).reverse());
 r=await send('issued',{...fact,wire:JSON.stringify(reordered)});same(intents(r),[],'Semantic exact native body accepts harmless object field ordering');same(r.models,originalModels);same(r.models[0].model.known.length,1,'Native issuance does not settle Unknown');
 r=await send('issued',fact);same(intents(r),[],'Repeated already-correlated fact is harmless');
 ({send,result:r}=await setup(1));const acquire=intents(r)[0];r=await send('quarantine',domain);same(kinds(r),['acquire'],'Oldest lost intent precedes deferred cleanup');same(r.realm.ingress.pending,1);same(r.realm.deferred,2);check(r.realm.inputBlocked);check(!r.models[0].model.demand);same(r.models[0].model.known.length,1);
 const seed={detachProtocol:1,kind:'native-preview-detach-seed',identity:id,...domain,subject:source.scope.context.incarnation,entry:'1',entryIssuedThrough:'1',requestFloor:'1'};
 r=await send('native',wrap(seed));same(r.realm.deferred,2,'Blocked input cannot overwrite deferred original commands');same(kinds(r),[]);same(r.models[0].model.known.length,1);
 r=await send('retry',{...domain,receiverEpoch:'2'});same(r.realm.deferred,2);same(kinds(r),[]);
 r=await send('issued',ticket(acquire));same(r.realm.ingress.pending,0);same(r.realm.deferred,2);
 r=await send('retry',domain);same(kinds(r),['reconcile']);same(r.realm.deferred,1);check(r.realm.inputBlocked);const reconcile=intents(r)[0];
 r=await send('issued',ticket(reconcile,'2'));same(r.realm.deferred,1);
 r=await send('retry',domain);same(kinds(r),['cancel']);same(r.realm.deferred,0);check(!r.realm.inputBlocked);const cancel=intents(r)[0];await send('issued',ticket(cancel,'3'));
 r=await send('native',wrap(seed));same(kinds(r),[]);same(r.models[0].model.known.length,1);
 r=await send('native',wrap({kind:'event',identity:id,event:{kind:'receipt',sequence:'4',event:{kind:'cancelled',job:frame.job}}}));same(kinds(r),['acknowledge']);same(r.realm.deferred,1);same(r.realm.deferredIntents[0].commands[0].kind,'detach-ready');same(r.models[0].model.known.length,0);
 const terminalAck=intents(r)[0];await send('issued',ticket(terminalAck,'4'));r=await send('retry',domain);same(kinds(r),['detach-ready']);same(r.realm.deferred,0);const ready=intents(r)[0];await send('issued',ticket(ready,'5'));
 const delivery={detachProtocol:1,kind:'native-preview-binding-detach-delivery',...domain,deliveryOrdinal:'1',event:{kind:'native-preview-actor-detached',identity:id,subject:seed.subject,entry:'1',entryIssuedThrough:'1',requestFloor:'1'}};
 r=await send('native',wrap(delivery));same(r.models,[]);same(kinds(r),['detach-delivery-ack']);const processing=intents(r)[0];
 r=await send('closed',domain);check(!r.realm.closed,'Empty membership cannot erase unissued processing intent');
 r=await send('grant',{...grant,receiverEpoch:'2'});same(r.realm.epoch,'1');same(intents(r),[processing]);
 r=await send('issued',ticket(processing,'18446744073709551615'));same(intents(r),[],'Native UInt64 ticket remains lossless without renderer allocation');
 r=await send('closed',domain);check(r.realm.closed);r=await send('grant',{...grant,receiverEpoch:'2'});same(r.realm.epoch,'2');same(r.realm.ingress.pending,0);
 r=await send('issued',fact);same(r.realm.ingress.pending,0);same(r.realm.epoch,'2','Old native ticket cannot retarget replacement');
 const urgent=worker(),neighbor='family:3',source3=structuredClone(source);source3.scope.context.incarnation='3';
 await urgent('grant',{...grant,capacity:1});await urgent('presentation',{...presentation,popup:[...presentation.popup,{id:neighbor,domId:'window-3',label:'Neighbor',ariaLabel:'Neighbor',detail:'',enabled:true}]});
 await urgent('native',wrap(sourceSeed));await urgent('native',wrap({kind:'event',identity:id,event:{kind:'request',trigger}}));
 await urgent('native',wrap({...sourceSeed,identity:neighbor,source:source3}));
 const trigger3=structuredClone(trigger);trigger3.context.incarnation='3';r=await urgent('native',wrap({kind:'event',identity:neighbor,event:{kind:'request',trigger:trigger3}}));
 same(r.models.length,2);same(r.realm.deferred,1);check(r.models.every(row=>row.model.demand && row.model.known.length===1));
 const beforeUrgent=structuredClone(r.realm.ingress.intents),deferredAcquire=structuredClone(r.realm.deferredIntents);
 r=await urgent('quarantine',domain);check(r.models.every(row=>!row.model.demand),'Urgent quarantine must revoke every demand while input is already blocked');
 same(r.realm.ingress.intents,beforeUrgent,'Urgent revoke retains original pending acquisition');
 same(r.realm.deferredIntents.slice(0,1),deferredAcquire,'Urgent cleanup preserves older deferred acquisition first');
 same(r.realm.deferredIntents.map(row=>row.commands[0].kind),['acquire','reconcile','cancel','cancel']);
 check(r.models.every(row=>row.model.known.length===1),'Urgent revoke retains both original Unknown obligations');
 const urgentOnce=structuredClone(r.realm.deferredIntents);r=await urgent('quarantine',domain);same(r.realm.deferredIntents,urgentOnce,'Repeated quarantine cannot grow another safety batch');
 console.log(JSON.stringify({passed:true,checks,optimizedElm:true,singlePreviewPolicy:true,syntheticNativeIssuedFacts:true,boundedDeferredCleanup:true,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
