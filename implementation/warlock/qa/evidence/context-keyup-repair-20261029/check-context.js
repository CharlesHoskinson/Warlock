'use strict';
// Mock DOM component test only. Neither synthetic event trust nor native proof is established.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const source=process.argv[2];if(!source)throw Error('expected private context.js');
const bytes=fs.readFileSync(source),sha=crypto.createHash('sha256').update(bytes).digest('hex');
assert.strictEqual(sha,'e843e72479a6e499a99f4369f145530e8e097c576e7d08926a6a912dbd50bc8d');
const handlers={},windowHandlers={},sent=[],checks=[];let mutation,focused=true;
const root={dataset:{mode:'bar',publication:'7',lease:'2'},isConnected:true,classList:{contains:()=>false},contains:x=>x===item};
const item={id:'entry',dataset:{surfaceControl:'bar:pin:peer'},disabled:false,isConnected:true,closest:s=>s==='[data-surface-control]'?item:root};
const other={id:'other',dataset:{surfaceControl:'bar:pin:other'},disabled:false,isConnected:true,closest:s=>s==='[data-surface-control]'?other:root};
const document={activeElement:item,body:{},hasFocus:()=>focused,querySelector:()=>null,addEventListener:(n,f)=>(handlers[n]??=[]).push(f)};
const window={webkit:{messageHandlers:{native:{postMessage:s=>sent.push(JSON.parse(s))}}},addEventListener:(n,f)=>(windowHandlers[n]??=[]).push(f)};
vm.runInNewContext(bytes.toString(),{document,window,MutationObserver:class{constructor(fn){mutation=fn}observe(){}},requestAnimationFrame:()=>0});
function emit(type,props={}){const e={key:'ContextMenu',code:'ContextMenu',target:item,isTrusted:true,repeat:false,isComposing:false,defaultPrevented:false,ctrlKey:false,altKey:false,metaKey:false,shiftKey:false,button:2,buttons:2,clientX:10,clientY:10,preventDefault(){this.defaultPrevented=true},stopImmediatePropagation(){this.stopped=true},...props};for(const f of handlers[type]||[]){f(e);if(e.stopped)break}return e}
function check(name,condition){assert(condition,name);checks.push(name)}
const down=(opts={})=>emit('keydown',opts),up=(opts={})=>emit('keyup',opts), reset=()=>{document.activeElement=item;focused=true;item.disabled=false;item.isConnected=true;root.isConnected=true;item.id='entry';item.dataset.surfaceControl='bar:pin:peer';root.dataset.publication='7';root.dataset.lease='2'};
let n=sent.length;let e=down();check('Menu press does not emit',sent.length===n&&e.defaultPrevented);up();check('Menu matching release emits once',sent.length===++n&&sent[n-1].trigger==='keyboard'&&sent[n-1].publication==='7'&&sent[n-1].lease==='2');up();check('duplicate release silent',sent.length===n);
down({key:'F10',code:'F10',shiftKey:true});up({key:'Shift',code:'ShiftLeft'});up({key:'F10',code:'F10',shiftKey:false});check('Shift may release before F10',sent.length===++n);
down();up({key:'F10',code:'F10'});up();check('wrong key cancels',sent.length===n);
down();up({code:'Other'});check('wrong code cancels',sent.length===n);
for(const modifier of ['ctrlKey','altKey','metaKey']){down();up({[modifier]:true});up();check(modifier+' release rejects',sent.length===n)}
down();up({target:other});check('wrong source cancels',sent.length===n);
down();document.activeElement=other;up();reset();check('focus change rejects',sent.length===n);
down();focused=false;up();reset();check('document focus loss rejects',sent.length===n);
down();root.dataset.publication='8';up();reset();check('publication replacement rejects',sent.length===n);
down();root.dataset.lease='3';up();reset();check('lease replacement rejects',sent.length===n);
down();item.dataset.surfaceControl='bar:pin:other';up();reset();check('control identity replacement rejects',sent.length===n);
down();item.id='replacement';up();reset();check('DOM identity replacement rejects',sent.length===n);
down();item.disabled=true;up();reset();check('disabled rejects',sent.length===n);
down();item.isConnected=false;up();reset();check('removed control rejects',sent.length===n);
down();root.isConnected=false;up();reset();check('removed root rejects',sent.length===n);
down();up({isTrusted:false});up();check('untrusted release consumes gesture',sent.length===n);
down({isTrusted:false});up();check('untrusted press cannot start',sent.length===n);
down();emit('focusout');up();check('focusout cancels',sent.length===n);
down();windowHandlers.blur[0]();up();check('blur cancels',sent.length===n);
for(const type of ['scroll','dragstart','compositionstart']){down();emit(type);up();if(type==='compositionstart')emit('compositionend');check(type+' cancels',sent.length===n)}
down();mutation([{type:'attributes',target:root}]);up();check('root mutation cancels even if stamp returns',sent.length===n);
down();mutation([{type:'childList',removedNodes:[item]}]);up();check('removal mutation cancels even if reattached',sent.length===n);
down();down({key:'a',code:'KeyA'});up();check('conflicting key cancels',sent.length===n);
down();down({repeat:true});up();check('held repeat never remints',sent.length===++n);up();check('repeat cannot emit twice',sent.length===n);
down({repeat:true});up();check('isolated sticky repeat still requires native fresh proof',sent.length===++n);
down();emit('mousedown',{button:2,buttons:2});up();check('pointer conflict cancels keyboard',sent.length===n);emit('mouseup',{button:2,buttons:0});check('pointer right click still posts once',sent.length===++n&&sent[n-1].trigger==='pointer'&&sent[n-1].x===10&&sent[n-1].y===10);
console.log(JSON.stringify({passed:true,checks,nativeAcceptance:false,scope:'mock DOM component only; isTrusted and native authority are not proven'}));
