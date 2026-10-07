'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {spawn}=require('node:child_process'),readline=require('node:readline');
require(process.argv[5]);let lastPolicyEnvelope;
const {Elm:DecoderElm}=require(process.argv[6]);const codec=DecoderElm.NativePreviewVisualReplay.init();let awaitingCodec;let visualChecks=0;let readonlyChecks=0;
codec.ports.outgoing.subscribe(v=>{assert(awaitingCodec);const resolve=awaitingCodec;awaitingCodec=null;resolve(v);});
function decodeProjection(value){return new Promise((resolve,reject)=>{assert(!awaitingCodec);const timer=setTimeout(()=>reject(Error('Original three-second visual decoder timeout')),3000);awaitingCodec=v=>{clearTimeout(timer);resolve(v);};codec.ports.incoming.send({kind:'projection',domain:{binding:value.binding,receiverEpoch:value.receiverEpoch},value});});}

const child=spawn(process.argv[3],[process.argv[2]],{stdio:['pipe','pipe','pipe']});
let stderr='',pending;const buffered=[];
child.stderr.on('data',v=>stderr+=v);
const terminal=new Promise(resolve=>child.on('close',(code,signal)=>{
 resolve({code,signal});if(pending){clearTimeout(pending.timer);pending.reject(Error('Native child exited: '+stderr));pending=null;}
}));
readline.createInterface({input:child.stdout}).on('line',line=>{
 const v=JSON.parse(line);if(pending){const p=pending;pending=null;clearTimeout(p.timer);p.resolve(v);}else buffered.push(v);
});
function next(){if(buffered.length)return Promise.resolve(buffered.shift());return new Promise((resolve,reject)=>{
 assert(!pending);const timer=setTimeout(()=>reject(Error('Original actual native fixture timeout '+stderr)),10000);pending={resolve,reject,timer};
});}
async function call(op,values={}){child.stdin.write(JSON.stringify({op,...values})+'\n');return next();}
let checks=0;
async function send(kind,value){const reply=await call('policy',{input:JSON.stringify({kind,value})});assert(reply.ok && !reply.refused && reply.result,'Actual native-owned JavaScriptCore Elm update');const result=reply.result;if(result.commands.kind==='preview-proposals')lastPolicyEnvelope=result.commands;
 const current=await call('policy-visuals');if(result.realm.closed || !result.realm.controlled){assert(!current.ok && current.refused && current.result===null,'Absent/closed native authority refuses current projection');readonlyChecks++;}else{assert(current.ok && !current.refused,'Creator-owned readonly visual copy');assert.deepEqual(current.result,result.visuals,'Readonly query returns only latest exact successful visual data');readonlyChecks+=2;}
 if(result.visuals!==null){const decoded=await decodeProjection(result.visuals);assert(decoded.accepted,'Actual optimized worker emits typed original visual projection');assert.deepEqual(decoded.value,result.visuals,'Pure decoder preserves exact projection');visualChecks+=2;
  for(const row of result.visuals.previews){const policy=result.models.find(item=>item.identity===row.identity);if(row.visual.kind==='lifecycle'){assert(policy?.active && policy.model);assert.equal(row.visual.state,policy.model.state);visualChecks+=2;
    if(row.visual.frame!==null){assert.equal('elm-shell://preview/'+row.visual.frame,policy.model.image);visualChecks++;}}
  }
 }
 return result;}
function check(v,m){assert(v,m);checks++;}function same(a,b,m){assert.deepEqual(a,b,m);checks++;}
const kinds=r=>r.commands.entries.flatMap(row=>row.commands).map(c=>c.kind);
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],
 popup:[{id:'family:21',domId:'window-21',label:'Window',ariaLabel:'Window',detail:'',enabled:true}]};
