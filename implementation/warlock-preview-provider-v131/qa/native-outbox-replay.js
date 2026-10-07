'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
function decode(v){if(Array.isArray(v))return v.map(decode);if(v && typeof v==='object'){if('#bigint' in v)return BigInt(v['#bigint']);return Object.fromEntries(Object.entries(v).map(([k,x])=>[k,decode(x)]));}return v;}
const states=decode(JSON.parse(fs.readFileSync(process.argv[3],'utf8'))).states.map(v=>v.s);
const context=vm.createContext({TextEncoder});vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),context);
const binding={lifetime:'18446744073709551615',session:'9007199254740993',frontend:'19'},epoch='1',posted=[],confirmations=[],wires=new Map();
let postFails=false,confirmFails=false,last=false,native=0n,seen=0,compared=0;
const outbox=context.WarlockNativePreviewControlOutbox({binding,receiverEpoch:epoch,capacity:2},wire=>{const ordinal=BigInt(JSON.parse(wire).controlOrdinal);if(wires.has(ordinal))assert.equal(wire,wires.get(ordinal),'Exact native retry bytes');else wires.set(ordinal,wire);posted.push(ordinal);if(postFails)throw Error('Dropped post');},wire=>{const r=JSON.parse(wire);assert.deepEqual(r.binding,binding);assert.equal(r.receiverEpoch,epoch);confirmations.push(BigInt(r.controlOrdinal));if(confirmFails)throw Error('Dropped confirmation');});
const ticket=(ordinal,advisory=false)=>({previewProtocol:3,kind:'preview-control-ticket',binding:{...binding},receiverEpoch:epoch,controlOrdinal:String(ordinal),alreadyDelivered:advisory,wire:JSON.stringify({previewProtocol:3,kind:'preview-commands',binding:{...binding},receiverEpoch:epoch,controlOrdinal:String(ordinal),entries:[{identity:'family:21',commands:[{kind:'cancel',text:'original native fixture bytes'}]}]})});
const receipt=ordinal=>({previewProtocol:3,kind:'preview-control-delivered',binding:{...binding},receiverEpoch:epoch,controlOrdinal:String(ordinal)});
for(const state of states){
 if(state.history.length===seen+1){const e=state.history.at(-1);seen++;
  if(e==='Issue'){native++;last=true;}
  else if(e==='Retain')last=native>BigInt(outbox.snapshot().nativeIssuedThrough)?outbox.retain(ticket(BigInt(outbox.snapshot().nativeIssuedThrough)+1n)):false;
  else if(e==='Duplicate' || e==='Advisory' || e==='Changed'){
   const s=outbox.snapshot(),ordinal=s.pending?BigInt(s.deliveredThrough)+1n:BigInt(s.deliveredThrough);
   if(!ordinal)last=false;else {const t=ticket(ordinal,e==='Advisory');if(e==='Changed'){const p=JSON.parse(t.wire);p.entries[0].commands[0].text='changed';t.wire=JSON.stringify(p);}last=outbox.retain(t);}
  }else if(e==='Gap')last=outbox.retain(ticket(BigInt(outbox.snapshot().nativeIssuedThrough)+2n));
  else if(/^Ack[1-4]$/.test(e))last=outbox.acknowledge(receipt(e.at(-1)));
  else if(e==='WrongEpoch')last=outbox.acknowledge({...receipt(BigInt(outbox.snapshot().deliveredThrough)+1n),receiverEpoch:'2'});
  else if(e==='WrongBinding')last=outbox.acknowledge({...receipt(BigInt(outbox.snapshot().deliveredThrough)+1n),binding:{...binding,frontend:'20'}});
  else if(e==='Retry')last=outbox.retry();
  else if(e==='FailPost'){postFails=true;last=true;}
  else if(e==='RecoverPost'){postFails=false;last=true;}
  else if(e==='FailConfirm'){confirmFails=true;last=true;}
  else if(e==='RecoverConfirm'){confirmFails=false;last=true;}
  else throw Error('Known native outbox event');
 }else assert.equal(state.history.length,seen,'Contiguous trace history');
 const s=outbox.snapshot();assert.equal(BigInt(s.nativeIssuedThrough),state.through,'Native ticket retained frontier');assert.equal(BigInt(s.deliveredThrough),state.delivered,'Original delivery prefix');assert.equal(BigInt(s.pending),BigInt(state.pending.length),'Bounded retained ticket occupancy');assert.deepEqual(posted,state.posted,'Ordered exact native transmissions');assert.deepEqual(confirmations,state.confirmations,'Independent retained confirmation attempts');assert.equal(last,state.last,'Actual transport result');compared++;
}
console.log(JSON.stringify({passed:true,statesCompared:compared,nativeIssuerIsTraceFixture:true,nativeAcceptance:false,fullReleaseAccepted:false}));
