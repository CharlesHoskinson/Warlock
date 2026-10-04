'use strict';
const assert=require('assert/strict');
// The trace itself gains the two observation steps. Returned rows are never
// rewritten, filtered, or relabelled; all final oracles see real worker output.
module.exports=replay=>async function stage(events){
 const selected=(await replay(events)).at(-1);
 const before=(await replay(events.slice(0,-1))).at(-1);
 assert(selected.preparedToken,'valid selected action must reserve a preparation');
 assert.equal(selected.frame.mode,'closed');
 assert.equal(selected.registry,before.registry,'no native receipt key before close facts');
 assert.equal(selected.shell.effects.request,before.shell.effects.request,'no native request before close facts');
 assert.equal(selected.shell.effects.generation,before.shell.effects.generation,'no native generation before close facts');
 assert.equal(selected.outstanding,before.outstanding+1,'one bounded local reservation');
 assert(selected.requests.every(r=>['projection-request','geometry-facts-request'].includes(r.kind)));
 const copy=x=>JSON.parse(JSON.stringify(x));
 const last=kind=>events.slice().reverse().find(e=>e.kind==='native'&&e.frame.kind===kind)?.frame;
 const p=copy(last('action-projection'));
 const projection=selected.requests.find(r=>r.kind==='projection-request');
 assert(projection);p.requestId=projection.requestId;
 const next=[...events,{kind:'native',frame:p}];
 const geometry=selected.requests.find(r=>r.kind==='geometry-facts-request');
 if(geometry){
  const partial=(await replay(next)).at(-1);
  assert.equal(partial.registry,before.registry);
  assert.equal(partial.shell.effects.request,before.shell.effects.request);
  assert(partial.preparedToken,'one stream cannot dispatch');
  const g=copy(last('geometry-facts'));g.requestId=geometry.requestId;
  next.push({kind:'native',frame:g});
 }
 const admitted=(await replay(next)).at(-1);
 assert.equal(admitted.preparedToken,null,'exact compatible observations must complete preparation');
 assert.equal(admitted.requests.length,1,'one command after complete close-fenced observations');
 assert.equal(admitted.requests[0].kind,'window-effect');
 assert.equal(admitted.registry,before.registry+1);
 return next;
};
