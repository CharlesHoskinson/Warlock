'use strict';
const fs=require('fs'),assert=require('assert/strict'),{spawn}=require('child_process'),readline=require('readline');
const [binary,policy,outbox,side]=process.argv.slice(2),child=spawn(binary,[policy,outbox],{stdio:['pipe','pipe','pipe']});
let stderr='',checks=0,pending;const rows=[],steps=[];child.stderr.on('data',v=>stderr+=v);
const terminal=new Promise(resolve=>child.on('close',(code,signal)=>{resolve({code,signal});if(pending){clearTimeout(pending.timer);pending.reject(Error('Native fixture exit '+stderr));pending=null;}}));
readline.createInterface({input:child.stdout}).on('line',line=>{const row=JSON.parse(line);if(pending){const p=pending;pending=null;clearTimeout(p.timer);p.resolve(row);}else rows.push(row);});
function next(){if(rows.length)return Promise.resolve(rows.shift());return new Promise((resolve,reject)=>{assert(!pending);const timer=setTimeout(()=>reject(Error('Original ten-second native fixture observation deadline '+stderr)),10000);pending={resolve,reject,timer};});}
async function call(op,values={}){child.stdin.write(JSON.stringify({op,...values})+'\n');const result=await next();steps.push({input:{op,...values},result});return result;}
const check=(value,label)=>{assert(value,label);checks++;},same=(a,b,label)=>{assert.deepEqual(a,b,label);checks++;};
async function inspect(){const r=await call('inspect');check(r.ok&&!r.refused,'Original creator diagnostic state');return r.result;}
async function pump(){for(let i=0;i<128;i++){const r=await call('step');check(r.ok&&!r.refused,'Original bounded driver action');if(!r.progressed)return;}throw Error('Original128 bounded driver actions exhausted');}
async function submit(epoch,events){if(!events.length)return;const r=await call('native',{epoch,events:JSON.stringify(events)});check(r.ok&&!r.refused,'Exact original native event batch retained');}
const presentation=(subject,stamp)=>({surfaceProtocol:2,publication:stamp,lease:stamp,mode:'picker',status:'',bar:[],popup:[{id:'family:'+subject,domId:'window-'+subject,label:'Window',ariaLabel:'Window',detail:'',enabled:true}]});
function empty(state){return !state.privatePolicy.models.length&&!state.privatePolicy.realm.ingress.pending&&!state.privatePolicy.realm.deferred&&!state.retainedInputs&&!state.postedTickets&&!state.confirmations&&!state.returnedEventBatches&&!state.transport.pending;}
async function start(epoch,events,subject,stamp){
 check((await call('presentation',{value:JSON.stringify(presentation(subject,stamp))})).ok,'Original admitted presentation');
 await submit(epoch,events);await pump();const state=await inspect();
 check(state.privatePolicy.models.some(row=>row.identity==='family:'+subject&&row.model?.image?.startsWith('elm-shell://preview/')),'Actual C sealed-FD offer/fence drawable in same policy');
 check((await call('readiness')).result.ready===false,'Live original physical/policy custody refuses readiness');
 check((await call('retire-probe')).refused,'No early original realm retirement');
 check((await call('reopen-probe')).refused,'No policy transfer from an open realm');
 return state;
}
async function drain(epoch,permanent){
 if(permanent){const r=await call('retired-subject');check(r.ok&&r.result.length>0,'Actual authenticated native Retired observation');await submit(epoch,r.result);}
 else {check((await call('quarantine',{epoch})).ok,'Original urgent quarantine');const r=await call('seed');check(r.ok&&r.result.receiverEpoch===epoch,'Actual original scoped detachment seed');await submit(epoch,[r.result]);}
 await pump();
 for(let round=0;round<12;round++){
  for(const op of ['poll','terminal',permanent?'retirement-pending':'pending']){const r=await call(op);check(r.ok&&!r.refused,'Original '+op+' producer custody');await submit(epoch,r.result);await pump();}
  const state=await inspect();if(empty(state)){
   check((await call('readiness')).result.ready===true,'Original policy/native/physical/journal/independent-confirmation readiness');return state;
  }
 }
 throw Error('Original finite12 retirement observation rounds exhausted');
}
(async()=>{
 assert(['near','expired'].includes(side),'exact modeled clock mode');
 const setup=await next();check(setup.preGrantFaultChecks===9,'Original pre-grant constructor controls retained');
 const original=(await call('original-job')).result.job;
 await start(setup.epoch,setup.events,'21','1');
 const boundary=await call('advance-original-clock',{side});check(boundary.ok&&!boundary.refused,'Actual modeled native source reached cutoff boundary');
 same(boundary.result.original,original,'One original complete native job and deadline before quarantine');
 const first=await drain(setup.epoch,false);check(empty(first),'Live subject original realm physical duties settled');
 const terminalSteps=steps.filter(row=>['poll','terminal','pending'].includes(row.input.op));
 const findJob=(value)=>{if(!value||typeof value!=='object')return false;if(value.job&&JSON.stringify(value.job)===JSON.stringify(original))return true;return Object.values(value).some(findJob);};
 check(terminalSteps.some(row=>findJob(row.result)),'Exact original job present in real drained bridge receipt');
 check((await call('retire')).ok,'Strict old owner retirement');
 const closed=await inspect();check(closed.privatePolicy.realm.closed,'Original policy reports closed old realm');
 const later=await call('next-realm');let comparison=null,openRefusal=null,finalEpoch=null;
 if(later.refused){
  openRefusal=later.result;check(openRefusal.classification==='open-refused','Record actual refused replacement without fabricating a job');
 } else {
  check(later.ok&&later.result.comparison,'Record actual later owner issuance');comparison=later.result.comparison;
  same(comparison.original,original,'Actual comparison retains original complete Job');
  check(['issued','no-job'].includes(comparison.classification)&&comparison.publication==='1'&&comparison.lease==='1','Record actual later issuance or no-job at original stamp');
  if(comparison.classification==='issued')check(comparison.sameNativeBinding&&comparison.sameSubject&&comparison.sameClock,'Same native binding, subject and clock for actual issued job');
  const grant=later.result.grant;check(BigInt(grant.receiverEpoch)>BigInt(setup.epoch),'Actual later receiver epoch');same(grant.binding,setup.grant.binding,'Original native binding unchanged');
  check((await call('reopen')).ok,'Actual policy driver reopens after strict close');finalEpoch=grant.receiverEpoch;
  const reopened=await inspect();same(reopened.privatePolicy.realm.epoch,finalEpoch,'Real policy observed later epoch');
  check((await call('presentation',{value:JSON.stringify(presentation('21','1'))})).ok,'Actual later same-stamp presentation');
  await submit(finalEpoch,later.result.events);await pump();
  const laterState=await inspect();comparison.policyModels=laterState.privatePolicy.models;comparison.afterPolicy=(await call('native-status')).result;
  const second=await drain(finalEpoch,false);check(empty(second),'Actual later owner duties settled');
 }
 const done=await call('finish');check(done.finished&&done.normalOwnedPeerExit&&done.nativeGrantResets===0,'Original strict close and peer exit');
 child.stdin.end();const exit=await terminal;check(exit.code===0&&exit.signal===null&&stderr==='','Original sanitizer normal teardown');
 fs.writeFileSync('steps-'+side+'.json',JSON.stringify(steps,null,2)+'\n');
 console.log(JSON.stringify({traceRecorded:true,side,checks,original,boundary:boundary.result,terminalSteps,comparison,openRefusal,finalEpoch,clockKind:'monotonic modeled source, not hardware time',actualWebKit:false,nativeAcceptance:false,requirementAccepted:false,fullReleaseAccepted:false}));
})().catch(error=>{child.kill('SIGTERM');fs.writeFileSync('failed-steps-'+side+'.json',JSON.stringify(steps,null,2)+'\n');console.error(error.stack);process.exitCode=1;});
