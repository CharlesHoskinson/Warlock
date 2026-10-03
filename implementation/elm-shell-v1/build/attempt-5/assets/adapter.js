'use strict';
const app = Elm.Main.init({node:document.getElementById('app'), flags:null});
const bridge = window.webkit.messageHandlers.native;
app.ports.nativeRequests.subscribe(message => bridge.postMessage(JSON.stringify(message)));
window.receiveNative = message => app.ports.nativeEvents.send(message);
// Fixture DOM/frame readiness only; GPU execution remains separately qualified.
const observer = new MutationObserver(() => {
  const entries = document.querySelectorAll('[data-incarnation]');
  console.log('fixture DOM entries:', entries.length);
  if (entries.length !== 2) return;
  observer.disconnect();
  requestAnimationFrame(() => {
    console.log('fixture first animation frame');
    requestAnimationFrame(() => {
      console.log('fixture second animation frame');
      bridge.postMessage(JSON.stringify({protocolVersion:1, kind:'render-report',
        body:{families:entries.length, secureContext:window.isSecureContext,
          actionsDisabled:[...entries].every(x=>x.querySelector('button').disabled),
          webgpuExposed:!!navigator.gpu}}));
    });
  });
});
observer.observe(document.getElementById('app'), {subtree:true, childList:true});
