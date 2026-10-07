'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Elm}=require(path.resolve(process.argv[2]));
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),source=fixture.clientScope,frame=fixture.terminalReceipts[0].event.event.frame;
const identity='family:'+source.scope.context.incarnation;
let checks=0;
function check(ok,message){assert(ok,message);checks++;}
function worker(){
 const app=Elm.PreviewPresenterReplay.init();let pending;
 app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});
 return (kind,value)=>new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>reject(new Error('Compiled retirement replay timeout')),3000);
  assert(!pending);pending=result=>{clearTimeout(timer);resolve(result);};app.ports.incoming.send({kind,value});
 });
}
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],
 popup:[identity,'family:3'].map(id=>({id,domId:'window-'+id,label:'Window',ariaLabel:'Window',detail:'',enabled:true}))};
const seed={kind:'source-seed',publication:'1',lease:'1',identity,source,title:'Native source',application:'fixture'};
const trigger={...frame.job};delete trigger.request;
const observation={kind:'native-incarnation-retirement',binding:source.binding,subject:source.scope.context.incarnation,
 request:'10',sequence:'1',clock:source.scope.clock,now:String(BigInt(source.scope.now)+100n),issuedThrough:'100',state:'Retired'};
const final={kind:'native-actor-retired',identity,binding:source.binding,subject:observation.subject,request:'11',sequence:'2',
 clock:observation.clock,now:String(BigInt(observation.now)+1n),issuedThrough:'100',entry:'1',entryIssuedThrough:'1',requestFloor:'1'};
async function setup(){
 const send=worker();await send('presentation',presentation);await send('native',seed);
 await send('native',{kind:'event',identity,event:{kind:'request',trigger}});return send;
}
async function unchanged(send,value,prior,message){
 const result=await send('native',value);assert.deepEqual(result,prior,message);checks++;return result;
}
(async()=>{
 const send=await setup();let result=await send('native',observation);
 check(!result.models[0].active && !result.models[0].model.demand && result.models[0].model.known.length===1,'Permanent retirement closes demand while preserving exact known job');
 check(result.commands.flatMap(row=>row.commands).map(row=>row.kind).join()==='cancel','Retired capturing job emits exact cancellation, never readiness');
 const pending={...result,commands:[]};
 await unchanged(send,final,pending,'Premature native fact cannot remove unsettled Elm history');
 for(const mutate of [
  v=>v.binding={...v.binding,session:'999'},v=>v.clock='1',v=>v.subject='999',v=>v.state='Active',
  v=>v.issuedThrough='0',v=>v.extra=true,v=>v.request=10,v=>v.sequence='01'
 ]){const value=structuredClone(observation);mutate(value);await unchanged(send,value,pending,'Malformed or foreign observation retains original job');}
 const cancelled={kind:'event',identity,event:{kind:'receipt',sequence:'4',event:{kind:'cancelled',job:frame.job}}};
 result=await send('native',cancelled);
 check(result.models[0].model.known.length===0 && result.models[0].model.cancelling.length===0,'Exact terminal proof settles known and cancellation obligations');
 assert.deepEqual(result.commands.flatMap(row=>row.commands).map(row=>row.kind),['acknowledge','retire-ready']);checks++;
 const ready={...result,commands:[]};
 await unchanged(send,cancelled,ready,'After readiness, duplicate terminal must not enqueue another ACK');
 for(const mutate of [
  v=>v.binding={...v.binding,session:'999'},v=>v.clock='1',v=>v.subject='999',v=>v.entry='0',
  v=>v.entryIssuedThrough='0',v=>v.sequence='1',v=>v.request='10',v=>v.now=String(BigInt(observation.now)-1n),
  v=>v.identity='family:999',v=>v.extra=true
 ]){const value=structuredClone(final);mutate(value);await unchanged(send,value,ready,'Malformed or mismatched native completion cannot erase Elm owner');}
 result=await send('native',final);check(result.models.length===0 && result.commands.length===0,'Exact confirmed native transaction removes settled Elm actor');
 await unchanged(send,seed,result,'Historical source seed cannot recreate retired Elm actor');
 await unchanged(send,fixture.terminalReceipts[0],result,'Old receipt cannot recreate retired actor');
 await unchanged(send,final,result,'Replayed native completion cannot resurrect retired actor');
 const nextSeed=structuredClone(seed);nextSeed.identity='family:3';nextSeed.source.scope.context.incarnation='3';
 nextSeed.source.requestId='12';nextSeed.source.scope.observation='76';nextSeed.source.scope.now=String(BigInt(final.now)+1n);
 result=await send('native',nextSeed);check(result.models.length===1 && result.models[0].identity==='family:3','Fresh native source after retirement cutoff can enroll a different live actor');
 // Accepted historical pixels must receive an immediate release on permanent
 // retirement, even with no future clock tick, expiry or source query.
 const accepted=await setup();
 await accepted('native',{kind:'event',identity,event:{kind:'offer',frame}});
 result=await accepted('native',observation);
 check(result.models[0].model.accepted===null && result.models[0].model.retiring.length===1,'Permanent retirement immediately retains accepted packet as retiring');
 assert.deepEqual(result.commands.flatMap(row=>row.commands).map(row=>row.kind),['release']);checks++;
 result=await accepted('native',fixture.terminalReceipts[0]);
 assert.deepEqual(result.commands.flatMap(row=>row.commands).map(row=>row.kind),['acknowledge','retire-ready']);checks++;
 check(result.models[0].model.known.length===0 && result.models[0].model.retiring.length===0,'Actual correlated release proof settles packet history before readiness');
 console.log(JSON.stringify({passed:true,checks,nativeAcceptance:false,fullReleaseAccepted:false,
 scope:'Actual optimized full-GUI Elm reducer, retained historical packet and synthetic native retirement facts; no native physical cleanup or ordered WebKit barrier qualification'}));
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
