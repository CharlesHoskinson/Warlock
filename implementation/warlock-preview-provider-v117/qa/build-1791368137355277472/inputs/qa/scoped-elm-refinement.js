'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Elm}=require(path.resolve(process.argv[2])),fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const source=fixture.clientScope,binding=source.binding,job=fixture.terminalReceipts[0].event.event.frame.job,id='family:'+source.scope.context.incarnation;
function decode(v){if(Array.isArray(v))return v.map(decode);if(v&&typeof v==='object')return '#bigint' in v?Number(v['#bigint']):Object.fromEntries(Object.entries(v).map(([k,x])=>[k,decode(x)]));return v;}
function worker(){const app=Elm.ScopedPreviewPresenterReplay.init();let pending;app.ports.outgoing.subscribe(v=>{assert(pending);const p=pending;pending=null;p(v);});
 return (kind,value)=>new Promise((resolve,reject)=>{assert(!pending);const t=setTimeout(()=>reject(Error('Original compiled Elm refinement timeout')),3000);pending=v=>{clearTimeout(t);resolve(v);};app.ports.incoming.send({kind,value});});}
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[{id,domId:'window',label:'Window',ariaLabel:'Window',detail:'',enabled:true}]};
const sourceSeed={kind:'source-seed',publication:'1',lease:'1',identity:id,source,title:'Source',application:'fixture'};
const trigger={...job};delete trigger.request;
const request={kind:'event',identity:id,event:{kind:'request',trigger}};
const terminal={kind:'event',identity:id,event:{kind:'receipt',sequence:'4',event:{kind:'cancelled',job}}};
const envelope=(event,epoch)=>({previewProtocol:3,kind:'native-preview-realm-event',binding,receiverEpoch:String(epoch),event});
const seed=(epoch,floor)=>({detachProtocol:1,kind:'native-preview-detach-seed',identity:id,binding,receiverEpoch:String(epoch),subject:source.scope.context.incarnation,entry:'1',entryIssuedThrough:'1',requestFloor:String(floor)});
const final=(epoch,floor)=>({detachProtocol:1,kind:'native-preview-binding-detach-delivery',binding,receiverEpoch:String(epoch),deliveryOrdinal:'1',event:{kind:'native-preview-actor-detached',identity:id,subject:source.scope.context.incarnation,entry:'1',entryIssuedThrough:'1',requestFloor:String(floor)}});
function projection(result){assert(result.models.length<=1);const model=result.models[0]?.model;
 const entries=Array.isArray(result.commands)?result.commands:result.commands.entries;
 for(const row of entries)for(const command of row.commands){
  if(command.kind==='reconcile')assert.equal(row.identity,'binding:'+Object.values(binding).join(':'),'Actual canonical native binding reconciliation identity');
  else assert.equal(row.identity,id,'Exact retained native subject');
  if(command.kind==='acknowledge')assert.deepEqual(command,{kind:'acknowledge',job,sequence:'4'},'Exact original terminal job and sequence');
 }
 return {epoch:Number(result.realm.epoch),held:!!model,known:!!model?.known.length,demand:!!model?.demand,closing:result.realm.closing,closed:result.realm.closed,processed:Number(result.realm.processed),
  commands:entries.flatMap(row=>row.commands).map(c=>c.kind)};
}
(async()=>{let compared=0;const traces=[];
 for(const file of process.argv.slice(4)){
  const states=decode(JSON.parse(fs.readFileSync(file,'utf8'))).states.map(v=>v.s),send=worker();
  await send('grant',{binding,receiverEpoch:'1',capacity:1065});await send('presentation',presentation);await send('native',envelope(sourceSeed,1));let result=await send('native',envelope(request,1));result={...result,commands:{...result.commands,entries:[]}};
  let seen=0,count=0,previous=states[0];
  for(const state of states){
   if(state.history.length>seen){assert.equal(state.history.length,seen+1);seen++;const e=state.history.at(-1),epoch=previous.epoch;
    if(e==='Close'||e==='ForeignClose')result=await send('closed',{binding,receiverEpoch:String(e==='Close'?epoch:epoch+1)});
    else if(e==='NextGrant')result=await send('grant',{binding,receiverEpoch:String(epoch+1),capacity:1065});
    else if(e==='Quarantine')result=await send('quarantine',{binding,receiverEpoch:String(epoch)});
    else if(e==='BareSource')result=await send('legacy',sourceSeed);
    else {
     let event,domain=epoch;
     if(e==='Seed'||e==='WrongFloor')event=seed(epoch,previous.floor+(e==='WrongFloor'?1:0));
     else if(e==='Terminal'||e==='ForeignTerminal'){event=terminal;if(e==='ForeignTerminal')domain=epoch+1;}
     else if(['Complete','Gap','WrongEntry','ChangedComplete'].includes(e)){event=final(epoch,previous.floor);if(e==='Gap')event.deliveryOrdinal='2';if(e==='WrongEntry')event.event.entry='2';if(e==='ChangedComplete')event.event.requestFloor=String(previous.floor+1);}
     else if(e==='Source'||e==='OldSource'){event=sourceSeed;if(e==='OldSource')domain=epoch-1;}
     else if(e==='Request')event=request;
     else throw Error('Unknown model input '+e);
     result=await send('native',envelope(event,domain));
    }
   }else assert.equal(state.history.length,seen);
   const wanted=Object.fromEntries(Object.entries(state).filter(([k])=>!['history','floor','seeded','ready','terminalSeen'].includes(k)));
   assert.deepEqual(projection(result),wanted,path.basename(file)+' step '+seen+' '+state.history.at(-1));previous=state;count++;compared++;
  }
  traces.push({trace:path.basename(file),statesCompared:count});
 }
 console.log(JSON.stringify({passed:true,statesCompared:compared,coupledTraces:traces,singlePreviewPolicy:true,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
