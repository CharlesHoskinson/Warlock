"use strict";
const post=v=>window.webkit.messageHandlers.native.postMessage(JSON.stringify(v));
let topology=null,selected="bar",publication=0,lease=0;
const frames=window.fixtureFrames;
function publish(){
 if(!topology||!topology.views.length)return;
 publication++;
 if(selected==="popup")lease++;
 const frame=JSON.parse(JSON.stringify(frames[selected==="popup"?"popup":"bar"]));
 frame.publication=String(publication);frame.lease=String(lease);
 const scope=topology.views[0];
 const focus=selected==="popup"?["qa-close"]:selected==="bar-focus"?["qa-refresh"]:[];
 post({viewProtocol:1,kind:"view-commit",projection:{viewProtocol:1,kind:"view-frame",revision:topology.revision,views:topology.views,popupOwner:selected==="popup"?scope:null,focusOwner:scope,frame},requests:[],focus});
 post({kind:"surface-inspection",body:{event:"fixture-publication",name:selected,publication:frame.publication,lease:frame.lease}});
}
window.receiveTopology=v=>{topology=v;publish()};
window.receiveNative=v=>{if(v.kind==="fixture-presentation"&&selected!==v.name){selected=v.name;publish()}};
window.receiveAction=v=>{post({kind:"surface-inspection",body:{event:"fixture-action",value:v}});if(v.action?.id==="qa-open"){selected="popup";publish()}else if(v.action?.id==="qa-close"){selected="bar";publish()}};
window.receiveDismiss=()=>{selected="bar";publish()};
window.receiveFocus=()=>{};window.receiveBatchDisposition=()=>{};window.receiveReflow=()=>{};
post({protocolVersion:3,kind:"host-ready"});
