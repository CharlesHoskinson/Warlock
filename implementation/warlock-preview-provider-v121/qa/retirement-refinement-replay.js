 'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Elm}=require(path.resolve(process.argv[2]));
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),source=fixture.clientScope,job=fixture.terminalReceipts[0].event.event.frame.job;
const ids={first:'family:'+source.scope.context.incarnation,second:'family:3',fresh:'family:4'};
const label=Object.fromEntries(Object.entries(ids).map(([k,v])=>[v,k]));
function decode(v){if(Array.isArray(v))return v.map(decode);if(v&&typeof v==='object')return '#bigint' in v?Number(v['#bigint']):Object.fromEntries(Object.entries(v).map(([k,x])=>[k,decode(x)]));return v;}
function worker(){const app=Elm.PreviewPresenterReplay.init();let pending;
 app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});
 return (kind,value)=>new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(new Error('Compiled async refinement timeout')),3000);
  assert(!pending);pending=result=>{clearTimeout(timer);resolve(result);};app.ports.incoming.send({kind,value});});}
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:Object.values(ids).map(id=>({id,domId:'window-'+id,label:'Window',ariaLabel:'Window',detail:'',enabled:true}))};
function seed(who,time){const native=structuredClone(source);if(who!=='first'){native.scope.context.incarnation=ids[who].slice(7);native.requestId=who==='fresh'?'15':'9';native.scope.observation=who==='fresh'?'77':String(BigInt(native.scope.observation)+1n);native.scope.now=String(BigInt(source.scope.now)+BigInt(time??1));}
 return {kind:'source-seed',publication:'1',lease:'1',identity:ids[who],source:native,title:'Native source',application:'fixture'};}
const observation=(subject,request,sequence,time)=>({kind:'native-incarnation-retirement',binding:source.binding,subject,request,sequence,clock:source.scope.clock,now:String(BigInt(source.scope.now)+BigInt(time)),issuedThrough:'100',state:'Retired'});
const final=(subject,entry,request,sequence,time)=>({kind:'native-actor-retired',identity:'family:'+subject,binding:source.binding,subject,entry,entryIssuedThrough:'2',requestFloor:entry==='1'?'1':'0',request,sequence,clock:source.scope.clock,now:String(BigInt(source.scope.now)+BigInt(time)),issuedThrough:'100'});
const firstFinal=final(source.scope.context.incarnation,'1','12','3',102),secondFinal=final('3','2','14','5',104);
const terminal={kind:'event',identity:ids.first,event:{kind:'receipt',sequence:'4',event:{kind:'cancelled',job}}};
const events={ObserveFirst:observation(source.scope.context.incarnation,'10','1',100),ObserveSecond:observation('3','13','4',103),
 TerminalFirst:terminal,DuplicateTerminal:terminal,FinalFirst:firstFinal,FinalSecond:secondFinal,PrematureFinal:firstFinal,
 ForeignFinal:{...firstFinal,binding:{...firstFinal.binding,session:'999'}},OldObservation:observation(source.scope.context.incarnation,'10','1',-1),
 OldSeedFirst:seed('first'),OldSeedSecond:seed('second'),MidSeedFresh:seed('fresh',103),FreshSeed:seed('fresh',105)};
function projection(result){const rows=Object.fromEntries(result.models.map(row=>[label[row.identity],row]));assert(Object.keys(rows).every(k=>k!=='undefined'));
 const ready=row=>Boolean(row&&!row.active&&!row.model.demand&&row.model.accepted===null&&row.model.known.length===0&&row.model.cancelling.length===0&&row.model.retiring.length===0);
 return {first:Boolean(rows.first),pendingFirst:Boolean(rows.first&&!rows.first.active),knownFirst:Boolean(rows.first&&rows.first.model.known.length),readyFirst:ready(rows.first),
  second:Boolean(rows.second),pendingSecond:Boolean(rows.second&&!rows.second.active),readySecond:ready(rows.second),fresh:Boolean(rows.fresh),
  commands:result.commands.flatMap(row=>row.commands.map(command=>label[row.identity]+':'+command.kind))};}
(async()=>{const traces=[];let compared=0;
 for(const file of process.argv.slice(4)){const states=decode(JSON.parse(fs.readFileSync(file,'utf8'))).states.map(v=>v.s),send=worker();
  await send('presentation',presentation);await send('native',seed('first'));await send('native',seed('second'));
  const trigger={...job};delete trigger.request;let result=await send('native',{kind:'event',identity:ids.first,event:{kind:'request',trigger}});
  let length=0,count=0;
  for(const state of states){if(state.history.length===0){assert.deepEqual(projection({...result,commands:[]}),Object.fromEntries(Object.entries(state).filter(([k])=>!['history','cutoff'].includes(k))));continue;}
   if(state.history.length===length)continue;assert.equal(state.history.length,length+1);length=state.history.length;
   const event=state.history.at(-1);assert(events[event],event);result=await send('native',events[event]);
   const wanted=Object.fromEntries(Object.entries(state).filter(([k])=>!['history','cutoff'].includes(k)));
   assert.deepEqual(projection(result),wanted,path.basename(file)+' step '+length+' '+event);count++;compared++;}
  traces.push({trace:path.basename(file),statesCompared:count});}
 console.log(JSON.stringify({passed:true,statesCompared:compared,coupledTraces:traces,nativeAcceptance:false,fullReleaseAccepted:false,
  scope:'Actual optimized immutable Elm observable actor/lifecycle state and ordered command projection; cutoff tested through source admission, not observed as an internal field. Synthetic native facts do not establish transport or physical cleanup.'}));
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
