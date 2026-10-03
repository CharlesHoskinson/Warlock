'use strict';
const app=Elm.Main.init({node:document.getElementById('app'),flags:null});
const bridge=window.webkit.messageHandlers.native;
app.ports.nativeRequests.subscribe(message=>bridge.postMessage(JSON.stringify(message)));
window.receiveNative=message=>app.ports.nativeEvents.send(message);
bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'host-ready'}));
