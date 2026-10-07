'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
function decode(value){if(Array.isArray(value))return value.map(decode);if(value && typeof value==='object'){if('#bigint' in value)return BigInt(value['#bigint']);return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,decode(v)]));}return value;}
const states=decode(JSON.parse(fs.readFileSync(process.argv[3],'utf8'))).states.map(value=>value.s);
let source=fs.readFileSync(process.argv[2],'utf8');
const context=vm.createContext({TextEncoder});vm.runInContext(source,context);
const grant={binding:{lifetime:'17',session:'18',frontend:'19'},receiverEpoch:'1',capacity:2};
const posted=[],wireByOrdinal=new Map();let fails=false,last=false,seen=0,compared=0;
const post=wire=>{
 const packet=JSON.parse(wire),ordinal=BigInt(packet.controlOrdinal);
 if(wireByOrdinal.has(ordinal))assert.equal(wire,wireByOrdinal.get(ordinal),'Exact immutable original retry bytes');
 else wireByOrdinal.set(ordinal,wire);
 posted.push(ordinal);if(fails)throw new Error('Lost transport post');
};
let outbox=context.WarlockRetainedPreviewControls(grant,post);
const receipt=ordinal=>({previewProtocol:3,kind:'preview-control-delivered',binding:{...grant.binding},receiverEpoch:'1',controlOrdinal:String(ordinal)});
for(const state of states){
 if(state.history.length===seen+1){const event=state.history.at(-1);seen++;
  if(event==='Boundary'){
   const boundary=vm.createContext({TextEncoder});vm.runInContext(source.replace('let issued=0n,confirmed=0n','let issued=18446744073709551614n,confirmed=18446744073709551614n'),boundary);
   outbox=boundary.WarlockRetainedPreviewControls(grant,post);last=true;
  }
  else if(event==='Offer')last=outbox.offer('family:21',{kind:'cancel',job:{request:String(BigInt(outbox.snapshot().issued)+1n)}});
  else if(event==='Retry')last=outbox.retry();
  else if(event==='FailPost'){fails=true;last=true;}
  else if(event==='RecoverPost'){fails=false;last=true;}
  else if(/^Ack[123]$/.test(event))last=outbox.acknowledge(receipt(event.at(-1)));
  else if(event==='WrongEpoch')last=outbox.acknowledge({...receipt(BigInt(outbox.snapshot().confirmed)+1n),receiverEpoch:'2'});
  else if(event==='WrongBinding')last=outbox.acknowledge({...receipt(BigInt(outbox.snapshot().confirmed)+1n),binding:{...grant.binding,frontend:'20'}});
  else if(event==='GapAck')last=outbox.acknowledge(receipt(BigInt(outbox.snapshot().confirmed)+2n));
  else throw new Error('Known outbox trace event');
  compared++;
 }else assert.equal(state.history.length,seen,'Contiguous trace history');
 const actual=outbox.snapshot();assert.equal(BigInt(actual.issued),state.issued,'Original issued ordinal');
 assert.equal(BigInt(actual.confirmed),state.confirmed,'Original receipt prefix');
 assert.equal(BigInt(actual.pending),BigInt(state.pending.length),'Bounded retained packet occupancy');
 assert.deepEqual(posted,state.posted,'Exact ordered transmission attempts');assert.equal(last,state.last,'Actual outbox result');
}
console.log(JSON.stringify({passed:true,statesCompared:compared,nativeAcceptance:false,fullReleaseAccepted:false}));
