// Run against a temporary copy of T07's host with patches/host-input.patch applied.
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const {createHost}=await import(pathToFileURL(process.argv[2]));
const listeners=new Map(), sent=[];
globalThis.location={origin:'https://example.test'};
globalThis.addEventListener=(k,f)=>listeners.set(k,f);
globalThis.removeEventListener=k=>listeners.delete(k);
const frames=Object.fromEntries(['controller','bar','popup'].map(id=>[id,{postMessage:p=>sent.push({id,...p})}]));
const host=createHost({frames});host.start();
let s=host.getSnapshot(), original=s.windows[0];
for (const [zone,geometry,mode] of [['left',{x:10,y:66,width:620,height:644},'snapped'],['bottom-right',{x:640,y:390,width:630,height:320},'snapped'],['maximize',{x:10,y:66,width:1260,height:644},'maximized']]) {
  assert(host.dispatchInput({kind:'placement',epoch:s.epoch,windowId:original.id,incarnation:original.incarnation,zone,geometry}));
  const w=host.getSnapshot().windows[0];assert.equal(w.placementMode,mode);assert.deepEqual(w.restoreGeometry,original.geometry);
}
assert.equal(host.dispatchInput({kind:'placement',epoch:s.epoch,windowId:original.id,incarnation:'999',zone:'left',geometry:{x:10,y:66,width:620,height:644}}),false);
host.dispatchInput({kind:'pointer',action:'start',windowId:original.id});
host.dispatchInput({kind:'pointer',action:'cancel',windowId:original.id});
assert.equal(host.getSnapshot().windows[0].placementMode,'maximized');
const receive=listeners.get('message');
const emit=(id,payload)=>receive({origin:location.origin,source:frames[id],data:{bridgeVersion:1,epoch:s.epoch,frameId:id,kind:'native',payload:JSON.stringify(payload)}});
emit('controller',{protocolVersion:3,kind:'host-ready'});
emit('controller',{viewProtocol:1,kind:'view-commit',projection:{revision:'1',frame:{publication:'1',lease:'7',mode:'applications',bar:[],popup:[]}},focus:[],requests:[]});
emit('popup',{surfaceProtocol:2,kind:'presentation-applied',publication:'1',lease:'7'});
assert.equal(host.dispatchInput({kind:'outside-press',epoch:s.epoch,publication:'1',lease:'6'}),false);
assert(host.dispatchInput({kind:'outside-press',epoch:s.epoch,publication:'1',lease:'7'}));
assert(sent.some(p=>p.id==='controller' && p.payload?.method==='receiveDismiss' && p.payload.value==='7'));
host.reset();
assert.equal(host.dispatchInput({kind:'outside-press',epoch:s.epoch,publication:'1',lease:'7'}),false);
host.destroy();console.log('Patched host: placement, cancel, stale identity and dismissal checks passed');
