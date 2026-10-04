'use strict';
const fs=require('fs'),assert=require('assert/strict'),cp=require('child_process'),path=require('path');
const app=require(process.argv[2]).Elm.BatchReplay.init({flags:null}),evidence=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const probe=process.argv[4],out=process.argv[5],copy=x=>JSON.parse(JSON.stringify(x)),native=frame=>({kind:'native',frame}),scope={id:'1',generation:'1'},checks=[];
const timer=setTimeout(()=>{throw Error('bounded local disposition replay timed out')},30000);
function replay(events){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows)};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events)})}
const last=async events=>(await replay(events)).at(-1),check=(name,test)=>{test();checks.push(name)};
function certificate(row){
 const p=path.join(path.dirname(out),'probe-input.json');fs.writeFileSync(p,JSON.stringify({original:JSON.stringify(row.submitted),binding:evidence.geometry52.binding,gate:{publication:row.frame.publication,lease:row.frame.lease,closed:row.frame.lease}}));
 return JSON.parse(cp.execFileSync(probe,[p],{encoding:'utf8'}).trim().split('\n').at(-1));
}
const disposition=frame=>({kind:'disposition',frame});
function outcome(command,status){return {protocolVersion:3,kind:'effect-outcome',binding:command.binding,effectProtocol:command.effectProtocol,intent:command.intent,status,reason:'CPU native outcome control',revision:command.intent.context.revision,outputGeneration:command.intent.context.output}}
function menuOpen(ready,application='elm-maximize-probe'){return {kind:'action',action:{viewProtocol:1,kind:'view-action',scope,action:{surfaceProtocol:2,kind:'surface-context',surface:'bar',publication:ready.frame.publication,lease:ready.frame.lease,id:'bar:group:application:'+application,trigger:'pointer',x:227,y:21}}}}
function select(menu,label){const row=menu.frame.popup.find(r=>r.label===label&&r.enabled);assert(row);return {kind:'action',action:{viewProtocol:1,kind:'view-action',scope,action:{surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:menu.frame.publication,lease:menu.frame.lease,id:row.id}}}}
(async()=>{
 const p=copy(evidence.projection51),g=copy(evidence.geometry52),a=copy(evidence.geometryAttach);p.requestId='1';a.requestId='2';g.requestId='3';
 const baseline=[{kind:'topology',frame:{viewProtocol:1,kind:'view-topology',revision:'1',views:[scope]}},native(evidence.attached),native(p),native({protocolVersion:3,kind:'host-geometry-negotiate'}),native(a),native(g)];
 assert((await last(baseline)).shell.available);
 for(const operation of ['minimize','restore-geometry'])for(const mixed of [false,true]){
  const events=[...baseline,{kind:'direct-native-begin',operation,incarnation:'1',mixed}],sent=await last(events),command=sent.requests.find(r=>r.kind==='window-effect');assert(command);assert.equal(sent.shell.effects.transaction.status,'Pending');
  const cert=certificate(sent),settled=await last([...events,disposition(cert)]);
  check(operation+'/'+mixed+' exact certified Pending locally refuses without native receipt or retry',()=>{assert.equal(settled.shell.effects.transaction.status,'Refused');assert.equal(settled.unresolvedFull.length,0);assert.equal(settled.issued.length,0);assert.equal(settled.shell.effects.request,sent.shell.effects.request);assert.equal(settled.shell.effects.generation,sent.shell.effects.generation);assert(!settled.requests.some(r=>r.kind==='window-effect'));assert.deepEqual(settled.geometry,sent.geometry)});
  if(mixed)check(operation+' mixed cert recovers observations with fresh IDs',()=>{assert.equal(settled.requests.length,2);assert(settled.requests.every(r=>r.kind!=='window-effect'&&BigInt(r.requestId)>BigInt(sent.correlation.geometry)))});
  const repeated=await last([...events,disposition(cert),disposition(cert)]);
  check(operation+'/'+mixed+' duplicate proof is consumed once',()=>{assert.deepEqual(repeated.shell.effects,settled.shell.effects);assert.equal(repeated.requests.length,0)});
  for(const state of ['admitted','uncertain']){const changed=copy(cert);changed.disposition=state;const r=await last([...events,disposition(changed)]);check(operation+'/'+mixed+' '+state+' retains original Pending full key',()=>{assert.deepEqual(r.issued,sent.issued);assert.deepEqual(r.unresolvedFull,sent.unresolvedFull);assert.equal(r.shell.effects.transaction.status,'Pending');assert(!r.requests.some(r=>r.kind==='window-effect'))})}
  for(const status of ['Unknown','Committed','Refused']){const ended=[...events,native(outcome(command,status))],before=await last(ended),after=await last([...ended,disposition(cert)]);check(operation+'/'+mixed+' existing real '+status+' outcome cannot be overwritten by local proof',()=>{assert.deepEqual(after.issued,before.issued);assert.deepEqual(after.unresolvedFull,before.unresolvedFull);assert.deepEqual(after.shell.effects,before.shell.effects);assert(!after.requests.some(r=>r.kind==='window-effect'))})}
  if(!mixed){
   const moved=[...events,{kind:'open'}],different=await last(moved);assert.notEqual(different.frame.lease,sent.frame.lease);assert.equal(different.frame.mode,'applications');
   const released=await last([...moved,disposition(cert)]);
   check(operation+' exact stored operation proof survives popup lease change without closing newer UI',()=>{assert.equal(released.shell.effects.transaction.status,'Refused');assert.equal(released.issued.length,0);assert.equal(released.frame.mode,'applications');assert.equal(released.frame.lease,different.frame.lease);assert(!released.requests.some(r=>r.kind==='window-effect'))});
  }
  for(const [name,mutate]of [['binding',c=>c.binding.frontend='999'],['protocol',c=>{const b=JSON.parse(c.batch);b.requests.find(r=>r.kind==='window-effect').effectProtocol=3;c.batch=JSON.stringify(b)}],['incarnation',c=>{const b=JSON.parse(c.batch);b.requests.find(r=>r.kind==='window-effect').intent.incarnation='999';c.batch=JSON.stringify(b)}],['request',c=>{const b=JSON.parse(c.batch);b.requests.find(r=>r.kind==='window-effect').intent.request='999';c.batch=JSON.stringify(b)}],['context',c=>{const b=JSON.parse(c.batch);b.requests.find(r=>r.kind==='window-effect').intent.context.revision='999';c.batch=JSON.stringify(b)}],['scope',c=>c.scope.generation='999']]){const bad=copy(cert);mutate(bad);const r=await last([...events,disposition(bad)]);check(operation+'/'+mixed+' altered '+name+' cannot retire original operation',()=>{assert.deepEqual(r.issued,sent.issued);assert.deepEqual(r.unresolvedFull,sent.unresolvedFull);assert(!r.requests.some(r=>r.kind==='window-effect'))})}
 }
 for(const label of ['Minimize','Restore']){
  const ready=await last(baseline),opened=[...baseline,menuOpen(ready)],menu=await last(opened),chosen=[...opened,select(menu,label)],prepared=await last(chosen);assert(prepared.prepared);
  const freshP=copy(p),freshG=copy(g);freshP.requestId=prepared.correlation.legacy;freshG.requestId=prepared.correlation.geometry;
  const events=[...chosen,native(freshP),native(freshG)],sent=await last(events),command=sent.requests.find(r=>r.kind==='window-effect');assert(command);assert.equal(sent.registry,1);assert.equal(sent.outstanding,1);
  const cert=certificate(sent),settled=await last([...events,disposition(cert)]);
  check(label+' exact native→local menu mapping terminates only original reservation',()=>{assert.equal(settled.registry,0);assert.equal(settled.outstanding,0);assert.equal(settled.issued.length,0);assert.equal(settled.unresolvedFull.length,0);assert.equal(settled.shell.effects.transaction.status,'Refused');assert(!settled.requests.some(r=>r.kind==='window-effect'))});
  const late=await last([...events,disposition(cert),native(outcome(command,'Committed'))]);
  check(label+' late original native outcome is stale after definite local refusal',()=>{assert.equal(late.shell.effects.transaction.status,'Refused');assert.equal(late.outstanding,0);assert.equal(late.registry,0);assert(!late.requests.some(r=>r.kind==='window-effect'))});
 }
 // Preserve an unrelated menu actor B actual Unknown mapping while retiring A.
 const twoP=copy(p),twoG=copy(g),bP=copy(p.scene.windows[0]),bG=copy(g.facts.windows[0]);bP.incarnation='20';bP.application='actor-b';bP.label='Actor B';bG.incarnation='20';twoP.scene.windows.push(bP);twoG.facts.windows.push(bG);
 const twoBase=baseline.map((e,i)=>i===2?native(twoP):i===5?native(twoG):e),ready=await last(twoBase),opened=[...twoBase,menuOpen(ready,'actor-b')],menu=await last(opened),chosen=[...opened,select(menu,'Restore')],prepared=await last(chosen);
 const bp=copy(twoP),bg=copy(twoG);bp.requestId=prepared.correlation.legacy;bg.requestId=prepared.correlation.geometry;
 const bSent=[...chosen,native(bp),native(bg)],bDispatch=await last(bSent),bCommand=bDispatch.requests.find(r=>r.kind==='window-effect');assert(bCommand);
 const uncertain=[...bSent,native(outcome(bCommand,'Unknown'))],refreshing=await last(uncertain),rp=copy(twoP),rg=copy(twoG);rp.requestId=refreshing.correlation.legacy;rg.requestId=refreshing.correlation.geometry;
 const stable=[...uncertain,native(rp),native(rg)],bReady=await last(stable);assert(bReady.shell.available);assert.equal(bReady.registry,1);
 const aEvents=[...stable,{kind:'direct-native-begin',operation:'minimize',incarnation:'1',mixed:true}],aSent=await last(aEvents),aCert=certificate(aSent),aDone=await last([...aEvents,disposition(aCert)]);
 check('unrelated actor B actual Unknown full native/local key survives A local refusal and mixed query recovery',()=>{assert.equal(aDone.registry,1);assert.equal(aDone.outstanding,1);assert.deepEqual(aDone.issued,bReady.issued);assert.deepEqual(aDone.unresolvedFull,bReady.unresolvedFull);assert(!aDone.requests.some(r=>r.kind==='window-effect'))});
 const bTerminal=await last([...aEvents,disposition(aCert),native(outcome(bCommand,'Committed'))]);
 check('unrelated B definitive original-key receipt still routes after A local refusal',()=>{assert.equal(bTerminal.registry,0);assert.equal(bTerminal.outstanding,0);assert.equal(bTerminal.issued.length,0);assert.equal(bTerminal.unresolvedFull.length,0);assert(!bTerminal.requests.some(r=>r.kind==='window-effect'))});
 fs.writeFileSync(out,JSON.stringify({passed:true,checks,scope:'Compiled shared controller+unchanged actual C proof; Pending-only local terminal, native receipt controls synthetic CPU only',nativeAcceptance:false},null,2)+'\n');clearTimeout(timer);
})().catch(e=>{fs.writeFileSync(out,JSON.stringify({passed:false,checks,error:String(e)},null,2)+'\n');clearTimeout(timer);console.error(e.stack);process.exitCode=1});
