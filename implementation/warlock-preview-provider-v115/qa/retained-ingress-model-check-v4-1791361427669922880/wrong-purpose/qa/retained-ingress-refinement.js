'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Elm}=require(path.resolve(process.argv[2])),fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const source=fixture.clientScope,binding=source.binding,job=fixture.terminalReceipts[0].event.event.frame.job,id='family:'+source.scope.context.incarnation;
function decode(v){if(Array.isArray(v))return v.map(decode);if(v&&typeof v==='object')return '#bigint' in v?Number(v['#bigint']):Object.fromEntries(Object.entries(v).map(([k,x])=>[k,decode(x)]));return v;}
function worker(){const app=Elm.RetainedPreviewPresenterReplay.init();let pending;app.ports.outgoing.subscribe(v=>{assert(pending);const p=pending;pending=null;p(v);});return (kind,value)=>new Promise((resolve,reject)=>{assert(!pending);const t=setTimeout(()=>reject(Error('Original compiled Elm refinement timeout')),3000);pending=v=>{clearTimeout(t);resolve(v);};app.ports.incoming.send({kind,value});});}
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[{id,domId:'window',label:'Window',ariaLabel:'Window',detail:'',enabled:true}]};
const sourceSeed={kind:'source-seed',publication:'1',lease:'1',identity:id,source,title:'Source',application:'fixture'};
const trigger={...job};delete trigger.request;
const request={kind:'event',identity:id,event:{kind:'request',trigger}},terminal={kind:'event',identity:id,event:{kind:'receipt',sequence:'4',event:{kind:'cancelled',job}}};
const envelope=(event,epoch)=>({previewProtocol:3,kind:'native-preview-realm-event',binding,receiverEpoch:String(epoch),event});
const seed=epoch=>({detachProtocol:1,kind:'native-preview-detach-seed',identity:id,binding,receiverEpoch:String(epoch),subject:source.scope.context.incarnation,entry:'1',entryIssuedThrough:'1',requestFloor:'1'});
const final=epoch=>({detachProtocol:1,kind:'native-preview-binding-detach-delivery',binding,receiverEpoch:String(epoch),deliveryOrdinal:'1',event:{kind:'native-preview-actor-detached',identity:id,subject:source.scope.context.incarnation,entry:'1',entryIssuedThrough:'1',requestFloor:'1'}});
function rowKinds(rows){return rows.flatMap(row=>row.commands).map(c=>c.kind);}
function projection(r){const model=r.models[0]?.model;return {epoch:Number(r.realm.epoch),held:!!model,known:!!model?.known.length,demand:!!model?.demand,closing:r.realm.closing,closed:r.realm.closed,processed:Number(r.realm.processed),pending:rowKinds(r.realm.ingress.intents),deferred:rowKinds(r.realm.deferredIntents),commands:rowKinds(Array.isArray(r.commands)?r.commands:r.commands.entries)};}
function fact(row,epoch,event){const body=structuredClone(row);if(event==='WrongTicket')body.commands[0].kind='foreign-purpose';const packet={previewProtocol:3,kind:'preview-commands',binding,receiverEpoch:String(event==='ForeignInnerTicket'?epoch+1:epoch),controlOrdinal:'1',entries:[body]};return {previewProtocol:3,kind:'preview-control-ticket',binding,receiverEpoch:String(event==='ForeignTicket'?epoch+1:epoch),controlOrdinal:'1',alreadyDelivered:false,wire:JSON.stringify(packet)};}
(async()=>{let compared=0;const traces=[];
 for(const file of process.argv.slice(4)){
  const states=decode(JSON.parse(fs.readFileSync(file,'utf8'))).states.map(v=>v.s),send=worker();
  await send('grant',{binding,receiverEpoch:'1',capacity:1});await send('presentation',presentation);await send('native',envelope(sourceSeed,1));let result=await send('native',envelope(request,1));
  let seen=0,count=0,previous=states[0];
  for(const state of states){
   if(state.history.length>seen){assert.equal(state.history.length,seen+1);seen++;const e=state.history.at(-1),epoch=previous.epoch,domain={binding,receiverEpoch:String(epoch)};
    if(['Issue','WrongTicket','ForeignTicket','ForeignInnerTicket'].includes(e))result=await send('issued',fact(result.realm.ingress.intents[0]||{identity:'absent',commands:[{kind:'absent'}]},epoch,e));
    else if(e==='Retry'||e==='ForeignRetry')result=await send('retry',{...domain,receiverEpoch:String(e==='ForeignRetry'?epoch+1:epoch)});
    else if(e==='Close')result=await send('closed',domain);
    else if(e==='NextGrant'||e==='RepeatGrant')result=await send('grant',{...domain,receiverEpoch:String(e==='NextGrant'?epoch+1:epoch),capacity:1});
    else if(e==='Quarantine')result=await send('quarantine',domain);
    else result=await send('native',envelope(e==='Seed'?seed(epoch):e==='Terminal'?terminal:final(epoch),epoch));
   }else assert.equal(state.history.length,seen);
   const wanted=Object.fromEntries(Object.entries(state).filter(([k])=>!['history','seeded','ready','terminalSeen'].includes(k)));
   assert.deepEqual(projection(result),wanted,path.basename(file)+' step '+seen+' '+state.history.at(-1));previous=state;count++;compared++;
  }
  traces.push({trace:path.basename(file),statesCompared:count});
 }
 console.log(JSON.stringify({passed:true,statesCompared:compared,coupledTraces:traces,singlePreviewPolicy:true,syntheticNativeIssuedFacts:true,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
