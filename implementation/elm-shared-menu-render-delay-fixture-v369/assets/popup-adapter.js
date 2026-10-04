'use strict';
const app = Elm.Popup.init({node:document.getElementById('app')});
const post = value => window.webkit.messageHandlers.native.postMessage(JSON.stringify(value));
window.receivePresentation = value => {
  app.ports.presentation.send(value);
  requestAnimationFrame(() => requestAnimationFrame(() => {
    const node=document.querySelector('.surface-popup');
    if (node?.dataset.publication===value.publication && node.dataset.lease===value.lease) {
      const acknowledge=()=>{const current=document.querySelector('.surface-popup');if(current?.dataset.publication===value.publication && current.dataset.lease===value.lease) post({surfaceProtocol:2,kind:'presentation-applied',publication:value.publication,lease:value.lease});};
      if(window.elmHostQA && node.dataset.mode==='menu'){post({kind:'menu-ack-delay-fixture',publication:value.publication,lease:value.lease,delayMs:600});setTimeout(acknowledge,600);}else acknowledge();
    }
  }));
};
window.receiveFocus = value => requestAnimationFrame(() => {
  const node=document.querySelector('.surface-popup');
  if(value.surfaceProtocol!==2 || value.kind!=='surface-focus' || !node || node.dataset.publication!==value.publication || node.dataset.lease!==value.lease) return;
  const focused=[];
  for (const target of value.targets) {
    const control=document.getElementById(target);
    if(control && node.contains(control) && !control.disabled){control.focus();if(document.activeElement===control) focused.push(target);}
  }
  post({surfaceProtocol:2,kind:'focus-applied',publication:value.publication,lease:value.lease,targets:focused});
});
app.ports.actions.subscribe(post);
post({surfaceProtocol:2,kind:'presentation-ready'});

if (window.elmHostQA) {
  let last='';
  const observe=()=>requestAnimationFrame(()=>{
    const buttons=[...document.querySelectorAll('button')].map(button=>{
      const r=button.getBoundingClientRect();return {id:button.id,label:button.textContent,accessibleName:button.getAttribute('aria-label'),disabled:button.disabled,x:r.x,y:r.y,width:r.width,height:r.height};
    });
    const node=document.querySelector('.surface-bar,.surface-popup');
    const body={publication:node?.dataset.publication||null,lease:node?.dataset.lease||null,buttons,focus:document.activeElement?.id||'',text:document.body.innerText};
    const current=JSON.stringify(body);if(current!==last){last=current;post({kind:'surface-report',body});}
  });
  document.addEventListener('scroll',observe,true);
  new MutationObserver(observe).observe(document.body,{subtree:true,childList:true,attributes:true});
  document.addEventListener('focusin',observe);observe();
}
