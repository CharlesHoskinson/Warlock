'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const context=vm.createContext({TextEncoder});vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),context);
let checks=0;function check(v,m){assert(v,m);checks++;}function same(a,b,m){assert.deepEqual(a,b,m);checks++;}
const binding={lifetime:'18446744073709551615',session:'9007199254740993',frontend:'9007199254740995'},grant={binding,receiverEpoch:'18446744073709551615',capacity:2};
const ticket=(ordinal,command={kind:'cancel'})=>({previewProtocol:3,kind:'preview-control-ticket',binding:{...binding},receiverEpoch:grant.receiverEpoch,controlOrdinal:String(ordinal),alreadyDelivered:false,wire:JSON.stringify({previewProtocol:3,kind:'preview-commands',binding:{...binding},receiverEpoch:grant.receiverEpoch,controlOrdinal:String(ordinal),entries:[{identity:'family:21',commands:[command]}]})});
const receipt=ordinal=>({previewProtocol:3,kind:'preview-control-delivered',binding:{...binding},receiverEpoch:grant.receiverEpoch,controlOrdinal:String(ordinal)});
const posted=[],confirmed=[],box=context.WarlockNativePreviewControlOutbox(grant,w=>posted.push(w),w=>confirmed.push(w));
for(const value of [null,{},ticket('0'),ticket('01'),ticket('18446744073709551616'),ticket(2),{...ticket(1),extra:true},{...ticket(1),receiverEpoch:'1'},{...ticket(1),binding:{...binding,frontend:'19'}},{...ticket(1),alreadyDelivered:'true'},{...ticket(1),wire:'not JSON'},ticket(1,{kind:'cancel',text:'Ж'.repeat(2048)})])check(!box.retain(value),'Invalid/foreign/gap/oversized native ticket refuses');
same(box.snapshot().nativeIssuedThrough,'0');same(posted.length,0,'Validation consumes no transport position');
const first=ticket(1),second=ticket(2);check(box.retain(first));check(box.retain(second));same(posted.length,1,'Queued neighbor stays behind receipt');
check(!box.retain({...first,wire:ticket(1,{kind:'release'}).wire}),'Same ordinal changed bytes refuse');check(!box.retain(ticket(3)),'Bounded native ticket retention');
check(box.acknowledge(receipt(1)));same(posted.at(-1),second.wire);check(box.acknowledge(receipt(2)));check(!box.retain(first),'Older native purpose cannot replay');check(box.retain(second),'Latest exact proposal confirms without replay');same(posted.length,2);
check(box.acknowledge(receipt(1)));same(JSON.parse(confirmed.at(-1)).controlOrdinal,'2','Old receipt re-confirms only current prefix');
for(const bad of [{...grant,capacity:0},{...grant,capacity:1066},{...grant,capacity:1.5},{...grant,receiverEpoch:'01'},{...grant,binding:{...binding,lifetime:18446744073709551615}}]){assert.throws(()=>context.WarlockNativePreviewControlOutbox(bad,()=>{},()=>{}));checks++;}
assert.throws(()=>context.WarlockNativePreviewControlOutbox(grant,()=>{}));checks++;
let reentrant,armed=false,depth=0,maximumDepth=0;const synchronous=[];
reentrant=context.WarlockNativePreviewControlOutbox(grant,w=>{depth++;maximumDepth=Math.max(maximumDepth,depth);synchronous.push(JSON.parse(w).controlOrdinal);if(armed)check(reentrant.acknowledge(receipt(JSON.parse(w).controlOrdinal)));depth--;},w=>{check(reentrant.acknowledge(receipt(JSON.parse(w).controlOrdinal)),'Synchronous duplicate confirmation does not recurse');});
check(reentrant.retain(first));check(reentrant.retain(second));armed=true;check(reentrant.retry());same(synchronous,['1','1'],'Synchronous first receipt waits for next host transport poll');same(reentrant.snapshot().pending,1);check(reentrant.retry());same(synchronous,['1','1','2']);same(maximumDepth,1,'No recursive data post');same(reentrant.snapshot().pending,0);
console.log(JSON.stringify({passed:true,checks,fullUint64BindingAndEpoch:true,reentrantDepth:maximumDepth,nativeIssuerIsFixture:true,nativeAcceptance:false,fullReleaseAccepted:false}));
