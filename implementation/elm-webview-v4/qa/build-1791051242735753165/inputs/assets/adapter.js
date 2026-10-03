'use strict';
const app=Elm.Main.init({node:document.getElementById('app'),flags:null});
const bridge=window.webkit.messageHandlers.native;
app.ports.nativeRequests.subscribe(message=>bridge.postMessage(JSON.stringify(message)));
window.receiveNative=message=>app.ports.nativeEvents.send(message);
bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'host-ready'}));
if(window.elmHostQA){
 let projectionScheduled=false;
 const projectionObserver=new MutationObserver(()=>{
  if(projectionScheduled)return;projectionScheduled=true;
  requestAnimationFrame(()=>{
   projectionScheduled=false;const root=document.getElementById('shell-root');if(!root)return;
   const fixture=[...document.querySelectorAll('[data-incarnation]')].find(row=>row.querySelector('.window-title').textContent==='ELM-AUTHORITY-FIXTURE');
   bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'projection-report',body:{phase:root.dataset.phase,fixtureIncarnation:fixture?fixture.dataset.incarnation:null}}));
  });
 });
 projectionObserver.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['data-phase']});
 const observer=new MutationObserver(()=>{
  const root=document.getElementById('shell-root');
  if(!root||root.dataset.phase!=='Coherent')return;
  const entries=[...document.querySelectorAll('[data-incarnation]')];
  if(!entries.some(row=>row.querySelector('.window-title').textContent==='ELM-AUTHORITY-FIXTURE'))return;
  observer.disconnect();
  requestAnimationFrame(()=>requestAnimationFrame(async()=>{
   const gpu={webgpuExposed:!!navigator.gpu,webglAvailable:false};
   const canvas=document.createElement('canvas');canvas.width=32;canvas.height=32;
   canvas.style.cssText='position:fixed;right:0;bottom:0;width:32px;height:32px';document.body.append(canvas);
   const gl=canvas.getContext('webgl',{preserveDrawingBuffer:true,antialias:false});
   if(gl){
    gpu.webglAvailable=true;const extension=gl.getExtension('WEBGL_debug_renderer_info');
    gpu.vendor=gl.getParameter(extension?extension.UNMASKED_VENDOR_WEBGL:gl.VENDOR);
    gpu.renderer=gl.getParameter(extension?extension.UNMASKED_RENDERER_WEBGL:gl.RENDERER);
    gl.clearColor(0,1,1,1);gl.clear(gl.COLOR_BUFFER_BIT);const pixel=new Uint8Array(4);
    gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,pixel);gpu.pixel=[...pixel];gpu.error=gl.getError();
   }
   if(navigator.gpu){try{const adapter=await navigator.gpu.requestAdapter();gpu.webgpuAdapter=!!adapter;}catch(_){gpu.webgpuAdapter=false;}}
   requestAnimationFrame(()=>bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'render-report',body:{windows:entries.length,fixturePresent:true,actionsDisabled:entries.every(row=>row.querySelector('button').disabled),secureContext:window.isSecureContext,gpu}})));
  }));
 });
 observer.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['data-phase']});
}
