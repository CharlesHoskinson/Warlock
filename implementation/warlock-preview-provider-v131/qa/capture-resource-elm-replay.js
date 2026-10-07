'use strict';
const {spawn}=require('node:child_process');
const {createInterface}=require('node:readline');
const {resolve}=require('node:path');
const assert=require('node:assert/strict');
const {Elm}=require(resolve(process.argv[3]));
let checks=0;
function check(value,message){assert(value,message);checks++;}
async function campaign(fault){
 const child=spawn(process.argv[2],fault?['post-transfer']:[],{stdio:['pipe','pipe','pipe']});
 const lines=[];let waiter=null,stderr='',terminal=null;
 child.stderr.on('data',chunk=>stderr+=chunk);
 const ended=new Promise((resolve,reject)=>{child.once('error',reject);child.once('close',(code,signal)=>{terminal={code,signal};resolve(terminal);});});
 createInterface({input:child.stdout}).on('line',line=>{if(waiter){const done=waiter;waiter=null;done(JSON.parse(line));}else lines.push(JSON.parse(line));});
 const read=()=>lines.length?Promise.resolve(lines.shift()):new Promise((resolve,reject)=>{const timer=setTimeout(()=>{waiter=null;reject(new Error('Actual mapped native reply timeout: '+stderr));},5000);waiter=value=>{clearTimeout(timer);resolve(value);};});
 try {
  const fixture=await read();check(fixture.postTransferAllocationFault===fault,'Actual capture prefix matches allocator-fault mode');
  const identity=fixture.seeds[0].identity;
  const app=Elm.PreviewPresenterReplay.init();let pending=null;
  app.ports.outgoing.subscribe(value=>{if(pending){const done=pending;pending=null;done(value);}});
  const send=(kind,value)=>new Promise((resolve,reject)=>{const timer=setTimeout(()=>{pending=null;reject(new Error('Actual Elm port timeout'));},3000);pending=value=>{clearTimeout(timer);resolve(value);};app.ports.incoming.send({kind,value});});
  const commands=value=>value.commands.flatMap(row=>row.commands),model=value=>value.models[0].model;
  await send('presentation',{surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[{id:identity,domId:'fixture-client',label:'Fixture',ariaLabel:'Fixture',detail:'',enabled:true}]});
  let result,issued=[];for(const seed of fixture.seeds){result=await send('native',seed);issued.push(...commands(result));}
  check(issued.length===1 && issued[0].kind==='acquire' && model(result).known.length===1,'Actual C source and request seed one original compiled Elm capture');
  const job=issued[0].job;
  // Native adopted the packet, but no offer reached Elm after the transport or
  // post-transfer allocation failure. Exhaustion retains the original Unknown.
  result=await send('native',{kind:'event',identity,event:{kind:'exhausted',binding:job.binding}});
  assert.deepEqual(commands(result),[{kind:'cancel',job},{kind:'reconcile',binding:job.binding}]);checks++;
  check(model(result).known.length===1 && model(result).cancelling.length===1 && !model(result).ready,'Original immutable Elm owner retains Unknown until physical proof');
  const before=structuredClone(model(result)),foreign=structuredClone(fixture.receipts.at(-1));foreign.event.event.job.request='999';
  result=await send('native',foreign);assert.deepEqual(model(result),before);checks++;check(commands(result).length===0,'Foreign terminal job cannot acknowledge original adopted storage');
  check(fixture.receipts[0].event.event.kind==='released' && fixture.receipts[1].event.event.kind==='cancelled','Actual adopted packet terminal wire is Released then Cancelled');
  result=await send('native',fixture.receipts[0]);
  check(commands(result).length===0 && model(result).known.length===1 && model(result).cancelling.length===1,'Unseen Released handle cannot discharge original Unknown cancellation');
  result=await send('native',fixture.receipts[1]);const ack=commands(result);
  assert.deepEqual(ack,[{kind:'acknowledge',job,sequence:fixture.receipts[1].event.sequence}]);checks++;
  check(model(result).known.length===0 && model(result).cancelling.length===0 && model(result).retiring.length===0 && !model(result).ready,'Actual final Cancelled proof drains Elm ownership while reconciliation remains required');
  child.stdin.write(JSON.stringify(ack[0])+'\n');child.stdin.end();const evidence=await read();const status=await ended;
  check(evidence.passed && evidence.actualImportedFDClosed && evidence.normalOwnedExit && evidence.postTransferAllocationFault===fault,'Actual compiled Elm final ACK reclaims mapped native journal');
  check(status.code===0 && !status.signal && !stderr,'Original mapped capture helper and socket child exit normally after all barriers');
 }finally{if(!terminal){child.stdin.end();child.kill('SIGTERM');await ended;}}
}
(async()=>{await campaign(false);await campaign(true);process.stdout.write(JSON.stringify({passed:true,checks,actualCompiledElm:true,actualMappedNativeACK:true,normalOwnedExits:2,nativeAcceptance:false})+'\n');})().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1;});
