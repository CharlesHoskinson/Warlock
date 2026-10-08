'use strict';
const app = Elm.Popup.init({node:document.getElementById('app')});
window.submitSurfaceAction = value => app.ports.requestAction.send(value);
const post = value => window.webkit.messageHandlers.native.postMessage(JSON.stringify(value));
let pickerSelection=null,observedPicker=null;
const pickerNode=()=>document.querySelector('.surface-popup[data-mode="picker"]');
const rememberPicker=control=>{
  const node=control?.closest?.('.surface-popup[data-mode="picker"]');
  if(node&&!control.disabled&&control.dataset.surfaceControl)pickerSelection={lease:node.dataset.lease,identity:control.dataset.surfaceControl};
};
const revealPicker=(force=false)=>{
  const node=pickerNode();
  if(!node||!document.hasFocus()||pickerSelection?.lease!==node.dataset.lease)return;
  const control=[...node.querySelectorAll('[data-surface-control]')].find(item=>item.dataset.surfaceControl===pickerSelection.identity&&!item.disabled);
  if(!control)return;
  if(document.activeElement!==control){control.focus({preventScroll:true});force=true;}
  if(force)control.scrollIntoView({block:'nearest',inline:'nearest'});
};
const pickerResize=window.ResizeObserver&&new ResizeObserver(()=>requestAnimationFrame(()=>revealPicker(true)));
const observePicker=()=>{
  const node=pickerNode();if(node===observedPicker)return;
  pickerResize?.disconnect();observedPicker=node;
  if(node){pickerResize?.observe(node);const controls=node.querySelector('.surface-controls');if(controls)pickerResize?.observe(controls);}
};
document.addEventListener('focusin',event=>{
  if(event.target.closest?.('.surface-popup[data-mode="picker"]')){rememberPicker(event.target);revealPicker(true);}
  else if(event.target!==document.body&&event.target!==document.documentElement)pickerSelection=null;
});
window.addEventListener('focus',()=>revealPicker());
window.addEventListener('resize',()=>requestAnimationFrame(()=>revealPicker(true)));
document.addEventListener('keydown',event=>{
  if(!['ArrowUp','ArrowDown','Home','End'].includes(event.key)||event.isComposing||event.defaultPrevented||event.ctrlKey||event.altKey||event.metaKey||event.shiftKey)return;
  const node=event.target.closest?.('.surface-popup[data-mode="picker"]');if(!node)return;
  const items=[...node.querySelectorAll('[data-surface-control]:not(:disabled)')],current=items.indexOf(document.activeElement);if(current<0)return;
  const index=event.key==='Home'?0:event.key==='End'?items.length-1:Math.max(0,Math.min(items.length-1,current+(event.key==='ArrowDown'?1:-1)));
  event.preventDefault();event.stopImmediatePropagation();items[index].focus({preventScroll:true});rememberPicker(items[index]);revealPicker(true);
},true);
window.receivePresentation = value => {
  app.ports.presentation.send(value);
  requestAnimationFrame(() => requestAnimationFrame(() => {
    const node=document.querySelector('.surface-popup');
    if (node?.dataset.publication===value.publication && node.dataset.lease===value.lease) {
      observePicker();revealPicker();
      post({surfaceProtocol:2,kind:'presentation-applied',publication:value.publication,lease:value.lease});
    }
  }));
};
window.receiveFocus = value => requestAnimationFrame(() => {
  const node=document.querySelector('.surface-popup');
  if(value.surfaceProtocol!==2 || value.kind!=='surface-focus' || !node || node.dataset.publication!==value.publication || node.dataset.lease!==value.lease) return;
  const focused=[];
  for (const target of value.targets) {
    const control=document.getElementById(target);
    if(control && node.contains(control) && !control.disabled){control.focus();control.scrollIntoView({block:'nearest',inline:'nearest'});if(document.activeElement===control){rememberPicker(control);focused.push(target);}}
  }
  post({surfaceProtocol:2,kind:'focus-applied',publication:value.publication,lease:value.lease,targets:focused});
});
app.ports.actions.subscribe(post);
// Forward only current-surface key observations. Elm owns candidate order,
// selection, ordinal bounds and mutation decisions; this is not a global chord
// journal and cannot attest to input arriving before native popup readiness.
let switcherTerminal=null;
document.addEventListener('keydown',event=>{
  const node=event.target?.closest?.('.surface-popup');
  const dismissal=event.key==='Escape' && ['switcher','overview','picker'].includes(node?.dataset.mode);
  if(!node || (node.dataset.mode!=='switcher' && !dismissal) || event.isComposing ||
     event.defaultPrevented || event.ctrlKey || event.metaKey) return;
  const id=event.key==='Tab'?(event.shiftKey?'control:reverse':'control:forward'):
    event.key==='ArrowRight'?'control:forward':event.key==='ArrowLeft'?'control:reverse':
    event.key==='Enter'?'control:commit':event.key==='Escape'?'control:close':null;
  if(!id || ((event.key==='Enter'||event.key==='Escape') && event.repeat)) return;
  event.preventDefault();event.stopImmediatePropagation();
  const control=[...node.querySelectorAll('[data-surface-control]')].find(row=>row.dataset.surfaceControl===id);
  if(!control || control.disabled) return;
  const packet=Object.freeze({surfaceProtocol:2,kind:'surface-action',surface:'popup',
    publication:node.dataset.publication,lease:node.dataset.lease,id});
  // Terminal keys retain the popup until their real keyup. Withdrawing it on
  // keydown loses the native release and leaves the compositor's repeat guard
  // held. A changed presentation cancels this gesture instead of reminting it.
  if(event.key==='Enter'||event.key==='Escape') switcherTerminal={node,key:event.key,packet};
  else app.ports.requestAction.send(packet);
},true);
document.addEventListener('keyup',event=>{
  const held=switcherTerminal;
  if(!held || held.key!==event.key) return;
  switcherTerminal=null;event.preventDefault();event.stopImmediatePropagation();
  if(event.isComposing || event.ctrlKey || event.metaKey || !held.node.isConnected ||
    (held.node.dataset.mode!=='switcher' && !(held.key==='Escape' && ['overview','picker'].includes(held.node.dataset.mode))) || held.node.dataset.publication!==held.packet.publication ||
    held.node.dataset.lease!==held.packet.lease || !held.node.contains(event.target)) return;
  app.ports.requestAction.send(held.packet);
},true);
window.addEventListener('blur',()=>{switcherTerminal=null;});
post({surfaceProtocol:2,kind:'presentation-ready'});

