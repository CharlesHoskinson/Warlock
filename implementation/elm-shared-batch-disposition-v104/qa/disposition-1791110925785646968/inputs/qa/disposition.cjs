'use strict';
const fs=require('fs'),assert=require('assert/strict'),cp=require('child_process'),path=require('path');
const app=require(process.argv[2]).Elm.BatchReplay.init({flags:null}),evidence=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const probe=process.argv[4],out=process.argv[5],copy=x=>JSON.parse(JSON.stringify(x)),native=frame=>({kind:'native',frame}),scope={id:'1',generation:'1'},checks=[];
const timer=setTimeout(()=>{throw Error('bounded CPU disposition replay timed out')},30000);
function replay(events){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows)};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events)})}
const last=async events=>(await replay(events)).at(-1),check=(name,test)=>{test();checks.push(name)};
function certificate(row,gate){
 const p=path.join(path.dirname(out),'probe-input.json');fs.writeFileSync(p,JSON.stringify({original:JSON.stringify(row.submitted),binding:evidence.geometry52.binding,gate}));
 const text=cp.execFileSync(probe,[p],{encoding:'utf8'});return JSON.parse(text.trim().split('\n').at(-1));
}
const disposition=frame=>({kind:'disposition',frame});
(async()=>{
 const p=copy(evidence.projection51),g=copy(evidence.geometry52),a=copy(evidence.geometryAttach);p.requestId='1';a.requestId='2';g.requestId='3';
 const baseline=[{kind:'topology',frame:{viewProtocol:1,kind:'view-topology',revision:'1',views:[scope]}},native(evidence.attached),native(p),native({protocolVersion:3,kind:'host-geometry-negotiate'}),native(a),native(g)];
 const ready=await last(baseline);assert(ready.shell.available);
 const open={kind:'action',action:{viewProtocol:1,kind:'view-action',scope,action:{surfaceProtocol:2,kind:'surface-context',surface:'bar',publication:ready.frame.publication,lease:ready.frame.lease,id:'bar:group:application:elm-maximize-probe',trigger:'pointer',x:227,y:21}}};
 const opened=[...baseline,open],menu=await last(opened),notification=native({protocolVersion:3,kind:'host-refresh'}),pendingEvents=[...opened,notification],pending=await last(pendingEvents);
 assert.equal(pending.frame.mode,'menu');assert.equal(pending.requests.length,2);
 const cert=certificate(pending,{publication:menu.frame.publication,lease:menu.frame.lease,closed:menu.frame.lease});
 const dismissal={kind:'dismiss',frame:{scope,lease:menu.frame.lease}},lost=[...pendingEvents,dismissal,notification],stranded=await last(lost);
 check('actual recorded retirement ordering strands both unsent correlations without disposition',()=>{assert.equal(stranded.requests.length,0);assert.deepEqual(stranded.correlation,(awaitValue=>awaitValue)(pending.correlation));assert.equal(stranded.shell.available,false)});
 const recovered=await last([...lost,disposition(cert)]);
 check('actual C preflight-unsent exact original string recovers shared Main registration after popup owner cleared',()=>{assert.equal(recovered.frame.mode,'closed');assert.equal(recovered.requests.length,2);assert.notEqual(recovered.correlation.legacy,pending.correlation.legacy);assert.notEqual(recovered.correlation.geometry,pending.correlation.geometry);assert.equal(recovered.registry,0);assert.equal(recovered.outstanding,0)});
 check('fresh observation IDs strictly exceed rejected originals; no effect replay',()=>{assert(recovered.requests.every(r=>BigInt(r.requestId)>BigInt(pending.requests[1].requestId)));assert.equal(recovered.shell.effects.request,'0')});
 const duplicate=await last([...lost,disposition(cert),disposition(cert)]);
 check('exact duplicate is consumed once',()=>{assert.equal(duplicate.requests.length,0);assert.deepEqual(duplicate.correlation,recovered.correlation)});
 const hp=copy(p),hg=copy(g);hp.requestId=pending.requests[0].requestId;hg.requestId=pending.requests[1].requestId;
 const stale=await last([...lost,disposition(cert),native(hp),native(hg)]);
 check('late rejected request IDs cannot satisfy fresh expected slots',()=>{assert.deepEqual(stale.correlation,recovered.correlation);assert.equal(stale.shell.available,false)});
 const freshP=copy(p),freshG=copy(g);freshP.requestId=recovered.correlation.legacy;freshP.scene.windows=[];freshP.scene.focused=null;freshP.scene.revision=freshP.context.revision=String(BigInt(p.scene.revision)+1n);freshG.requestId=recovered.correlation.geometry;freshG.sequence=String(BigInt(g.sequence)+1n);freshG.revision=String(BigInt(g.revision)+1n);freshG.facts.windows=[];freshG.facts.focused=null;
 const retired=await last([...lost,disposition(cert),native(freshP),native(freshG)]);
 check('CPU synthetic retirement control admits fresh correlated facts and removes target',()=>{assert(retired.shell.available);assert.equal(retired.geometry.windows.length,0)});
 const bads=[['wrong kind',c=>c.kind='wrong'],['wrong protocol',c=>c.viewProtocol=2],['wrong disposition',c=>c.disposition='refused'],['wrong scope',c=>c.scope.id='2'],['wrong generation',c=>c.scope.generation='2'],['zero scope',c=>c.scope.id='0'],['wrong topology revision',c=>c.revision='2'],['wrong publication',c=>c.publication=String(BigInt(c.publication)+1n)],['wrong lease',c=>c.lease='999'],['wrong binding',c=>c.binding.frontend='2'],['noncanonical counter',c=>c.publication='01'],['extra field',c=>c.extra=true],['missing binding',c=>delete c.binding],['batch object instead of literal string',c=>c.batch=JSON.parse(c.batch)],['altered request order',c=>{const b=JSON.parse(c.batch);b.requests.reverse();c.batch=JSON.stringify(b)}],['altered request ID',c=>{const b=JSON.parse(c.batch);b.requests[0].requestId='999';c.batch=JSON.stringify(b)}],['altered request binding',c=>{const b=JSON.parse(c.batch);b.requests[0].binding.frontend='999';c.batch=JSON.stringify(b)}],['batch over byte bound',c=>c.batch='😀'.repeat(40000)]];
 for(const [name,change]of bads){const bad=copy(cert);change(bad);const result=await last([...lost,disposition(bad)]);check(name+' cannot consume or clear observations',()=>{assert.deepEqual(result.correlation,stranded.correlation);assert.equal(result.requests.length,0);assert.equal(result.batchCount,stranded.batchCount)})}
 for(const state of ['admitted','uncertain']){const other=copy(cert);other.disposition=state;const r=await last([...lost,disposition(other)]);check(state+' never proves unsent observations',()=>{assert.deepEqual(r.correlation,stranded.correlation);assert.equal(r.requests.length,0);assert.equal(r.batchCount,stranded.batchCount-1)})}
 const replacement={kind:'topology',frame:{viewProtocol:1,kind:'view-topology',revision:'2',views:[{id:'1',generation:'2'}]}};
 const replaced=await last([...lost,replacement,disposition(cert)]);
 check('retired/replaced scope cannot reauthorize old batch; old records retire without erasing intent ledger',()=>{assert.equal(replaced.batchCount,0);assert.equal(replaced.shell.effects.request,'0');assert.equal(replaced.requests.length,0)});
 // Invoke the actual typed native operation through the QA-only input route.
 for(const mixed of [false,true]){
  const effectEvents=[...baseline,{kind:'direct-native-begin',operation:'minimize',incarnation:'1',mixed}],effect=await last(effectEvents);
  assert(effect.requests.some(r=>r.kind==='window-effect'));
  const gate={publication:effect.frame.publication,lease:effect.frame.lease,closed:effect.frame.lease},ec=certificate(effect,gate);
  const er=await last([...effectEvents,disposition(ec)]);
  check((mixed?'mixed':'operation-only')+' exact unsent certificate preserves actual Pending intent/full issued key; no retry',()=>{assert.deepEqual(er.unresolved,effect.unresolved);assert.deepEqual(er.shell.effects.transaction,effect.shell.effects.transaction);assert.equal(er.shell.effects.request,effect.shell.effects.request);assert(!er.requests.some(r=>r.kind==='window-effect'))});
  const command=effect.requests.find(r=>r.kind==='window-effect'),unknown={protocolVersion:3,kind:'effect-outcome',binding:command.binding,effectProtocol:command.effectProtocol,intent:command.intent,status:'Unknown',reason:'held-test',revision:command.intent.context.revision,outputGeneration:command.intent.context.output};
  const unknownBefore=await last([...effectEvents,native(unknown)]);assert(unknownBefore.unresolved.some(r=>r.status==='Unknown'));const unknownAfter=await last([...effectEvents,native(unknown),disposition(ec)]);
  check((mixed?'mixed':'operation-only')+' exact original-key Unknown survives late unsent disposition',()=>{assert.deepEqual(unknownAfter.unresolved,unknownBefore.unresolved);assert.equal(unknownAfter.shell.effects.request,unknownBefore.shell.effects.request);assert(!unknownAfter.requests.some(r=>r.kind==='window-effect'))});
 }
 fs.writeFileSync(out,JSON.stringify({passed:true,checks,scope:'Actual compiled shared registration/Controller and actual C preflight/certificate; exact recorded producer fields, CPU-only synthetic retirement control; operation terminal/recovery incomplete',nativeAcceptance:false,cert,pending,stranded,recovered,retired},null,2)+'\n');clearTimeout(timer);
})().catch(e=>{fs.writeFileSync(out,JSON.stringify({passed:false,checks,error:String(e)},null,2)+'\n');clearTimeout(timer);console.error(e.stack);process.exitCode=1});
