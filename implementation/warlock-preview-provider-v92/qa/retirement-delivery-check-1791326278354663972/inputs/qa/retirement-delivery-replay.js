'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Elm}=require(path.resolve(process.argv[2]));
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const source=fixture.clientScope,frame=fixture.terminalReceipts[0].event.event.frame;
const first='family:'+source.scope.context.incarnation,second='family:3';let checks=0;
const check=(ok,name)=>{assert(ok,name);checks++;};
function worker(){
 const app=Elm.PreviewPresenterReplay.init();let pending;
 app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});
 return value=>new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>reject(new Error('Compiled retained delivery timeout')),3000);
  assert(!pending);pending=result=>{clearTimeout(timer);resolve(result);};app.ports.incoming.send(value);
 });
}
const shown={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],
 popup:[first,second,'family:4'].map(id=>({id,domId:'window-'+id,label:'Window',ariaLabel:'Window',detail:'',enabled:true}))};
function seed(id=first,time=0){const native=structuredClone(source);
 native.scope.context.incarnation=id.slice(7);native.requestId=String(9+time);
 native.scope.now=String(BigInt(source.scope.now)+BigInt(time));
 native.scope.observation=String(BigInt(source.scope.observation)+BigInt(time));
 return {kind:'source-seed',publication:'1',lease:'1',identity:id,source:native,title:'Source',application:'fixture'};}
const observation=(subject,request,sequence,time)=>({kind:'native-incarnation-retirement',binding:source.binding,subject,
 request,sequence,clock:source.scope.clock,now:String(BigInt(source.scope.now)+BigInt(time)),issuedThrough:'100',state:'Retired'});
const final=(subject,entry,request,sequence,time)=>({kind:'native-actor-retired',identity:'family:'+subject,binding:source.binding,subject,
 entry,entryIssuedThrough:'2',requestFloor:entry==='1'?'1':'0',request,sequence,clock:source.scope.clock,
 now:String(BigInt(source.scope.now)+BigInt(time)),issuedThrough:'100'});
const obsA=observation(first.slice(7),'10','1',100),obsB=observation('3','13','4',103);
const finalA=final(first.slice(7),'1','12','3',102),finalB=final('3','2','14','5',104);
const channel={kind:'native-actor-retirement-channel',binding:source.binding};
const delivery=(ordinal,fact)=>({kind:'native-actor-retirement-delivery',deliveryOrdinal:ordinal,fact});
const native=(send,value)=>send({kind:'native',value});
async function setup(activate=true){const send=worker();await send({kind:'presentation',value:shown});
 await native(send,seed());await native(send,seed(second));
 if(activate)await native(send,channel);
 const trigger={...frame.job};delete trigger.request;
 await native(send,{kind:'event',identity:first,event:{kind:'request',trigger}});return send;}
async function ready(send){await native(send,obsA);
 let value=await native(send,{kind:'event',identity:first,event:{kind:'receipt',sequence:'4',event:{kind:'cancelled',job:frame.job}}});
 assert.deepEqual(value.commands.flatMap(v=>v.commands).map(v=>v.kind),['acknowledge','retire-ready']);checks++;
 await native(send,obsB);return value;}
