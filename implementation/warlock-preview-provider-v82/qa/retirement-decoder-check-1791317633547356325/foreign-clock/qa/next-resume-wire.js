'use strict';
const assert=require('node:assert/strict'),{spawn}=require('node:child_process'),{createInterface}=require('node:readline'),{resolve}=require('node:path');
const {Elm}=require(resolve(process.argv[3]));let checks=0;
const check=(a,b,message)=>{assert.deepEqual(a,b,message);checks++;};
const presentation=(id,publication,lease,open=true)=>({surfaceProtocol:2,publication:String(publication),lease:String(lease),mode:open?'picker':'closed',status:'',bar:[],popup:open?[{id,domId:'next-resume',label:'Client',ariaLabel:'Client',detail:'',enabled:true}]:[]});
const cmds=r=>r.commands.flatMap(row=>row.commands);
async function main(){
 const child=spawn(process.argv[2],['next-resume'],{stdio:['pipe','pipe','pipe']});let stderr='',terminal=null,waiter=null;const lines=[];
 child.stderr.on('data',v=>stderr+=v);const ended=new Promise((resolve,reject)=>{child.once('error',reject);child.once('close',(code,signal)=>{terminal={code,signal};resolve(terminal);});});
 createInterface({input:child.stdout}).on('line',line=>{const value=JSON.parse(line);if(waiter){const done=waiter;waiter=null;done(value);}else lines.push(value);});
 const read=()=>lines.length?Promise.resolve(lines.shift()):new Promise((resolve,reject)=>{const timer=setTimeout(()=>{waiter=null;reject(Error('Original five-second C fixture deadline: '+stderr));},5000);waiter=v=>{clearTimeout(timer);resolve(v);};});
 const native=async command=>{child.stdin.write(JSON.stringify(command)+'\n');return read();};
 try{
  const fixture=await read();const app=Elm.PreviewFeedbackReplay.init();let pending=null;
  app.ports.outgoing.subscribe(v=>{assert(pending);const done=pending;pending=null;done(v);});
  const send=(kind,value)=>new Promise((resolve,reject)=>{assert.equal(pending,null);const timer=setTimeout(()=>{pending=null;reject(Error('Original three-second Elm port deadline'));},3000);pending=v=>{clearTimeout(timer);resolve(v);};app.ports.incoming.send({kind,value});});
  await send('presentation',presentation(fixture.identity,1,1));let result;
  for(const value of fixture.originalRegistration)result=await send('native',value);
  check(cmds(result),[{kind:'acquire',job:fixture.originalJob}],'Original actual job registers in same Elm owner');
  const originalProof=fixture.originalReceipts.at(-1);result=await send('native',originalProof);
  check(cmds(result),[{kind:'acknowledge',job:fixture.originalJob,sequence:originalProof.event.sequence}],'Original exact native terminal tuple');
  check(result.models[0].model.nextRequest,'2','Original terminal keeps next request2');check(result.models[0].model.known,[],'Original known job settles');
  await send('presentation',presentation(fixture.identity,2,1,false));await send('presentation',presentation(fixture.identity,3,2));
  for(const value of fixture.waiting)result=await send('native',value);
  check(result.feedback[0].label,'Waiting for preview capacity','Actual unissued resume reaches same presenter');check(cmds(result),[],'Capacity emits no job effect');check(result.models[0].model.nextRequest,'2','Capacity keeps old request history');
  for(const value of fixture.expired)result=await send('native',value);
  check(result.feedback[0].label,'Preview request expired','Actual original resume expiry');check(result.feedback[0].deadline,fixture.waiting[0].deadline,'Same-intent original cutoff');check(cmds(result),[],'Expired unissued resume cannot acquire or ACK');
  await send('presentation',presentation(fixture.identity,4,2,false));await send('presentation',presentation(fixture.identity,5,3));
  for(const value of fixture.successor)result=await send('native',value);
  check(result.feedback[0].label,'Waiting for preview capacity','Explicit successor respects native capacity');check(result.feedback[0].deadline,fixture.successor[0].deadline,'Successor original cutoff');check(result.models[0].model.nextRequest,'2','Succession cannot reset Elm history');
  const current=structuredClone(result.feedback);for(const value of fixture.expired)result=await send('native',value);
  check(result.feedback,current,'Old stamp/sequence cannot replace successor');check(cmds(result),[],'Old expiry cannot issue or consume proof');
  const finalProof=fixture.receipts.at(-1);result=await send('native',finalProof);check(cmds(result),[],'Unknown future terminal proof cannot settle before registration');
  for(const value of fixture.registration)result=await send('native',value);
  check(result.feedback[0].outcome,null,'Actual issued source clears wait');check(cmds(result),[{kind:'acquire',job:fixture.job}],'Exact next native job reaches unchanged Elm lifecycle');check(fixture.job.request,'2','Native floor and Elm counter agree');check(fixture.job.deadline,fixture.successor[0].deadline,'Issued job keeps successor cutoff');
  let actual=await native(cmds(result)[0]);check(actual,{accepted:true,events:[],records:2,floor:2},'Real native rejection suppresses replay and retains proof/other owner');
  actual=await native({kind:'acknowledge',job:fixture.job,sequence:String(BigInt(finalProof.event.sequence)+1n)});check(actual.accepted,false,'Wrong final sequence refused');check(actual.records,2,'Wrong ACK leaves original ownership');
  result=await send('native',finalProof);check(cmds(result),[{kind:'acknowledge',job:fixture.job,sequence:finalProof.event.sequence}],'Exact new native terminal tuple');
  actual=await native(cmds(result)[0]);check(actual,{accepted:true,events:[],records:1,floor:2},'Actual Elm ACK retires only the rejected successor');
  actual=await native(cmds(result)[0]);check(actual.accepted,false,'Consumed final proof cannot be replayed');check(actual.floor,2,'Duplicate ACK cannot reset native floor');
  child.stdin.end();const summary=await read();check(summary.passed,true,'Exact C remaining ownership cleanup');const status=await ended;check(status,{code:0,signal:null},'Actual C/socket fixture normal exit');check(stderr,'','No sanitizer or native errors');
  process.stdout.write(JSON.stringify({passed:true,checks,cControls:summary.checks,nativeAcceptance:false,fullReleaseAccepted:false,scope:'Actual own C/socket/bootstrap/delivery successor resume outputs and final ACK through current optimized Elm. Native scope fault is synthetic; no compositor/pixel/whole-policy refinement claim.'})+'\n');
 }finally{if(!terminal){child.stdin.end();child.kill('SIGTERM');await ended;}}
}
main().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1;});
