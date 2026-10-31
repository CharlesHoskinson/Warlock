import assert from 'node:assert/strict';
import {edgeZone, zoneGeometry, placeInZone} from './pointer.js';
assert.equal(edgeZone(3,30,1000,700),'top-left');
assert.equal(edgeZone(999,680,1000,700),'bottom-right');
assert.equal(edgeZone(500,2,1000,700),'maximize');
assert.equal(edgeZone(500,500,1000,700),null);
const snapshot={epoch:3,windows:[{id:'1',incarnation:'7',geometry:{x:30,y:80,width:400,height:300}}],workArea:{x:0,y:50,width:1000,height:650}};
const input=[];
const host={getSnapshot:()=>snapshot,dispatchInput(event){input.push(event);return true;}};
for (const zone of ['left','bottom-right','maximize']) {
  assert(placeInZone(host,'1','7',zone));
  assert.deepEqual(input.at(-1),{kind:'placement',epoch:3,windowId:'1',incarnation:'7',zone,geometry:zoneGeometry(zone,snapshot.workArea)});
}
assert.equal(placeInZone(host,'1','8','right'),false);
assert.equal(placeInZone(host,'1','7','invalid'),false);
assert.equal(input.length,3);
console.log('Placement inputs, zones and incarnation checks passed');

// Exercise gesture admission and capture loss without depending on an OS chord.
const {installPointer} = await import('./pointer.js');
class Root extends EventTarget {
  constructor() { super(); this.ownerDocument={defaultView:new EventTarget()}; }
  getBoundingClientRect() { return {left:0,top:0,width:1000,height:700}; }
}
const root=new Root(), trace=[];
const state={epoch:1,output:{width:1000,height:700},workArea:{x:0,y:50,width:1000,height:650},windows:[{id:'1',incarnation:'7'}]};
const gestureHost={getSnapshot:()=>state,dispatchInput:e=>{trace.push(e);return true;},subscribe:()=>()=>{}};
const stop=installPointer({root,host:gestureHost});
const win={dataset:{windowId:'1'},contains:()=>true};
const bar={};
const makeTarget=(kind)=>({setPointerCapture(){},matches:s=>kind==='title' && s==='button.stage-title',closest(s){
  if(s==='[data-window-id]') return win;
  if(s==='.stage-titlebar') return bar;
  if(s==='[disabled], [aria-disabled="true"]') return null;
  if(s==='button, a, input, select, textarea, [role="button"]') return kind==='blank'?null:this;
  return null;
}});
const send=(type,target,x,y,options={})=>{const e=new Event(type,{cancelable:true});Object.defineProperties(e,{target:{value:target},pointerId:{value:1},button:{value:0},altKey:{value:false},clientX:{value:x},clientY:{value:y},...Object.fromEntries(Object.entries(options).map(([k,v])=>[k,{value:v}]))}); root.dispatchEvent(e);return e;};
const title=makeTarget('title'), action=makeTarget('action');
send('pointerdown',action,50,50);send('pointermove',action,90,90);send('pointerup',action,90,90);assert.equal(trace.length,0);
send('pointerdown',title,50,50);send('pointerup',title,50,50);assert.equal(trace.length,0);
send('pointerdown',title,50,50);send('pointermove',title,90,90);send('pointerup',title,90,90);
assert.deepEqual(trace.map(x=>x.action),['start','move','end']);
assert.equal(send('click',title,90,90).defaultPrevented,true);
trace.length=0;
send('pointerdown',title,50,50);send('pointermove',title,90,90);send('lostpointercapture',title,90,90);send('pointerup',title,90,90);
assert.deepEqual(trace.map(x=>x.action),['start','move','cancel']);
trace.length=0;
send('pointerdown',title,50,50);send('pointermove',title,90,90);send('pointerup',title,1,699);
assert.deepEqual(trace.map(x=>x.action||x.kind),['start','move','cancel','placement']);assert.equal(trace.at(-1).zone,'bottom-left');
stop();console.log('Titlebar gesture, action exclusion, capture loss and corner snap checks passed');
