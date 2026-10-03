"use strict";
const app=Elm.Main.init({node:document.getElementById('app'),flags:null});
const bridge=window.webkit.messageHandlers.native;
app.ports.nativeRequests.subscribe(message=>bridge.postMessage(JSON.stringify(message)));
window.receiveNative=message=>app.ports.nativeEvents.send(message);
bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'host-ready'}));
if(window.elmHostQA){
 let scheduled=false,reported=false;
 const point=node=>{const r=node.getBoundingClientRect();return[r.x+r.width/2,r.y+r.height/2]};
 const report=()=>{
  if(scheduled)return;scheduled=true;
  requestAnimationFrame(()=>{
   scheduled=false;const root=document.getElementById('shell-root');if(!root)return;
   const rows=[...document.querySelectorAll('[data-incarnation]')].map(row=>({
    incarnation:row.dataset.incarnation,label:row.querySelector('.window-title').textContent,
    state:row.querySelector('.state').textContent,point:point(row)
   }));
   const menu=document.getElementById('context-menu');
   const body={phase:root.dataset.phase,rows,transaction:root.dataset.transaction,
    status:document.getElementById('connection-status').textContent,
    focused:document.activeElement?.id||null,
    menu:menu?{id:menu.dataset.menuId,actions:[...menu.querySelectorAll('[role=menuitem]')].map(b=>({index:Number(b.dataset.index),label:b.textContent,disabled:b.disabled,point:point(b)})),dismiss:point(document.getElementById('context-dismiss'))}:null};
   bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'projection-report',body}));
   if(!reported&&root.dataset.phase==='Coherent'&&rows.length){reported=true;bridge.postMessage(JSON.stringify({protocolVersion:3,kind:'render-report',body:{windows:rows.length,actionsDisabled:false}}));}
  });
 };
 new MutationObserver(report).observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['data-phase','data-transaction','data-menu-id','disabled']});
 document.addEventListener('focusin',report);
}
