'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {spawn}=require('node:child_process'),readline=require('node:readline');
const context=vm.createContext({TextEncoder});vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),context);
const child=spawn(process.argv[3],[],{stdio:['pipe','pipe','pipe']});let stderr='',pending;
child.stderr.on('data',value=>stderr+=value);const buffered=[];
const terminal=new Promise(resolve=>child.on('close',(code,signal)=>{resolve({code,signal});if(pending){clearTimeout(pending.timer);pending.reject(new Error(stderr));pending=null;}}));
readline.createInterface({input:child.stdout}).on('line',line=>{const value=JSON.parse(line);if(pending){const waiter=pending;pending=null;clearTimeout(waiter.timer);waiter.resolve(value);}else buffered.push(value);});
function next(){if(buffered.length)return Promise.resolve(buffered.shift());return new Promise((resolve,reject)=>{assert(!pending);const timer=setTimeout(()=>reject(new Error('Native transport fixture timeout '+stderr)),10000);pending={resolve,reject,timer};});}
async function native(wire){child.stdin.write(JSON.stringify({op:'packet',wire})+'\n');return next();}
let checks=0;function check(ok){assert(ok);checks++;}
const same=(a,b)=>{assert.deepEqual(a,b);checks++;};
const plain=value=>JSON.parse(JSON.stringify(value));
(async()=>{
 const binding={lifetime:'17',session:'18',frontend:'19'},grant={binding,receiverEpoch:'1',capacity:2};
 const posted=[];let failPost=false;
 const outbox=context.WarlockRetainedPreviewControls(grant,wire=>{posted.push(wire);if(failPost)throw new Error('Lost native post');});
 const command={kind:'acquire',job:{request:'1'}};
 check(outbox.offer('family:21',command));const first=posted.at(-1);command.kind='release';grant.binding.frontend='20';grant.receiverEpoch='2';
 check(JSON.parse(first).entries[0].commands[0].kind==='acquire');check(JSON.parse(first).binding.frontend==='19' && JSON.parse(first).receiverEpoch==='1');
 // Drop its initial transmission before native sees it.
 check(outbox.retry());same(posted.at(-1),first);
 const arrived=await native(posted.at(-1));same(arrived.decision,1);same(arrived.invoked,1);same(arrived.effectOutcome,'Unknown');
 // Lose native's first delivery receipt. Changed bytes under that ordinal are
 // refused; the retained immutable original may repeat only the receipt.
 const changed=JSON.parse(first);changed.entries[0].commands[0].kind='cancel';
 const rejected=await native(JSON.stringify(changed));same(rejected.decision,0);same(rejected.invoked,1);same(rejected.receipt,null);
 check(outbox.offer('family:21',{kind:'cancel',job:{request:'1'}}));same(posted.length,2);
 check(outbox.retry());same(posted.at(-1),first);
 const retry=await native(first);same(retry.decision,2);same(retry.invoked,1);same(retry.receipt,arrived.receipt);
 for(const receipt of [
  {...retry.receipt,receiverEpoch:'2'},
  {...retry.receipt,binding:{...retry.receipt.binding,frontend:'20'}},
  {...retry.receipt,controlOrdinal:'2'},
  {...retry.receipt,controlOrdinal:'01'},
  {...retry.receipt,controlOrdinal:'18446744073709551616'},
  {...retry.receipt,extra:true}
 ])check(!outbox.acknowledge(receipt));
 same(plain(outbox.snapshot()),{issued:'2',confirmed:'0',pending:2,capacity:2});
 check(outbox.acknowledge(retry.receipt));const second=posted.at(-1);check(JSON.parse(second).controlOrdinal==='2');
 const secondDelivery=await native(second);same(secondDelivery.decision,1);same(secondDelivery.invoked,2);
 check(outbox.acknowledge(secondDelivery.receipt));same(plain(outbox.snapshot()),{issued:'2',confirmed:'2',pending:0,capacity:2});
 check(!outbox.acknowledge(retry.receipt));const stale=await native(first);same(stale.decision,0);same(stale.invoked,2);
 failPost=true;check(outbox.offer('family:21',{kind:'release',job:{request:'1'}}));const third=posted.at(-1);
 check(outbox.offer('family:21',{kind:'acknowledge',sequence:'3'}));
 check(!outbox.offer('family:21',{kind:'retire-ready'}));same(plain(outbox.snapshot()),{issued:'4',confirmed:'2',pending:2,capacity:2});
 failPost=false;check(outbox.retry());same(posted.at(-1),third);
 const thirdDelivery=await native(third);same(thirdDelivery.decision,1);same(thirdDelivery.invoked,3);
 check(outbox.acknowledge(thirdDelivery.receipt));const fourth=posted.at(-1);
 const fourthDelivery=await native(fourth);same(fourthDelivery.decision,1);same(fourthDelivery.invoked,4);check(outbox.acknowledge(fourthDelivery.receipt));
 same(plain(outbox.snapshot()),{issued:'4',confirmed:'4',pending:0,capacity:2});
 check(!outbox.offer('',{}));const cyclic={};cyclic.self=cyclic;check(!outbox.offer('family:21',cyclic));
 check(!outbox.offer('family:21',{kind:'cancel',text:'Ж'.repeat(2048)}));same(outbox.snapshot().issued,'4');check(!outbox.retry());
 // The same native grant cannot turn a new local outbox into permission to
 // replay old effects. Native rejects its restarted ordinal.
 const freshPosted=[],reloaded=context.WarlockRetainedPreviewControls({binding:{lifetime:'17',session:'18',frontend:'19'},receiverEpoch:'1',capacity:2},wire=>freshPosted.push(wire));
 check(reloaded.offer('family:21',{kind:'acquire'}));const oldGrant=await native(freshPosted[0]);same(oldGrant.decision,0);same(oldGrant.invoked,4);same(reloaded.snapshot().pending,1);
 // Explicit boundary fixture in a separate VM; native admission cleanup
 // reservation is still required before any product use of the final ordinal.
 const boundary=vm.createContext({TextEncoder});vm.runInContext(fs.readFileSync(process.argv[2],'utf8').replace('let issued=0n,confirmed=0n','let issued=18446744073709551614n,confirmed=18446744073709551614n'),boundary);
 const tailPosted=[],tail=boundary.WarlockRetainedPreviewControls({binding:{lifetime:'17',session:'18',frontend:'19'},receiverEpoch:'1',capacity:2},wire=>tailPosted.push(wire));
 check(tail.offer('family:21',{kind:'acknowledge'}));check(!tail.offer('family:21',{kind:'cancel'}));same(JSON.parse(tailPosted[0]).controlOrdinal,'18446744073709551615');check(tail.retry());same(tailPosted[0],tailPosted[1]);
 child.stdin.write(JSON.stringify({op:'finish'})+'\n');const done=await next();same(done,{finished:true,invoked:4});child.stdin.end();same(await terminal,{code:0,signal:null});same(stderr,'');
 console.log(JSON.stringify({passed:true,checks,normalOwnedExit:true,nativeAcceptance:false,fullReleaseAccepted:false,
 scope:'Actual immutable bounded JS outbox and compiled native C receipt/deduplication functions through strict C++ wire decoding. Lost transmission/receipt, changed bytes, Unknown handler outcome, backpressure, failed post, UTF8 bound, original grant, ordered controls and normal cleanup. No actual WebKit activation, native admission cleanup reservations, fresh-grant reload reconciliation, real effects or physical acceptance.'}));
})().catch(async error=>{console.error(error.stack);child.stdin.destroy();child.kill('SIGTERM');await terminal;process.exitCode=1;});
