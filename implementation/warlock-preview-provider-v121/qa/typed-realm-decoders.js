'use strict';
const assert=require('node:assert/strict');const app=require(process.argv[2]).Elm.NativePreviewRealmReplay.init({flags:null});
let pending,checks=0;app.ports.outgoing.subscribe(v=>{const p=pending;pending=null;p(v);});
const call=(op,value,grant)=>new Promise(resolve=>{assert(!pending);pending=resolve;app.ports.incoming.send({op,value,...(grant?{grant}:{})});});
function same(a,b,message){assert.deepEqual(a,b,message);checks++;}
(async()=>{
 const binding={lifetime:'18446744073709551615',session:'9007199254740993',frontend:'9007199254740995'},receiverEpoch='18446744073709551615';
 const grant={binding,receiverEpoch,capacity:1065};same((await call('grant',grant)).body,grant,'Actual Elm keeps full uint64 native realm');
 for(const bad of [{...grant,receiverEpoch:'0'},{...grant,receiverEpoch:'01'},{...grant,receiverEpoch:'18446744073709551616'},{...grant,receiverEpoch:1},{...grant,capacity:1066},{...grant,capacity:0},{...grant,extra:true},{...grant,binding:{...binding,frontend:'0'}}])same(await call('grant',bad),{accepted:false},'Malformed or unbounded native grant');
 const seed={detachProtocol:1,kind:'native-preview-detach-seed',identity:'family:21',binding,receiverEpoch,subject:'21',entry:'1',entryIssuedThrough:'1',requestFloor:'0'};
 const expected={kind:'detach-ready',binding,receiverEpoch,subject:'21',entry:'1',entryIssuedThrough:'1',requestFloor:'0'};
 same(await call('seed',seed),{accepted:true,body:expected},'Cold scoped readiness preserves native zero request floor');
 for(const bad of [{...seed,kind:'native-actor-retired'},{...seed,identity:'family:22'},{...seed,entry:'2'},{...seed,requestFloor:'00'},{...seed,receiverEpoch:'0'},{...seed,extra:true}])same(await call('seed',bad),{accepted:false},'Distinct scoped seed domain and fields');
 const delivery={detachProtocol:1,kind:'native-preview-binding-detach-delivery',binding,receiverEpoch,deliveryOrdinal:'1',event:{kind:'native-preview-actor-detached',identity:'family:21',subject:'21',entry:'1',entryIssuedThrough:'1',requestFloor:'0'}};
 same(await call('delivery',delivery),{accepted:true,body:{kind:'detach-delivery-ack',binding,receiverEpoch,deliveryOrdinal:'1'}},'Actual Elm final processing ACK preserves exact native realm');
 for(const bad of [{...delivery,kind:'native-actor-retirement-delivery'},{...delivery,deliveryOrdinal:'0'},{...delivery,event:{...delivery.event,kind:'native-actor-retired'}},{...delivery,event:{...delivery.event,identity:'family:22'}},{...delivery,event:{...delivery.event,entry:'2'}},{...delivery,event:{...delivery.event,requestFloor:'01'}}])same(await call('delivery',bad),{accepted:false},'Permanent facts cannot substitute for scoped completion');
 const envelope={previewProtocol:3,kind:'native-preview-realm-event',binding,receiverEpoch,event:{kind:'event',identity:'family:21',event:{kind:'close'}}};
 same(await call('envelope',envelope,grant),{accepted:true,body:envelope.event},'Current exact realm unwraps original input');
 for(const bad of [{...envelope,receiverEpoch:'1'},{...envelope,binding:{...binding,frontend:'1'}},{...envelope,previewProtocol:2},{...envelope,kind:'preview-commands'},{...envelope,extra:true}])same(await call('envelope',bad,grant),{accepted:false},'Old/foreign realm cannot reach preview reducer');
 console.log(JSON.stringify({passed:true,checks,optimizedElm:true,fullUint64:true,actualPolicyIntegration:false,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
