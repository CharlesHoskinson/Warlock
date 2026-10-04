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
