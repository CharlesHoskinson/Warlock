'use strict';
const app=Elm.Main.init({node:document.getElementById('app'),flags:null});
const bridge=window.webkit.messageHandlers.native;
app.ports.nativeRequests.subscribe(message=>bridge.postMessage(JSON.stringify(message)));
let requestProjectionReport=()=>{};
window.receiveNative=message=>{app.ports.nativeEvents.send(message);requestProjectionReport();};
bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'host-ready'}));
if(window.elmHostQA){
 let scheduled=false,reported=false;
 const control=b=>{
  const r=b.getBoundingClientRect(),owner=b.closest('.picker-windows,.application-list'),c=owner?owner.getBoundingClientRect():{left:0,top:0,right:innerWidth,bottom:innerHeight};
  const clip=[Math.max(0,c.left),Math.max(0,c.top),Math.min(innerWidth,c.right),Math.min(innerHeight,c.bottom)];
  return {disabled:b.disabled,label:b.getAttribute('aria-label'),point:[r.x+r.width/2,r.y+r.height/2],rect:[r.x,r.y,r.width,r.height],clip,visible:r.width>0&&r.height>0&&r.left>=clip[0]&&r.top>=clip[1]&&r.right<=clip[2]&&r.bottom<=clip[3]};
 };
 requestProjectionReport=()=>{
  if(scheduled)return;scheduled=true;
  requestAnimationFrame(()=>{
   scheduled=false;const applications=document.getElementById('applications');
   if(applications){
    const entries=[...document.querySelectorAll('[data-application]')].map(b=>({...control(b),id:b.dataset.application}));
    const controls=[...applications.querySelectorAll('.launcher-controls button')].map(b=>({...control(b),text:b.textContent}));
    bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'projection-report',body:{phase:'Applications',launchStatus:applications.dataset.launchStatus,entries,controls,focus:document.activeElement?document.activeElement.id:null,status:applications.querySelector('[role=status]').textContent}}));return;
   }
   const root=document.getElementById('shell-root');if(!root)return;
   const groups=[...document.querySelectorAll('[data-group]')].map(b=>({...control(b),key:b.dataset.group,title:b.dataset.title,active:b.classList.contains('active'),expanded:b.getAttribute('aria-expanded')==='true'}));
   const picker=document.getElementById('window-picker');
   const selections=[...document.querySelectorAll('[data-incarnation]')].map(b=>({...control(b),incarnation:b.dataset.incarnation,title:b.dataset.title,state:b.querySelector('.state').textContent}));
   const reconnect=document.getElementById('reconnect');
   bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'projection-report',body:{phase:root.dataset.phase,focus:document.activeElement?document.activeElement.id:null,groups,picker:picker?{generation:picker.dataset.generation,selections,close:control(document.getElementById('close-picker'))}:null,status:document.querySelector('[role=status]').textContent,transaction:root.dataset.transaction,openApplications:document.querySelector('[data-launcher-opener]')?control(document.querySelector('[data-launcher-opener]')):null,reconnect:reconnect?control(reconnect):null}}));
   if(!reported&&root.dataset.phase==='Coherent'&&groups.length){reported=true;bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'render-report',body:{groups:groups.length,actionsDisabled:groups.every(group=>group.disabled)}}));}
  });
 };
 document.addEventListener('focusin',requestProjectionReport);
 document.addEventListener('scroll',requestProjectionReport,true);
 new MutationObserver(requestProjectionReport).observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['data-phase','data-transaction','data-launch-status','data-generation','class','disabled','aria-busy','aria-expanded']});
}
