import assert from 'node:assert/strict';
import {createHost} from './index.js';
const events=[], listeners={};
globalThis.location={origin:'https://test.invalid'};
globalThis.addEventListener=(name,fn)=>listeners[name]=fn;
globalThis.removeEventListener=()=>{};
const frames=Object.fromEntries(['controller','bar','popup'].map(id=>[id,{postMessage:p=>events.push(p)}]));
const host=createHost({frames}); host.start();
const emit=(id,packet)=>listeners.message({origin:location.origin,source:frames[id],data:{bridgeVersion:1,epoch:host.getSnapshot().epoch,frameId:id,kind:'native',payload:JSON.stringify(packet)}});
const row=id=>({id,domId:id,label:id,enabled:true});
let n=0;
function frame(mode, popup=[]) { const publication=String(++n),lease='1'; emit('controller',{viewProtocol:1,kind:'view-commit',projection:{revision:'1',frame:{publication,lease,mode,bar:[row('bar:pin:warlock-editor')],popup:popup.map(row)}},focus:[],requests:[]}); for (const id of ['bar','popup']) emit(id,{surfaceProtocol:2,kind:'presentation-applied',publication,lease}); }
const tick=()=>new Promise(r=>setTimeout(r,30));
const actions=()=>events.filter(e=>e.frameId==='controller'&&e.payload?.method==='receiveAction').map(e=>e.payload.value.action);
emit('controller',{protocolVersion:3,kind:'host-ready'});
for (const trigger of ['pointer','keyboard']) {
  frame('closed');
  const anchor=trigger==='pointer'?{x:320,y:180}:{x:170,y:240};
  const promise=host.invoke('window-menu',{windowId:'1',incarnation:'1',trigger,anchor});
  await tick();
  assert.deepEqual({...actions().at(-1)}, {surfaceProtocol:2,kind:'surface-context',surface:'bar',publication:String(n),lease:'1',id:'bar:pin:warlock-editor',trigger,...anchor});
  frame('picker',['family:1']); await tick();
  assert.equal(actions().at(-1).id,'family:1'); assert.equal(actions().at(-1).trigger,trigger);
  assert.equal(actions().at(-1).x,anchor.x); assert.equal(actions().at(-1).y,anchor.y);
  frame('menu'); await tick(); assert.equal(await promise,true);
  assert.equal(host.getSnapshot().popupPlacement.x,anchor.x); assert.equal(host.getSnapshot().popupPlacement.y,anchor.y);
}
frame('closed');
assert.equal(await host.invoke('window-menu',{windowId:'2',incarnation:'2',trigger:'pointer',anchor:{x:2,y:3}}),false);
assert.equal(await host.invoke('window-menu',{windowId:'1',incarnation:'1',trigger:'pointer',anchor:{x:NaN,y:3}}),false);
const stale=host.invoke('window-menu',{windowId:'1',incarnation:'1',trigger:'pointer',anchor:{x:200,y:200}}); await tick();
host.dispatchInput({kind:'window',action:'focus',windowId:'2',incarnation:'2',epoch:host.getSnapshot().epoch});
frame('picker',['family:1']); await tick(); assert.equal(await stale,false);
host.destroy(); console.log('Captured pointer and keyboard anchors, picker propagation, and stale target checks passed.');
