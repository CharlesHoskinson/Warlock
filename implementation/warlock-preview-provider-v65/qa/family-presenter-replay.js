'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {Elm} = require(path.resolve(process.argv[2]));
const fixture = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
let checks = 0;
function worker() {
  const app = Elm.PreviewPresenterReplay.init(); let pending = null;
  app.ports.outgoing.subscribe(value => {assert(pending); const done = pending; pending = null; done(value);});
  return (kind, value) => new Promise((resolve, reject) => {
    assert.equal(pending, null); const timer = setTimeout(() => reject(new Error('Original compiled presenter deadline')), 3000);
    pending = result => {clearTimeout(timer); resolve(result);}; app.ports.incoming.send({kind,value});
  });
}
(async () => {
  const source = fixture.scopes[2]; const identity = 'family:'+source.scope.context.incarnation;
  const send = worker();
  await send('presentation',{surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[{id:identity,domId:'family',label:'Family',ariaLabel:'Family',detail:'',enabled:true}]});
  let result = await send('native',{kind:'source-seed',publication:'1',lease:'1',identity,source,title:'Native family sample',application:'Native family'});
  assert.equal(result.models.length,1);assert.equal(result.models[0].model.demand,true);checks+=2;
  const trigger = {binding:source.scope.binding,context:source.scope.context,origin:'1',clock:source.scope.clock,deadline:String(BigInt(source.scope.now)+2000000000n)};
  result = await send('native',{kind:'event',identity,event:{kind:'request',trigger}});assert.equal(result.commands[0].commands[0].kind,'acquire');checks++;
  const job = result.commands[0].commands[0].job;
  const frame = {job,handle:'1'.repeat(64),owned:true,signaled:false,fidelity:'family',coverage:['client','decoration','modal','popup'],expires:String(BigInt(source.scope.now)+5000000000n)};
  const prior = result.models;
  const client = structuredClone(frame);client.fidelity='client';client.coverage=['client'];
  result = await send('native',{kind:'event',identity,event:{kind:'offer',frame:client}});assert.deepEqual(result.models,prior);assert.equal(result.commands.length,0);checks+=2;
  result = await send('native',{kind:'event',identity,event:{kind:'offer',frame}});assert(result.models[0].model.candidate);checks++;
  const ready = {...frame,signaled:true};result=await send('native',{kind:'event',identity,event:{kind:'fence',frame:ready}});assert.equal(result.models[0].model.accepted.fidelity,'family');checks++;
  const held = result.models;const wrong = {...ready,coverage:['client','decoration','modal']};
  result=await send('native',{kind:'event',identity,event:{kind:'expired',frame:wrong}});assert.deepEqual(result.models,held);assert.equal(result.commands.length,0);checks+=2;
  result=await send('native',{kind:'event',identity,event:{kind:'expired',frame:ready}});assert.equal(result.commands[0].commands[0].kind,'release');checks++;
  const pending = result.models;
  result=await send('native',{kind:'event',identity,event:{kind:'receipt',sequence:'1',event:{kind:'released',frame:{...ready,fidelity:'client',coverage:['client']}}}});assert.deepEqual(result.models,pending);assert.equal(result.commands.length,0);checks+=2;
  result=await send('native',{kind:'event',identity,event:{kind:'receipt',sequence:'1',event:{kind:'released',frame:ready}}});assert.equal(result.commands[0].commands[0].kind,'acknowledge');assert.equal(result.models[0].model.known.length,0);checks+=2;
  process.stdout.write(JSON.stringify({passed:true,checks,nativeAcceptance:false,scope:'Actual optimized single Popup-shared presenter/lifecycle typed family source/packet/retained receipt replay; no WebKit or new native effects.'})+'\n');
})().catch(e => {process.stderr.write(e.stack+'\n');process.exitCode=1;});
