'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Elm}=require(path.resolve(process.argv[2]));
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),source=fixture.clientScope,job=fixture.terminalReceipts[0].event.event.frame.job;
const first='family:'+source.scope.context.incarnation,second='family:3';let checks=0;
function check(ok,message){assert(ok,message);checks++;}
function worker(){
 const app=Elm.PreviewPresenterReplay.init();let pending;
 app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});
 return (kind,value)=>new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>reject(new Error('Asynchronous compiled retirement timeout')),3000);
  assert(!pending);pending=result=>{clearTimeout(timer);resolve(result);};app.ports.incoming.send({kind,value});
 });
}
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],
 popup:[first,second,'family:4'].map(id=>({id,domId:'window-'+id,label:'Window',ariaLabel:'Window',detail:'',enabled:true}))};
function seed(id=first){
 const native=structuredClone(source);if(id!==first){native.scope.context.incarnation=id.slice(7);native.requestId='9';native.scope.observation=String(BigInt(native.scope.observation)+1n);native.scope.now=String(BigInt(native.scope.now)+1n);}
 return {kind:'source-seed',publication:'1',lease:'1',identity:id,source:native,title:'Native source',application:'fixture'};
}
const observation=(subject,request,sequence,time)=>({kind:'native-incarnation-retirement',binding:source.binding,subject,
 request,sequence,clock:source.scope.clock,now:String(BigInt(source.scope.now)+BigInt(time)),issuedThrough:'100',state:'Retired'});
const final=(subject,entry,request,sequence,time)=>({kind:'native-actor-retired',identity:'family:'+subject,binding:source.binding,subject,
 entry,entryIssuedThrough:'2',requestFloor:entry==='1'?'1':'0',request,sequence,clock:source.scope.clock,
 now:String(BigInt(source.scope.now)+BigInt(time)),issuedThrough:'100'});
const oldFinal=final(source.scope.context.incarnation,'1','12','3',102);
const newFinal=final('3','2','14','5',104);
async function setup(){
 const send=worker();await send('presentation',presentation);await send('native',seed());await send('native',seed(second));
 const trigger={...job};delete trigger.request;await send('native',{kind:'event',identity:first,event:{kind:'request',trigger}});
 await send('native',observation(source.scope.context.incarnation,'10','1',100));
 const result=await send('native',{kind:'event',identity:first,event:{kind:'receipt',sequence:'4',event:{kind:'cancelled',job}}});
 assert.deepEqual(result.commands.flatMap(v=>v.commands).map(v=>v.kind),['acknowledge','retire-ready']);checks++;
 await send('native',observation('3','13','4',103));return send;
}
(async()=>{
 const send=await setup();let result=await send('native',oldFinal);
 check(result.models.length===1 && result.models[0].identity===second,'Exact delayed completion must survive a newer sibling observation');
 result=await send('native',newFinal);check(result.models.length===0,'Sibling completion removes only its own settled actor');
 const reordered=await setup();result=await reordered('native',newFinal);
 check(result.models.length===1 && result.models[0].identity===first,'Newer sibling completion preserves the older waiting actor');
 result=await reordered('native',oldFinal);check(result.models.length===0,'Older exact final fact must complete its still-pending actor');
 result=await reordered('native',seed(second));check(result.models.length===0 && result.commands.length===0,'Older completion cannot rewind native clock cutoff or permit a historical sibling seed');
 result=await reordered('native',seed());check(result.models.length===0,'Both old source seeds remain refused after reordered completion');
 const fresh=seed('family:4');fresh.source.scope.now=String(BigInt(newFinal.now)+1n);fresh.source.requestId='15';fresh.source.scope.observation='77';
 result=await reordered('native',fresh);check(result.models.length===1 && result.models[0].identity==='family:4','Fresh later source remains admissible after independent completion ordering');
 console.log(JSON.stringify({passed:true,checks,nativeAcceptance:false,fullReleaseAccepted:false,
 scope:'Actual optimized immutable Elm model with independently queued synthetic native retirement facts; no real WebKit transport, physical resources or whole retirement acceptance.'}));
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
