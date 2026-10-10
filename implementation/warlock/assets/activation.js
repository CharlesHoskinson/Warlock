'use strict';
// Routes are DOM observations. No pointerId/detail/isTrusted is source authority.
(() => {
  let pending=null, pairing=null, generated=null, quarantine=false, token=0;
  const compat=Object.freeze({kind:'compat'});
  const control=element=>element?.closest?.('[data-surface-control]');
  const owner=item=>item?.closest('.surface-bar,.surface-popup');
  const read=item=>{
    const root=owner(item);
    return item&&root&&Object.freeze({item,root,id:item.dataset.surfaceControl,domId:item.id,
      surface:root.classList.contains('surface-popup')?'popup':'bar',
      publication:root.dataset.publication,lease:root.dataset.lease,
      mode:root.dataset.mode||'closed',enabled:!item.disabled});
  };
  const current=stamp=>{
    const now=read(stamp.item);
    return stamp.item.isConnected&&stamp.root.isConnected&&now&&stamp.enabled&&now.enabled&&
      ['item','root','id','domId','surface','publication','lease','mode'].every(key=>now[key]===stamp[key]);
  };
  const direct=event=>Number.isInteger(event.pointerId)&&event.pointerId>0?
    Object.freeze({kind:'direct',id:event.pointerId}):null;
  const keyboard=event=>{
    if(event.key==='Enter'&&['Enter','NumpadEnter'].includes(event.code)||event.key===' '&&event.code==='Space')
      return Object.freeze({kind:'keyboard',key:event.key,code:event.code});
    return null;
  };
  const same=(a,b)=>a&&b&&a.kind===b.kind&&
    (a.kind==='direct'?a.id===b.id:a.kind==='keyboard'?a.key===b.key&&a.code===b.code:true);
  const matches=(held,item,route)=>held&&held.stamp.item===item&&same(held.route,route);
  const block=event=>{event.preventDefault();event.stopImmediatePropagation();};
  const deliver=stamp=>{
    const value=Object.freeze({surfaceProtocol:2,kind:'surface-action',surface:stamp.surface,
      publication:stamp.publication,lease:stamp.lease,id:stamp.id});
    window.submitSurfaceAction?.(value);
  };
  const quarantineTurn=()=>{
    quarantine=true;const held=++token;
    // OPEN timing boundary: expiry cannot authenticate later detail0 as AT.
    setTimeout(()=>{if(held===token)quarantine=false;},0);
  };
  const begin=(item,route)=>{
    const stamp=read(item);pairing=null;
    if(!stamp?.enabled||!stamp.item.isConnected)return;
    pending=Object.freeze({stamp,route,phase:'pressed',canceled:false});
    quarantine=false;++token;
  };
  const cancel=()=>{
    pairing=null;if(pending)pending=Object.freeze({...pending,canceled:true});
  };
  document.addEventListener('pointerdown',event=>{
    const route=direct(event);pairing=null;
    if(event.button!==0||!route)return;
    const item=control(event.target);begin(item,route);
    if(matches(pending,item,route)&&current(pending.stamp))pairing=pending;
  },true);
  document.addEventListener('mousedown',event=>{
    if(event.button!==0){pairing=null;return;}
    const item=control(event.target),held=pending,paired=pairing;pairing=null;
    // Fresh no-remint refinement: never replace a canceled direct stamp at the
    // same actual node with pub2 merely because compatibility pairing expired.
    if(held?.route.kind==='direct'&&held.stamp.item===item&&
      (held.canceled||!current(held.stamp))){cancel();return;}
    if(paired===held&&held?.route.kind==='direct'&&held.phase==='pressed'&&
      held.stamp.item===item&&current(held.stamp))return;
    begin(item,compat);
  },true);
  const release=(event,route)=>{
    pairing=null;const item=control(event.target),held=pending;
    if(event.button!==0||!matches(held,item,route))return;
    if(held.canceled||!current(held.stamp)){pending=null;quarantineTurn();return;}
    pending=Object.freeze({...held,phase:'released'});
  };
  document.addEventListener('pointerup',event=>release(event,direct(event)),true);
  document.addEventListener('mouseup',event=>release(event,compat),true);
  document.addEventListener('click',event=>{
    pairing=null;const item=control(event.target),root=owner(item);if(!item||!root)return;
    // Unchanged earlier context handler owns native menu detail0 routing.
    if(root.dataset.mode==='menu'&&event.detail===0&&
       (item.dataset.surfaceControl.startsWith('menu:')||item.dataset.surfaceControl==='control:menu-close'))return;
    const held=pending;
    if(held){
      const route=held.route.kind==='keyboard'&&generated===held?held.route:direct(event)||compat;
      if(!matches(held,item,route)||held.phase!=='released'){block(event);return;}
      const valid=!held.canceled&&current(held.stamp)&&
        (held.route.kind!=='keyboard'||document.activeElement===item&&generated===held);
      pending=null;quarantineTurn();block(event);if(valid)deliver(held.stamp);return;
    }
    const stamp=read(item);block(event);
    if(!quarantine&&event.detail===0&&stamp?.enabled&&current(stamp))deliver(stamp);
    // Current atomic detail0 is compatible, never authenticated AT evidence.
  },true);
  const invoke=held=>{
    pending=Object.freeze({...held,phase:'released'});generated=pending;
    try{held.stamp.item.click();}finally{generated=null;}
  };
  const composing=root=>root?.closest?.('[data-input-composing]')?.dataset.inputComposing==='true';
  const qualified=event=>!event.repeat&&!event.isComposing&&!composing(owner(event.target))&&!event.defaultPrevented&&
    !event.ctrlKey&&!event.altKey&&!event.metaKey&&!event.shiftKey;
  const activationKey=event=>event.key==='Enter'||event.key===' ';
  document.addEventListener('keydown',event=>{
    if(event.key==='Enter'&&event.target?.dataset?.surfaceField==='control:search'){
      if(!qualified(event))return;
      const root=owner(event.target),route=keyboard(event);if(!route)return;
      const first=[...root.querySelectorAll('[data-surface-control]')].find(item=>item.dataset.surfaceControl.startsWith('entry:')&&!item.disabled);
      block(event);if(first){first.focus();begin(first,route);}
      return;
    }
    if(event.key==='Tab'){
      const root=event.target?.closest?.('.surface-popup');
      if(!root||root.dataset.mode==='menu'||event.repeat||event.isComposing||
        event.defaultPrevented||event.ctrlKey||event.altKey||event.metaKey)return;
      const items=[...root.querySelectorAll('[data-surface-control]:not(:disabled),[data-surface-field]:not(:disabled)')];
      if(!items.length)return;
      const current=items.indexOf(document.activeElement);
      const next=items[(current+(event.shiftKey?-1:1)+items.length)%items.length];
      block(event);next.focus();next.scrollIntoView({block:'nearest',inline:'nearest'});
      return;
    }
    if(event.key==='Escape'){
      pairing=null;
      const root=event.target?.closest?.('.surface-popup');
      // The popup adapter owns Apps Escape through its matched release and
      // composition guard. Never remint a keydown close through this fallback.
      if(!root||root.dataset.mode==='menu'||root.dataset.mode==='applications'||!qualified(event))return;
      const item=[...root.querySelectorAll('[data-surface-control]')].find(node=>node.dataset.surfaceControl==='control:close');
      const stamp=read(item);block(event);
      if(stamp?.enabled&&current(stamp))deliver(stamp);
      return;
    }
    if(!activationKey(event)){pairing=null;return;}
    const item=control(event.target),root=owner(item);pairing=null;
    if(!item||!root||(root.dataset.mode==='menu'&&
       (item.dataset.surfaceControl.startsWith('menu:')||item.dataset.surfaceControl==='control:menu-close')))return;
    const route=keyboard(event),wasQualified=qualified(event);event.preventDefault();
    if(!route){quarantineTurn();return;}
    const held=pending;
    if(event.repeat&&!event.isComposing&&matches(held,item,route)&&
      document.activeElement===item&&current(held.stamp))return;
    if(!wasQualified||document.activeElement!==item||item.disabled){
      if(matches(held,item,route))cancel();quarantineTurn();return;
    }
    // Keep the current surface alive until the physical release reaches this
    // document. Enter can open another popup or withdraw this one; activation
    // on keydown loses its keyup and poisons later WebKit/GTK key delivery.
    begin(item,route);
  },true);
  document.addEventListener('keyup',event=>{
    if(!activationKey(event)){pairing=null;return;}
    const item=control(event.target),root=owner(item);pairing=null;
    if(!item||!root||(root.dataset.mode==='menu'&&
       (item.dataset.surfaceControl.startsWith('menu:')||item.dataset.surfaceControl==='control:menu-close')))return;
    const route=keyboard(event),wasQualified=qualified(event);event.preventDefault();
    const held=pending;
    if(!route||!matches(held,item,route))return;
    if(!wasQualified||document.activeElement!==item||held.canceled||!current(held.stamp)){
      pending=null;quarantineTurn();return;
    }
    invoke(held);
  },true);
  document.addEventListener('focusout',event=>{
    pairing=null;if(pending?.route.kind==='keyboard'&&event.target===pending.stamp.item)cancel();
  },true);
  document.addEventListener('pointercancel',event=>{
    pairing=null;if(pending&&same(pending.route,direct(event)))cancel();
  },true);
  document.addEventListener('dragstart',event=>{
    pairing=null;if(pending&&control(event.target)===pending.stamp.item)cancel();
  },true);
  document.addEventListener('scroll',cancel,true);
  document.addEventListener('compositionstart',event=>{
    pairing=null;if(pending?.route.kind==='keyboard'&&
      (control(event.target)===pending.stamp.item||document.activeElement===pending.stamp.item))cancel();
  },true);
  window.addEventListener('blur',()=>{cancel();pending=null;quarantineTurn();});
  new MutationObserver(()=>{
    pairing=null;if(pending&&!current(pending.stamp))cancel();
  }).observe(document.body,{subtree:true,childList:true,attributes:true});
})();
