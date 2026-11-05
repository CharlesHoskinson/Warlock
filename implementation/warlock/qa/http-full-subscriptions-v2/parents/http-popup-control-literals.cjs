'use strict';
// Source-literal QA only. `given` and `viewNativeQuarantine` are synthetic
// observer inputs, not HTTP gateway admissions or native producer evidence.
const fs=require('node:fs');
const crypto=require('node:crypto');
const path=require('node:path');
const pins={
 'implementation/warlock/qa/tea-subscriptions-cases.cjs':'a7f7cf418977cd4f49d2c6cb70f9313fd4992ea18e82c4289b0985026ae2c930',
 'implementation/warlock/qa/joined-control-literals.cjs':'6cb3275f6bb551d5ab100a0e8cc3e0880e2756344fbc6ea63b78a523109d47b6',
 'implementation/warlock/qa/sol-http-popup-literals-0525.cjs':'ab7af2abe53a36eae18c90762001a7f3647b47ed400b15bdd5aaba56f49f21f1',
 'implementation/warlock/src/Popup.elm':'c87f2b149b5bceae178484752a4ac75d869238026c6c4debe1b2ec6c7fd961eb',
 'implementation/warlock/src/HttpPopup.elm':'b0c3596d0e637722050830ca50ed2dd116b5c95953a3e6b988683d649563a52d',
 'implementation/warlock/src/UiHttp.elm':'73ae1bcb1d1d98fbe8ecbcfebca879f3df1e668dc2366cdfb37979fa6c3cf846',
 'implementation/warlock/src/NativePreviewRealm.elm':'2a3de2f3eacdf5b00489e5c1f5e5cef058e8f36d74fefecb25a5d3d9ea6024cf',
 'implementation/warlock/src/RetainedPreviewPresenter.elm':'7d3206e62e547af98171018a3bb65acdde0701393f35ea652bfffd1d5890810b',
 'implementation/warlock/src/PreviewPaintGate.elm':'fa2194375853ba16d5c783d04d110b052c43dccc89faf9fb6c4dce7aef709d4f',
 'implementation/warlock/src/Presentation.elm':'745a143ac94ab15a27a2c8d494bf66c167a42816cdddd71ffe877ba3627b3396'
};
const C=(tag,...xs)=>Object.fromEntries([['$',tag],...xs.map((x,i)=>[String.fromCharCode(97+i),x])]);
const L=xs=>xs.reduceRight((t,x)=>C('::',x,t),C('[]'));
const N=()=>C('Nothing'),J=x=>C('Just',x),V=x=>({$:0,a:x});
const S=()=>({$:2,m:C('[]')});
const D=(module,effects)=>({module,effects:L(effects)});
const copy=x=>JSON.parse(JSON.stringify(x));
const R=()=>C('ReadEvents');
const cancel=()=>[C('CancelEvents'),C('CancelPost')];
const returned=(h,fx,event=N())=>({kind:'transition',value:C('#3',h,L(fx),event)});
const given=state=>({input:{kind:'given'},expected:{state,subscriptions:S(),descriptions:[],transportReturns:[]}});
const reason='Native previews are unavailable in this HTTP profile. No preview command was sent.';
function build(repository){
 for(const [p,want] of Object.entries(pins)){
  const got=crypto.createHash('sha256').update(fs.readFileSync(path.join(repository,p))).digest('hex');
  if(got!==want) throw new Error('popup-control literal source changed: '+p);
 }
 const joined=require('./joined-control-literals.cjs').build(repository);
 const open=joined.cases.find(x=>x.name==='HttpJoined-open-given-dismiss-closed-presentation');
 if(!open||open.steps.length!==5||open.steps[1].input.kind!=='given') throw new Error('open popup independent GIVEN missing');
 const openState=copy(open.steps[1].expected.state), idle=copy(openState.http);
 if(idle.a.role.$!=='Renderer'||idle.a.active.$!=='Nothing'||openState.popup.presentation.a.last.a!=='7') throw new Error('open popup tuple changed');
 const action={surface:'popup',surfaceProtocol:2,kind:'surface-action',publication:'7',lease:'1',id:'control:close'};
 const sending=copy(idle);sending.a.active=J(V(action));
 const actionStep={input:{kind:'viewAction',value:action},expected:{state:{popup:copy(openState.popup),http:sending},subscriptions:S(),
  descriptions:[D('Popup',[C('Dispatch',V(action))]),D('UiHttp',[C('SendRenderer',V(action))])],
  transportReturns:[returned(sending,[C('SendRenderer',V(action))])]}};
 const settled={input:{kind:'postedOk',body:''},expected:{state:{popup:copy(openState.popup),http:idle},subscriptions:S(),
  descriptions:[D('UiHttp',[])],transportReturns:[returned(idle,[])]}};
 const sourceWire={bridgeProtocol:1,kind:'native-event',payload:{protocolVersion:3,kind:'host-disconnected'}};
 const rejected=copy(idle);rejected.a.failed=J(C('EventSourceRejected'));
 const rejectedStep={input:{kind:'polledOk',body:JSON.stringify(sourceWire)},expected:{state:{popup:copy(openState.popup),http:rejected},subscriptions:S(),
  descriptions:[D('UiHttp',cancel())],transportReturns:[returned(rejected,cancel(),J(C('Lost','UI event source is not allowed for this role.'))) ]}};
 const oracle=require(path.join(repository,'implementation/warlock/qa/tea-subscriptions-cases.cjs'));
 const record=oracle.cases.find(x=>x.name==='popup-realm-ingress-and-closed-revocation');
 if(!record) throw new Error('independent popup realm case missing');
 const realm=oracle.materialize(record);
 const before=realm.steps[10],after=realm.steps[11];
 if(before.input.kind!=='popup-native-issued'||after.input.kind!=='popup-native-quarantine'||after.expected.effects.$!=='PopupEffects') throw new Error('independent realm trace shape changed');
 const control=copy(after.input.value), beforePopup=copy(before.expected.state.model), afterPopup=copy(after.expected.state.model);
 const stopped=copy(idle);stopped.a.failed=J(C('ExplicitStop',reason));
 const refusal={input:{kind:'viewNativeQuarantine',value:control},expected:{state:{popup:afterPopup,http:stopped},subscriptions:S(),
  descriptions:[{module:'Popup',effects:copy(after.expected.effects.a)},D('UiHttp',cancel())],
  transportReturns:[returned(stopped,cancel(),J(C('Lost',reason)))]}};
 const late={input:{kind:'polledOk',body:JSON.stringify(sourceWire)},expected:{state:{popup:copy(afterPopup),http:stopped},subscriptions:S(),
  descriptions:[D('UiHttp',[])],transportReturns:[returned(stopped,[])]}};
 return {cases:[
  {name:'HttpPopup-action-sends-renderer-then-settles',root:'HttpPopup',steps:[given(copy(openState)),actionStep,settled]},
  {name:'HttpPopup-native-event-gateway-rejected',root:'HttpPopup',steps:[given(copy(openState)),rejectedStep]},
  {name:'HttpPopup-synthetic-quarantine-preview-command-refused',root:'HttpPopup',steps:[given({popup:beforePopup,http:copy(idle)}),refusal,late]}
 ],coverage:{complete:false,originalAccepted:false,nativeAccepted:false,limits:['given is an independent synthetic condition','direct View quarantine is QA-only; no HTTP or native producer','no preview command is interpreted','unexecuted source proposal']}};
}
module.exports={schema:1,build,pins};
