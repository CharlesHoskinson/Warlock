'use strict';
(() => {
  let pressed = null;
  const owner = element => element?.closest('.surface-bar,.surface-popup');
  const control = element => element?.closest('[data-surface-control]');
  const stamp = node => node && ({publication:node.dataset.publication,lease:node.dataset.lease});
  const same = (a,b) => a && b && a.publication===b.publication && a.lease===b.lease;
  const post = value => window.webkit.messageHandlers.native.postMessage(JSON.stringify(value));
  const diagnostic=(phase,event)=>{if(window.elmHostQA)post({kind:'context-input-report',phase,button:event.button,buttons:event.buttons,key:event.key,repeat:event.repeat,composing:event.isComposing,prevented:event.defaultPrevented,trusted:event.isTrusted,id:control(event.target)?.dataset.surfaceControl||null});};
  const invoke = (item,node,trigger,x,y) => post({surfaceProtocol:2,kind:'surface-context',
    surface:node.classList.contains('surface-popup')?'popup':'bar',...stamp(node),
    id:item.dataset.surfaceControl,trigger,x,y});
  // Keyboard menu activation uses the native proof route. WebKit's implicit
  // zero-detail button click must not also invoke Elm's pointer-click handler.
  document.addEventListener('click',event => {
    const item=control(event.target),node=owner(item);
    const nativeOperation=item&&(item.dataset.surfaceControl.startsWith('menu:')||item.dataset.surfaceControl==='control:menu-close');
    if(node?.dataset.mode==='menu' && nativeOperation && event.detail===0){event.preventDefault();event.stopImmediatePropagation();}
  },true);
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
    diagnostic('key',event);
    const contextKey=event.key==='ContextMenu' || (event.key==='F10' && event.shiftKey);
    // WebKit can retain repeat=true after the key release went to a grabbed
    // popup. Context requests still need the native fresh physical-key proof;
    // its held-key guard rejects genuine repeats across both surfaces.
    if(!event.isTrusted || (event.repeat&&!contextKey) || event.isComposing || event.defaultPrevented || event.ctrlKey || event.altKey || event.metaKey) return;
    const menu=document.querySelector('.surface-popup[data-mode="menu"]');
    // Dismissal belongs to the live popup, including when a disabled row blurs focus.
    if(event.key==='Escape' && menu){
      event.preventDefault();post({surfaceProtocol:2,kind:'surface-menu-navigation',surface:'popup',...stamp(menu),key:'Escape'});return;
    }
    const item=control(document.activeElement),node=owner(item);
    if(!item || !node) return;
    if(contextKey) {
      if(item.disabled) return;
      event.preventDefault();invoke(item,node,'keyboard',0,0);return;
    }
    if(node.dataset.mode==='menu') {
      if(event.key==='Tab'){
        event.preventDefault();
        const selected=node.querySelector('[aria-current="true"]'),close=node.querySelector('[data-surface-control="control:menu-close"]');
        const utilities=[...node.querySelectorAll('[data-surface-control^="control:"]:not(:disabled)')].filter(control=>control!==close);
        const stops=[close,selected,...utilities].filter(control=>control&&!control.disabled);
        const current=stops.indexOf(item);
        stops[(current+(event.shiftKey?-1:1)+stops.length)%stops.length]?.focus();revealMenu(false,true);return;
      }
      if(event.key==='Enter' && item.dataset.surfaceControl==='control:menu-close'){
        event.preventDefault();post({surfaceProtocol:2,kind:'surface-menu-navigation',surface:'popup',...stamp(node),key:'Close'});return;
      }
      if(['Escape','ArrowUp','ArrowDown','Home','End','Enter'].includes(event.key)) {
        // Utility activation belongs to its own current surface action. Enter
        // must never apply the independently selected window operation.
        if(event.key==='Enter'&&!item.dataset.surfaceControl.startsWith('menu:'))return;
        if(['ArrowUp','ArrowDown','Home','End'].includes(event.key))revealMenu(false,true);
        event.preventDefault();post({surfaceProtocol:2,kind:'surface-menu-navigation',surface:'popup',...stamp(node),key:event.key});
      }
    }
  },true);
  let observedMenu=null,previousSelection=null,previousLayout=null;
  const revealMenu=(select=false,force=false)=>{
    const node=document.querySelector('.surface-popup[data-mode="menu"]');
    if(node!==observedMenu){
      menuResize?.disconnect();observedMenu=node;previousSelection=null;previousLayout=null;
      if(node){menuResize?.observe(node);const controls=node.querySelector('.surface-controls');if(controls)menuResize?.observe(controls);}
    }
    const selected=node?.querySelector('[aria-current="true"]'),changed=selected!==previousSelection;
    previousSelection=selected;
    const layout=node&&[node.clientWidth,node.clientHeight,node.scrollHeight].join(':');
    force=force||changed||layout!==previousLayout;previousLayout=layout;
    if(!node||!document.hasFocus())return;
    // The selected operation comes only from the current Elm projection.
    const focused=control(document.activeElement);
    // Preserve a current enabled utility reached by Tab across unrelated
    // publications; an actual operation-selection change still owns focus.
    const retainedUtility=focused&&node.contains(focused)&&!focused.disabled&&focused.dataset.surfaceControl.startsWith('control:');
    if(select&&selected&&!selected.disabled&&(changed||!retainedUtility)&&document.activeElement!==selected){selected.focus({preventScroll:true});force=true;}
    const revealed=control(document.activeElement);
    if(force&&revealed&&node.contains(revealed)&&!revealed.disabled)revealed.scrollIntoView({block:'nearest',inline:'nearest'});
  };
  const menuResize=window.ResizeObserver&&new ResizeObserver(()=>requestAnimationFrame(()=>revealMenu(false,true)));
  new MutationObserver(()=>revealMenu(true)).observe(document.body,{subtree:true,childList:true,attributes:true});
  window.addEventListener('resize',()=>requestAnimationFrame(()=>revealMenu(false,true)));
  window.addEventListener('focus',()=>revealMenu(true,true));
})();
