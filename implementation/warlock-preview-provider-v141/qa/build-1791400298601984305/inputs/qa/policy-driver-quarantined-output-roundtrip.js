'use strict';
const fs=require('fs'),assert=require('assert/strict'),{spawn}=require('child_process'),readline=require('readline');
const [binary,policy,outbox]=process.argv.slice(2);const child=spawn(binary,[policy,outbox],{stdio:['pipe','pipe','pipe']});
let stderr='',checks=0,pending;const rows=[],steps=[];child.stderr.on('data',v=>stderr+=v);
const terminal=new Promise(resolve=>child.on('close',(code,signal)=>{resolve({code,signal});if(pending){clearTimeout(pending.timer);pending.reject(Error('Native fixture exit '+stderr));pending=null;}}));
readline.createInterface({input:child.stdout}).on('line',line=>{const row=JSON.parse(line);if(pending){const p=pending;pending=null;clearTimeout(p.timer);p.resolve(row);}else rows.push(row);});
function next(){if(rows.length)return Promise.resolve(rows.shift());return new Promise((resolve,reject)=>{assert(!pending);const timer=setTimeout(()=>reject(Error('Original ten-second native fixture observation deadline '+stderr)),10000);pending={resolve,reject,timer};});}
async function call(op,values={}){child.stdin.write(JSON.stringify({op,...values})+'\n');const result=await next();steps.push({input:{op,...values},result});return result;}
const check=(value,label)=>{assert(value,label);checks++;},same=(a,b,label)=>{assert.deepEqual(a,b,label);checks++;};
async function inspect(){const r=await call('inspect');check(r.ok && !r.refused,'Original native driver diagnostic custody');return r.result;}
async function one(){const r=await call('step');check(r.ok && !r.refused,'Original bounded driver action');return r.progressed;}
async function pump(){for(let i=0;i<128;i++)if(!await one())return;throw Error('Fixture128 bounded driver actions exhausted; keep original trace');}
async function submit(epoch,events){const r=await call('native',{epoch,events:JSON.stringify(events)});check(r.ok && !r.refused,'Original native batch retained atomically before JS');}
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[{id:'family:21',domId:'window-21',label:'Window',ariaLabel:'Window',detail:'',enabled:true}]};
(async()=>{
 const setup=await next(),epoch=setup.epoch;
 check(setup.preGrantFaultChecks===9,'Four pre-grant driver faults cleanly release only their own contexts/registry while original native namespace stays claimed');
 let before=await inspect();same(before.transport,{nativeIssuedThrough:'0',deliveredThrough:'0',pending:0,capacity:1065},'Original empty native outbox');same(before.privatePolicy.models,[],'One native policy starts without reconstructed window models');
 check((await call('duplicate-driver')).refused,'Same original native owner cannot instantiate another empty window policy');
 const invalid=await call('foreign-native',{epoch,events:JSON.stringify(setup.events)});check(!invalid.ok && invalid.refused,'Foreign creator cannot retain original native input');same(await inspect(),before,'Foreign input leaves original custody and policy unchanged');
 const foreign=await call('native',{epoch:'2',events:JSON.stringify(setup.events)});check(!foreign.ok && foreign.refused,'Old/foreign source epoch refused before JS');same(await inspect(),before,'Wrong epoch cannot be restamped as current input');
 const malformed=await call('native',{epoch,events:'[{},null]'});check(!malformed.ok && malformed.refused,'Malformed batch refuses atomically');same(await inspect(),before,'No partial batch enters original input queue');
 check((await call('presentation',{value:JSON.stringify(presentation)})).ok,'Original presentation retained');same((await inspect()).privatePolicy.visuals.surface,null,'Retaining input runs no policy or native effect');
 await one();same((await inspect()).privatePolicy.visuals.surface,presentation,'Exactly one action processes the retained original presentation');
 await submit(epoch,setup.events);
 before=await inspect();same(before.retainedInputs,setup.events.length,'Whole batch owned before admission to policy');same(before.privatePolicy.models,[],'Retained native facts do not reentrantly process the policy');
 const baseline=(await call('native-status')).result;
 for(let i=0;i<setup.events.length;i++)await one();
 let state=await inspect();same(state.retainedInputs,0,'Only successful invocation removes retained original input');same(state.privatePolicy.realm.ingress.pending,1,'Original acquisition proposal retained in immutable Elm');same((await call('native-status')).result,baseline,'Policy processing dispatches no native effect');
 await one();state=await inspect();check(state.ticketUnnotified && state.postedTickets===1,'Native ticket owned before issued fact; JS callback stores exact post only');same(state.privatePolicy.realm.ingress.pending,1,'Ticket custody alone does not erase Elm intent');same(state.transport.nativeIssuedThrough,'1','Only original Native issuer assigns ordinal');same((await call('native-status')).result,baseline,'Outbox retain callback cannot dispatch an effect');
 await one();state=await inspect();check(!state.ticketUnnotified && state.postedTickets===1,'Original issued fact processed before staged effect');same(state.privatePolicy.realm.ingress.pending,0,'Native ticket fact removes only its exact original proposal');same(state.privatePolicy.models[0].model.known.length,1,'Original known job survives transport custody');same((await call('native-status')).result,baseline,'Issued policy invocation performs no native effect');
 await one();state=await inspect();same(state.transport.deliveredThrough,'1','Actual native dispatch receipt observed');same(state.transport.pending,0,'Only exact returned native data receipt releases outbox row');same(state.confirmations,1,'Independent original receipt confirmation remains retained');check(!state.ticketUnnotified && !state.postedTickets,'Original staged ticket consumed once');same(state.privatePolicy.models[0].model.known.length,1,'Transport delivery does not settle the Elm job');
 const dispatched=(await call('native-status')).result;check(dispatched.captures==='1' && dispatched.charge==='4096' && !dispatched.terminal,'Actual synthetic native FD capture retains original physical obligation');
 same(state.returnedEventBatches,1,'Original actual C offer/fence retained in one separate batch');
 check(state.returnedEventBytes>0 && state.returnedEventBytes<=8192 && state.nativeEffectError==='','Original successful C FD/mapping produces bounded offer/fence bytes before policy processing');
 check((await call('duplicate-driver')).refused,'An issued original native realm cannot reconstruct another policy');
 await one();same((await inspect()).confirmations,0,'Independent native confirmation completed separately');same((await call('native-status')).result,dispatched,'Confirmation has no physical/job settlement authority');check((await call('close-probe')).refused,'Known job prevents normal driver closure');
 check((await call('quarantine',{epoch})).ok,'Original urgent quarantine conceals while offer/fence bytes remain retained');const beforeOffer=await inspect();check(!beforeOffer.privatePolicy.models[0].model.demand && beforeOffer.returnedEventBatches===1,'Quarantine retains original queued native output and known duty');await one();const offered=await inspect();
 check(offered.returnedEventBatches===1 && offered.returnedEventBytes<beforeOffer.returnedEventBytes,'Exactly one original admitted offer processed before further effect output');
 check(offered.privatePolicy.realm.ingress.pending>=beforeOffer.privatePolicy.realm.ingress.pending,'Original cleanup intents retained while admitted output takes priority');
 await one();const fenced=await inspect();same(fenced.returnedEventBatches,0,'Exactly one original fence consumes the remaining retained batch');
 same(fenced.privatePolicy.models[0].model.image,null,'Late offer/fence cannot revive quarantined visuals');check(!fenced.privatePolicy.models[0].model.demand && fenced.privatePolicy.models[0].model.known.length===1,'Late output retains original known obligation without demand');
 same((await call('native-status')).result,dispatched,'Processing native outputs performs no native dispatch or physical settlement');

 // Use the original accepted popup maximum independently of the retained input
 // queue bound. Queue pressure neither narrows the visual protocol nor runs JS.
 before=await inspect();const empty=JSON.stringify(presentation);
 for(let i=0;i<1065;i++)check((await call('presentation',{value:empty})).ok,'Bounded exact ordinary input custody');
 state=await inspect();same(state.retainedInputs,1065,'Original candidate input queue maximum');same(state.privatePolicy,before.privatePolicy,'Retaining1065 inputs advances no policy');
 const refused=await call('presentation',{value:empty});check(!refused.ok && refused.refused && refused.code===27,'Full input custody explicitly WOULD_BLOCK before processing');same(await inspect(),state,'Refusal leaves original retained bytes/state unchanged');
 check((await call('quarantine',{epoch})).ok,'Urgent native quarantine bypasses full ordinary input custody');state=await inspect();same(state.retainedInputs,1065,'Quarantine does not erase queued original ordinary input');check(!state.privatePolicy.models[0].model.demand && state.privatePolicy.models[0].model.known.length===1,'Quarantine revokes demand but retains Unknown job');
 // Drain only this actual finite original queue; retain its complete event log.
 for(let i=0;i<1200;i++){if(!await one())break;if(i===1199)throw Error('Original1200 bounded queue-drain actions exhausted');}
 state=await inspect();same(state.retainedInputs,0,'All original queued inputs admitted without rewriting');same(state.transport.pending,0,'Original cleanup tickets returned data receipts');
 check((await call('large-presentation',{length:9*1024*1024})).ok,'Single bounded large native-generated input retained before policy');
 const largeState=await inspect();check(largeState.retainedInputBytes>9*1024*1024 && largeState.retainedInputs===1,'Serialized wrapped byte custody accounted independently of item count');
 const largeRefusal=await call('large-presentation',{length:9*1024*1024});check(!largeRefusal.ok && largeRefusal.code===27,'Aggregate byte bound refuses even with item capacity available');same(await inspect(),largeState,'Aggregate-byte refusal preserves exact original queue/policy/outbox');
 await pump();same((await inspect()).retainedInputBytes,0,'Successful policy processing releases only consumed retained byte custody');
 check((await call('poll')).ok,'Actual native cancellation/terminal polling');const seed=(await call('seed')).result;check(seed && seed.receiverEpoch===epoch,'Original native scoped detachment seed');await submit(epoch,[seed]);await pump();
 for(let round=0;round<6;round++){
  const proof=(await call('terminal')).result,pending=(await call('pending')).result;
  if(proof.length)await submit(epoch,proof);if(pending.length)await submit(epoch,pending);await pump();
  state=await inspect();if(state.privatePolicy.models.length===0 && state.privatePolicy.realm.ingress.pending===0 && state.transport.pending===0)break;
 }
 state=await inspect();same(state.privatePolicy.models,[],'Original actual terminal/detachment processing settles membership');same(state.transport.pending,0,'No retained native ticket is discarded at close');same(state.confirmations,0,'Original independent confirmation is drained');same(state.retainedInputs,0,'Original input custody is drained');
 const visual=(await call('visual')).result;check(visual && visual.binding.lifetime===setup.grant.binding.lifetime && visual.receiverEpoch===epoch,'Readonly visual projection remains in the original native domain');
 const finished=await call('finish');check(finished.finished && finished.normalOwnedPeerExit && finished.nativeGrantResets===0,'Original native/Elm strict close with unchanged Native grant and Active synthetic subject');child.stdin.end();const done=await terminal;check(done.code===0 && done.signal===null && stderr==='','Normal sanitizer driver/peer teardown');
 fs.writeFileSync('steps.json',JSON.stringify(steps,null,2)+'\n');console.log(JSON.stringify({passed:true,checks,preGrantFaultChecks:setup.preGrantFaultChecks,nativePolicyInstances:1,nativeTransportInstances:1,rendererWindowPolicies:0,ordinaryInputsRetained:1065,retainedInputByteLimit:16*1024*1024,normalOwnedExit:true,normalOwnedPeerExit:true,nativeGrantResets:0,actualControlledC:true,syntheticNativePeer:true,actualWebKit:false,actualSyntheticCapturedFD:true,realCoreCapturedFD:false,actualCapturedFD:false,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(error=>{child.kill('SIGTERM');fs.writeFileSync('failed-steps.json',JSON.stringify(steps,null,2)+'\n');console.error(error.stack);process.exitCode=1;});
