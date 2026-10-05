'use strict';
// Real compiled PreviewPresenter/PreviewLifecycle ports and a live physical
// Broker journal. Explicit native CPU fixture clocks, no compositor claim.
const {spawn}=require('node:child_process');
const {createInterface}=require('node:readline');
const {resolve}=require('node:path');
const assert=require('node:assert/strict');
const {Elm}=require(resolve(process.argv[3]));
let checks=0;
function check(value,message){assert(value,message);checks++;}
async function campaign(kind){
 const child=spawn(process.argv[2],['--bridge-'+kind],{stdio:['pipe','pipe','pipe']});
 const lines=[];let waiter=null,stderr='';let terminal=null;
 child.stderr.on('data',chunk=>stderr+=chunk);
 const ended=new Promise((resolve,reject)=>{child.once('error',reject);child.once('close',(code,signal)=>{terminal={code,signal};resolve(terminal);});});
 createInterface({input:child.stdout}).on('line',line=>{if(waiter){const done=waiter;waiter=null;done(JSON.parse(line));}else lines.push(JSON.parse(line));});
 const read=()=>lines.length?Promise.resolve(lines.shift()):new Promise((resolve,reject)=>{const timer=setTimeout(()=>{waiter=null;reject(new Error('Native receipt reply timeout: '+stderr));},5000);waiter=value=>{clearTimeout(timer);resolve(value);};});
 const nativeAck=async command=>{child.stdin.write(JSON.stringify(command)+'\n');return read();};
 try {
  const fixture=await read();const scope=JSON.parse(fixture.scopeJSON),identity=fixture.identity;
  const app=Elm.PreviewPresenterReplay.init();const results=[];let pending=null;
  app.ports.outgoing.subscribe(value=>{results.push(value);if(pending){const done=pending;pending=null;done(value);}});
  const send=(kind,value)=>new Promise((resolve,reject)=>{const timer=setTimeout(()=>{pending=null;reject(new Error('Actual Elm port timeout'));},3000);pending=value=>{clearTimeout(timer);resolve(value);};app.ports.incoming.send({kind,value});});
  await send('presentation',{surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[{id:identity,domId:'fixture-family',label:'Fixture',ariaLabel:'Fixture',detail:'',enabled:true}]});
  let result=await send('native',{kind:'seed',publication:'1',lease:'1',identity,scope,title:'Fixture',application:'CPU source'});
  check(result.models.length===1 && result.models[0].model.demand,'Actual Presenter accepts exact published family seed');
  const terminalEvent=fixture.receipts[0].event.event;
  const job=terminalEvent.job || terminalEvent.frame.job;
  const trigger={...job};delete trigger.request;
  result=await send('native',{kind:'event',identity,event:{kind:'request',trigger}});
  assert.deepEqual(result.commands,[{identity,commands:[{kind:'acquire',job}]}]);checks++;
  if(kind==='released') {
   const offer=JSON.parse(fixture.offerJSON),fence=JSON.parse(fixture.fenceJSON);
   await send('native',{kind:'event',identity,event:{kind:'offer',frame:offer}});
   result=await send('native',{kind:'event',identity,event:{kind:'fence',frame:fence}});
   check(result.models[0].model.state==='Live' && result.models[0].model.accepted.fidelity==='family','Actual Elm accepts exact native family packet and fence');
   result=await send('native',{kind:'event',identity,event:{kind:'expired',frame:fence}});
   check(result.commands[0].commands[0].kind==='release' && result.models[0].model.retiring.length===1,'Actual Elm expiration requests physical release and retains owner');
  }
  result=await send('presentation',{surfaceProtocol:2,publication:'2',lease:'1',mode:'closed',status:'',bar:[],popup:[]});
  check(result.models.length===1 && !result.models[0].active && result.models[0].model.known.length===1,'UI close retains actual lifecycle cleanup journal');
  const final=fixture.receipts.at(-1).event.sequence;
  const wrong={kind:'acknowledge',job,sequence:String(BigInt(final)+1n)};
  let native=await nativeAck(wrong);
  check(!native.accepted && native.records===1 && native.pending===fixture.receipts.length,'Wrong final sequence leaves actual live Broker proof retained');
  if(kind==='refused') {
   native=await nativeAck({...wrong,sequence:fixture.receipts[0].event.sequence});
   check(!native.accepted && native.records===1,'Earlier raced refusal cannot reclaim cancellation proof');
  }
  const mutated=structuredClone(fixture.receipts.at(-1));mutated.identity='family:1';
  result=await send('native',mutated);
  check(result.commands.length===0 && result.models[0].model.known.length===1,'Foreign family terminal event cannot discharge actual Elm owner');
  let acknowledgments=[];
  for(const receipt of fixture.receipts){result=await send('native',receipt);acknowledgments.push(...result.commands.flatMap(value=>value.commands));}
  check(acknowledgments.length===1 && acknowledgments[0].kind==='acknowledge' && acknowledgments[0].sequence===final,'Actual Elm emits exact final cleanup ACK after native proof');
  native=await nativeAck(acknowledgments[0]);
  check(native.accepted && native.records===0 && native.pending===0,'Actual compiled Elm ACK retires the live physical Broker journal');
  check(result.models[0].model.known.length===0 && result.models[0].model.cancelling.length===0 && result.models[0].model.retiring.length===0,'Actual Elm cleanup obligations drain');
  result=await send('native',fixture.receipts.at(-1));
  native=await nativeAck(result.commands[0].commands[0]);
  check(!native.accepted && native.records===0,'Replayed actual Elm ACK cannot recreate or retire another native job');
  child.stdin.end();const status=await ended;
  check(status.code===0 && !status.signal && !stderr,'Native bridge fixture exits normally with empty retained journal');
 }finally{if(!terminal){child.stdin.end();child.kill('SIGTERM');await ended;}}
}
(async()=>{await campaign('refused');await campaign('released');process.stdout.write(JSON.stringify({passed:true,checks,nativeAcceptance:false,scope:'Actual compiled Presenter lifecycle and live Broker terminal journal'})+'\n');})().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1;});
