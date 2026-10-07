'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process'),readline=require('node:readline');
function decode(v){if(Array.isArray(v))return v.map(decode);if(v&&typeof v==='object')return '#bigint' in v?Number(v['#bigint']):Object.fromEntries(Object.entries(v).map(([k,x])=>[k,decode(x)]));return v;}
async function replay(file){
 const child=spawn(process.argv[2],[],{stdio:['pipe','pipe','pipe']});let stderr='',pending;const buffered=[];
 child.stderr.on('data',v=>stderr+=v);const terminal=new Promise(resolve=>child.on('close',(code,signal)=>{resolve({code,signal});if(pending){clearTimeout(pending.timer);pending.reject(Error('Owned C fixture exited '+stderr));pending=null;}}));
 readline.createInterface({input:child.stdout}).on('line',line=>{const v=JSON.parse(line);if(pending){const p=pending;pending=null;clearTimeout(p.timer);p.resolve(v);}else buffered.push(v);});
 function next(){if(buffered.length)return Promise.resolve(buffered.shift());return new Promise((resolve,reject)=>{assert(!pending);const timer=setTimeout(()=>reject(Error('Original native ingress timeout '+stderr)),10000);pending={resolve,reject,timer};});}
 async function call(op,values={}){child.stdin.write(JSON.stringify({op,...values})+'\n');return next();}
 try{
  const setup=await next(),binding=setup.grant.binding,epoch=setup.epoch;
  const row={identity:'binding:'+Object.values(binding).join(':'),commands:[{kind:'reconcile',binding}]};
  const envelope=entries=>({previewProtocol:3,kind:'preview-proposals',binding,receiverEpoch:epoch,entries});
  const original=(await call('status')).result;let seen=0,accepted=false,ticket,count=0;
  for(const state of decode(JSON.parse(fs.readFileSync(file,'utf8'))).states.map(v=>v.s)){
   if(state.history.length>seen){assert.equal(state.history.length,seen+1);seen++;
    const e=state.history.at(-1),value=envelope([row]);let wire;
    if(e==='ForeignEpoch')value.receiverEpoch='2';
    else if(e==='ForeignBinding')value.binding={...binding,frontend:'1'};
    else if(e==='ExtraHeader')value.extra=true;
    else if(e==='MultipleRows')value.entries=[row,row];
    else if(e==='EmptyRows')value.entries=[];
    else if(e==='MalformedCommand')value.entries=[{...row,commands:[null]}];
    else if(e==='NumericEpoch')value.receiverEpoch=1;
    else if(e==='OrdinalHeader')value.controlOrdinal='1';
    else if(e==='Oversized')wire=JSON.stringify(value)+' '.repeat(4097);
    else assert.equal(e,'Valid');
    const result=await call('propose-envelope',{envelope:wire||JSON.stringify(value)});accepted=result.ok;
    assert.equal(accepted,state.accepted,path.basename(file)+' exact original admission '+e);
    if(accepted){assert(!result.refused && result.result);if(ticket)assert.equal(result.result.wire,ticket.wire,'Original native purpose bytes');ticket=result.result;}
    else assert(result.refused && result.result===null,'Refusal publishes no native ticket');
   }else assert.equal(state.history.length,seen);
   const inventory=await call('recovery-begin',{epoch});assert(inventory.ok);assert.equal(Number(inventory.result.issuedThrough),state.issued,path.basename(file)+' original native issued frontier');
   assert.deepEqual((await call('status')).result,original,'Ingress cannot settle or mutate original job/physical capture obligation');count++;
  }
  async function deliver(identity,command){const proposed=await call('propose-envelope',{envelope:JSON.stringify(envelope([{identity,commands:[command]}]))});assert(proposed.ok && !proposed.refused);
   const dispatched=await call('dispatch',{wire:proposed.result.wire});assert(dispatched.ok && dispatched.receipt);
   const confirmed=await call('confirm',{wire:JSON.stringify({...dispatched.receipt,kind:'preview-control-confirmed'})});assert(confirmed.ok && !confirmed.refused);
  }
  await deliver(row.identity,row.commands[0]);assert((await call('poll')).ok);
  const state=(await call('status')).result;assert(state.terminal && state.charge==='0');
  await deliver('family:21',{kind:'acknowledge',job:state.job,sequence:state.sequence});
  const seed=(await call('seed')).result;await deliver('family:21',{kind:'detach-ready',binding,receiverEpoch:epoch,subject:seed.subject,entry:seed.entry,entryIssuedThrough:seed.entryIssuedThrough,requestFloor:seed.requestFloor});
  assert((await call('poll')).ok);const final=(await call('pending')).result;assert.equal(final.length,1);
  await deliver('family:21',{kind:'detach-delivery-ack',binding,receiverEpoch:epoch,deliveryOrdinal:final[0].deliveryOrdinal});
  child.stdin.write(JSON.stringify({op:'finish'})+'\n');assert.deepEqual(await next(),{finished:true,normalOwnedPeerExit:true});child.stdin.end();assert.deepEqual(await terminal,{code:0,signal:null});assert.equal(stderr,'');
  return {trace:path.basename(file),statesCompared:count,normalOwnedExit:true};
 }catch(e){child.stdin.destroy();child.kill('SIGTERM');await terminal;throw e;}
}
(async()=>{const traces=[];for(const file of process.argv.slice(3))traces.push(await replay(file));
 console.log(JSON.stringify({passed:true,statesCompared:traces.reduce((n,t)=>n+t.statesCompared,0),coupledTraces:traces,actualControlledC:true,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
