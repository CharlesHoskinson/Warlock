'use strict';
const fs=require('fs'),assert=require('assert/strict'),{spawn}=require('child_process'),readline=require('readline');
const [binary,policy,outbox]=process.argv.slice(2),child=spawn(binary,[policy,outbox],{stdio:['pipe','pipe','pipe']});
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
 const setup=await next();check(setup.preGrantFaultChecks===9,'Original pre-grant constructor controls retained');
 await start(setup.epoch,setup.events,'21','1');const first=await drain(setup.epoch,true);
 check(empty(first),'First original realm duties settled');check((await call('retire')).ok,'Strict original C/Bootstrap close retains policy');
 const closed=await inspect();check(closed.privatePolicy.realm.closed&&closed.privatePolicy.realm.epoch===setup.epoch,'Same policy acknowledges original Native close');
 const later=await call('next-realm');check(later.ok&&!later.refused,'Original Native issues later empty namespace after strict close');const grant=later.result.grant;
 check(BigInt(grant.receiverEpoch)>BigInt(setup.epoch),'Original epoch strictly advances');same(grant.binding,setup.grant.binding,'Original Native transport binding unchanged');
 for(const variant of ['old-epoch','foreign-binding','outbox']){
  check((await call('bad-reopen',{variant})).refused,'Reject '+variant+' before policy custody transfer');same(await inspect(),closed,'Pre-transfer refusal retains exact closed policy/custody');
 }
 check((await call('reopen')).ok,'Rebind actual later C namespace to exact same persistent policy');
 const opened=await inspect();same(opened.privatePolicy.realm.epoch,grant.receiverEpoch,'Original policy enrolls actual later epoch');
 check(!opened.privatePolicy.realm.closed&&!opened.privatePolicy.realm.closing,'Later realm open in same policy');
 same(opened.transport,{nativeIssuedThrough:'0',deliveredThrough:'0',pending:0,capacity:1065},'Only later realm-bound outbox begins empty');
 check((await call('native',{epoch:setup.epoch,events:JSON.stringify(setup.events)})).refused,'Old epoch refused before JS');same(await inspect(),opened,'Old source epoch changes no policy/native custody');
 // Trusted adversarial replay of the exact original source facts in the later
 // envelope must still respect the permanent incarnation-retirement ledger.
 await submit(grant.receiverEpoch,setup.events);await pump();const retiredReplay=await inspect();
 same(retiredReplay.privatePolicy.models,[],'Same persistent policy refuses resurrection of permanently retired subject21');
 same(retiredReplay.transport.nativeIssuedThrough,'0','Retired replay issues no new original native acquisition');
 await start(grant.receiverEpoch,later.result.events,'22','2');const captured=(await call('native-status')).result;
 same(captured.captures,'2','Two actual C captures on original authenticated synthetic peer');
 const second=await drain(grant.receiverEpoch,false);check(empty(second),'Second independent original physical/journal/confirmation drain');
 const done=await call('finish');check(done.finished&&done.normalOwnedPeerExit&&done.nativeGrantResets===0,'Original strict final close on unchanged Native grant');
 child.stdin.end();const exit=await terminal;check(exit.code===0&&exit.signal===null&&stderr==='','Normal sanitizer owner and peer teardown');
 fs.writeFileSync('steps.json',JSON.stringify(steps,null,2)+'\n');
 console.log(JSON.stringify({passed:true,checks,nativePolicyInstances:1,nativeTransportInstances:2,rendererWindowPolicies:0,actualControlledC:true,actualSyntheticCapturedFD:true,normalOwnedExit:true,normalOwnedPeerExit:true,nativeGrantResets:0,originalBindingPreserved:true,originalPolicyPointerPreserved:true,permanentRetiredSubjectCannotResurrect:true,actualWebKit:false,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(error=>{child.kill('SIGTERM');fs.writeFileSync('failed-steps.json',JSON.stringify(steps,null,2)+'\n');console.error(error.stack);process.exitCode=1;});
