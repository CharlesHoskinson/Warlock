'use strict';
// Source-only extension of the unchanged independently authored and tested
// five-step dismissal history. No captured reducer state is used as an oracle.
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const pins={
 'implementation/warlock/qa/joined-control-literals.cjs':'6cb3275f6bb551d5ab100a0e8cc3e0880e2756344fbc6ea63b78a523109d47b6',
 'implementation/warlock/src/OutputController.elm':'fdf7b44483ec9312182a1b50bb2bbb5d52b804538e5c4d4ce5a4a8479e9af6ae',
 'implementation/warlock/src/Desktop.elm':'2ef557760c8405dd5dce7172ca29a5d81525fc6738d017cec0008a09b10a08db',
 'implementation/warlock/src/SurfaceController.elm':'2e86781c41c1b1c62d518e886ee965a875a04ea88980159a00511c549b25e998',
 'implementation/warlock/src/Shell.elm':'6f6a63168d1d39da6e85290b564074ca21f7c719140aacee939973e3706ad094',
 'implementation/warlock/src/TaskbarShell.elm':'eeb91d15cab97c94bf12ef3d1e25f513ac6c037774bef5150867eb01c6f86c26',
 'implementation/warlock/src/Surface.elm':'175d4432e2a28c18cfa18e72f2effc61bf8d551ddce0679e14e25681fc78ec1c',
 'implementation/warlock/src/Popup.elm':'c87f2b149b5bceae178484752a4ac75d869238026c6c4debe1b2ec6c7fd961eb',
 'implementation/warlock/src/Presentation.elm':'745a143ac94ab15a27a2c8d494bf66c167a42816cdddd71ffe877ba3627b3396',
 'implementation/warlock/src/UiHttp.elm':'c3543e27ad787d3c84894554178121205d19b9868c250d0717989c1207cdc72f',
 'implementation/warlock/haskell/runtime/src/Warlock/Ui/Owner.hs':'3585e3ca0f8fbca8dc9b66d54821e8e60707b6798550945ea983c81a4181926f'
};
const C=(tag,...xs)=>Object.fromEntries([['$',tag],...xs.map((x,i)=>[String.fromCharCode(97+i),x])]);
const L=xs=>xs.reduceRight((tail,x)=>C('::',x,tail),C('[]'));
const N=()=>C('Nothing'), J=x=>C('Just',x), V=x=>({$:0,a:x}), U=x=>C('Counter',String(x));
const S=()=>({$:2,m:C('[]')});
const desc=(module,effects)=>({module,effects:L(effects)});
const copy=x=>JSON.parse(JSON.stringify(x));
const read=()=>C('ReadEvents');
const ret=(h,fx,event=N())=>({kind:'transition',value:C('#3',h,L(fx),event)});
const gate=(kind,payload)=>({bridgeProtocol:1,kind,payload});
function build(repository){
 for(const [p,want] of Object.entries(pins)){
  const got=crypto.createHash('sha256').update(fs.readFileSync(path.join(repository,p))).digest('hex');
  if(got!==want) throw new Error('closed-topology pinned source changed: '+p);
 }
 const base=require('./joined-control-literals.cjs').build(repository);
 const prior=base.cases.find(x=>x.name==='HttpJoined-open-given-dismiss-closed-presentation');
 if(!prior||prior.steps.length!==5||prior.steps[2].join.kind!=='commit') throw new Error('dismiss prefix shape changed');
 // Exact unchanged independent prefix. New values are source-derived changes
 // to these literal objects, never actual observer output.
 const steps=copy(prior.steps), originalMain=copy(steps[2].expected.state), popup=copy(steps[4].expected.state.popup);
 const beforePolicy=originalMain.policy, beforeHttp=originalMain.http;
 if(beforeHttp.a.active.$!=='Just'||beforePolicy.controller.a.revision.a!=='1'||
    beforePolicy.controller.a.controller.a.publication.a!=='8'||popup.presentation.a.last.a!=='8') throw new Error('dismiss preimage mismatch');
 const idle=copy(beforeHttp); idle.a.active=N();
 const settle={root:'HttpMain',input:{kind:'postedOk',body:''},expected:{state:{policy:beforePolicy,http:idle},subscriptions:S(),
  descriptions:[desc('UiHttp',[])],transportReturns:[ret(idle,[])]}};
 const policy=copy(beforePolicy), output=policy.controller.a, controller=output.controller.a;
 if(output.selected.$!=='Just'||output.views.$!=='::'||controller.desktop.ownerScope.$!=='Just'||!controller.desktop.windows.shell.applicationOnly) throw new Error('topology preimage mismatch');
 output.revision=U(2); output.views=L([]); output.selected=N();
 controller.desktop.ownerScope=N(); controller.publication=U(9);
 // No extra NativeDismiss: the previous close already removed popup ownership.
 // Highest scope, lease, retained pending pin/batches and Desktop presentation
 // remain unchanged. Application-only shell supersession does not issue reads.
 const commit=copy(steps[2].join.commit),projection=commit.projection,frame=projection.frame;
 projection.revision='2';projection.views=[];projection.focusOwner=null;projection.popupOwner=null;projection.announcer=null;
 frame.publication='9';commit.requests=[];commit.focus=[];
 const top=gate('view-topology',{viewProtocol:1,kind:'view-topology',revision:'2',views:[]});
 const active=copy(idle);active.a.active=J(V(commit));
 const send=C('SendController',V(commit)), policyEffects=L([C('Publish',V(commit))]);
 const transition={root:'HttpMain',input:{kind:'polledOk',body:JSON.stringify(top)},
  expected:{state:{policy,http:active},subscriptions:S(),descriptions:[desc('UiHttp',[read()]),{module:'DesktopPolicy',effects:policyEffects},
    {module:'HttpMain.effects',effects:policyEffects},desc('UiHttp',[send])],
   transportReturns:[ret(idle,[read()],J(C('Incoming',V(top)))),ret(active,[send])]},
  join:{kind:'commit',commit,selected:null}};
 const rendererHttp=copy(steps[4].expected.state.http), presented=copy(popup);
 presented.presentation.a.last=U(9);
 presented.presentation.a.snapshot.a.a.publication=U(9);
 const announcement={announcementProtocol:1,kind:'announcement-projection',recipient:{scope:null,surface:'popup'},announcer:null,
   publication:'9',lease:'1',message:null,deliver:false};
 const receive=(kind,payload,domain,effects)=>{const wire=gate(kind,payload);return {root:'HttpPopup',input:{kind:'polledOk',body:JSON.stringify(wire)},
   expected:{state:{popup:domain,http:rendererHttp},subscriptions:S(),descriptions:[desc('UiHttp',[read()]),desc('Popup',effects)],
    transportReturns:[ret(rendererHttp,[read()],J(C('Incoming',V(wire))))]},join:{kind,commitStep:6}};};
 const presentation=receive('presentation',frame,presented,[C('PreviewCommand',V([])),C('PaintRequest',V([]))]);
 // The actual Owner projection carries null recipient scope; the strict popup
 // announcement route rejects it and retains the already inactive model.
 const announce=receive('announcements',announcement,presented,[]);
 const finish={root:'HttpMain',input:{kind:'postedOk',body:''},expected:{state:{policy,http:idle},subscriptions:S(),
  descriptions:[desc('UiHttp',[])],transportReturns:[ret(idle,[])]}};
 const duplicate={root:'HttpMain',input:{kind:'polledOk',body:JSON.stringify(top)},expected:{state:{policy,http:idle},subscriptions:S(),
  descriptions:[desc('UiHttp',[read()]),desc('DesktopPolicy',[]),desc('HttpMain.effects',[])],
  transportReturns:[ret(idle,[read()],J(C('Incoming',V(top))))]}};
 return {cases:[{name:'HttpJoined-dismiss-then-closed-empty-topology',root:'HttpJoined',steps:steps.concat([settle,transition,presentation,announce,finish,duplicate])}],
  coverage:{complete:false,originalAccepted:false,nativeAccepted:false,limits:['source-literal GIVEN','Owner projection relation only, not Haskell execution','popup lifetime after unmap conditional','native preview revocation not covered','unexecuted proposal']}};
}
module.exports={schema:1,build,pins};