if (window.elmHostQA) {
  let last='';
  const observe=()=>requestAnimationFrame(()=>{
    const buttons=[...document.querySelectorAll('button')].map(button=>{
      const r=button.getBoundingClientRect();return {id:button.id,identity:button.dataset.surfaceControl,label:button.textContent,accessibleName:button.getAttribute('aria-label'),disabled:button.disabled,x:r.x,y:r.y,width:r.width,height:r.height};
    });
    const node=document.querySelector('.surface-bar,.surface-popup');
    const fields=[...document.querySelectorAll('[data-surface-field]')].map(field=>({id:field.id,value:field.value,accessibleName:field.getAttribute('aria-label'),disabled:field.disabled}));
    const body={publication:node?.dataset.publication||null,lease:node?.dataset.lease||null,buttons,fields,focus:document.activeElement?.id||'',documentFocused:document.hasFocus(),fontSize:getComputedStyle(document.body).fontSize,viewportWidth:innerWidth,viewportHeight:innerHeight,scrollTop:node?.scrollTop||0,scrollHeight:node?.scrollHeight||0,text:document.body.innerText};
    const current=JSON.stringify(body);if(current!==last){last=current;post({kind:'surface-report',body});}
  });
  document.addEventListener('scroll',observe,true);
  new MutationObserver(observe).observe(document.body,{subtree:true,childList:true,attributes:true});
  document.addEventListener('focusin',observe);observe();
  window.addEventListener('resize',observe);window.addEventListener('focus',observe);window.addEventListener('blur',observe);
}

window.receiveNativePreview = value => app.ports.nativePreviews.send(value);
window.receiveNativePreviewBatch = values => { for (const value of values) app.ports.nativePreviews.send(value); };
let previewControlOrdinal=0n;
app.ports.previewCommands.subscribe(value => {
  for (const entry of value) for (const command of entry.commands) {
    if (previewControlOrdinal===18446744073709551615n) return;
    previewControlOrdinal+=1n;
    post({previewProtocol:2,kind:"preview-commands",controlOrdinal:String(previewControlOrdinal),
      entries:[{identity:entry.identity,commands:[command]}]});
  }
});

if (window.elmPreviewQA) {
  const inspectNativePreviewQA=()=>{
    const images=[...document.querySelectorAll('img.preview-image')].slice(0,2).map(image=>{
      const rect=image.getBoundingClientRect();return {uri:image.src,complete:image.complete,naturalWidth:image.naturalWidth,naturalHeight:image.naturalHeight,width:Math.round(rect.width),height:Math.round(rect.height)};
    });
    post({kind:'preview-image-report',images});
    const fallbacks=[...document.querySelectorAll('.window-preview')].filter(node=>node.querySelector('.preview-title')).slice(0,2).map(node=>({
      state:node.dataset.previewState,title:node.querySelector('.preview-title').textContent,
      icons:[...node.querySelectorAll('img.preview-icon')].map(image=>{const rect=image.getBoundingClientRect();return {uri:image.src,complete:image.complete,naturalWidth:image.naturalWidth,naturalHeight:image.naturalHeight,width:Math.round(rect.width),height:Math.round(rect.height)};})
    }));
    post({kind:'preview-fallback-report',fallbacks});
  };
  // The private native owner may read the same DOM while an offscreen renderer
  // has no next presentation frame. This observer supplies no policy inputs.
  window.inspectNativePreviewQA=inspectNativePreviewQA;
  const reportImages=()=>requestAnimationFrame(inspectNativePreviewQA);
  document.addEventListener('load',reportImages,true);
  new MutationObserver(reportImages).observe(document.getElementById('app'),{subtree:true,childList:true,attributes:true});
}
