'use strict';
const app = Elm.Popup.init({node:document.getElementById('app')});
const post = value => window.webkit.messageHandlers.native.postMessage(JSON.stringify(value));
window.receivePresentation = value => app.ports.presentation.send(value);
window.receiveFocus = targets => requestAnimationFrame(() => {
  for (const target of targets) document.getElementById(target)?.focus();
});
app.ports.actions.subscribe(post);
post({surfaceProtocol:1,kind:'presentation-ready'});
