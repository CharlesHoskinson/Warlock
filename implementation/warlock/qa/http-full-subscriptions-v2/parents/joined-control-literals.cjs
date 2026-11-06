'use strict';
// Independent literal proposal; no reducer invocation or observed state.
// Root must independently review and run under the protected profile.
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const pins={
 'implementation/warlock/qa/tea-contract-cases.cjs':'41e3ccabc5843153b604205dd937c56890f659e294929788a959951d39b7bcb7',
 'implementation/warlock/qa/sol-http-popup-literals-0525.cjs':'ab7af2abe53a36eae18c90762001a7f3647b47ed400b15bdd5aaba56f49f21f1',
 'implementation/warlock/src/Desktop.elm':'2ef557760c8405dd5dce7172ca29a5d81525fc6738d017cec0008a09b10a08db',
 'implementation/warlock/src/DesktopPolicy.elm':'018934fe4762e8357665ce7c37cb289883c6cdd1bad31d6592402b369d7bad3e',
 'implementation/warlock/src/OutputController.elm':'fdf7b44483ec9312182a1b50bb2bbb5d52b804538e5c4d4ce5a4a8479e9af6ae',
 'implementation/warlock/src/SurfaceController.elm':'2e86781c41c1b1c62d518e886ee965a875a04ea88980159a00511c549b25e998',
 'implementation/warlock/src/Surface.elm':'175d4432e2a28c18cfa18e72f2effc61bf8d551ddce0679e14e25681fc78ec1c',
 'implementation/warlock/src/OutcomeAnnouncements.elm':'e1160f27432b3869ceb3627224d07cfdbfc9a996d83bf063f9563ec5c29216bb',
 'implementation/warlock/src/Popup.elm':'c87f2b149b5bceae178484752a4ac75d869238026c6c4debe1b2ec6c7fd961eb',
 'implementation/warlock/src/Presentation.elm':'745a143ac94ab15a27a2c8d494bf66c167a42816cdddd71ffe877ba3627b3396',
 'implementation/warlock/src/UiHttp.elm':'c3543e27ad787d3c84894554178121205d19b9868c250d0717989c1207cdc72f',
 'implementation/warlock/src/HttpMain.elm':'c0dcd27b03b737b83be70d439944ea9741128e18dd9405b55595c559e8bef3cf',
 'implementation/warlock/src/HttpPopup.elm':'e7a8b1d479d3b8d728bf97b5bab8a2cfee7b2a1010902d984690215574ee84e2',
 'implementation/warlock/haskell/runtime/src/Warlock/Ui/Owner.hs':'3585e3ca0f8fbca8dc9b66d54821e8e60707b6798550945ea983c81a4181926f'
};
const C=(tag,...v)=>Object.fromEntries([['$',tag],...v.map((x,i)=>[String.fromCharCode(97+i),x])]);
const L=xs=>xs.reduceRight((tail,x)=>C('::',x,tail),C('[]'));
const N=()=>C('Nothing'), J=x=>C('Just',x), V=x=>({$:0,a:x}), U=x=>C('Counter',String(x));
const sub=()=>({$:2,m:C('[]')});
const desc=(module,effects)=>({module,effects:L(effects)});
const copy=x=>JSON.parse(JSON.stringify(x));
const http=(role,active=null)=>C('Model',{role:C(role),pending:L([]),active:active===null?N():J(V(active)),polling:true,failed:N()});
const returned=(h,fx,event=N())=>({kind:'transition',value:C('#3',h,L(fx),event)});
const gate=(kind,payload)=>({bridgeProtocol:1,kind,payload});
const read=()=>C('ReadEvents');
const row=x=>({identity:x.id,domId:x.domId,label:x.label,ariaLabel:x.ariaLabel,detail:x.detail,enabled:x.enabled,focusOnly:x.focusOnly,checked:N()});
const snapshot=f=>C('Snapshot',{publication:U(f.publication),lease:U(f.lease),keyboardParent:J(true),mode:f.mode,status:f.status,
 appearance:{theme:C('Night'),textScale:100,effectsOff:false,reducedTransparency:false},motion:'reduced',bar:L(f.bar.map(row)),popup:L(f.popup.map(row))});
