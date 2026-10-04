'use strict';
const app=Elm.Main.init({node:document.getElementById('app'),flags:null});
const bridge=window.webkit.messageHandlers.native;
app.ports.nativeRequests.subscribe(message=>bridge.postMessage(JSON.stringify(message)));
let requestProjectionReport=()=>{};
window.receiveNative=message=>{app.ports.nativeEvents.send(message);requestProjectionReport();};
bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'host-ready'}));
if(window.elmHostQA){
 let scheduled=false,reported=false;
 const control=b=>{const r=b.getBoundingClientRect();return {disabled:b.disabled,label:b.getAttribute('aria-label'),point:[r.x+r.width/2,r.y+r.height/2],visible:r.width>0&&r.height>0&&r.x>=0&&r.y>=0&&r.right<=innerWidth&&r.bottom<=innerHeight};};
 requestProjectionReport=()=>{
  if(scheduled)return;scheduled=true;
  requestAnimationFrame(()=>{
   scheduled=false;const root=document.getElementById('shell-root');if(!root)return;
   const groups=[...document.querySelectorAll('[data-group]')].map(b=>({...control(b),key:b.dataset.group,title:b.dataset.title,active:b.classList.contains('active'),expanded:b.getAttribute('aria-expanded')==='true'}));
   const picker=document.getElementById('window-picker');
   const selections=[...document.querySelectorAll('[data-incarnation]')].map(b=>({...control(b),incarnation:b.dataset.incarnation,title:b.dataset.title,state:b.querySelector('.state').textContent}));
   const reconnect=document.getElementById('reconnect');
   bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'projection-report',body:{phase:root.dataset.phase,focus:document.activeElement?document.activeElement.id:null,groups,picker:picker?{generation:picker.dataset.generation,selections,close:control(document.getElementById('close-picker'))}:null,status:document.querySelector('[role=status]').textContent,transaction:root.dataset.transaction,reconnect:reconnect?control(reconnect):null}}));
   if(!reported&&root.dataset.phase==='Coherent'&&groups.length){reported=true;bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'render-report',body:{groups:groups.length,actionsDisabled:groups.every(group=>group.disabled)}}));}
  });
 };
 document.addEventListener('focusin',requestProjectionReport);
 new MutationObserver(requestProjectionReport).observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['data-phase','data-transaction','data-generation','class','disabled','aria-busy','aria-expanded']});
}
