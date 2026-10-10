'use strict';
// Exercise the shipped listener order, including the activation fallback.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const handlers={},windowHandlers={},sent=[];
const composing={dataset:{inputComposing:'false'}};
const node={dataset:{mode:'applications',publication:'7',lease:'2'},isConnected:true,
  closest:()=>composing,contains:target=>target===field||target===close,
  querySelectorAll:()=>[close]};
const close={dataset:{surfaceControl:'control:close'},id:'close',disabled:false,isConnected:true,
  closest:()=>node};
const field={dataset:{surfaceField:'control:search'},id:'launcher-search',closest:()=>node};
const document={body:{},documentElement:{},activeElement:field,getElementById:()=>null,
  querySelector:()=>node,addEventListener:(name,fn)=>(handlers[name]??=[]).push(fn)};
const ports=new Proxy({},{get:(_,name)=>({send:packet=>{if(name==='requestAction')sent.push(packet);},subscribe:()=>{}})});
const window={addEventListener:(name,fn)=>(windowHandlers[name]??=[]).push(fn),
  webkit:{messageHandlers:{native:{postMessage:()=>{}}}}};
const context={Elm:{Popup:{init:()=>({ports})}},window,document,requestAnimationFrame:()=>{},
  MutationObserver:class{observe(){}},setTimeout:()=>0,Object};
vm.createContext(context);
for(const file of ['popup-adapter.js','activation.js'])vm.runInContext(fs.readFileSync('assets/'+file,'utf8'),context);
const emit=(type,extra={})=>{
  const event={key:'Escape',target:field,repeat:false,isComposing:false,defaultPrevented:false,
    preventDefault(){this.defaultPrevented=true;},stopImmediatePropagation(){this.stopped=true;},...extra};
  for(const fn of handlers[type]||[]){fn(event);if(event.stopped)break;}
};
const checks=[];
const check=(name,condition)=>{assert(condition,name);checks.push(name);};
emit('keydown');check('Current Apps remains open until release',sent.length===0);
emit('keyup');check('Matched release sends exactly one current close',sent.length===1&&sent[0].id==='control:close'&&sent[0].publication==='7'&&sent[0].lease==='2');
emit('keyup');check('Duplicate release does not close again',sent.length===1);
node.dataset.publication='8';node.dataset.lease='3';emit('keydown');emit('keyup');
check('Reopened Apps has a fresh release gesture',sent.length===2&&sent[1].lease==='3');
emit('keydown');node.dataset.publication='9';emit('keyup');check('Changed publication cancels without reminting',sent.length===2);
emit('keydown');node.dataset.lease='4';emit('keyup');check('Retired lease cancels',sent.length===2);
emit('keydown',{repeat:true});emit('keyup');check('Held repeat cannot start another dismissal',sent.length===2);
emit('keydown',{isComposing:true});emit('keyup');check('Composition Escape is not popup dismissal',sent.length===2);
composing.dataset.inputComposing='true';emit('keydown');composing.dataset.inputComposing='false';emit('keyup');
check('Elm preedit guard holds even if the DOM event omits composing',sent.length===2);
emit('keydown');emit('compositionstart');emit('keyup');check('Starting composition cancels a held dismissal',sent.length===2);
emit('keydown');for(const fn of windowHandlers.blur)fn();emit('keyup');check('Lost document focus cancels a held dismissal',sent.length===2);
emit('keydown');node.isConnected=false;emit('keyup');check('Disconnected surface cannot close its successor',sent.length===2);node.isConnected=true;
emit('keydown',{altKey:true});emit('keyup');check('Modified Escape is not ordinary Apps dismissal',sent.length===2);
emit('keydown');emit('keyup');check('Cancellation does not poison the next fresh gesture',sent.length===3);
console.log(JSON.stringify({passed:true,checks,nativeAcceptance:false}));