function build(repository) {
 for (const [name,want] of Object.entries(pins)) {
  const got=crypto.createHash('sha256').update(fs.readFileSync(path.join(repository,name))).digest('hex');
  if (got!==want) throw new Error('pinned literal input changed: '+name);
 }
 const oracle=require(path.join(repository,'implementation/warlock/qa/tea-contract-cases.cjs'));
 const item=oracle.cases.find(x=>x.name==='pin-wrong-request-retains-pending');
 if (!item) throw new Error('independent pending open baseline absent');
 const baseline=oracle.materialize(item).steps[1];
 if (baseline.input.kind!=='prelude') throw new Error('open baseline shape');
 const before=copy(baseline.expected.state), open=copy(baseline.expected.effects.a.a.a);
 const scope={id:'1',generation:'1'};
 if (open.projection.revision!=='1'||open.projection.frame.publication!=='7'||open.projection.frame.lease!=='1'||open.projection.frame.mode!=='applications') throw new Error('open baseline tuple');
 const after=copy(before);
 const control=after.controller.a.controller.a, desktop=control.desktop;
 if (control.publication.a!=='7'||desktop.presentation.a.a!=='6'||!desktop.open||desktop.expected.$!=='Just'||!desktop.catalogOpening) throw new Error('independent GIVEN preimage changed');
 control.publication=U(8); desktop.presentation=J(U(7)); desktop.open=false; desktop.expected=N(); desktop.catalogOpening=false;
 // CloseApplications advances Desktop presentation to 7 and focuses its bar opener.
 // The prior pending pin transaction and OutputController batches are preserved.
 const close=copy(open), f=close.projection.frame;
 close.projection.popupOwner=null;
 close.projection.announcer={scope,surface:'bar'};
 f.publication='8'; f.mode='closed'; f.popup=[];
 const from='applications:{"lifetime":"1","session":"1","frontend":"1"}:6:';
 const to='applications:{"lifetime":"1","session":"1","frontend":"1"}:7:';
 f.bar=f.bar.map(x=>({...x,domId:x.domId.startsWith(from)?to+x.domId.slice(from.length):x.domId}));
 close.requests=[]; close.focus=[to+'control:opener'];
 const popupOracle=require('./sol-http-popup-literals-0525.cjs').build(repository);
 const initial=popupOracle.cases.find(x=>x.name==='HttpPopup-poll-delay-allowed-event-failed-sticky');
 if (!initial) throw new Error('popup initial literal absent');
 const domain=copy(initial.steps[0].expected.state.popup);
 domain.presentation=C('Model',{last:U(7),lease:U(1),snapshot:J(snapshot(open.projection.frame))});
 // GIVEN assumes the open frame and its null-message popup announcement were
 // already delivered, while no preview and no local edit are active.
 domain.announcements=C('Model',{last:U(0),active:true,message:N()});
 const closedDomain=copy(domain);
 closedDomain.presentation=C('Model',{last:U(8),lease:U(1),snapshot:J(snapshot(f))});
 const announcedDomain=copy(closedDomain);
 announcedDomain.announcements=C('Model',{last:U(0),active:false,message:N()});
 const m0=http('Controller'),m1=http('Controller',close),p0=http('Renderer');
 const given=(root,state)=>({root,input:{kind:'given'},expected:{state,subscriptions:sub(),descriptions:[],transportReturns:[]}});
 const dismissal=gate('view-dismiss',{scope,lease:'1'});
 const publish=C('Publish',V(close)), policyEffects=L([publish]);
 const mainStep={root:'HttpMain',input:{kind:'polledOk',body:JSON.stringify(dismissal)},
  expected:{state:{policy:after,http:m1},subscriptions:sub(),descriptions:[desc('UiHttp',[read()]),{module:'DesktopPolicy',effects:policyEffects},{module:'HttpMain.effects',effects:policyEffects},desc('UiHttp',[C('SendController',V(close))])],
   transportReturns:[returned(m0,[read()],J(C('Incoming',V(dismissal)))),returned(m1,[C('SendController',V(close))])]},
  join:{kind:'commit',commit:close,selected:scope}};
 const announcement={announcementProtocol:1,kind:'announcement-projection',recipient:{scope,surface:'popup'},announcer:{scope,surface:'bar'},publication:'8',lease:'1',message:null,deliver:false};
 const receive=(kind,payload,popup,effects)=>{const wire=gate(kind,payload);return {root:'HttpPopup',input:{kind:'polledOk',body:JSON.stringify(wire)},expected:{state:{popup,http:p0},subscriptions:sub(),descriptions:[desc('UiHttp',[read()]),desc('Popup',effects)],transportReturns:[returned(p0,[read()],J(C('Incoming',V(wire))))]},join:{kind,commitStep:2}};};
 return {cases:[{name:'HttpJoined-open-given-dismiss-closed-presentation',root:'HttpJoined',steps:[
  given('HttpMain',{policy:before,http:m0}),given('HttpPopup',{popup:domain,http:p0}),mainStep,
  receive('presentation',f,closedDomain,[C('PreviewCommand',V([])),C('PaintRequest',V([]))]),
  receive('announcements',announcement,announcedDomain,[])
 ]}],coverage:{complete:false,nativeAccepted:false,originalAccepted:false,limits:['source-literal GIVEN, not runtime reachability','source-derived Owner projection, not Owner execution','native preview producer unqualified','unexecuted proposal']}};
}
module.exports={schema:1,build,pins};
