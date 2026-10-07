'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const posted=[],received=[];let emit;
const app={ports:{
 requestAction:{send(){}},presentation:{send(){}},nativePreviews:{send:v=>received.push(v)},
 actions:{subscribe(){}},previewCommands:{subscribe:callback=>{emit=callback;}}
}};
const context=vm.createContext({
 Elm:{Popup:{init:()=>app}},document:{getElementById:()=>({})},
 window:{webkit:{messageHandlers:{native:{postMessage:value=>posted.push(JSON.parse(value))}}}},
 requestAnimationFrame:()=>{},console
});
vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),context);
posted.length=0;
emit([{identity:'family:21',commands:[{kind:'acknowledge',job:{},sequence:'3'}]},
 {identity:'family:21',commands:[{kind:'retire-ready',subject:'21'}]}]);
assert.deepEqual(posted.map(v=>v.controlOrdinal),['1','2']);
assert.deepEqual(posted.map(v=>v.entries[0].commands[0].kind),['acknowledge','retire-ready']);
assert(posted.every(v=>v.previewProtocol===2 && v.entries.length===1 && v.entries[0].commands.length===1));
emit([{identity:'family:22',commands:[]},{identity:'family:22',commands:[{kind:'cancel'},{kind:'release'}]}]);
assert.deepEqual(posted.map(v=>v.controlOrdinal),['1','2','3','4']);
assert.deepEqual(posted.slice(2).map(v=>v.entries[0].commands[0].kind),['cancel','release']);
context.window.receiveNativePreviewBatch([{kind:'receipt',sequence:'1'},{kind:'receipt',sequence:'2'}]);
assert.deepEqual(received.map(v=>v.sequence),['1','2']);
vm.runInContext('previewControlOrdinal=18446744073709551614n',context);
emit([{identity:'family:21',commands:[{kind:'acknowledge'},{kind:'retire-ready'}]}]);
assert.equal(posted.at(-1).controlOrdinal,'18446744073709551615');assert.equal(posted.length,5);
emit([{identity:'family:22',commands:[{kind:'cancel'}]}]);assert.equal(posted.length,5);
console.log(JSON.stringify({passed:true,checks:10,nativeAcceptance:false,fullReleaseAccepted:false,
 scope:'Actual popup adapter executed in a Node VM with mock DOM/ports; same-port cleanup-before-readiness order, singleton native rows, lossless ordinals and exhaustion; real WebKit/native delivery remains unqualified.'}));
