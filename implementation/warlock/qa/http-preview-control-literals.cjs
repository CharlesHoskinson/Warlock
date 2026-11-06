'use strict';
// Independent source literals for the first HTTP preview-control increment.
// No production reducer is invoked to manufacture expected values.
const path = require('node:path');
const copy = value => JSON.parse(JSON.stringify(value));
const C = (tag, ...values) => Object.fromEntries([['$', tag], ...values.map((value, index) => [String.fromCharCode(97 + index), value])]);
const N = () => C('Nothing');
const J = value => C('Just', value);
const L = values => values.reduceRight((tail, head) => C('::', head, tail), C('[]'));
const D = (module, values) => ({module, effects:L(values)});
const V = value => ({$:0,a:value});
function build(repository) {
  const baseline = require(path.join(repository,'implementation/warlock/qa/sol-http-popup-literals-0525.cjs')).build(repository);
  const initial = copy(baseline.cases.find(item => item.name==='HttpPopup-poll-delay-allowed-event-failed-sticky').steps[0]);
  const binding = {lifetime:'1',session:'1',frontend:'1'};
  const domain = epoch => ({lifetime:C('Counter','1'),session:C('Counter','1'),frontend:C('Counter','1'),receiverEpoch:C('Counter',epoch)});
  const grant = epoch => ({domain:domain(epoch),capacity:1});
  const enrolled = copy(initial.expected.state);
  const retained = enrolled.popup.previews;
  retained.a.c.channel=J('1:1:1');
  retained.a.d.grant=J(grant('1'));
  retained.b=J(grant('1'));
  retained.c=J(C('Model',grant('1'),L([])));
  const closed=copy(enrolled);
  closed.popup.previews.a.d.closing=true;
  closed.popup.previews.a.d.closed=true;
  const renewed=copy(enrolled);
  renewed.popup.previews.a.d.grant=J(grant('2'));
  renewed.popup.previews.b=J(grant('2'));
  renewed.popup.previews.c=J(C('Model',grant('2'),L([])));
  const input=(kind,payload)=>({kind:'polledOk',body:JSON.stringify({bridgeProtocol:1,kind,payload})});
  const step=(kind,payload,state,popupEffects=[])=>{
    const packet=JSON.parse(input(kind,payload).body);
    return {input:input(kind,payload),expected:{state:copy(state),subscriptions:copy(initial.expected.subscriptions),
      descriptions:[D('UiHttp',[C('ReadEvents')]),D('Popup',popupEffects)],
      transportReturns:[{kind:'transition',value:C('#3',copy(state.http),L([C('ReadEvents')]),J(C('Incoming',V(packet))))}]}};
  };
  const wire=epoch=>({binding,receiverEpoch:epoch});
  const emptyProposal={previewProtocol:3,kind:'preview-proposals',...wire('1'),entries:[]};
  const quarantined=copy(enrolled);
  quarantined.popup.previews.a.d.closing=true;
  const reconcile={kind:'reconcile',binding};
  quarantined.popup.previews.c.a.b=L([{identity:'binding:1:1:1',command:V(reconcile)}]);
  const proposal={...emptyProposal,entries:[{identity:'binding:1:1:1',commands:[reconcile]}]};
  const refusalReason='Native previews are unavailable in this HTTP profile. No preview command was sent.';
  quarantined.http.a.failed=J(C('ExplicitStop',refusalReason));
  const matching=step('native-preview-quarantine',wire('1'),quarantined,[C('PreviewCommand',V(proposal)),C('PaintRequest',V([]))]);
  // First HTTP incoming is observed before Popup revokes the realm. Its
  // unsupported reconcile proposal then stops transport without fake issuance.
  matching.expected.transportReturns[0].value.a=copy(enrolled.http);
  matching.expected.descriptions.push(D('UiHttp',[C('CancelEvents'),C('CancelPost')]));
  matching.expected.transportReturns.push({kind:'transition',value:C('#3',copy(quarantined.http),L([C('CancelEvents'),C('CancelPost')]),J(C('Lost',refusalReason)))});
  const late={input:input('native-preview-closed',wire('1')),expected:{state:copy(quarantined),subscriptions:copy(initial.expected.subscriptions),
    descriptions:[D('UiHttp',[])],transportReturns:[{kind:'transition',value:C('#3',copy(quarantined.http),L([]),N())}]}};
  let random=20261105;
  const generated=Array.from({length:32},(_,index)=>{
    random=(Math.imul(1664525,random)+1013904223)>>>0;
    const stale=random%2===0 ? {binding:{...binding,frontend:'2'},receiverEpoch:'1'} : wire(String(3+random%97));
    const conflict=random%2===0 ? {...wire('1'),capacity:2} : {...wire('2'),capacity:1};
    return {name:`HttpPopup-control-LCG20261105-${index}-${random}`,root:'HttpPopup',steps:[copy(initial),
      step('native-preview-grant',{...wire('1'),capacity:1},enrolled),
      step('native-preview-grant',conflict,enrolled),
      step('native-preview-closed',stale,enrolled),
      step('native-preview-closed',wire('1'),closed),
      step('native-preview-grant',{...wire('1'),capacity:1},closed),
      step('native-preview-grant',{...wire('2'),capacity:1},renewed)]};
  });
  return {schema:1,cases:[{name:'HttpPopup-native-control-closed-realm-lifetime',root:'HttpPopup',steps:[initial,
    step('native-preview-grant',{...wire('1'),capacity:1},enrolled),
    step('native-preview-grant',{...wire('1'),capacity:1},enrolled),
    step('native-preview-quarantine',wire('2'),enrolled,[C('PreviewCommand',V(emptyProposal)),C('PaintRequest',V([]))]),
    step('native-preview-closed',wire('2'),enrolled),
    step('native-preview-closed',wire('1'),closed),
    step('native-preview-grant',{...wire('1'),capacity:1},closed),
    step('native-preview-grant',{...wire('2'),capacity:1},renewed)
  ]},{name:'HttpPopup-matching-quarantine-retains-unconfirmed-reconcile',root:'HttpPopup',steps:[copy(initial),
    step('native-preview-grant',{...wire('1'),capacity:1},enrolled),matching,late
  ]},{name:'HttpPopup-restart-enrolls-new-realm-without-old-effect-replay',root:'HttpPopup',steps:[copy(initial),
    step('native-preview-grant',{...wire('2'),capacity:1},renewed)
  ]},...generated],fuzz:{seed:20261105,generator:'LCG32 1664525/1013904223; 32 seven-step realm sequences',cases:32},coverage:{complete:false,originalAccepted:false,nativeAccepted:false,
    limits:['first typed control increment only','nonempty proposals and paint remain unsupported and fail closed',
      'real authenticated Owner boundary execution required in addition to pure root replay',
      'no native producer or resource execution qualification']}};
}
module.exports={schema:1,build};