function ack(result,ordinal,id){assert.deepEqual(result.commands,[{identity:id,commands:[{kind:'retire-delivery-ack',binding:source.binding,deliveryOrdinal:ordinal}]}]);checks++;}
async function inert(send,value,prior,name){const result=await native(send,value);assert.deepEqual(result,{...prior,commands:[]},name);checks++;return result;}
(async()=>{
 const send=await setup();let result=await native(send,obsA);
 await inert(send,delivery('1',finalA),result,'PrematureDeliveryCannotForgetKnownJob');
 await ready(send);result=await native(send,delivery('2',finalB));
 check(result.models.length===2 && result.commands.length===0,'DeliveryGapCannotRemoveReadySibling');
 await inert(send,finalA,result,'RetainedChannelRejectsBareCompletionBeforeFirstDelivery');
 for(const mutate of [
  v=>v.deliveryOrdinal='0',v=>v.deliveryOrdinal='01',v=>v.deliveryOrdinal=1,
  v=>v.deliveryOrdinal='18446744073709551616',v=>v.deliveryOrdinal='18446744073709551615',
  v=>v.extra=true,v=>v.fact.extra=true,v=>v.fact.kind='native-incarnation-retirement',
  v=>v.fact.binding={...v.fact.binding,frontend:'999'},v=>v.fact.clock='1',
  v=>v.fact.identity=second,v=>v.fact.request='10',v=>v.fact.sequence='1',
  v=>v.fact.entry='0',v=>v.fact.entryIssuedThrough='0',v=>v.fact.subject='99'
 ]){const value=delivery('1',structuredClone(finalA));mutate(value);await inert(send,value,result,'MalformedOrForeignDeliveryCannotAdvancePrefix');}
 result=await native(send,delivery('1',finalA));
 check(result.models.length===1 && result.models[0].identity===second,'NextDeliveryRemovesOnlyItsSettledActor');ack(result,'1',first);
 const afterFirst=result;result=await native(send,delivery('1',finalA));
 assert.deepEqual(result,afterFirst,'LostProcessingAckRetriesTransportOnly');checks++;
 await inert(send,channel,result,'RepeatActivationCannotResetProcessingPrefix');
 await inert(send,{...channel,binding:{...source.binding,frontend:'999'}},result,'ReplacementCannotResetProcessingPrefix');
 await inert(send,finalB,result,'RetainedChannelRejectsBareCompletionAfterProcessing');
 const foreignDuplicate=delivery('1',{...finalA,binding:{...source.binding,frontend:'999'}});
 await inert(send,foreignDuplicate,result,'ForeignDuplicateCannotObtainAcknowledgment');
 await inert(send,delivery('3',finalB),result,'LaterGapCannotAdvanceProcessingPrefix');
 result=await native(send,delivery('2',finalB));check(result.models.length===0,'ContiguousSecondDeliveryCompletesSibling');ack(result,'2',second);
 await inert(send,seed(),result,'OldSourceCannotRecreateCompletedActor');
 result=await native(send,delivery('1',finalA));check(result.models.length===0,'OlderDuplicateCannotRecreateActor');ack(result,'1',first);
 result=await native(send,delivery('2',finalB));ack(result,'2',second);
 result=await native(send,seed('family:4',105));check(result.models.length===1,'FreshActorSurvivesOriginalNativeClockCutoff');
 // Native completion order and native proof chronology are distinct domains.
 const reverse=await setup();await ready(reverse);
 result=await native(reverse,delivery('1',finalB));ack(result,'1',second);
 result=await native(reverse,delivery('2',finalA));ack(result,'2',first);
 check(result.models.length===0,'OlderNativeFactSettlesAtLaterDeliveryOrdinal');
 await inert(reverse,seed('family:4',103),result,'ReorderedNativeCompletionCannotRewindCutoff');
 // Historical protocol remains usable but cannot be switched after retirement.
 const legacy=await setup(false);await ready(legacy);
 result=await native(legacy,channel);check(result.commands.length===0 && result.models.length===2,'LateActivationIsRefused');
 await inert(legacy,delivery('1',finalA),result,'UnactivatedWrapperHasNoAuthority');
 result=await native(legacy,finalA);check(result.models.length===1 && result.commands.length===0,'OriginalLegacyCompletionRemainsUsable');
 const unknown=worker();await native(unknown,channel);await unknown({kind:'presentation',value:shown});await native(unknown,seed());
 await native(unknown,obsA);result=await native(unknown,delivery('1',finalA));
 check(result.models.length===1 && result.commands.length===0,'ActivationWithoutAdmittedBindingCannotOpenChannel');
 console.log(JSON.stringify({passed:true,checks,nativeAcceptance:false,fullReleaseAccepted:false,
  scope:'Actual compiled immutable Elm processing prefix and commands with synthetic exact native records. Legacy compatibility, loss/retry, gaps, downgrade, foreign bindings, independent chronology and stale-seed refusal. No host/WebKit or physical/native release acceptance.'}));
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
