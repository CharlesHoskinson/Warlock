'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process'),readline=require('node:readline');
const {Elm}=require(path.resolve(process.argv[2]));
const child=spawn(path.resolve(process.argv[3]),[],{stdio:['pipe','pipe','pipe']});
let stderr='',pending,exitResult;const buffered=[];child.stderr.on('data',v=>stderr+=v);
const terminal=new Promise(resolve=>child.on('close',(code,signal)=>{exitResult={code,signal};resolve(exitResult);if(pending){pending.reject(new Error('Native child exited: '+stderr));pending=null;}}));
const lines=readline.createInterface({input:child.stdout});
lines.on('line',line=>{const value=JSON.parse(line);if(pending){const waiter=pending;pending=null;clearTimeout(waiter.timer);waiter.resolve(value);}else buffered.push(value);});
function next(){if(buffered.length)return Promise.resolve(buffered.shift());return new Promise((resolve,reject)=>{assert(!pending);const timer=setTimeout(()=>reject(new Error('Actual native/Elm channel timeout: '+stderr)),10000);pending={resolve,reject,timer};});}
async function control(value){child.stdin.write(JSON.stringify(value)+'\n');return next();}
const app=Elm.RetainedLegacyPresenterReplay.init();let elmPending,checks=0;
app.ports.outgoing.subscribe(value=>{assert(elmPending);const done=elmPending;elmPending=null;done(value);});
function send(kind,value){return new Promise((resolve,reject)=>{assert(!elmPending);const timer=setTimeout(()=>reject(new Error('Compiled Elm round trip timeout')),3000);elmPending=result=>{clearTimeout(timer);resolve(result);};app.ports.incoming.send({kind,value});});}
async function feed(rows){let result;for(const row of rows)result=await send('native',row);return result;}
(async()=>{
 const start=await next();assert.equal(start.stage,'start');checks++;
 const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:['family:21','family:22'].map(id=>({id,domId:'window-'+id,label:'Window',ariaLabel:'Window',detail:'',enabled:true}))};
 await send('presentation',presentation);let result;const issued=[];
 for(const event of start.events){result=await send('native',event);issued.push(...result.commands.flatMap(row=>row.commands));}
 assert.equal(result.models.length,2);checks++;
 assert.equal(issued.length,2);assert.equal(issued[0].kind,'acquire');assert.deepEqual(issued[0].job,start.job);checks++;
 // ImportedClients already emits each original exact request after its seed.
 // A repeated Request deliberately emits nothing; never invent another request.
 await send('native',start.channel);
 const neighbor=structuredClone(result.models.find(v=>v.identity==='family:22'));
 const observed=await control({op:'observe'});result=await feed(observed.events);
 assert.deepEqual(result.commands.flatMap(v=>v.commands).map(v=>v.kind),['cancel']);checks++;
 await control({op:'controls',entries:result.commands});
 const proof=await control({op:'terminal'});result=await feed(proof.events);
 assert.deepEqual(result.commands.flatMap(v=>v.commands).map(v=>v.kind),['acknowledge','retire-ready']);checks++;
 const blocked=await control({op:'controls',entries:result.commands});assert.deepEqual(blocked.events,[]);checks++;
 const stillBlocked=await control({op:'blocked-poll'});assert.deepEqual(stillBlocked.events,[]);checks++;
 // Elm emitted its single readiness already. Only native receiver retirement
 // and revalidation of that retained input may unblock native completion.
 const completed=await control({op:'release-receiver'});
 assert.equal(completed.events.length,1);assert.equal(completed.events[0].kind,'native-actor-retirement-delivery');checks++;
 // Drop the first actual final transmission. Its actor has been removed from
 // native maps, but remains in Elm until the retained native retry arrives.
 assert.equal(result.models.length,2);checks++;
 const retried=await control({op:'pending'});assert.deepEqual(retried.events,completed.events);checks++;
 result=await feed(retried.events);
 assert.deepEqual(result.models,[neighbor]);checks++;
 const firstAck=structuredClone(result.commands);
 assert.equal(firstAck.length,1);assert.equal(firstAck[0].commands[0].kind,'retire-delivery-ack');checks++;
 // Lose Elm's first processing ACK, then retry the original native record.
 const lostAckRetry=await control({op:'pending'});assert.deepEqual(lostAckRetry.events,completed.events);checks++;
 result=await feed(lostAckRetry.events);assert.deepEqual(result.models,[neighbor]);assert.deepEqual(result.commands,firstAck);checks++;
 const drained=await control({op:'drain-neighbor'});result=await feed(drained.events);
 assert.deepEqual(result.commands.flatMap(v=>v.commands).map(v=>v.kind),['acknowledge']);checks++;
 await control({op:'controls',entries:result.commands});
 const closeBarrier=await control({op:'check-close'});assert.deepEqual(closeBarrier.events,completed.events);checks++;
 const confirmed=await control({op:'controls',entries:firstAck});assert.deepEqual(confirmed.events,[]);checks++;
 const duplicate=await control({op:'controls',entries:firstAck});assert.deepEqual(duplicate.events,[]);checks++;
 const finished=await control({op:'finish'});assert(finished.passed);checks++;
 child.stdin.end();const exited=await terminal;assert.deepEqual(exited,{code:0,signal:null});assert.equal(stderr,'');checks++;
 console.log(JSON.stringify({passed:true,checks,nativeCChecks:finished.checks,normalOwnedExit:true,nativeAcceptance:false,fullReleaseAccepted:false,
 scope:'Actual original C bootstrap/socket/Native/ImportedClients/retained journal and compiled immutable Elm. Actual cancellation, terminal proof/ACK then readiness, loss of final transmission and processing ACK, retained neighbor/counter, close barrier and normal cleanup. Synthetic peer native retirement and untouched reservations; no compositor window destruction, captured FD/reader/fence or real WebKit acceptance.'}));
})().catch(async error=>{console.error(error.stack);child.stdin.destroy();child.kill('SIGTERM');await terminal;process.exitCode=1;});
