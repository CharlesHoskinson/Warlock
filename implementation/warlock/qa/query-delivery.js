'use strict';
// Exercise the actual adapter with controlled port/rAF ordering. This isolates
// transport; real WebKit/keyboard/AT/pixels are qualified by the native runner.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const frames=[],posts=[];let subscriber,hook=()=>{},node=null;
const document={getElementById:()=>({}),querySelector:s=>s==='.surface-popup'?node:null,
  addEventListener:()=>{},hasFocus:()=>false,activeElement:{},body:{},documentElement:{}};
const window={addEventListener:()=>{},webkit:{messageHandlers:{native:{postMessage:s=>posts.push(JSON.parse(s))}}}};
const app={ports:{requestAction:{send:()=>{}},presentation:{send:v=>hook(v)},
  announcements:{send:()=>{}},previewCommands:{subscribe:()=>{}},actions:{subscribe:f=>subscriber=f}}};
vm.runInNewContext(fs.readFileSync(require('path').join(__dirname,'../assets/popup-adapter.js'),'utf8'),
  {Elm:{Popup:{init:()=>app}},document,window,requestAnimationFrame:f=>frames.push(f),console});
const packet=(query,pub='1',lease='1')=>({surfaceProtocol:2,kind:'surface-query',surface:'popup',publication:pub,lease,id:'control:search',query});
const present=(pub,lease='1')=>{
  node={dataset:{publication:pub,lease,mode:'applications'},querySelectorAll:()=>[],contains:()=>false};
  window.receivePresentation({surfaceProtocol:2,mode:'applications',publication:pub,lease});
};
const drain=()=>{while(frames.length)frames.shift()();};
posts.length=0; // Initial presentation-ready is a separate startup handshake.
hook=()=>subscriber(packet('editor'));present('1');
assert.equal(posts.length,0,'Retained query must wait for presentation acknowledgement');
subscriber(packet('editors'));drain();
assert.deepEqual(posts.map(p=>p.kind),['presentation-applied','surface-query']);
assert.equal(posts[1].query,'editors','Only latest observational query is sent');
posts.length=0;subscriber(packet('direct'));assert.equal(posts[0].query,'direct');
posts.length=0;hook=()=>subscriber(packet('old','2'));present('2');
hook=()=>subscriber(packet('current','3'));present('3');drain();
assert.deepEqual(posts.map(p=>[p.kind,p.publication,p.query]),[['presentation-applied','3',undefined],['surface-query','3','current']]);
posts.length=0;hook=()=>subscriber(packet('retired','4'));present('4');
hook=()=>{};present('5','2');subscriber(packet('old-lease','5','1'));drain();
assert.deepEqual(posts.map(p=>p.kind),['presentation-applied'],'Retired publication/lease query must not replay');
posts.length=0;const action={surfaceProtocol:2,kind:'surface-action',publication:'5',lease:'2',surface:'popup',id:'entry:warlock-editor'};
subscriber(action);assert.deepEqual(posts,[action],'Effect actions keep their original forwarding/admission');
posts.length=0;present('6','2');subscriber(packet('new','6','2'));subscriber(packet('obsolete','5','2'));drain();
assert.equal(posts.at(-1).query,'new','Obsolete query cannot replace current queued query');
posts.length=0;present('7','2');subscriber(packet('retained','7','2'));present('7','2');drain();
assert.deepEqual(posts.filter(p=>p.kind==='surface-query').map(p=>p.query),['retained'],'Duplicate presentation must preserve the pending query and send it once');
console.log(JSON.stringify({passed:true,scope:'Actual adapter transport only; native admission unchanged',checks:8}));
