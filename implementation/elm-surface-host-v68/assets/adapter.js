'use strict';
const app = Elm.Main.init({node:document.getElementById('app')});
const post = value => window.webkit.messageHandlers.native.postMessage(JSON.stringify(value));
window.receiveNative = value => app.ports.nativeEvents.send(value);
window.receiveAction = value => app.ports.rendererActions.send(value);
window.receiveDismiss = lease => app.ports.nativeDismissals.send(lease);
window.receiveFocus = targets => requestAnimationFrame(() => {
  for (const target of targets) document.getElementById(target)?.focus();
});
app.ports.surfaceCommits.subscribe(post);
post({protocolVersion:3,kind:'host-ready'});

if (window.elmHostQA) {
  let last='';
  const observe=()=>requestAnimationFrame(()=>{
    const buttons=[...document.querySelectorAll('button')].map(button=>{
      const r=button.getBoundingClientRect();return {id:button.id,label:button.textContent,disabled:button.disabled,x:r.x,y:r.y,width:r.width,height:r.height};
    });
    const body={buttons,focus:document.activeElement?.id||'',text:document.body.innerText};
    const current=JSON.stringify(body);if(current!==last){last=current;post({kind:'surface-report',body});}
  });
  new MutationObserver(observe).observe(document.getElementById('app'),{subtree:true,childList:true,attributes:true});
  document.addEventListener('focusin',observe);observe();
}
