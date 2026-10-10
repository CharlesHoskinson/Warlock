'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const handlers={},windowHandlers={},sent=[],checks=[];
const composing={dataset:{inputComposing:'false'}};
const root={dataset:{mode:'picker',publication:'7',lease:'2'},isConnected:true,
  classList:{contains:()=>true},closest:()=>composing,querySelectorAll:()=>[item]};
const item={id:'family-current',dataset:{surfaceControl:'entry:current'},disabled:false,isConnected:true,
  closest:selector=>selector==='[data-surface-control]'?item:root,
  focus(){if(document.activeElement!==item){emit('focusout',{target:document.activeElement});document.activeElement=item;}},
  click(){emit('click',{detail:0,target:item});}};
const field={dataset:{surfaceField:'control:search'},closest:selector=>selector==='[data-surface-control]'?null:root};
const document={activeElement:item,body:{},addEventListener:(name,fn)=>(handlers[name]??=[]).push(fn)};
const window={submitSurfaceAction:packet=>sent.push(packet),addEventListener:(name,fn)=>(windowHandlers[name]??=[]).push(fn)};
vm.runInNewContext(fs.readFileSync('assets/activation.js','utf8'),{document,window,Object,setTimeout:()=>0,MutationObserver:class{observe(){}}});
function emit(type,extra={}){const event={key:'Enter',code:'Enter',target:item,repeat:false,isComposing:false,defaultPrevented:false,
  preventDefault(){this.defaultPrevented=true;},stopImmediatePropagation(){this.stopped=true;},...extra};
  for(const fn of handlers[type]||[]){fn(event);if(event.stopped)break;}}
const check=(name,condition)=>{assert(condition,name);checks.push(name);};
emit('keydown');check('Enter cannot activate before release',sent.length===0);
emit('keydown',{repeat:true});check('Held Enter repeats do not activate',sent.length===0);
emit('keyup');check('Matched Enter release activates once',sent.length===1&&sent[0].publication==='7'&&sent[0].lease==='2');
emit('keyup');check('Duplicate Enter release has no effect',sent.length===1);
emit('keydown');root.dataset.publication='8';emit('keyup');check('Changed publication cancels the captured activation',sent.length===1);
emit('keydown');root.dataset.lease='3';emit('keyup');check('Changed lease cannot inherit the old activation',sent.length===1);
emit('keydown');emit('compositionstart');emit('keyup');check('Composition cancels a held activation',sent.length===1);
emit('keydown');for(const fn of windowHandlers.blur)fn();emit('keyup');check('Blur cancels without reminting on release',sent.length===1);
emit('keydown');item.disabled=true;emit('keyup');item.disabled=false;check('Disabled control cannot activate',sent.length===1);
emit('keydown');item.isConnected=false;emit('keyup');item.isConnected=true;check('Disconnected control cannot activate its replacement',sent.length===1);
emit('keydown',{repeat:true});emit('keyup');check('An isolated repeat cannot start an activation',sent.length===1);
emit('keydown',{key:' ',code:'Space'});check('Space also waits for release',sent.length===1);emit('keyup',{key:' ',code:'Space'});check('Space still activates exactly once',sent.length===2);
root.dataset.mode='applications';document.activeElement=field;emit('keydown',{target:field});check('Search Enter selects the current entry without launching on press',document.activeElement===item&&sent.length===2);emit('keyup');check('Search Enter launches on its matched entry release',sent.length===3);
document.activeElement=field;emit('keydown',{target:field,code:'NumpadEnter'});emit('keyup',{code:'Enter'});check('Different physical Enter code cannot complete the gesture',sent.length===3);emit('keyup',{code:'NumpadEnter'});check('Numpad Enter retains its actual key identity',sent.length===4);
document.activeElement=field;composing.dataset.inputComposing='true';emit('keydown',{target:field});emit('keyup',{target:field});check('Elm preedit keeps field focus and prevents launch when DOM composing flag is absent',sent.length===4&&document.activeElement===field);
composing.dataset.inputComposing='false';document.activeElement=item;emit('keydown');emit('keyup');check('Fresh activation works after cancellation',sent.length===5);
console.log(JSON.stringify({passed:true,checks,nativeAcceptance:false}));
