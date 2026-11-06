'use strict';
// Independent representation migration of the original two literal histories.
// This file imports no production reducer or compiled output.
const {isDeepStrictEqual} = require('node:util');
const five = require('./parents/joined-control-literals.cjs');
const eleven = require('./parents/closed-topology-after-dismiss-literals.cjs');
const copy = x => JSON.parse(JSON.stringify(x));
const C = (tag,...args) => Object.fromEntries([['$',tag],...args.map((x,i)=>[String.fromCharCode(97+i),x])]);
const N = () => C('Nothing');
const U = n => C('Counter',String(n));
const L = xs => xs.reduceRight((tail,x)=>C('::',x,tail),C('[]'));
const insist = (ok,why) => {if(!ok) throw new Error(why);};
function values(list) {
  const out=[];
  while(list && list.$==='::') {out.push(list.a);list=list.b;}
  insist(list && list.$==='[]','malformed literal list');
  return out;
}
// Each tuple is [counter, active request id]. null means no active request.
// Return tuples describe EACH actual UiHttp transition return, in order.
const prefix = Object.freeze([
  {state:[0,null],returns:[]},
  {state:[0,null],returns:[]},
  {state:[1,1],returns:[[0,null],[1,1]],send:1},
  {state:[0,null],returns:[[0,null]]},
  {state:[0,null],returns:[[0,null]]},
]);
const extension = Object.freeze([
  {state:[1,null],returns:[[1,null]],completion:1},
  {state:[2,2],returns:[[1,null],[2,2]],send:2},
  {state:[0,null],returns:[[0,null]]},
  {state:[0,null],returns:[[0,null]]},
  {state:[2,null],returns:[[2,null]],completion:2},
  {state:[2,null],returns:[[2,null]]},
]);
const journals = Object.freeze({
  'HttpJoined-open-given-dismiss-closed-presentation':prefix,
  'HttpJoined-dismiss-then-closed-empty-topology':prefix.concat(extension),
});
function liftHttp(old,root,entry) {
  const next=copy(old), m=next.a, [counter,active]=entry;
  insist(next.$==='Model' && isDeepStrictEqual(Object.keys(m).sort(),['active','failed','pending','polling','role']), 'unexpected original complete HTTP record');
  insist(values(m.pending).length===0,'these original histories have no pending request');
  if(root==='HttpPopup') {
    insist(m.role.$==='Renderer','original popup role changed');
    m.role=C('PopupRole');
  } else insist(root==='HttpMain' && m.role.$==='Controller','unexpected original controller role');
  m.counter=U(counter);
  if(active===null) insist(m.active.$==='Nothing','original active slot differs from journal');
  else {
    insist(m.active.$==='Just' && m.active.a.$===0 && root==='HttpMain','original commit body absent');
    m.active=C('Just',{id:C('RequestId',U(active)),kind:C('ControllerCommit'),body:m.active.a,ticket:N()});
  }
  return next;
}
function lowerHttp(current,root,entry) {
  const old=copy(current),m=old.a,[counter,active]=entry;
  insist(isDeepStrictEqual(m.counter,U(counter)),'derived counter differs from independent journal');
  delete m.counter;
  if(root==='HttpPopup') {insist(m.role.$==='PopupRole','derived popup role changed');m.role=C('Renderer');}
  if(active!==null) {
    const q=m.active.a;
    insist(m.active.$==='Just' && isDeepStrictEqual(Object.keys(q).sort(),['body','id','kind','ticket']) &&
      isDeepStrictEqual(q.id,C('RequestId',U(active))) && q.kind.$==='ControllerCommit' && q.ticket.$==='Nothing', 'derived request metadata differs');
    m.active=C('Just',q.body);
  } else insist(m.active.$==='Nothing','unexpected derived active request');
  return old;
}
function liftEffects(old,id) {
  return L(values(old).map(effect=>{
    if(effect.$==='SendController') {
      insist(id===1 || id===2,'controller send absent from independent journal');
      return C('SendRequest',C('RequestId',U(id)),C('ControllerCommit'),copy(effect.a));
    }
    insist(effect.$!=='SendRenderer','original joined histories cannot send renderer actions');
    return copy(effect);
  }));
}
function lowerEffects(current,id) {
  return L(values(current).map(effect=>{
    if(effect.$==='SendRequest') {
      insist(isDeepStrictEqual(effect.a,C('RequestId',U(id))) && effect.b.$==='ControllerCommit','derived send identity/kind differs');
      return C('SendController',copy(effect.c));
    }
    return copy(effect);
  }));
}
function lift(original) {
  const next=copy(original),journal=journals[next.name];
  insist(journal && journal.length===next.steps.length,'original ordered step budget differs');
  next.steps.forEach((step,index)=>{
    const item=journal[index],root=step.root,e=step.expected;
    e.state.http=liftHttp(e.state.http,root,item.state);
    if(root==='HttpPopup') {
      insist(!Object.hasOwn(e.state.popup,'confirmationOutbox'),'original literal already has a new outbox');
      e.state.popup.confirmationOutbox=L([]);
    }
    e.descriptions.forEach(description=>{
      if(description.module==='UiHttp') description.effects=liftEffects(description.effects,item.send);
    });
    insist(e.transportReturns.length===item.returns.length,'original transport return budget differs');
    e.transportReturns.forEach((returned,k)=>{
      insist(returned.kind==='transition' && returned.value.$==='#3','original return shape changed');
      returned.value.a=liftHttp(returned.value.a,root,item.returns[k]);
      returned.value.b=liftEffects(returned.value.b,item.send);
    });
    if(item.completion) {
      insist(step.input.kind==='postedOk' && step.input.body==='','original completion position/body changed');
      step.input={kind:'postedForOk',body:'',requestId:String(item.completion),requestKind:'ControllerCommit'};
    }
  });
  return next;
}
function project(current) {
  const old=copy(current),journal=journals[old.name];
  old.steps.forEach((step,index)=>{
    const item=journal[index],root=step.root,e=step.expected;
    e.state.http=lowerHttp(e.state.http,root,item.state);
    if(root==='HttpPopup') {
      insist(isDeepStrictEqual(e.state.popup.confirmationOutbox,L([])),'new outbox must be asserted empty in original histories');
      delete e.state.popup.confirmationOutbox;
    }
    e.descriptions.forEach(description=>{
      if(description.module==='UiHttp') description.effects=lowerEffects(description.effects,item.send);
    });
    e.transportReturns.forEach((returned,k)=>{
      returned.value.a=lowerHttp(returned.value.a,root,item.returns[k]);
      returned.value.b=lowerEffects(returned.value.b,item.send);
    });
    if(item.completion) {
      insist(isDeepStrictEqual(step.input,{kind:'postedForOk',body:'',requestId:String(item.completion),requestKind:'ControllerCommit'}),'derived callback identity changed');
      step.input={kind:'postedOk',body:''};
    }
  });
  return old;
}
function build(repository) {
  const originals=five.build(repository).cases.concat(eleven.build(repository).cases);
  insist(originals.length===2 && originals[0].steps.length===5 && originals[1].steps.length===11,'original five/eleven case inventory changed');
  insist(isDeepStrictEqual(originals[1].steps.slice(0,5),originals[0].steps),'original five-step prefix differs');
  const cases=originals.map(lift);
  cases.forEach((derived,index)=>insist(isDeepStrictEqual(project(derived),originals[index]),'original complete model/effect/input assertions did not round-trip'));
  insist(isDeepStrictEqual(cases[1].steps.slice(0,5),cases[0].steps),'derived five-step prefix differs');
  return {schema:1,originals,cases,journals,coverage:{complete:false,originalAcceptanceClaim:false,nativeAcceptance:false,
    limits:['original independent literal GIVEN, not runtime reachability','source-derived Owner projection only',
      'new request identity journal is independently specified, not observed','legacy error preserves fail-closed original; empty legacy success cannot acknowledge']}};
}
module.exports={build,project,journals};
