'use strict';
const app = Elm.Main.init({node:document.getElementById('app'),flags:Boolean(window.elmHostQA)});
const post = value => window.webkit.messageHandlers.native.postMessage(JSON.stringify(value));
window.receiveBatchDisposition = value => app.ports.nativeBatchDispositions.send(value);
window.receiveTopology = value => app.ports.nativeViews.send(value);
window.receiveNative = value => app.ports.nativeEvents.send(value);
window.receiveAction = value => app.ports.rendererActions.send(value);
window.receiveDismiss = lease => app.ports.nativeDismissals.send(lease);
window.receiveFocus = value => requestAnimationFrame(() => {
  const node=document.querySelector('.surface-bar');
  if(value.surfaceProtocol!==2 || value.kind!=='surface-focus' || !node || node.dataset.publication!==value.publication || node.dataset.lease!==value.lease) return;
  for (const target of value.targets) document.getElementById(target)?.focus();
});
app.ports.surfaceCommits.subscribe(post);
if(window.elmHostQA) app.ports.inspections.subscribe(post);
post({protocolVersion:3,kind:'host-ready'});

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

window.receiveReflow = value => app.ports.nativeReflows.send(value);
