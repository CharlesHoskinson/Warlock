'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Elm}=require(path.resolve(process.argv[2])),fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const source=fixture.clientScope,binding=source.binding,job=fixture.terminalReceipts[0].event.event.frame.job,id='family:'+source.scope.context.incarnation,neighbor='family:3',domain={binding,receiverEpoch:'1'};
function decode(v){if(Array.isArray(v))return v.map(decode);if(v&&typeof v==='object')return '#bigint' in v?Number(v['#bigint']):Object.fromEntries(Object.entries(v).map(([k,x])=>[k,decode(x)]));return v;}
function worker(){const app=Elm.RetainedPreviewPresenterReplay.init();let pending;app.ports.outgoing.subscribe(v=>{assert(pending);const p=pending;pending=null;p(v);});return (kind,value)=>new Promise((resolve,reject)=>{assert(!pending);const t=setTimeout(()=>reject(Error('Original urgent Elm refinement timeout')),3000);pending=v=>{clearTimeout(t);resolve(v);};app.ports.incoming.send({kind,value});});}
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[id,neighbor].map(identity=>({id:identity,domId:'window-'+identity,label:'Window',ariaLabel:'Window',detail:'',enabled:true}))};
const sourceSeed={kind:'source-seed',publication:'1',lease:'1',identity:id,source,title:'Source',application:'fixture'},trigger={...job};delete trigger.request;
const wrap=event=>({previewProtocol:3,kind:'native-preview-realm-event',...domain,event});
function rowKinds(rows){return rows.flatMap(row=>row.commands.map(c=>c.kind+':'+(row.identity===id?'first':row.identity===neighbor?'neighbor':'binding')));}
function projection(r){return {pending:rowKinds(r.realm.ingress.intents),deferred:rowKinds(r.realm.deferredIntents),closing:r.realm.closing,demand:r.models.every(row=>row.model.demand),known:r.models.reduce((n,row)=>n+row.model.known.length,0),held:r.models.length,commands:rowKinds(Array.isArray(r.commands)?r.commands:r.commands.entries)};}
function fact(row,foreign){const packet={previewProtocol:3,kind:'preview-commands',...domain,controlOrdinal:'1',entries:[row]};return {previewProtocol:3,kind:'preview-control-ticket',...domain,receiverEpoch:foreign?'2':'1',controlOrdinal:'1',alreadyDelivered:false,wire:JSON.stringify(packet)};}
(async()=>{let compared=0;const traces=[];
 for(const file of process.argv.slice(4)){
  const states=decode(JSON.parse(fs.readFileSync(file,'utf8'))).states.map(v=>v.s),send=worker();
  await send('grant',{...domain,capacity:1});await send('presentation',presentation);await send('native',wrap(sourceSeed));await send('native',wrap({kind:'event',identity:id,event:{kind:'request',trigger}}));
  const source3=structuredClone(source);source3.scope.context.incarnation='3';await send('native',wrap({...sourceSeed,identity:neighbor,source:source3}));const trigger3=structuredClone(trigger);trigger3.context.incarnation='3';let result=await send('native',wrap({kind:'event',identity:neighbor,event:{kind:'request',trigger:trigger3}}));
  let seen=0,count=0;
  for(const state of states){
   if(state.history.length>seen){assert.equal(state.history.length,seen+1);seen++;const e=state.history.at(-1);
    if(e==='Issue'||e==='ForeignTicket')result=await send('issued',fact(result.realm.ingress.intents[0]||{identity:'absent',commands:[{kind:'absent'}]},e==='ForeignTicket'));
    else if(e==='Retry')result=await send('retry',domain);
    else if(e==='Quarantine'||e==='ForeignQuarantine')result=await send('quarantine',{...domain,receiverEpoch:e==='ForeignQuarantine'?'2':'1'});
    else result=await send('native',wrap({kind:'not-an-input'}));
   }else assert.equal(state.history.length,seen);
   const wanted=Object.fromEntries(Object.entries(state).filter(([k])=>k!=='history'));
   assert.deepEqual(projection(result),wanted,path.basename(file)+' step '+seen+' '+state.history.at(-1));count++;compared++;
  }
  traces.push({trace:path.basename(file),statesCompared:count});
 }
 console.log(JSON.stringify({passed:true,statesCompared:compared,coupledTraces:traces,singlePreviewPolicy:true,syntheticNativeIssuedFacts:true,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
