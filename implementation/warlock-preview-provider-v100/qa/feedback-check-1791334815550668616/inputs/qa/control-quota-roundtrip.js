'use strict';
const assert=require('node:assert/strict'),path=require('node:path'),cp=require('node:child_process'),readline=require('node:readline');
const {Elm}=require(path.resolve(process.argv[2]));
const child=cp.spawn(path.resolve(process.argv[3]),[],{stdio:['pipe','pipe','pipe']});
let stderr='',waiting=null;const queued=[];child.stderr.on('data',value=>stderr+=value);
readline.createInterface({input:child.stdout}).on('line',line=>{const value=JSON.parse(line);if(waiting){const done=waiting;waiting=null;done(value);}else queued.push(value);});
const exited=new Promise(resolve=>child.on('exit',(code,signal)=>resolve({code,signal})));
function next(){if(queued.length)return Promise.resolve(queued.shift());return new Promise((resolve,reject)=>{assert(!waiting);const timer=setTimeout(()=>reject(new Error('Original three-second native fixture response bound')),3000);waiting=value=>{clearTimeout(timer);resolve(value);};});}
async function native(value){child.stdin.write(JSON.stringify(value)+'\n');return next();}
const app=Elm.PreviewPresenterReplay.init();let frontendPending=null,checks=0;
app.ports.outgoing.subscribe(value=>{assert(frontendPending);const done=frontendPending;frontendPending=null;done(value);});
function elm(kind,value){return new Promise((resolve,reject)=>{assert(!frontendPending);const timer=setTimeout(()=>reject(new Error('Original three-second compiled Elm response bound')),3000);frontendPending=result=>{clearTimeout(timer);resolve(result);};app.ports.incoming.send({kind,value});});}
const check=(ok,name)=>{assert(ok,name);checks++;};
const kinds=value=>value.commands.flatMap(entry=>entry.commands.map(command=>command.kind));
async function issue(value){const output=[];for(const entry of value.commands)for(const command of entry.commands){const body=JSON.stringify({identity:entry.identity,commands:[command]});output.push(await native({op:'command',body}));}return output;}
(async()=>{
 const initial=await next();check(initial.jobQuota===5 && initial.actorQuota===2 && initial.reconciliationQuota===1,'Native conservative quotas are explicit');
 const identity=initial.seed.identity;
 await elm('presentation',{surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[{id:identity,domId:'window-'+identity,label:'Window',ariaLabel:'Window',detail:'',enabled:true}]});
 await elm('native',initial.seed);let value=await elm('native',initial.request);
 assert.deepEqual(kinds(value),['acquire']);checks++;
 const acquired=(await issue(value))[0];check(acquired.decision===1 && acquired.invocations===1 && acquired.events.length===2,'Native single capture and producer completion for fixture bytes');
 check((await native({op:'confirm',ordinal:acquired.delivered})).accepted,'Original Acquire transport receipt confirmed');
 // Hold the actual native offer delivery while Elm requests cancellation.
 value=await elm('native',{kind:'event',identity,event:{kind:'close'}});assert.deepEqual(kinds(value),['cancel']);checks++;
 const cancelled=(await issue(value))[0];check(cancelled.decision===1 && cancelled.invocations===2 && cancelled.events.length===0,'Real held URI reader prevents terminal native proof');
 check((await native({op:'confirm',ordinal:cancelled.delivered})).accepted,'Original Cancel transport receipt confirmed');
 value=await elm('native',acquired.events[0]);assert.deepEqual(kinds(value),['release']);checks++;
 const released=(await issue(value))[0];check(released.decision===1 && released.invocations===3 && released.events.length===2,'Late actual offer consumes only original Release slot and produces two terminal proofs');
 check((await native({op:'confirm',ordinal:released.delivered})).accepted,'Original Release transport receipt confirmed');
 value=await elm('native',acquired.events[1]);check(kinds(value).length===0,'Late fence cannot revive cancelled ownership');
 value=await elm('native',released.events[0]);check(kinds(value).length===0,'First terminal proof cannot erase the outstanding cancellation');
 value=await elm('native',released.events[1]);assert.deepEqual(kinds(value),['acknowledge']);checks++;
 const finalAck=value;const acknowledged=(await issue(value))[0];check(acknowledged.decision===1 && acknowledged.invocations===4 && acknowledged.effectReturned,'Final original terminal proof acknowledged by actual native Broker');
 let status=await native({op:'status'});check(status.records===0 && status.readers===0 && status.charge==='0' && !status.prefixConfirmed,'Native physical/terminal drain precedes final frontend receipt confirmation');
 check(status.issued==='4' && status.tickets===4 && status.reserved==='4' && !status.transportEmpty && !status.fullCloseAllowed,'One job cleanup slot plus actor/reconciliation quotas remain; no native close assertion');
 check((await native({op:'confirm',ordinal:acknowledged.delivered})).accepted,'Original final ACK transport receipt confirmed separately');
 for(let i=0;i<25;++i){
  value=await elm('native',released.events[1]);assert.deepEqual(value.commands,finalAck.commands);checks++;
  const repeated=(await issue(value))[0];check(repeated.ticket===acknowledged.ticket && repeated.decision===2 && repeated.invocations===4 && repeated.events.length===0,'Repeated actual Elm ACK reuses original native ticket without another effect');
 }
 status=await native({op:'status'});check(status.issued==='4' && status.tickets===4 && status.reserved==='4' && status.prefixConfirmed && !status.fullCloseAllowed,'Arbitrarily repeated ACKs do not spend fresh quota or imply actor retirement');
 await native({op:'exit-fixture'});child.stdin.end();const exit=await exited;check(exit.code===0 && exit.signal===null && !stderr,'Normal owned metadata fixture exit after real URI/Broker settlement');
 console.log(JSON.stringify({passed:true,checks,distinctJobControls:4,repeatedAcknowledgments:25,normalOwnedExit:true,nativeAcceptance:false,fullReleaseAccepted:false,scope:'Actual optimized immutable Elm and native Coordinator/Broker/URI reader/control reservation/dispatcher/receipt coupling with synthetic native observation and fixture PNG header bytes. Worst-case Acquire/Cancel/late Release/final ACK, two real terminal proofs, exact repeat tickets and separate final confirmation. Actor/reconciliation credits stay retained; no real capture, WebKit, actor retirement or host close acceptance.'}));
})().catch(error=>{child.kill('SIGTERM');console.error(error.stack+'\n'+stderr);process.exitCode=1;});
