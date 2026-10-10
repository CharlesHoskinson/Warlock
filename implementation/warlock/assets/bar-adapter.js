'use strict';
const app = Elm.Bar.init({node:document.getElementById('app')});
window.submitSurfaceAction = value => app.ports.requestAction.send(value);
const post = value => window.webkit.messageHandlers.native.postMessage(JSON.stringify(value));
let selectedIdentity=null, observedActions=null;
const actionsNode=()=>document.querySelector('.surface-actions');
const revealSelection=(restoreOnly=false)=>{
  const actions=actionsNode();
  if(!actions||!document.hasFocus()||!selectedIdentity)return;
  const control=[...actions.querySelectorAll('[data-surface-control]')].find(item=>item.dataset.surfaceControl===selectedIdentity&&!item.disabled);
  if(!control)return;
  if(restoreOnly&&document.activeElement===control)return;
  if(document.activeElement!==control)control.focus({preventScroll:true});
  control.scrollIntoView({block:'nearest',inline:'nearest'});
};
const resizeObserver=window.ResizeObserver&&new ResizeObserver(()=>requestAnimationFrame(()=>revealSelection()));
const observeActions=()=>{
  const actions=actionsNode();
  if(actions===observedActions)return;
  resizeObserver?.disconnect();observedActions=actions;if(actions)resizeObserver?.observe(actions);
};
document.addEventListener('focusin',event=>{
  const control=event.target.closest?.('[data-surface-control]');
  if(control?.closest('.surface-actions')){selectedIdentity=control.dataset.surfaceControl;revealSelection();}
  else if(event.target!==document.body&&event.target!==document.documentElement)selectedIdentity=null;
});
// Keep the view's logical selection through a popup grab. Restoration still
// requires real document focus and a currently rendered enabled control.
window.addEventListener('focus',()=>revealSelection(true));
window.addEventListener('resize',()=>requestAnimationFrame(()=>revealSelection()));
document.addEventListener('keydown',event=>{
  const trace=phase=>{if(window.elmHostQA && event.key==='Home')post({kind:'context-input-report',phase,key:event.key,repeat:event.repeat,composing:event.isComposing,prevented:event.defaultPrevented,trusted:event.isTrusted,id:document.activeElement?.dataset?.surfaceControl||null,targetId:event.target?.dataset?.surfaceControl||null,anchor:selectedIdentity,documentFocused:document.hasFocus()});};
  trace('bar-navigation');
  if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key)||event.defaultPrevented||event.isComposing||event.ctrlKey||event.altKey||event.metaKey||event.shiftKey)return;
  const actions=event.target.closest?.('.surface-actions');if(!actions)return;
  const items=[...actions.querySelectorAll('[data-surface-control]:not(:disabled)')],current=items.indexOf(document.activeElement);if(current<0)return;
  const index=event.key==='Home'?0:event.key==='End'?items.length-1:Math.max(0,Math.min(items.length-1,current+(event.key==='ArrowRight'?1:-1)));
  event.preventDefault();event.stopImmediatePropagation();items[index].focus({preventScroll:true});
  selectedIdentity=items[index].dataset.surfaceControl;revealSelection();
  trace('bar-navigated');
},true);
document.addEventListener('wheel',event=>{
  const actions=event.target.closest?.('.surface-actions');if(!actions||actions.scrollWidth<=actions.clientWidth||!event.deltaY||event.deltaX)return;
  const unit=event.deltaMode===1?parseFloat(getComputedStyle(actions).fontSize):event.deltaMode===2?actions.clientWidth:1;
  actions.scrollLeft+=event.deltaY*unit;event.preventDefault();
},{passive:false});
window.receiveAnnouncement = value => app.ports.announcements.send(value);
window.receivePresentation = value => {
  app.ports.presentation.send(value);
  requestAnimationFrame(() => requestAnimationFrame(() => {
    const node=document.querySelector('.surface-bar');
    if (node?.dataset.publication===value.publication && node.dataset.lease===value.lease) {
      observeActions();revealSelection(true);
      post({surfaceProtocol:2,kind:'presentation-applied',publication:value.publication,lease:value.lease});
    }
  }));
};
window.receiveFocus = value => requestAnimationFrame(() => {
  const node=document.querySelector('.surface-bar');
  if(value.surfaceProtocol!==2 || value.kind!=='surface-focus' || !node || node.dataset.publication!==value.publication || node.dataset.lease!==value.lease) return;
  const focused=[];
  for (const target of value.targets) {
    const control=document.getElementById(target);
    if(control && node.contains(control) && !control.disabled){control.focus();control.scrollIntoView({block:'nearest',inline:'nearest'});if(document.activeElement===control){selectedIdentity=control.dataset.surfaceControl;focused.push(target);}}
  }
  post({surfaceProtocol:2,kind:'focus-applied',publication:value.publication,lease:value.lease,targets:focused});
});
app.ports.actions.subscribe(post);
post({surfaceProtocol:2,kind:'presentation-ready'});

