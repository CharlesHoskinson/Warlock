'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Elm}=require(path.resolve(process.argv[2]));
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const source=fixture.clientScope,job=fixture.terminalReceipts[0].event.event.frame.job;
const ids={first:'family:'+source.scope.context.incarnation,second:'family:3'};
const names=Object.fromEntries(Object.entries(ids).map(([k,v])=>[v,k]));
function decode(v){if(Array.isArray(v))return v.map(decode);if(v&&typeof v==='object')return '#bigint' in v?Number(v['#bigint']):Object.fromEntries(Object.entries(v).map(([k,x])=>[k,decode(x)]));return v;}
function worker(){const app=Elm.PreviewPresenterReplay.init();let pending;
 app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});
 return (kind,value)=>new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(new Error('Retained delivery refinement timeout')),3000);
  assert(!pending);pending=result=>{clearTimeout(timer);resolve(result);};app.ports.incoming.send({kind,value});});}
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:Object.values(ids).map(id=>({id,domId:'window-'+id,label:'Window',ariaLabel:'Window',detail:'',enabled:true}))};
function seed(first){const native=structuredClone(source);if(!first){native.scope.context.incarnation='3';native.requestId='9';native.scope.observation=String(BigInt(native.scope.observation)+1n);native.scope.now=String(BigInt(native.scope.now)+1n);}
 return {kind:'source-seed',publication:'1',lease:'1',identity:first?ids.first:ids.second,source:native,title:'Source',application:'fixture'};}
const observation=(subject,request,sequence,time)=>({kind:'native-incarnation-retirement',binding:source.binding,subject,request,sequence,clock:source.scope.clock,now:String(BigInt(source.scope.now)+BigInt(time)),issuedThrough:'100',state:'Retired'});
const fact=(subject,entry,request,sequence,time)=>({kind:'native-actor-retired',identity:'family:'+subject,binding:source.binding,subject,entry,entryIssuedThrough:'2',requestFloor:entry==='1'?'1':'0',request,sequence,clock:source.scope.clock,now:String(BigInt(source.scope.now)+BigInt(time)),issuedThrough:'100'});
const finalA=fact(ids.first.slice(7),'1','12','3',102),finalB=fact('3','2','14','5',104);
const delivery=(ordinal,fact)=>({kind:'native-actor-retirement-delivery',deliveryOrdinal:ordinal,fact});
const channel={kind:'native-actor-retirement-channel',binding:source.binding};
const terminal={kind:'event',identity:ids.first,event:{kind:'receipt',sequence:'4',event:{kind:'cancelled',job}}};
const events={Activate:channel,ObserveFirst:observation(ids.first.slice(7),'10','1',100),ObserveSecond:observation('3','13','4',103),TerminalFirst:terminal,
 DeliverFirst1:delivery('1',finalA),DeliverFirst2:delivery('2',finalA),DeliverSecond1:delivery('1',finalB),DeliverSecond2:delivery('2',finalB),GapFirst3:delivery('3',finalA),
 LegacyFirst:finalA,ForeignFirst1:delivery('1',{...finalA,binding:{...source.binding,frontend:'999'}}),Replacement:{...channel,binding:{...source.binding,frontend:'999'}},DuplicateTerminal:terminal,OldSeed:seed(true)};
function projection(result){const rows=Object.fromEntries(result.models.map(v=>[names[v.identity],v]));assert(Object.keys(rows).every(k=>k!=='undefined'));
 const ready=row=>Boolean(row&&!row.active&&!row.model.demand&&row.model.accepted===null&&row.model.known.length===0&&row.model.cancelling.length===0&&row.model.retiring.length===0);
 return {first:Boolean(rows.first),pendingFirst:Boolean(rows.first&&!rows.first.active),knownFirst:Boolean(rows.first&&rows.first.model.known.length),readyFirst:ready(rows.first),
 second:Boolean(rows.second),pendingSecond:Boolean(rows.second&&!rows.second.active),readySecond:ready(rows.second),
 commands:result.commands.flatMap(row=>row.commands.map(command=>names[row.identity]+':'+command.kind+(command.kind==='retire-delivery-ack'?':'+command.deliveryOrdinal:'')))};}
(async()=>{let compared=0;const coupled=[];
 for(const file of process.argv.slice(4)){const states=decode(JSON.parse(fs.readFileSync(file,'utf8'))).states.map(v=>v.s),send=worker();
  await send('presentation',presentation);await send('native',seed(true));await send('native',seed(false));
  const trigger={...job};delete trigger.request;let result=await send('native',{kind:'event',identity:ids.first,event:{kind:'request',trigger}});
  let length=0,count=0;
  for(const state of states){const wanted=Object.fromEntries(Object.entries(state).filter(([k])=>!['history','cutoff','channel','processed'].includes(k)));
   if(state.history.length===0){assert.deepEqual(projection({...result,commands:[]}),wanted);continue;}
   if(state.history.length===length)continue;assert.equal(state.history.length,length+1);length=state.history.length;
   const event=state.history.at(-1);assert(events[event],event);result=await send('native',events[event]);
   assert.deepEqual(projection(result),wanted,path.basename(file)+' step '+length+' '+event);count++;compared++;}
  coupled.push({trace:path.basename(file),statesCompared:count});}
 console.log(JSON.stringify({passed:true,statesCompared:compared,coupledTraces:coupled,nativeAcceptance:false,fullReleaseAccepted:false,
 scope:'Actual compiled Elm actor/lifecycle projection and exact ordered processing-ACK payloads coupled to Quint. Prefix/channel are exercised through outcomes, not reported as directly observed internal fields. Synthetic facts; native/WebKit/physical qualification remains separate.'}));
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
