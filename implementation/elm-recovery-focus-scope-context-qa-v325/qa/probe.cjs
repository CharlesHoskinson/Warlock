const fs=require('fs'),vm=require('vm');
function evaluate(path){
 const source=fs.readFileSync(path,'utf8'),checks=[];
 function check(name,action){try{action();checks.push({name,passed:true})}catch(e){checks.push({name,passed:false,error:String(e)})}}
 const assert=(v,message)=>{if(!v)throw Error(message||'Expected contract failed')};
 function setup({selected=true,recovery=false,selectedDisabled=false,recoveryDisabled=false}={}){
  const handlers={},posted=[];let doc;
  const node={dataset:{mode:'menu',publication:'21',lease:'4'},classList:{contains:n=>n==='surface-popup'}};
  function make(id,disabled=false,current=false){return {dataset:{surfaceControl:id},disabled,current,closest:selector=>selector==='[data-surface-control]'?controls[id]:node,focus(){doc.activeElement=this}}}
  const controls={'control:menu-close':make('control:menu-close')};
  if(selected)controls['action:selected']=make('action:selected',selectedDisabled,true);
  if(recovery)controls['control:recovery-refresh']=make('control:recovery-refresh',recoveryDisabled);
  node.querySelector=selector=>selector==='[aria-current="true"]'?controls['action:selected']||null:selector==='[data-surface-control="control:menu-close"]'?controls['control:menu-close']:selector==='[data-surface-control="control:recovery-refresh"]'?controls['control:recovery-refresh']||null:null;
  doc={activeElement:controls['control:menu-close'],querySelector:()=>node,body:{},addEventListener(name,fn){(handlers[name]??=[]).push(fn)}};
  const sandbox={document:doc,window:{addEventListener(){},webkit:{messageHandlers:{native:{postMessage:raw=>posted.push(JSON.parse(raw))}}}},MutationObserver:class{observe(){}},Math};
  vm.runInNewContext(source,sandbox,{filename:path});
  function send(type,fields){const e={isTrusted:true,repeat:false,isComposing:false,defaultPrevented:false,ctrlKey:false,altKey:false,metaKey:false,shiftKey:false,target:doc.activeElement,preventDefault(){this.defaultPrevented=true},stopImmediatePropagation(){this.stopped=true},...fields};for(const fn of handlers[type]||[])fn(e);return e}
  return {doc,controls,posted,send,focus:()=>doc.activeElement.dataset.surfaceControl,tab:shiftKey=>send('keydown',{key:'Tab',shiftKey:!!shiftKey})};
 }
 check('normalCloseSelectedForwardCycle',()=>{const s=setup();s.tab();assert(s.focus()==='action:selected');s.tab();assert(s.focus()==='control:menu-close');assert(s.posted.length===0)});
 check('normalCloseSelectedReverseCycle',()=>{const s=setup();s.tab(true);assert(s.focus()==='action:selected');s.tab(true);assert(s.focus()==='control:menu-close')});
 check('normalEnterKeepsNativeCommandRoute',()=>{const s=setup();s.doc.activeElement=s.controls['action:selected'];const e=s.send('keydown',{key:'Enter'});assert(e.defaultPrevented && s.posted.length===1 && s.posted[0].kind==='surface-menu-navigation' && s.posted[0].key==='Enter' && s.posted[0].publication==='21' && s.posted[0].lease==='4')});
 check('normalImplicitClickStillSuppressed',()=>{const s=setup();const e=s.send('click',{detail:0});assert(e.defaultPrevented && e.stopped && s.posted.length===0)});
 check('recoveryForwardCycleIncludesSelected',()=>{const s=setup({recovery:true});for(const expected of ['action:selected','control:recovery-refresh','control:menu-close']){s.tab();assert(s.focus()===expected,expected)}assert(s.posted.length===0)});
 check('recoveryReverseCycleIncludesSelected',()=>{const s=setup({recovery:true});for(const expected of ['control:recovery-refresh','action:selected','control:menu-close']){s.tab(true);assert(s.focus()===expected,expected)}});
 check('allDisabledCommandsStillReachRecovery',()=>{const s=setup({recovery:true,selectedDisabled:true});s.tab();assert(s.focus()==='control:recovery-refresh');s.tab();assert(s.focus()==='control:menu-close')});
 check('missingSelectionStillReachRecovery',()=>{const s=setup({recovery:true,selected:false});s.tab();assert(s.focus()==='control:recovery-refresh');s.tab(true);assert(s.focus()==='control:menu-close')});
 check('disabledRecoveryExcluded',()=>{const s=setup({recovery:true,recoveryDisabled:true});s.tab();assert(s.focus()==='action:selected');s.tab();assert(s.focus()==='control:menu-close')});
 check('disabledOnlyRetainsDismissal',()=>{const s=setup({recovery:true,recoveryDisabled:true,selectedDisabled:true});s.tab();assert(s.focus()==='control:menu-close')});
 for(const key of ['Enter',' '])check('enabledRecoveryDefaultActivation:'+JSON.stringify(key),()=>{const s=setup({recovery:true});s.doc.activeElement=s.controls['control:recovery-refresh'];const e=s.send('keydown',{key});assert(!e.defaultPrevented && s.posted.length===0);const click=s.send('click',{detail:0});assert(!click.defaultPrevented && !click.stopped)});
 check('recoveryControlPreservesEscapeDismissal',()=>{const s=setup({recovery:true});s.doc.activeElement=s.controls['control:recovery-refresh'];const e=s.send('keydown',{key:'Escape'});assert(e.defaultPrevented && s.posted.length===1 && s.posted[0].key==='Escape')});
 check('modifiedKeysDoNotChangeRecoveryFocus',()=>{const s=setup({recovery:true});s.send('keydown',{key:'Tab',ctrlKey:true});assert(s.focus()==='control:menu-close' && s.posted.length===0)});
 check('blurredScopeTabReturnsClose',()=>{const s=setup({selected:false,recovery:true});s.doc.activeElement=null;const e=s.tab();assert(e.defaultPrevented && s.focus()==='control:menu-close')});
 check('blurredScopeShiftTabReachesRecovery',()=>{const s=setup({selected:false,recovery:true});s.doc.activeElement=null;const e=s.send('keydown',{key:'Unidentified',code:'Tab',shiftKey:true});assert(e.defaultPrevented && s.focus()==='control:recovery-refresh')});
 check('shiftedPhysicalTabWrapsBackToClose',()=>{const s=setup({selected:false,recovery:true});s.doc.activeElement=s.controls['control:recovery-refresh'];const e=s.send('keydown',{key:'Unidentified',code:'Tab',shiftKey:true});assert(e.defaultPrevented && s.focus()==='control:menu-close')});
 check('unrelatedUnknownPhysicalKeyUnchanged',()=>{const s=setup({selected:false,recovery:true});const e=s.send('keydown',{key:'Unidentified',code:'KeyA',shiftKey:true});assert(!e.defaultPrevented && s.focus()==='control:menu-close' && s.posted.length===0)});
 check('composingTabDoesNotChangeScope',()=>{const s=setup({selected:false,recovery:true});const e=s.send('keydown',{key:'Tab',isComposing:true});assert(!e.defaultPrevented && s.focus()==='control:menu-close')});
 check('untrustedTabDoesNotChangeScope',()=>{const s=setup({selected:false,recovery:true});const e=s.send('keydown',{key:'Tab',isTrusted:false});assert(!e.defaultPrevented && s.focus()==='control:menu-close')});
 return {path,passed:checks.every(c=>c.passed),checks};
}
const current=evaluate(process.argv[2]),before=evaluate(process.argv[3]);
const oldNormals=before.checks.filter(c=>c.name.startsWith('normal'));
const counterexamples=before.checks.filter(c=>!c.passed);
const passed=current.passed && oldNormals.every(c=>c.passed) && counterexamples.some(c=>c.name==='missingSelectionStillReachRecovery') && counterexamples.some(c=>c.name.startsWith('enabledRecoveryDefaultActivation:'));
process.stdout.write(JSON.stringify({passed,current,before,counterexamples},null,2)+'\n');process.exitCode=passed?0:1;
