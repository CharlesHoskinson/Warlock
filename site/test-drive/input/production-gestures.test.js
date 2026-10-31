import assert from 'node:assert/strict';
import {createHost} from '../host/index.js';
import {installPointer} from './pointer.js';
import {mountLegend} from './legend.js';
globalThis.location={origin:'https://example.test'};
globalThis.addEventListener=()=>{}; globalThis.removeEventListener=()=>{};
const frames=Object.fromEntries(['controller','bar','popup'].map(id=>[id,{postMessage(){}}]));
const host=createHost({frames}); host.start();
class Element extends EventTarget {
  constructor(tag='div') { super(); this.tag=tag; this.children=[]; this.dataset={}; this.textContent=''; this.ownerDocument=doc; }
  append(...nodes){this.children.push(...nodes);} replaceChildren(...nodes){this.children=nodes;}
  contains(){return true;} getBoundingClientRect(){const o=host.getSnapshot().output; return {left:0,top:0,width:o.width,height:o.height};}
}
const doc={defaultView:new EventTarget(),createElement:tag=>new Element(tag),createTextNode:text=>({textContent:text})}; globalThis.document=doc;
const root=new Element(), initial=host.getSnapshot().windows.find(w=>w.focused);
const target={dataset:{windowId:initial.id},contains:()=>true}; const bar={};
const title={setPointerCapture(){},matches:s=>s==='button.stage-title',closest:s=>s==='[data-window-id]'?target:s==='.stage-titlebar'?bar:s==='button, a, input, select, textarea, [role="button"]'?title:null};
function send(type,x,y){const e=new Event(type,{cancelable:true}); for(const [k,v] of Object.entries({target:title,pointerId:1,button:0,altKey:false,clientX:x,clientY:y})) Object.defineProperty(e,k,{value:v}); root.dispatchEvent(e);}
const stop=installPointer({root,host});
send('pointerdown',100,100);send('pointermove',140,130);send('pointerup',140,130);
let win=host.getSnapshot().windows.find(w=>w.id===initial.id); assert.equal(win.placementMode,'floating'); assert.equal(win.geometry.x,initial.geometry.x+40);
send('pointerdown',140,130);send('pointermove',180,160);send('pointercancel',180,160);
win=host.getSnapshot().windows.find(w=>w.id===initial.id); assert.equal(win.geometry.x,initial.geometry.x+40);
send('pointerdown',140,130);send('pointermove',180,160);send('pointerup',1,host.getSnapshot().output.height/2);
win=host.getSnapshot().windows.find(w=>w.id===initial.id); assert.equal(win.placementMode,'snapped');
const legend=new Element(); const unmount=mountLegend(legend,host);
function find(node,label){if(node.tag==='button' && node.textContent===label)return node; for(const child of node.children||[]){const result=find(child,label);if(result)return result;} }
find(legend,'Move right').dispatchEvent(new Event('click'));
win=host.getSnapshot().windows.find(w=>w.id===initial.id); assert.equal(win.placementMode,'floating'); assert.equal(win.geometry.x,initial.geometry.x+72);
const width=win.geometry.width; find(legend,'Make wider').dispatchEvent(new Event('click'));
assert.equal(host.getSnapshot().windows.find(w=>w.id===initial.id).geometry.width,width+32);
unmount(); stop(); host.destroy();
// Legend follows observed inventory transitions and leaves its button usable.
let listener; const row={active:'default',defaultAvailable:true,alternateAvailable:true,defaultChord:'SUPER + ALT + SPACE',alternateChord:'SUPER + CTRL + ALT + SPACE'};
const state={services:{shortcutInventory:{applications:row}}}; const calls=[];
const fake={getSnapshot:()=>state,subscribe:fn=>(listener=fn,()=>{}),dispatchInput:input=>calls.push(input)};
const keyLegend=new Element(); const disposeLegend=mountLegend(keyLegend,fake);
function spanContaining(node,fragment){if(node.tag==='span' && node.textContent.includes(fragment))return node; for(const child of node.children||[]){const result=spanContaining(child,fragment);if(result)return result;}}
assert(spanContaining(keyLegend,'SUPER + ALT + SPACE: Applications'));
row.active='alternate'; listener(state); assert(spanContaining(keyLegend,'SUPER + CTRL + ALT + SPACE: Applications'));
row.active='keep'; listener(state); assert(spanContaining(keyLegend,'No Warlock chord active: Applications'));
find(keyLegend,'Applications').dispatchEvent(new Event('click')); assert.deepEqual(calls.at(-1),{kind:'shortcut',route:'applications'});
disposeLegend(); console.log('Production host pointer and legend gesture checks passed');
