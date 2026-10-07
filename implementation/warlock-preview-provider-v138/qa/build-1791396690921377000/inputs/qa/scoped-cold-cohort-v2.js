'use strict';
const assert=require('node:assert/strict');const {Elm}=require(process.argv[2]);
let checks=0;function same(a,b,m){assert.deepEqual(a,b,m);checks++;}function check(v,m){assert(v,m);checks++;}
const binding={lifetime:'18446744073709551615',session:'9007199254740993',frontend:'9007199254740994'};
const grant={binding,receiverEpoch:'1',capacity:1065};
const app=Elm.ScopedPreviewPresenterReplay.init();let pending;
app.ports.outgoing.subscribe(v=>{assert(pending);const p=pending;pending=null;p(v);});
function send(kind,value){return new Promise((resolve,reject)=>{assert(!pending);const timer=setTimeout(()=>reject(Error('Original cold Elm timeout')),3000);pending=v=>{clearTimeout(timer);resolve(v);};app.ports.incoming.send({kind,value});});}
const wrap=(event,epoch='1')=>({previewProtocol:3,kind:'native-preview-realm-event',binding,receiverEpoch:epoch,event});
const ids=Array.from({length:256},(_,i)=>String(i+1));
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:ids.map(id=>({id:'family:'+id,domId:'window-'+id,label:'Window',ariaLabel:'Window',detail:'',enabled:true}))};
const catalog=(request='1',rows=ids)=>({protocolVersion:3,kind:'catalog',publication:'1',lease:'1',binding,requestId:request,sequence:request,revision:request,windows:rows.map(incarnation=>({incarnation,application:'fixture',label:'Window '+incarnation,minimized:false}))});
const seed=subject=>({detachProtocol:1,kind:'native-preview-detach-seed',identity:'family:'+subject,binding,receiverEpoch:'1',subject,entry:subject,entryIssuedThrough:'256',requestFloor:'0'});
const completion=subject=>({detachProtocol:1,kind:'native-preview-binding-detach-delivery',binding,receiverEpoch:'1',deliveryOrdinal:subject,event:{kind:'native-preview-actor-detached',identity:'family:'+subject,subject,entry:subject,entryIssuedThrough:'256',requestFloor:'0'}});
const kinds=r=>r.commands.entries.flatMap(row=>row.commands).map(c=>c.kind);
(async()=>{
 await send('grant',grant);await send('presentation',presentation);let r=await send('native',wrap(catalog()));
 same(r.models.length,256,'Original bounded catalog enrolls metadata without synthetic jobs');check(r.models.every(row=>row.model===null));
 const original=structuredClone(r.models);r=await send('native',wrap(catalog('2',[...ids,'257'])));same(r.models,original,'257-row catalog refuses atomically');
 r=await send('quarantine',{binding,receiverEpoch:'1'});same(kinds(r),['reconcile']);same(r.models.length,256);
 r=await send('presentation',{...presentation,publication:'2',lease:'2',popup:[]});same(r.models.length,256,'UI closure retains cold scoped obligations');
 for(const subject of ids){r=await send('native',wrap(seed(subject)));same(kinds(r),['detach-ready'],'Zero floor requires no fabricated lifecycle');same(r.commands.entries[0].commands[0].requestFloor,'0');}
 for(const subject of ids){r=await send('native',wrap(completion(subject)));same(kinds(r),['detach-delivery-ack']);same(r.models.length,256-Number(subject));same(r.realm.processed,subject);same(r.realm.completed,Number(subject));}
 r=await send('native',wrap(completion('1')));same(kinds(r),['detach-delivery-ack'],'Old exact duplicate remains distinguishable at bounded completion capacity');
 r=await send('native',wrap({...completion('1'),event:{...completion('1').event,requestFloor:'1'}}));same(kinds(r),[]);
 r=await send('closed',{binding,receiverEpoch:'1'});check(r.realm.closed);
 r=await send('grant',{...grant,receiverEpoch:'2'});same(r.realm.completed,0);same(r.realm.processed,'0');
 await send('presentation',{...presentation,publication:'3',lease:'3'});r=await send('native',wrap({...catalog('2'),publication:'3',lease:'3'},'2'));same(r.models.length,256,'Same live cold subjects rejoin under greater realm and original global catalog chronology');
 check(r.models.every(row=>row.model===null));
 console.log(JSON.stringify({passed:true,checks,optimizedElm:true,singlePreviewPolicy:true,coldMetadataEntries:256,syntheticScopedFacts:true,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