if (window.elmHostQA) {
  let last='';
  const observe=()=>requestAnimationFrame(()=>{
    const buttons=[...document.querySelectorAll('button')].map(button=>{
      const r=button.getBoundingClientRect();return {id:button.id,identity:button.dataset.surfaceControl,label:button.textContent,accessibleName:button.getAttribute('aria-label'),disabled:button.disabled,x:r.x,y:r.y,width:r.width,height:r.height};
    });
    const node=document.querySelector('.surface-bar,.surface-bar');
    const status=document.querySelector('[role="status"]'),box=status?.getBoundingClientRect(),style=status&&getComputedStyle(status);
    const feedback=status?{text:status.textContent,accessibleName:status.getAttribute('aria-label'),live:status.getAttribute('aria-live'),atomic:status.getAttribute('aria-atomic'),x:box.x,y:box.y,width:box.width,height:box.height,clip:style.clipPath,display:style.display}:null;
    const actions=actionsNode(),actionBox=actions?.getBoundingClientRect();
    const palette={background:getComputedStyle(document.body).backgroundColor,foreground:getComputedStyle(document.body).color};
    const active=document.activeElement,activeStyle=active&&getComputedStyle(active),activeBox=active?.getBoundingClientRect();
    const focusStyle=activeStyle?{color:activeStyle.color,background:activeStyle.backgroundColor,outlineColor:activeStyle.outlineColor,outlineWidth:activeStyle.outlineWidth,outlineOffset:activeStyle.outlineOffset,x:activeBox.x,y:activeBox.y,width:activeBox.width,height:activeBox.height}:null;
    const body={announcements:[...document.querySelectorAll(".shell-announcement")].map(n=>({text:n.textContent,sequence:n.querySelector("[data-announcement-sequence]")?.dataset.announcementSequence||null,correlation:n.querySelector("[data-announcement-correlation]")?.dataset.announcementCorrelation||null,live:n.getAttribute("aria-live")})),motionProfile:node?.dataset.motion||null,motionAnimations:document.getAnimations().length,palette,focusStyle,publication:node?.dataset.publication||null,lease:node?.dataset.lease||null,buttons,feedback,focus:document.activeElement?.id||'',documentFocused:document.hasFocus(),selectionAnchor:selectedIdentity,text:document.body.innerText,fontSize:getComputedStyle(document.body).fontSize,theme:document.documentElement.dataset.theme||null,textScale:document.documentElement.dataset.textScale||null,effects:document.documentElement.dataset.effects||null,reducedTransparency:document.documentElement.dataset.reducedTransparency||null,viewportWidth:innerWidth,scrollLeft:actions?.scrollLeft||0,scrollWidth:actions?.scrollWidth||0,clientWidth:actions?.clientWidth||0,actions:actionBox?{x:actionBox.x,y:actionBox.y,width:actionBox.width,height:actionBox.height}:null};
    const current=JSON.stringify(body);if(current!==last){last=current;post({kind:'surface-report',body});}
  });
  document.addEventListener('scroll',observe,true);
  new MutationObserver(observe).observe(document.body,{subtree:true,childList:true,attributes:true});
  document.addEventListener('focusin',observe);observe();
  window.addEventListener('resize',observe);
  window.addEventListener('focus',observe);window.addEventListener('blur',observe);
}
