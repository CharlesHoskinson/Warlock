'use strict';
const fs=require('fs'),assert=require('assert/strict'),{spawn}=require('child_process'),readline=require('readline');
const [binary,policy,outbox,tracePath]=process.argv.slice(2),trace=JSON.parse(fs.readFileSync(tracePath));
const child=spawn(binary,[policy,outbox],{stdio:['pipe','pipe','pipe']});let stderr='',pending,observations=0;const rows=[],steps=[];child.stderr.on('data',v=>stderr+=v);
const terminal=new Promise(resolve=>child.on('close',(code,signal)=>{resolve({code,signal});if(pending){clearTimeout(pending.timer);pending.reject(Error('Native fixture exited '+stderr));pending=null;}}));
readline.createInterface({input:child.stdout}).on('line',line=>{const r=JSON.parse(line);if(pending){const p=pending;pending=null;clearTimeout(p.timer);p.resolve(r);}else rows.push(r);});
function next(){if(rows.length)return Promise.resolve(rows.shift());return new Promise((resolve,reject)=>{assert(!pending);const timer=setTimeout(()=>reject(Error('Original ten-second native observation deadline '+stderr)),10000);pending={resolve,reject,timer};});}
async function call(op,values={}){child.stdin.write(JSON.stringify({op,...values})+'\n');const r=await next();steps.push({input:{op,...values},result:r});return r;}
async function one(){const r=await call('step');assert(r.ok && !r.refused);return r.progressed;}
async function pump(){for(let n=0;n<128;n++)if(!await one())return;throw Error('Original128 bounded driver actions exhausted');}
async function submit(epoch,events){const r=await call('native',{epoch,events:JSON.stringify(events)});assert(r.ok && !r.refused);}
(async()=>{
 const setup=await next(),epoch=setup.epoch;
 const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[{id:'family:21',domId:'window-21',label:'Window',ariaLabel:'Window',detail:'',enabled:true}]};
 assert((await call('presentation',{value:JSON.stringify(presentation)})).ok);await one();await submit(epoch,setup.events);for(let n=0;n<setup.events.length;n++)await one();
 let action={refused:false,code:0},history=[];
 for(const model of trace){
  if(model.history.length>history.length){assert.equal(model.history.length,history.length+1);const event=model.history.at(-1);
   if(event==='Step')action=await call('step');
   else if(event==='Held' || event==='Open')action=await call('output-held',{value:event==='Held'});
   else if(event==='Quarantine')action=await call('quarantine',{epoch});
   else if(event==='Foreign')action=await call('foreign-native',{epoch,events:'[]'});
   else throw Error('Closed model event union');
   history=model.history;
  }
  const state=(await call('inspect')).result,recovery=(await call('recovery')).result,native=(await call('native-status')).result,held=(await call('output-state')).result;
  const observed={issued:Number(recovery.issuedThrough),notified:state.ticketUnnotified?0:Number(state.transport.nativeIssuedThrough),delivered:Number(recovery.deliveredThrough),confirmed:Number(recovery.confirmedThrough),effects:Number(native.captures),held,demand:state.privatePolicy.models[0].model.demand,known:native.records==='1' && native.charge==='4096' && !native.terminal && state.privatePolicy.models[0].model.known.length===1,refused:action.refused,code:action.code};
  const expected=Object.fromEntries(Object.keys(observed).map(k=>[k,model[k]]));assert.deepEqual(observed,expected,'Actual original C/JSC first-ticket/independent-confirmation/physical duty versus selected Quint state');observations++;
 }
 assert((await call('output-held',{value:false})).ok);assert((await call('quarantine',{epoch})).ok);await pump();assert((await call('poll')).ok);
 const seed=(await call('seed')).result;assert(seed && seed.receiverEpoch===epoch);await submit(epoch,[seed]);await pump();
 for(let n=0;n<6;n++){const proof=(await call('terminal')).result,more=(await call('pending')).result;if(proof.length)await submit(epoch,proof);if(more.length)await submit(epoch,more);await pump();const s=(await call('inspect')).result;if(s.privatePolicy.models.length===0 && s.transport.pending===0 && s.confirmations===0)break;}
 const finished=await call('finish');assert(finished.finished && finished.normalOwnedPeerExit && finished.nativeGrantResets===0);child.stdin.end();const done=await terminal;assert(done.code===0 && done.signal===null && stderr==='');
 fs.writeFileSync('native-model-steps.json',JSON.stringify(steps,null,2)+'\n');console.log(JSON.stringify({passed:true,observations,normalOwnedExit:true,normalOwnedPeerExit:true,nativeGrantResets:0,compiledStricterOutputGate:true,actualOutputQueueExhaustion:false,actualCore:false,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(error=>{child.kill('SIGTERM');fs.writeFileSync('failed-native-model-steps.json',JSON.stringify(steps,null,2)+'\n');console.error(error.stack);process.exitCode=1;});
