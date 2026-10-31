import assert from 'node:assert/strict';
import {createHost} from './index.js';
const events=[], listeners={}; globalThis.location={origin:'https://test.invalid'};globalThis.addEventListener=(name,fn)=>listeners[name]=fn;globalThis.removeEventListener=()=>{};
const frames=Object.fromEntries(['controller','bar','popup'].map(id=>[id,{postMessage:p=>events.push(p)}]));
const host=createHost({frames});host.start();
const emit=(id,packet)=>listeners.message({origin:location.origin,source:frames[id],data:{bridgeVersion:1,epoch:host.getSnapshot().epoch,frameId:id,kind:'native',payload:JSON.stringify(packet)}});
const wait=()=>new Promise(r=>setTimeout(r,30));
const actions=()=>events.filter(e=>e.frameId==='controller'&&e.payload?.method==='receiveAction').map(e=>e.payload.value.action.id);
const row=id=>({id,domId:id,label:id,ariaLabel:id,detail:'',enabled:true,focusOnly:false});
let pub=0;
function frame(mode) { const publication=String(++pub),lease='1';emit('controller',{viewProtocol:1,kind:'view-commit',projection:{revision:'1',frame:{surfaceProtocol:2,publication,lease,mode,bar:[row('bar:switcher'),row('bar:pin:warlock-editor')],popup:mode==='switcher'?['control:forward','control:reverse','control:commit','control:close'].map(row):[]}},focus:[],requests:[]});return {publication,lease}; }
function applied(id,stamp){emit(id,{surfaceProtocol:2,kind:'presentation-applied',...stamp});}
emit('controller',{protocolVersion:3,kind:'host-ready'}); let stamp=frame('closed');applied('bar',stamp);
host.dispatchInput({kind:'switcher',action:'next'});host.dispatchInput({kind:'switcher',action:'activate'});await wait();assert.deepEqual(actions(),['bar:switcher']);stamp=frame('switcher');await wait();assert.deepEqual(actions(),['bar:switcher']);applied('popup',stamp);await wait();assert.deepEqual(actions(),['bar:switcher','control:commit']);
stamp=frame('closed');applied('bar',stamp);host.dispatchInput({kind:'switcher',action:'previous'});host.dispatchInput({kind:'switcher',action:'cancel'});await wait();stamp=frame('switcher');applied('popup',stamp);await wait();assert.equal(actions().at(-1),'control:reverse');stamp=frame('switcher');applied('popup',stamp);await wait();assert.equal(actions().at(-1),'control:close');
// A popup-owned terminal action closes the admitted switcher independently of the chord queue.
stamp=frame('closed');applied('bar',stamp);host.dispatchInput({kind:'switcher',action:'next'});await wait();stamp=frame('switcher');applied('popup',stamp);await wait();
stamp=frame('closed');applied('bar',stamp);assert.equal(host.dispatchInput({kind:'switcher',action:'activate'}),false);assert.equal(host.dispatchInput({kind:'switcher',action:'next'}),true);await wait();assert.equal(actions().at(-1),'bar:switcher');
stamp=frame('closed');applied('bar',stamp);const beforeSnap=actions().length;assert.equal(await host.invoke('snap'),false);assert.equal(actions().length,beforeSnap);assert.equal(host.getSnapshot().presentation.mode,'closed');
host.dispatchInput({kind:'switcher',action:'next'});host.dispatchInput({kind:'switcher',action:'activate'});host.dispatchInput({kind:'viewport',width:1440,height:844});host.reset();await wait();assert.equal(host.getSnapshot().output.height,844);assert.ok(host.getSnapshot().windows.filter(w=>w.workspace==='1').every(w=>w.geometry.y+w.geometry.height<=834));
const snap=host.getSnapshot();const pinned=snap.windows[0];host.reset({...snap,activeWorkspace:'2',windows:snap.windows.map(w=>({...w,focused:false,...(w.id===pinned.id?{pinned:true,placementMode:'floating'}:{})}))});assert.equal(host.dispatchInput({kind:'window',action:'focus',epoch:host.getSnapshot().epoch,incarnation:pinned.incarnation,windowId:pinned.id}),true);assert.equal(host.getSnapshot().activeWorkspace,'2');assert.equal(host.getSnapshot().windows.find(w=>w.id===pinned.id).focused,true);
host.destroy();console.log('Quick switcher release/cancel, epoch cancellation, measured viewport and pinned focus checks passed.');