(async()=>{
 let setup=await next(),epoch=setup.epoch;const beforeGrant=await call('policy-visuals');assert(!beforeGrant.ok && beforeGrant.refused && beforeGrant.result===null,'No automatic authority from native factory creation');readonlyChecks++;const binding=structuredClone(setup.grant.binding);
 let posted=[],confirmed=[],outbox,lastTicket,lastReceipt;
 const wrap=event=>({previewProtocol:3,kind:'native-preview-realm-event',binding,receiverEpoch:epoch,event});
 const domain=()=>({binding,receiverEpoch:epoch});
 function create(pages=[]){const ctx=vm.createContext({TextEncoder});vm.runInContext(fs.readFileSync(process.argv[4],'utf8'),ctx);
  return ctx.WarlockRecoveredNativePreviewControlOutbox(setup.grant,w=>posted.push(w),w=>confirmed.push(w),pages);
 }
 async function propose(row){const [envelope]=WarlockNativePreviewProposals({...lastPolicyEnvelope,entries:[row]});const p=await call('propose-envelope',{envelope});
  check(p.ok && !p.refused && p.result,'Actual C approves the compiled Elm command');const issued=await send('issued',p.result);check(issued.realm.ingress.pending>=0,'Exact original native ticket correlates in immutable Elm ingress');return p.result;
 }
 async function dispatch(ticket){const d=await call('dispatch',{wire:ticket.wire});
  check(d.receipt,'Native transport receipt is independent of effect success');return d;
 }
 async function confirm(){const c=await call('confirm',{wire:confirmed.at(-1)});check(c.ok && !c.refused,'Actual independent native confirmation');}
 async function deliver(row){const ticket=await propose(row);check(outbox.retain(ticket),'Original native ticket retained');
  check(outbox.retry());same(posted.at(-1),ticket.wire,'Actual native bytes reach dispatcher without reserialization');
  const d=await dispatch(ticket);check(outbox.acknowledge(d.receipt));await confirm();lastTicket=ticket;lastReceipt=d.receipt;return d;
 }
 async function deliverAll(result){check(result.commands.receiverEpoch===epoch && result.commands.kind==='preview-proposals');
  for(const row of result.commands.entries){check(row.commands.length===1);await deliver(row);}
 }
 await send('grant',setup.grant);await send('presentation',presentation);outbox=create();check(!(await call('policy-close-probe')).ok,'Open native realm retains its policy owner');
 const originalStatus=(await call('status')).result;
 const valid={previewProtocol:3,kind:'preview-proposals',binding,receiverEpoch:epoch,entries:[{identity:'binding:'+Object.values(binding).join(':'),commands:[{kind:'reconcile',binding}]}]};
 for(const bad of [{...valid,receiverEpoch:'2'},{...valid,binding:{...binding,frontend:'1'}},{...valid,controlOrdinal:'1'},{...valid,entries:[...valid.entries,...valid.entries]},{...valid,entries:[]},{...valid,entries:[{...valid.entries[0],commands:[]}]},{...valid,entries:[{...valid.entries[0],extra:true}]},{...valid,entries:[{...valid.entries[0],commands:[null]}]}]){const refused=await call('propose-envelope',{envelope:JSON.stringify(bad)});check(!refused.ok && refused.refused && refused.result===null,'Malformed/foreign typed ingress refuses before native issuance');same((await call('status')).result,originalStatus,'Refused ingress preserves original obligations');}
 same((await call('recovery-begin',{epoch})).result.issuedThrough,'0','Refused ingress consumes no native ordinal');
 for(let round=0;round<2;round++){
  let result;
  for(const event of setup.events){result=await send('native',wrap(event));await deliverAll(result);}
  same(result.models.length,1);same(result.models[0].model.known.length,1,'Actual original issued job remains in the single Elm policy');
  same(kinds(result),['acquire']);
  same(result.realm.ingress.pending,1,'Before the native fact the original acquisition intent was retained');
  const retryAfterIssued=await send('retry',domain());same(kinds(retryAfterIssued),[],'Exact native issuance removes only its proposal intent');
  const acquisition=lastTicket;
  const before=(await call('status')).result;
  check(!before.terminal && before.charge==='4096','Native capture refusal leaves original physical settlement pending');
  const duplicate=await dispatch(acquisition);same(duplicate.receipt,lastReceipt,'Delivered Unknown acquisition retry is transport only');
  same((await call('status')).result,before,'Original Unknown obligation remains unchanged on duplicate dispatch');
  result=await send('quarantine',domain());same(kinds(result),['reconcile','cancel']);
  same(result.commands.entries[0].identity,'binding:'+Object.values(binding).join(':'),'Compiled Elm uses actual C canonical binding identity');
  same(result.models[0].model.known.length,1);check(!result.models[0].model.demand);
  // Lose the first reconciliation delivery receipt. A fresh renderer obtains
  // only the original native retained ticket; the Elm policy is retained.
  const reconcile=await propose(result.commands.entries[0]);check(outbox.retain(reconcile));
  const receipt=await dispatch(reconcile);check(receipt.ok && !receipt.refused);
  const head=(await call('recovery-begin',{epoch})).result;
  same(head.ticket.wire,reconcile.wire,'Actual recovery captures the lost receipt ticket');
  const end=await call('recovery-next',{epoch,issued:head.issuedThrough,delivered:head.deliveredThrough,confirmed:head.confirmedThrough,after:reconcile.controlOrdinal});
  check(end.ok && end.result.ticket===null);posted=[];confirmed=[];outbox=create([head,end.result]);
  same(posted,[],'Fresh renderer context constructor emits no effects');check(outbox.retry());same(posted.at(-1),reconcile.wire);
  const retried=await dispatch(reconcile);same(retried.receipt,receipt.receipt,'Lost reconciliation receipt repeats original prefix');
  check(outbox.acknowledge(retried.receipt));await confirm();
  await deliver(result.commands.entries[1]);
  check((await call('poll')).ok);
  const seed=(await call('seed')).result;check(seed && seed.requestFloor==='1' && seed.receiverEpoch===epoch);
  result=await send('native',wrap(seed));same(kinds(result),[],'Native scope seed cannot erase unresolved Elm job');
  same(result.models[0].model.known.length,1);same((await call('close-probe')).ok,false);
  const proofs=(await call('terminal')).result;check(proofs.length>0,'Actual terminal proof journal');
  for(const event of proofs){result=await send('native',wrap(event));
   if(kinds(result).includes('detach-ready')){
    const original=result.commands.entries.find(row=>row.commands[0].kind==='detach-ready');
    for(const row of result.commands.entries.filter(row=>row!==original))await deliver(row);
    const frontier=(await call('recovery-begin',{epoch})).result.issuedThrough;
    const recoveredIntent=await send('retry',domain());same(recoveredIntent.commands.entries,[original],'Lost ready proposal before native issuance remains exact Elm intent');
    same((await call('recovery-begin',{epoch})).result.issuedThrough,frontier,'Native ticket recovery cannot synthesize an unissued proposal');
    await deliver(original);
   }else await deliverAll(result);
  }
  check(kinds(result).includes('detach-ready'),'Compiled Elm readiness follows actual original terminal proof and ACK');
  same(result.models[0].model.known.length,0);check((await call('poll')).ok);
  const final=(await call('pending')).result;check(final.length===1,'Actual retained scoped native completion');
  // Drop final delivery, then processing ACK, then final independent native
  // confirmation. None grants an early physical or realm close.
  const repeated=(await call('pending')).result;same(repeated,final);
  result=await send('native',wrap(repeated[0]));same(result.models,[]);same(kinds(result),['detach-delivery-ack']);
  const processing=result.commands.entries[0];same((await call('close-probe')).ok,false);
  const lostAck=(await call('pending')).result;same(lostAck,final);
  result=await send('native',wrap(lostAck[0]));same(result.commands.entries,[processing],'Exact scoped retry re-ACKs only the original final fact');
  const finalTicket=await propose(processing);check(outbox.retain(finalTicket));const done=await dispatch(finalTicket);
  check(outbox.acknowledge(done.receipt));same((await call('close-probe')).ok,false,'Processing ACK is distinct from independent native confirmation');
  check(outbox.retry());await confirm();same(outbox.snapshot().pending,0);
  if(round===0){const oldEpoch=epoch,oldTicket=reconcile;
   setup=(await call('replace')).result;same(setup.grant.binding,binding,'Native close and replacement preserve the shared grant');
   await send('closed',domain());epoch=setup.epoch;same(epoch,'2');result=await send('grant',setup.grant);same(result.realm.epoch,epoch);
   const foreign=await call('dispatch',{wire:oldTicket.wire});check(!foreign.ok && foreign.refused && foreign.receipt===null);
   result=await send('native',{...wrap(setup.events[0]),receiverEpoch:oldEpoch});same(result.models,[],'Old domain is refused before same Active subject reopens');
   posted=[];confirmed=[];outbox=create();check(!outbox.retain(oldTicket));
  }
 }
 child.stdin.write(JSON.stringify({op:'finish'})+'\n');same(await next(),{finished:true,normalOwnedPeerExit:true});
 child.stdin.end();same(await terminal,{code:0,signal:null});same(stderr,'');
 console.log(JSON.stringify({passed:true,checks,singlePreviewPolicy:true,optimizedElm:true,actualControlledC:true,
  readonlyProjectionChecks:readonlyChecks,visualProjectionChecks:visualChecks,pureRendererDecoderInstances:1,rendererWindowPolicyInstances:0,realmEpochs:2,nativeGrantResets:0,syntheticNativeRemainsActive:true,freshJSContexts:2,normalOwnedExit:true,nativeOwnedJavaScriptCore:true,persistentPolicyContexts:1,rendererElmInstances:0,
  nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(async e=>{console.error(e.stack);child.stdin.destroy();child.kill('SIGTERM');await terminal;process.exitCode=1;});
