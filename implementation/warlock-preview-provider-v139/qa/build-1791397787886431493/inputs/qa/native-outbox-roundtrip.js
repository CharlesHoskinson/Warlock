'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {spawn}=require('node:child_process'),readline=require('node:readline');
const context=vm.createContext({TextEncoder});vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),context);
const child=spawn(process.argv[3],[],{stdio:['pipe','pipe','pipe']});let stderr='',pending;const buffered=[];
child.stderr.on('data',v=>stderr+=v);
const terminal=new Promise(resolve=>child.on('close',(code,signal)=>{resolve({code,signal});if(pending){clearTimeout(pending.timer);pending.reject(new Error(stderr));pending=null;}}));
readline.createInterface({input:child.stdout}).on('line',line=>{const value=JSON.parse(line);if(pending){const p=pending;pending=null;clearTimeout(p.timer);p.resolve(value);}else buffered.push(value);});
function next(){if(buffered.length)return Promise.resolve(buffered.shift());return new Promise((resolve,reject)=>{assert(!pending);const timer=setTimeout(()=>reject(new Error('Original native fixture timeout '+stderr)),10000);pending={resolve,reject,timer};});}
async function call(op,values={}){child.stdin.write(JSON.stringify({op,...values})+'\n');return next();}
let checks=0;function check(value,message){assert(value,message);checks++;}function same(a,b,message){assert.deepEqual(a,b,message);checks++;}
const plain=value=>JSON.parse(JSON.stringify(value));
(async()=>{
 let setup=await next(),epoch=setup.epoch;const binding={...setup.grant.binding};let posted=[],confirmations=[],failPost=false,failConfirm=false;
 const create=()=>context.WarlockNativePreviewControlOutbox(setup.grant,wire=>{posted.push(wire);if(failPost)throw Error('Application dropped post');},wire=>{confirmations.push(wire);if(failConfirm)throw Error('Application dropped confirmation');});
 let outbox=create();check(typeof outbox.offer==='undefined','Renderer cannot assign a ticket');
 const reconcile=JSON.stringify({kind:'reconcile',binding});
 const propose=async command=>{const p=await call('propose',{epoch,command:typeof command==='string'?command:JSON.stringify(command)});check(p.ok && !p.refused,'Actual native purpose reservation');return p.result;};
 const dispatch=async ticket=>{const d=await call('dispatch',{wire:ticket.wire});check(d.ok && d.receipt,'Actual C dispatch receipt');return d;};
 const confirm=async()=>{const c=await call('confirm',{wire:confirmations.at(-1)});check(c.ok && !c.refused,'Independent native confirmation');return c;};
 const first=await propose(reconcile);same(first.controlOrdinal,'1','Native first ordinal');const retainedWire=first.wire;
 failPost=true;check(outbox.retain(first),'Lost transmission retains native ticket');same(posted.at(-1),retainedWire);first.wire='{}';setup.grant.binding.frontend='1';setup.grant.receiverEpoch='9';
 same(outbox.snapshot().pending,1);failPost=false;check(outbox.retry());same(posted.at(-1),retainedWire,'No renderer reserialization');
 const initial=await call('dispatch',{wire:retainedWire});check(initial.ok && initial.receipt);same((await call('status')).result.terminal,false,'Delivery does not physically settle original job');
 const repeated=await propose(reconcile);same(repeated.wire,retainedWire);check(repeated.alreadyDelivered);check(outbox.retain(repeated));same(outbox.snapshot().pending,1,'Native advisory cannot release queue');
 const changed=JSON.parse(retainedWire);changed.entries[0].commands[0].kind='cancel';const tampered=await call('dispatch',{wire:JSON.stringify(changed)});check(!tampered.ok && tampered.refused && tampered.receipt===null,'Native refuses changed issued bytes');
 const again=await dispatch(repeated);same(again.receipt,initial.receipt,'Lost receipt repeats original prefix');
 for(const receipt of [{...again.receipt,receiverEpoch:'2'},{...again.receipt,binding:{...binding,frontend:'1'}},{...again.receipt,controlOrdinal:'2'},{...again.receipt,controlOrdinal:'01'},{...again.receipt,extra:true}])check(!outbox.acknowledge(receipt),'Foreign/future/noncanonical receipt cannot drain');
 failConfirm=true;check(outbox.acknowledge(again.receipt));same(outbox.snapshot().deliveredThrough,'1');const confirmation=confirmations.at(-1);failConfirm=false;check(outbox.retry());same(confirmations.at(-1),confirmation,'Lost confirmation retains exact bytes');await confirm();
 const before=(await call('status')).result;check(!before.terminal && before.charge==='4096','Independent confirmation still cannot settle physical job');
 check((await call('poll')).ok);const terminalJob=(await call('status')).result;check(terminalJob.terminal && terminalJob.proofs==='2' && terminalJob.charge==='0','Original native physical retirement and proofs');
 async function deliver(command){const p=await propose(command);check(outbox.retain(p));same(posted.at(-1),p.wire);const d=await dispatch(p);check(outbox.acknowledge(d.receipt));await confirm();return p;}
 async function settle(){const state=(await call('status')).result;await deliver({kind:'acknowledge',job:state.job,sequence:state.sequence});const seed=(await call('seed')).result;await deliver({kind:'detach-ready',...seed});check((await call('poll')).ok);const completion=(await call('pending')).result;check(completion.length===1,'Actual retained scoped completion');await deliver({kind:'detach-delivery-ack',binding,receiverEpoch:epoch,deliveryOrdinal:completion[0].deliveryOrdinal});}
 await settle();same(outbox.snapshot().pending,0);const oldOutbox=outbox,oldReceipt=again.receipt;
 setup=(await call('replace')).result;epoch=setup.epoch;same(epoch,'2','Same Native realm replacement');same(setup.grant.binding,binding,'Original Native grant retained');posted=[];confirmations=[];outbox=create();
 const second=await propose(reconcile);same(second.controlOrdinal,'1');check(second.wire!==retainedWire,'Native epoch changes exact ticket');check(!outbox.retain(repeated),'Old epoch ticket refuses before renderer retention');check(!outbox.acknowledge(oldReceipt),'Old epoch receipt refuses');
 const old=await call('dispatch',{wire:retainedWire});check(!old.ok && old.refused && old.receipt===null,'Actual C rejects prior epoch before replacement handler');same((await call('status')).result.terminal,false);
 check(outbox.retain(second));const d=await dispatch(second);check(outbox.acknowledge(d.receipt));await confirm();check((await call('poll')).ok);await settle();
 same(oldOutbox.snapshot().pending,0,'Old realm object cannot affect replacement');
 child.stdin.write(JSON.stringify({op:'finish'})+'\n');same(await next(),{finished:true,normalOwnedPeerExit:true});child.stdin.end();same(await terminal,{code:0,signal:null});same(stderr,'');
 console.log(JSON.stringify({passed:true,checks,normalOwnedExit:true,actualControlledC:true,realmEpochs:2,syntheticNativeRemainsActive:true,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(async error=>{console.error(error.stack);child.stdin.destroy();child.kill('SIGTERM');await terminal;process.exitCode=1;});
