'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const {Elm}=require(process.argv[2]),fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const source=fixture.clientScope,frame=fixture.terminalReceipts[0].event.event.frame,binding=source.binding,identity='family:'+source.scope.context.incarnation;
const grant={binding,receiverEpoch:'1',capacity:1065};let checks=0;
function check(v,m){assert(v,m);checks++;}function same(a,b,m){assert.deepEqual(a,b,m);checks++;}
function worker(){const app=Elm.ScopedPreviewPresenterReplay.init();let pending;app.ports.outgoing.subscribe(v=>{const p=pending;pending=null;p(v);});return (kind,value)=>new Promise((resolve,reject)=>{assert(!pending);const timer=setTimeout(()=>reject(Error('Original compiled Elm replay timeout')),3000);pending=v=>{clearTimeout(timer);resolve(v);};app.ports.incoming.send({kind,value});});}
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[identity,'family:3'].map(id=>({id,domId:'window-'+id,label:'Window',ariaLabel:'Window',detail:'',enabled:true}))};
const sourceSeed={kind:'source-seed',publication:'1',lease:'1',identity,source,title:'Native source',application:'fixture'};
const wrap=(event,epoch='1')=>({previewProtocol:3,kind:'native-preview-realm-event',binding,receiverEpoch:epoch,event});
const seed={detachProtocol:1,kind:'native-preview-detach-seed',identity,binding,receiverEpoch:'1',subject:source.scope.context.incarnation,entry:'1',entryIssuedThrough:'1',requestFloor:'1'};
const delivery={detachProtocol:1,kind:'native-preview-binding-detach-delivery',binding,receiverEpoch:'1',deliveryOrdinal:'1',event:{kind:'native-preview-actor-detached',identity,subject:seed.subject,entry:'1',entryIssuedThrough:'1',requestFloor:'1'}};
const kinds=r=>r.commands.entries.flatMap(row=>row.commands).map(v=>v.kind);
(async()=>{
 const send=worker();let r=await send('grant',grant);check(r.realm.controlled && r.realm.epoch==='1');await send('presentation',presentation);
 r=await send('legacy',sourceSeed);same(r.models,[],'Bare event cannot enter a controlled policy');
 const foreignSource=structuredClone(source);foreignSource.binding.frontend='9';foreignSource.scope.binding.frontend='9';
 r=await send('native',wrap({...sourceSeed,source:foreignSource}));same(r.models,[],'Current wrapper cannot admit a foreign inner source binding');
 r=await send('native',wrap({protocolVersion:3,kind:'catalog',publication:'1',lease:'1',binding:{...binding,frontend:'9'},requestId:'1',sequence:'1',revision:'1',windows:[{incarnation:seed.subject,label:'Foreign',application:'fixture',minimized:false}]}));same(r.models,[],'Current wrapper cannot admit a foreign metadata-only catalog');
 r=await send('native',wrap(sourceSeed));check(r.models.length===1,'Current realm admits original native source');
 const trigger={...frame.job};delete trigger.request;r=await send('native',wrap({kind:'event',identity,event:{kind:'request',trigger}}));same(kinds(r),['acquire']);check(r.models[0].model.known.length===1);
 const originalModels=structuredClone(r.models);
 for(const event of [{kind:'observe',scope:{...source.scope,binding:{...binding,frontend:'9'},observation:'999'}},{kind:'attach',previous:binding,scope:{...source.scope,binding:{...binding,frontend:'9'},observation:'999'}}]){r=await send('native',wrap({kind:'event',identity,event}));same(r.models,originalModels,'Current wrapper cannot retarget a lifecycle to a foreign native binding');same(kinds(r),[]);}
 r=await send('native',wrap({...seed,requestFloor:'0'}));check(!r.realm.closing && r.models[0].model.known.length===1,'Wrong native request floor cannot begin detachment');
 r=await send('native',wrap(seed));same(kinds(r),['cancel']);check(r.realm.closing && r.models[0].model.known.length===1 && !r.models[0].model.demand,'Scoped close retains actual unresolved job');
 r=await send('native',wrap(delivery));same(kinds(r),[]);same(r.models.length,1,'Premature completion cannot erase unsettled Elm history');
 r=await send('native',wrap({kind:'event',identity,event:{kind:'request',trigger}}));same(kinds(r),[],'Quarantined realm cannot acquire again');
 for(const bad of [{...wrap(delivery),receiverEpoch:'2'},{...wrap(delivery),binding:{...binding,frontend:'9'}},wrap({...delivery,event:{...delivery.event,entry:'2'}}),wrap({...delivery,deliveryOrdinal:'2'})]){r=await send('native',bad);same(r.models.length,1);same(kinds(r),[]);}
 const cancelled={kind:'event',identity,event:{kind:'receipt',sequence:'4',event:{kind:'cancelled',job:frame.job}}};
 r=await send('native',wrap(cancelled));same(kinds(r),['acknowledge','detach-ready'],'Exact terminal ACK precedes distinct readiness');same(r.models[0].model.known.length,0);same(r.realm.processed,'0');
 r=await send('native',wrap(delivery));same(r.models,[]);same(kinds(r),['detach-delivery-ack']);same(r.realm.processed,'1');same(r.realm.completed,1);
 r=await send('native',wrap(delivery));same(kinds(r),['detach-delivery-ack'],'Exact duplicate completion re-ACKs without another mutation');
 r=await send('native',wrap({...delivery,event:{...delivery.event,requestFloor:'0'}}));same(kinds(r),[],'Changed completion under processed ordinal cannot impersonate exact fact');
 r=await send('native',wrap(sourceSeed));same(r.models,[],'Same closed preview membership cannot reopen before realm close');
 r=await send('grant',{...grant,receiverEpoch:'2'});same(r.realm.epoch,'1','Greater epoch cannot replace an unclosed realm');
 r=await send('closed',{binding,receiverEpoch:'2'});check(!r.realm.closed,'Foreign close cannot finish original realm');
 r=await send('closed',{binding,receiverEpoch:'1'});check(r.realm.closed);
 r=await send('grant',{...grant,receiverEpoch:'2'});same(r.realm.epoch,'2');same(r.realm.processed,'0');check(!r.realm.closing && !r.realm.closed,'Native fresh epoch opens same policy without grant reset');
 r=await send('native',wrap(sourceSeed));same(r.models,[],'Old realm source remains denied on unchanged Native binding');
 r=await send('native',wrap(sourceSeed,'2'));same(r.models.length,1,'Same Active subject can open under its greater native realm');
 r=await send('quarantine',{binding,receiverEpoch:'2'});same(r.commands.entries[0],{identity:'binding:'+Object.values(binding).join(':'),commands:[{kind:'reconcile',binding}]},'One canonical native binding purpose precedes cleanup');
 console.log(JSON.stringify({passed:true,checks,optimizedElm:true,singlePreviewPolicy:true,syntheticScopedFacts:true,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
