'use strict';
(() => {
  let pressed = null;
  const owner = element => element?.closest('.surface-bar,.surface-popup');
  const control = element => element?.closest('[data-surface-control]');
  const stamp = node => node && ({publication:node.dataset.publication,lease:node.dataset.lease});
  const same = (a,b) => a && b && a.publication===b.publication && a.lease===b.lease;
  const post = value => window.webkit.messageHandlers.native.postMessage(JSON.stringify(value));
  const diagnostic=(phase,event)=>{if(window.elmHostQA)post({kind:'context-input-report',phase,button:event.button,buttons:event.buttons,trusted:event.isTrusted,id:control(event.target)?.dataset.surfaceControl||null});};
  const invoke = (item,node,trigger,x,y) => post({surfaceProtocol:2,kind:'surface-context',
    surface:node.classList.contains('surface-popup')?'popup':'bar',...stamp(node),
    id:item.dataset.surfaceControl,trigger,x,y});
  document.addEventListener('contextmenu',event => { if(owner(event.target)) event.preventDefault(); });
  document.addEventListener('mousedown',event => {
    diagnostic('press',event);
    pressed=null;
    if(!event.isTrusted || event.button!==2 || event.buttons!==2) return;
    const item=control(event.target),node=owner(item);
    if(!item || !node || item.disabled) return;
    pressed={item,node,shown:stamp(node),x:event.clientX,y:event.clientY};
  },true);
  document.addEventListener('mousemove',event => {
    if(pressed && ((event.clientX-pressed.x)**2+(event.clientY-pressed.y)**2>25 || event.buttons!==2)) pressed=null;
  },true);
  document.addEventListener('mouseup',event => {
    diagnostic('release',event);
    const pending=pressed;pressed=null;
    if(!event.isTrusted || event.button!==2 || event.buttons!==0 || !pending) return;
    const item=control(event.target),node=owner(item);
    if(item!==pending.item || node!==pending.node || !same(pending.shown,stamp(node)) || item.disabled) return;
    if((event.clientX-pending.x)**2+(event.clientY-pending.y)**2>25) return;
    event.preventDefault();invoke(item,node,'pointer',Math.round(event.clientX),Math.round(event.clientY));
  },true);
  window.addEventListener('blur',()=>{pressed=null;});
  for(const name of ['scroll','dragstart']) document.addEventListener(name,()=>{pressed=null;},true);
  document.addEventListener('keydown',event => {
    if(!event.isTrusted || event.repeat || event.isComposing || event.defaultPrevented || event.ctrlKey || event.altKey || event.metaKey) return;
    const item=control(document.activeElement),node=owner(item);
    if(!item || !node) return;
    if(event.key==='ContextMenu' || (event.key==='F10' && event.shiftKey)) {
      if(item.disabled) return;
      event.preventDefault();invoke(item,node,'keyboard',0,0);return;
    }
    if(node.dataset.mode==='menu') {
      if(event.key==='Tab'){
        event.preventDefault();
        const selected=node.querySelector('[aria-current="true"]'),close=node.querySelector('[data-surface-control="control:menu-close"]');
        (item===close?selected:close)?.focus();return;
      }
      if(event.key==='Enter' && item.dataset.surfaceControl==='control:menu-close'){
        event.preventDefault();post({surfaceProtocol:2,kind:'surface-action',surface:'popup',...stamp(node),id:'control:menu-close'});return;
      }
      if(['Escape','ArrowUp','ArrowDown','Home','End','Enter'].includes(event.key)) {
        event.preventDefault();post({surfaceProtocol:2,kind:'surface-menu-navigation',surface:'popup',...stamp(node),key:event.key});
      }
    }
  },true);
  new MutationObserver(() => {
    const node=document.querySelector('.surface-popup[data-mode="menu"]');
    const selected=node?.querySelector('[aria-current="true"]');
    if(selected && !selected.disabled && document.activeElement!==selected) selected.focus();
  }).observe(document.body,{subtree:true,childList:true,attributes:true});
})();
