'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {spawn}=require('node:child_process'),readline=require('node:readline');
const context=vm.createContext({TextEncoder});vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),context);
const child=spawn(process.argv[3],[],{stdio:['pipe','pipe','pipe']});let stderr='',pending;
child.stderr.on('data',value=>stderr+=value);const buffered=[];
const terminal=new Promise(resolve=>child.on('close',(code,signal)=>{resolve({code,signal});if(pending){clearTimeout(pending.timer);pending.reject(new Error(stderr));pending=null;}}));
readline.createInterface({input:child.stdout}).on('line',line=>{const value=JSON.parse(line);if(pending){const waiter=pending;pending=null;clearTimeout(waiter.timer);waiter.resolve(value);}else buffered.push(value);});
function next(){if(buffered.length)return Promise.resolve(buffered.shift());return new Promise((resolve,reject)=>{assert(!pending);const timer=setTimeout(()=>reject(new Error('Native confirmation fixture timeout '+stderr)),10000);pending={resolve,reject,timer};});}
async function native(op,wire){child.stdin.write(JSON.stringify({op,...(wire===undefined?{}:{wire:typeof wire==='string'?wire:JSON.stringify(wire)})})+'\n');return next();}
let checks=0;function check(ok){assert(ok);checks++;}function same(a,b){assert.deepEqual(a,b);checks++;}
const binding={lifetime:'17',session:'18',frontend:'19'},grant={binding,receiverEpoch:'1',capacity:2};
const packets=[],confirmations=[];let failConfirmation=false;
const outbox=context.WarlockRetainedPreviewControls(grant,wire=>packets.push(wire),receipt=>{confirmations.push(JSON.parse(JSON.stringify(receipt)));if(failConfirmation)throw new Error('Lost confirmation post');});
(async()=>{
 check(outbox.offer('family:21',{kind:'acquire',job:{request:'1'}}));const original=packets.at(-1);
 const delivered=await native('packet',original);same(delivered.invoked,1);same(delivered.effectOutcome,'Unknown');
 const blocked=await native('status');check(!blocked.closeAllowed);same(blocked.nativeConfirmed,'0');same(blocked.receipt,delivered.receipt);
 // Lose native's receipt; exact packet retry repeats the receipt only.
 check(outbox.retry());same(packets.at(-1),original);const repeated=await native('packet',original);same(repeated.decision,2);same(repeated.invoked,1);
 check(outbox.acknowledge(repeated.receipt));same(outbox.snapshot().pending,0);same(confirmations.at(-1).controlOrdinal,'1');
 // Lose frontend's first confirmation, despite known frontend receipt delivery.
 const stillBlocked=await native('status');check(!stillBlocked.closeAllowed);same(stillBlocked.nativeConfirmed,'0');
 const nativeRetry=await native('replay-receipt');same(nativeRetry.invoked,1);same(nativeRetry.receipt,repeated.receipt);
 const packetCount=packets.length;check(outbox.acknowledge(nativeRetry.receipt));same(packets.length,packetCount);same(confirmations.at(-1).controlOrdinal,'1');
 const confirmed=await native('confirm',confirmations.at(-1));same(confirmed,{confirmed:true,invoked:1,nativeConfirmed:'1',closeAllowed:true});
 const future=await native('confirm',{...confirmations.at(-1),controlOrdinal:'3'});check(!future.confirmed);same(future.nativeConfirmed,'1');
 check(outbox.offer('family:21',{kind:'cancel',job:{request:'1'}}));const second=await native('packet',packets.at(-1));same(second.invoked,2);check(!(await native('status')).closeAllowed);
 failConfirmation=true;check(outbox.acknowledge(second.receipt));same(outbox.snapshot().pending,0);same(outbox.snapshot().confirmed,'2');
 const lostAgain=await native('status');check(!lostAgain.closeAllowed);same(lostAgain.nativeConfirmed,'1');
 failConfirmation=false;const beforeRetryPackets=packets.length;check(outbox.retry());same(packets.length,beforeRetryPackets);
 same(confirmations.at(-1).controlOrdinal,'2');const cumulative=await native('confirm',confirmations.at(-1));same(cumulative,{confirmed:true,invoked:2,nativeConfirmed:'2',closeAllowed:true});
 // A known older receipt repeats the latest compact confirmation, never a job.
 check(outbox.acknowledge(delivered.receipt));same(confirmations.at(-1).controlOrdinal,'2');same(packets.length,beforeRetryPackets);
 check(outbox.offer('family:21',{kind:'release',job:{request:'1'}}));const third=await native('packet',packets.at(-1));same(third.invoked,3);
 for(const bad of [{...confirmations.at(-1),controlOrdinal:'3',receiverEpoch:'2'},
  {...confirmations.at(-1),controlOrdinal:'3',binding:{...binding,frontend:'20'}}]){
  const rejected=await native('confirm',bad);check(!rejected.confirmed);check(!rejected.closeAllowed);same(rejected.nativeConfirmed,'2');
 }
 check(outbox.acknowledge(third.receipt));const final=await native('confirm',confirmations.at(-1));same(final,{confirmed:true,invoked:3,nativeConfirmed:'3',closeAllowed:true});
 same(outbox.snapshot().pending,0);same(outbox.snapshot().confirmed,'3');
 // Confirmation callbacks cannot recursively repost a duplicate receipt.
 let synchronous,depth=0,maxDepth=0,confirmCount=0;const immediatePackets=[];
 synchronous=context.WarlockRetainedPreviewControls(grant,wire=>immediatePackets.push(wire),receipt=>{
  depth++;maxDepth=Math.max(depth,maxDepth);confirmCount++;
  synchronous.acknowledge({...receipt,kind:'preview-control-delivered'});depth--;
 });
 check(synchronous.offer('family:21',{kind:'acknowledge'}));check(synchronous.acknowledge({previewProtocol:3,kind:'preview-control-delivered',binding,receiverEpoch:'1',controlOrdinal:'1'}));
 same(maxDepth,1);same(confirmCount,1);same(immediatePackets.length,1);
 const done=await native('finish');same(done,{finished:true,invoked:3});child.stdin.end();same(await terminal,{code:0,signal:null});same(stderr,'');
 console.log(JSON.stringify({passed:true,checks,normalOwnedExit:true,nativeAcceptance:false,fullReleaseAccepted:false,
 scope:'Actual compiled native C control confirmation/close predicate and immutable JS outbox through strict metadata wire decoding. Lost packet receipt and frontend confirmation, byte-identical retry without another Unknown effect invocation, native receipt rebroadcast, compact cumulative confirmation, failed post retry with empty data queue, future/foreign refusal, reopened barrier and callback reentrancy. Synthetic metadata only; no admission cleanup reservation, actual WebKit or physical acceptance.'}));
})().catch(async error=>{console.error(error.stack);child.stdin.destroy();child.kill('SIGTERM');await terminal;process.exitCode=1;});
