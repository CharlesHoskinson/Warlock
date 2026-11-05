'use strict';
// Source-literal representation migration ONLY. No production reducer imports.
const {isDeepStrictEqual:eq}=require('node:util');
const copy=x=>JSON.parse(JSON.stringify(x));
const C=(tag,...xs)=>Object.fromEntries([['$',tag],...xs.map((x,i)=>[String.fromCharCode(97+i),x])]);
const N=()=>C('Nothing'),U=n=>C('Counter',String(n));
const L=xs=>xs.reduceRight((t,x)=>C('::',x,t),C('[]'));
const insist=(ok,msg)=>{if(!ok)throw new Error(msg);};
function vals(xs){const out=[];while(xs&&xs.$==='::'){out.push(xs.a);xs=xs.b;}insist(xs&&xs.$==='[]','literal list');return out;}
// Exact counters for EACH original step, independent of observed output.
const counters={
 'HttpPopup-poll-delay-allowed-event-failed-sticky':[0,0,0,0,0,0,0,0,0],
 'HttpPopup-late-delivery-error-before-sleep-target':[0,0,0,0,0],
 'HttpBar-poll-delay-allowed-event-failed-sticky':[0,0,0,0,0,0,0,0,0],
 'HttpBar-late-delivery-error-before-sleep-target':[0,0,0,0,0],
 'HttpMain-complete-publish-queue-http-completion-is-not-native-ack':[0,1,2,2,2,2],
 'HttpMain-unknown-delivery-retains-active-and-pending-no-replay':[0,1,2,2,2,2,2],
 'HttpMain-polling-failure-retains-queued-data-and-policy-loss':[0,1,2,2,2,2],
 'HttpBar-visible-loading-delayed-synchronous-stale-and-queue':[0,0,1,1,1,1,1,2,2,2,2,2,2,2,2,2],
 'HttpPopup-action-sends-renderer-then-settles':[0,1,1],
 'HttpPopup-native-event-gateway-rejected':[0,0],
 'HttpPopup-synthetic-quarantine-preview-command-refused':[0,0,0],
};
function bodyJournal(spec){
 const s=spec.steps;
 if(spec.root==='HttpMain')return [s[1].expected.state.http.a.active.a,vals(s[2].expected.state.http.a.pending)[0]];
 if(spec.name==='HttpBar-visible-loading-delayed-synchronous-stale-and-queue')return [s[2].expected.state.http.a.active.a,vals(s[7].expected.state.http.a.pending)[0]];
 if(spec.name==='HttpPopup-action-sends-renderer-then-settles')return [s[1].expected.state.http.a.active.a];
 return [];
}
function migrate(original){
 const next=copy(original),cs=counters[next.name],bodies=bodyJournal(original);
 insist(cs&&cs.length===next.steps.length,'undeclared original case/step budget');
 insist(bodies.every(x=>x&&x.$===0)&&bodies.every((x,i)=>bodies.findIndex(y=>eq(x,y))===i),'independent request body journal distinct');
 const kind=next.root==='HttpMain'?'ControllerCommit':'RendererAction';
 function request(body){const i=bodies.findIndex(x=>eq(x,body));insist(i>=0,'request absent from literal body journal');return {id:C('RequestId',U(i+1)),kind:C(kind),body:copy(body),ticket:N()};}
 function http(old,counter){const h=copy(old),m=h.a;insist(h.$==='Model'&&eq(Object.keys(m).sort(),['active','failed','pending','polling','role']),'original complete HTTP shape');m.counter=U(counter);if(next.root==='HttpPopup'){insist(m.role.$==='Renderer','old popup role');m.role=C('PopupRole');}if(m.active.$==='Just')m.active=C('Just',request(m.active.a));m.pending=L(vals(m.pending).map(request));return h;}
 function effects(old){return L(vals(old).map(x=>{if(['SendController','SendRenderer'].includes(x.$)){const q=request(x.a);insist((x.$==='SendController')===(kind==='ControllerCommit'),'old send role');return C('SendRequest',q.id,q.kind,q.body);}return copy(x);}));}
 next.steps.forEach((step,i)=>{
  const e=step.expected;
  e.state.http=http(e.state.http,cs[i]);
  if(next.root==='HttpPopup'){insist(!Object.hasOwn(e.state.popup,'confirmationOutbox'),'old outbox absent');e.state.popup.confirmationOutbox=L([]);}
  e.descriptions.forEach(d=>{if(d.module==='UiHttp')d.effects=effects(d.effects);});
  e.transportReturns.forEach((r,j)=>{
   // Main incoming-policy enqueue has two returns: before/after allocation.
   const counter=next.root==='HttpMain'&&(i===1||i===2)&&j===0?cs[i]-1:cs[i];
   r.value.a=http(r.value.a,counter);r.value.b=effects(r.value.b);
  });
  const previous=i?original.steps[i-1].expected.state.http.a:null;
  if(['postedOk','postedNetworkError'].includes(step.input.kind)&&previous&&previous.active.$==='Just'&&previous.failed.$==='Nothing'){
   const q=request(previous.active.a);
   step.input={...step.input,kind:step.input.kind==='postedOk'?'postedForOk':'postedForNetworkError',requestId:q.id.a.a,requestKind:kind};
  }
 });
 // Exact inverse checks every original assertion and input, not observed state.
 const back=copy(next);
 function lower(h){const m=h.a;insist(m.counter&&m.counter.$==='Counter','counter present');delete m.counter;if(next.root==='HttpPopup'){insist(m.role.$==='PopupRole','popup role');m.role=C('Renderer');}if(m.active.$==='Just')m.active=C('Just',lowerRequest(m.active.a));m.pending=L(vals(m.pending).map(lowerRequest));return h;}
 function lowerRequest(q){const expected=request(q.body);insist(eq(q,expected),'new exact request metadata');return q.body;}
 function lowerEffects(xs){return L(vals(xs).map(x=>{if(x.$==='SendRequest'){const q=request(x.c);insist(eq(x.a,q.id)&&eq(x.b,q.kind),'new exact send metadata');return C(kind==='ControllerCommit'?'SendController':'SendRenderer',x.c);}return x;}));}
 back.steps.forEach((step,i)=>{insist(eq(step.expected.state.http.a.counter,U(cs[i])),'literal counter journal');lower(step.expected.state.http);if(next.root==='HttpPopup'){insist(eq(step.expected.state.popup.confirmationOutbox,L([])),'new outbox empty');delete step.expected.state.popup.confirmationOutbox;}step.expected.descriptions.forEach(d=>{if(d.module==='UiHttp')d.effects=lowerEffects(d.effects);});step.expected.transportReturns.forEach(r=>{lower(r.value.a);r.value.b=lowerEffects(r.value.b);});if(['postedForOk','postedForNetworkError'].includes(step.input.kind)){step.input=copy(original.steps[i].input);}});
 insist(eq(back,original),'ALL original complete assertions failed inverse preservation');
 return next;
}
function build(repository){
 const base=require('./parents/sol-http-popup-literals-0525.cjs').build(repository),peer=require('./parents/httpbar-literals.cjs').build(repository),control=require('./parents/http-popup-control-literals.cjs').build(repository);
 const originals=base.cases.concat(peer.cases),controlOriginals=control.cases;
 insist(originals.length===8&&controlOriginals.length===3,'original whole case counts');
 return {cases:originals.map(migrate),controlCases:controlOriginals.map(migrate),originals,controlOriginals,counters,policyOracle:base.policyOracle};
}
module.exports={build,migrate,counters};
