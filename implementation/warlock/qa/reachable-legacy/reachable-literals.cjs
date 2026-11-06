'use strict';
// Independent source-literal model/effect expectations. Build from the
// existing inverse-checked original baseline; never from runtime observations.
const path=require('node:path');
const C=(tag,...xs)=>Object.fromEntries([['$',tag],...xs.map((x,i)=>[String.fromCharCode(97+i),x])]);
const L=xs=>xs.reduceRight((b,a)=>C('::',a,b),C('[]'));
const N=()=>C('Nothing'),J=x=>C('Just',x),V=x=>({$:0,a:x}),copy=x=>JSON.parse(JSON.stringify(x));
const D=(module,effects)=>({module,effects:L(effects)}),U=n=>C('Counter',String(n));
const read=()=>C('ReadEvents'),cancel=()=>[C('CancelEvents'),C('CancelPost')];
const B={lifetime:'1',session:'1',frontend:'1'}, domain={binding:B,receiverEpoch:'1'};
const gateway=(kind,payload)=>({bridgeProtocol:1,kind,payload});
const preview=payload=>[C('PreviewCommand',V(payload)),C('PaintRequest',V([]))];
const request=(n,body)=>({id:C('RequestId',U(n)),kind:C('PopupProposal'),body:V(body),ticket:N()});
const sender=req=>C('SendRequest',req.id,req.kind,req.body);
const ret=(http,fx,event)=>({kind:'transition',value:C('#3',copy(http),L(fx),event)});
const incoming=packet=>J(C('Incoming',V(packet)));
function poll(kind,payload,state,popupEffects,additional=[],returns=[]){
 const packet=gateway(kind,payload), http=copy(state.http);
 return {input:{kind:'polledOk',body:JSON.stringify(packet)},expected:{state:copy(state),subscriptions:{$:2,m:L([])},
   descriptions:[D('UiHttp',[read()]),...(popupEffects===null?[]:[D('Popup',popupEffects)]),...additional],
   transportReturns:[ret(http,[read()],incoming(packet)),...returns]}};
}
function build(repo,baseline,seed){
 if(![20261105,20261106].includes(seed))throw new Error("undeclared seed");
 const orig=require(path.join(repo,'implementation/warlock/qa/tea-subscriptions-cases.cjs'));
 const legacy=orig.cases.find(x=>x.name==='popup-overlay-and-paint-gate-subscriptions');
 if(!legacy || legacy.steps.length!==9)throw new Error('original Core literal changed');
 const init=copy(baseline.cases.find(x=>x.name==='HttpPopup-poll-delay-allowed-event-failed-sticky').steps[0]);
 if(init.input.kind!=='init'||init.expected.state.http.a.role.$!=='PopupRole')throw new Error('missing current init literal');
 const closed=copy(init.expected.state);
 closed.popup.presentation=copy(legacy.steps[1].expected.state.model.presentation);
 const closedPacket=legacy.steps[1].input.value;
 const closedStep=poll('presentation',closedPacket,closed,preview([]));
 const retry=poll('native-preview-retry',domain,closed,preview([]));
 const retired=copy(closed);retired.popup.previews.a.d.closing=true;
 const retirement=poll('native-preview-retirement',B,retired,preview([]));
 const duplicate=poll('native-preview-retirement',B,retired,preview([]));
 const emptyScoped={previewProtocol:3,kind:'preview-proposals',...domain,entries:[]};
 const grant={...domain,capacity:1};
 const granted=copy(closed), g={domain:{lifetime:U(1),session:U(1),frontend:U(1),receiverEpoch:U(1)},capacity:1};
 granted.popup.previews.a.c.channel=J('1:1:1');granted.popup.previews.a.d.grant=J(g);
 granted.popup.previews.b=J(g);granted.popup.previews.c=J(C('Model',g,L([])));
 const proposal={...emptyScoped,entries:[{identity:'binding:1:1:1',commands:[{kind:'reconcile',binding:B}]}]};
 const pending=copy(granted);pending.popup.previews.a.d.closing=true;
 pending.popup.previews.c.a.b=L([{identity:'binding:1:1:1',command:V({kind:'reconcile',binding:B})}]);
 pending.http.a.counter=U(1);pending.http.a.active=J(request(1,proposal));
 const q=poll('native-preview-quarantine',domain,pending,preview(proposal),
   [D('UiHttp',[sender(request(1,proposal))])],[ret(pending.http,[sender(request(1,proposal))],N())]);
 q.expected.transportReturns[0].value.a=copy(granted.http);
 const settled=copy(pending);settled.http.a.active=N();
 const posted={input:{kind:'postedForOk',requestId:'1',requestKind:'PopupProposal',body:''},expected:{state:copy(settled),subscriptions:{$:2,m:L([])},descriptions:[D('UiHttp',[])],transportReturns:[ret(settled.http,[],N())]}};
 const reoffered=copy(settled);reoffered.http.a.counter=U(2);reoffered.http.a.active=J(request(2,proposal));
 const reoffer=poll('native-preview-retry',domain,reoffered,preview(proposal),
   [D('UiHttp',[sender(request(2,proposal))])],[ret(reoffered.http,[sender(request(2,proposal))],N())]);
 reoffer.expected.transportReturns[0].value.a=copy(settled.http);
 function invalid(kind,payload){
   const state=copy(closed);state.http.a.failed=J(C('ExplicitStop','Invalid native preview control.'));
   const step=poll(kind,payload,state,null,[D('UiHttp',cancel())],
     [ret(state.http,cancel(),J(C('Lost','Invalid native preview control.')))]);
   step.expected.transportReturns[0].value.a=copy(closed.http);return step;
 }
 const cases=[
  {name:'closed-empty-retry-retirement-duplicate',root:'HttpPopup',steps:[copy(init),closedStep,retry,retirement,duplicate,poll('native-preview-retry',{binding:{...B,frontend:'2'},receiverEpoch:'1'},retired,preview([])),poll('native-preview-retry',{...domain,receiverEpoch:'2'},retired,preview([])),poll('native-preview-retry',domain,retired,preview([]))]},
  {name:'closed-reconcile-after-correlated-http204-reoffers',root:'HttpPopup',steps:[copy(init),closedStep,poll('native-preview-grant',grant,granted,[]),q,posted,reoffer]},
  {name:'retry-extra-rejected',root:'HttpPopup',steps:[copy(init),closedStep,invalid('native-preview-retry',{...domain,extra:seed})]},
  {name:'retirement-wrapped-rejected',root:'HttpPopup',steps:[copy(init),closedStep,invalid('native-preview-retirement',domain)]},
  {name:'retirement-zero-rejected',root:'HttpPopup',steps:[copy(init),closedStep,invalid('native-preview-retirement',{...B,lifetime:'0'})]},
  {name:'retry-missing-epoch-rejected',root:'HttpPopup',steps:[copy(init),closedStep,invalid('native-preview-retry',{binding:B})]},
  {name:'retry-zero-rejected',root:'HttpPopup',steps:[copy(init),closedStep,invalid('native-preview-retry',{...domain,receiverEpoch:'0'})]},
  {name:'retry-numeric-rejected',root:'HttpPopup',steps:[copy(init),closedStep,invalid('native-preview-retry',{...domain,receiverEpoch:1})]},
  {name:'retirement-extra-rejected',root:'HttpPopup',steps:[copy(init),closedStep,invalid('native-preview-retirement',{...B,extra:true})]},
  {name:'retirement-overflow-rejected',root:'HttpPopup',steps:[copy(init),closedStep,invalid('native-preview-retirement',{...B,lifetime:'18446744073709551616'})]}
 ];
 // Independent final returned-Cmd counts from the source branches, not
 // from constructed descriptions, observed output or Cmd identity/provenance.
 const returnedHttp={
  'closed-empty-retry-retirement-duplicate':[1,1,1,1,1,1,1,1],
  'closed-reconcile-after-correlated-http204-reoffers':[1,1,1,2,0,2],
  'retry-extra-rejected':[1,1,2],
  'retirement-wrapped-rejected':[1,1,2],
  'retirement-zero-rejected':[1,1,2],
  'retry-missing-epoch-rejected':[1,1,2],
  'retry-zero-rejected':[1,1,2],
  'retry-numeric-rejected':[1,1,2],
  'retirement-extra-rejected':[1,1,2],
  'retirement-overflow-rejected':[1,1,2]
 };
 for(const spec of cases){
  const counts=returnedHttp[spec.name];
  if(!counts||counts.length!==spec.steps.length)throw new Error('independent returned command journal differs');
  spec.steps.forEach((step,index)=>{step.expected.commandLeaves={Http:counts[index],Task:0};});
 }
 return {cases,expected:{caseCount:10,steps:38},originalCoreCase:legacy.name};
}
module.exports={build};
