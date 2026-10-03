'use strict';
const app=Elm.Main.init({node:document.getElementById('app'),flags:null});
const bridge=window.webkit.messageHandlers.native;
app.ports.nativeRequests.subscribe(message=>bridge.postMessage(JSON.stringify(message)));
window.receiveNative=message=>app.ports.nativeEvents.send(message);
bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'host-ready'}));
if(window.elmHostQA){
 let scheduled=false,reported=false;
 new MutationObserver(()=>{
  if(scheduled)return;scheduled=true;
  requestAnimationFrame(()=>{
   scheduled=false;const root=document.getElementById('shell-root');if(!root)return;
   const rows=[...document.querySelectorAll('[data-incarnation]')].map(row=>{
    const b=row.querySelector('button'),r=b.getBoundingClientRect();
    return {incarnation:row.dataset.incarnation,label:row.querySelector('.window-title').textContent,state:row.querySelector('.state').textContent,action:b.textContent,disabled:b.disabled,point:[r.x+r.width/2,r.y+r.height/2]};
   });
   bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'projection-report',body:{phase:root.dataset.phase,rows,status:document.querySelector('[role=status]').textContent}}));
   if(!reported&&root.dataset.phase==='Coherent'&&rows.length){reported=true;bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'render-report',body:{windows:rows.length,actionsDisabled:rows.every(row=>row.disabled)}}));}
  });
 }).observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['data-phase','disabled']});
}
