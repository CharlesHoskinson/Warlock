'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {Elm}=require(path.resolve(process.argv[2]));
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
assert.equal(crypto.createHash('sha256').update(fs.readFileSync(fixture.sourceReport)).digest('hex'),fixture.sourceReportSHA256);
const source=fixture.clientScope,frame=fixture.terminalReceipts[0].event.event.frame,job=frame.job,identity='family:'+job.context.incarnation;
let checks=0;
function check(ok,message){assert(ok,message);checks++;}
function equal(actual,expected,message){assert.deepEqual(actual,expected,message);checks++;}
function worker(){
 const app=Elm.PreviewPresenterReplay.init();let pending=null;
 app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});
 return (kind,value)=>new Promise((resolve,reject)=>{assert.equal(pending,null);const timer=setTimeout(()=>{pending=null;reject(new Error('Original three-second Elm denial replay deadline'));},3000);pending=value=>{clearTimeout(timer);resolve(value);};app.ports.incoming.send({kind,value});});
}
const native=(event)=>({kind:'event',identity,event});
const trigger=(owned=job)=>{const value=structuredClone(owned);delete value.request;return value;};
const seed=()=>({kind:'source-seed',publication:'1',lease:'1',identity,source:structuredClone(source),title:'Native source',application:'warlock-child-probe'});
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[{id:identity,domId:'client',label:'Client',ariaLabel:'Client',detail:'',enabled:true}]};
const commands=r=>r.commands.flatMap(row=>row.commands),model=r=>r.models[0].model;
async function prepared(stage){const send=worker();await send('presentation',presentation);await send('native',seed());let result=await send('native',native({kind:'request',trigger:trigger()}));equal(commands(result),[{kind:'acquire',job}],'Original exact Acquire');
 if(stage!=='capturing')result=await send('native',native({kind:'offer',frame:{...frame,signaled:false}}));
 if(stage==='accepted')result=await send('native',native({kind:'fence',frame}));
 return {send,result};}
(async()=>{
 check(BigInt(job.binding.lifetime)>2n**53n,'Actual native identity remains lossless beyond JavaScript integer precision');
 for(const reason of ['locked','source-unavailable','output-unavailable','layout-unsupported'])for(const stage of ['capturing','candidate','accepted']){
  let {send,result}=await prepared(stage);const before=structuredClone(model(result));
  for(const mutation of [v=>{v.reason='transport-error';},v=>{v.extra=true;},v=>{v.job.binding.session='999';},v=>{v.job.request='999';},v=>{v.job.clock='1';},v=>{v.job.deadline='1';},v=>{v.job.binding.lifetime=Number(v.job.binding.lifetime);},v=>{v.reason=false;}]){
   const value={kind:'source-denied',job:structuredClone(job),reason};mutation(value);const ignored=await send('native',native(value));equal(model(ignored),before,'Malformed/foreign/stale denial retains owner');equal(commands(ignored),[],'Ignored denial emits no effect');
  }
  result=await send('native',native({kind:'source-denied',job,reason}));
  const expected=stage==='capturing'?{kind:'cancel',job}:{kind:'release',frame:stage==='candidate'?{...frame,signaled:false}:frame};
  equal(commands(result),[expected],'Exact original owned cleanup command');equal(model(result).scope,before.scope,'Denial fabricates no scope, clock or generation');
  check(!model(result).ready && model(result).known.length===1 && model(result).state==='unavailable','Capture suspended with original obligation retained');
  check(stage==='capturing'?model(result).cancelling.length===1:model(result).retiring.length===1,'No fabricated Refused or terminal resource outcome');
  const suspended=structuredClone(model(result));
  result=await send('native',native({kind:'source-denied',job,reason}));equal(model(result),suspended,'Duplicate denial is idempotent');equal(commands(result),[],'No duplicate cleanup');
  result=await send('native',native({kind:'request',trigger:trigger()}));equal(model(result),suspended,'Suspended demand cannot recapture');equal(commands(result),[],'No replayed Acquire');
  result=await send('native',native({kind:'observe',scope:source.scope}));equal(model(result),suspended,'Stale scope cannot resume');
  let observed=structuredClone(source.scope);observed.observation=String(BigInt(observed.observation)+1n);observed.now=String(BigInt(observed.now)+1n);observed.locked=true;
  result=await send('native',native({kind:'observe',scope:observed}));check(!model(result).ready,'Admitted locked observation remains suspended');equal(commands(result),[],'No cleanup replay on locked observation');
  observed={...observed,observation:String(BigInt(observed.observation)+1n),now:String(BigInt(observed.now)+1n),locked:false};
  result=await send('native',native({kind:'observe',scope:observed}));check(model(result).ready && model(result).known.length===1,'Fresh coherent live native scope resumes authority while ownership remains');equal(commands(result),[],'Scope resume creates no automatic Acquire');
  result=await send('native',native({kind:'request',trigger:trigger()}));equal(commands(result),[],'Cleanup still blocks new allocation after resume');
  const terminal=stage==='capturing'?native({kind:'receipt',sequence:'3',event:{kind:'cancelled',job}}):fixture.terminalReceipts[0];
  result=await send('native',terminal);equal(commands(result),[{kind:'acknowledge',job,sequence:'3'}],'Exact terminal proof yields original ACK');check(model(result).known.length===0 && model(result).retiring.length===0 && model(result).cancelling.length===0,'Only terminal proof drains Elm obligations');
  result=await send('native',native({kind:'request',trigger:trigger()}));const next={...job,request:'2'};equal(commands(result),[{kind:'acquire',job:next}],'Explicit new demand has new request and unchanged original trigger deadline');
  const newer=structuredClone(model(result));result=await send('native',native({kind:'source-denied',job,reason}));equal(model(result),newer,'Late older denial cannot suspend newer capture');equal(commands(result),[],'No newer cleanup from old denial');
 }
 for(const stage of ['capturing','candidate']){
  let {send,result}=await prepared('accepted');const next={...job,request:'2',origin:'2'};
  result=await send('native',native({kind:'request',trigger:trigger(next)}));equal(commands(result),[{kind:'acquire',job:next}],'Second capture retains accepted first frame');
  if(stage==='candidate')result=await send('native',native({kind:'offer',frame:{...frame,job:next,handle:'0000000000000000000000000000000000000000000000000000000000000002',signaled:false}}));
  const before=structuredClone(model(result));result=await send('native',native({kind:'source-denied',job,reason:'locked'}));equal(model(result),before,'Older accepted packet denial does not revoke newer capturing/waiting owner');equal(commands(result),[],'Newer owner remains unaffected');
 }
 {
  const {send}=await prepared('capturing');let result=await send('native',native({kind:'exhausted',binding:job.binding}));check(!model(result).ready,'Unknown authority requires reconciliation');
  let observed=structuredClone(source.scope);observed.observation=String(BigInt(observed.observation)+1n);observed.now=String(BigInt(observed.now)+1n);
  result=await send('native',native({kind:'observe',scope:observed}));check(!model(result).ready,'Fresh observation cannot automatically reconcile Unknown');equal(commands(result),[],'Unknown operation is not replayed');
 }
 console.log(JSON.stringify({passed:true,checks,nativeAcceptance:false,fullReleaseAccepted:false,scope:'Actual optimized Elm Popup-shared lifecycle typed denial and scope-resume policy against retained original native fixture; simulated delivery, no live native lock/physical retirement claim'}));
})().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1;});
