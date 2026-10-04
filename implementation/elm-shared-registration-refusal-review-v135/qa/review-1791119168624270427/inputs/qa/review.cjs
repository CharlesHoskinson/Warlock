'use strict';
const fs=require('fs'),assert=require('assert/strict');
const app=require(process.argv[2]).Elm.BatchReplay.init({flags:null}),e=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),out=process.argv[4],copy=x=>JSON.parse(JSON.stringify(x));
const native=frame=>({kind:'native',frame}),scope={id:'1',generation:'1'},checks=[],findings=[],traces={};
const timer=setTimeout(()=>{throw Error('bounded CPU review timeout')},30000);
const replay=events=>new Promise(resolve=>{const cb=r=>{app.ports.outgoing.unsubscribe(cb);resolve(r)};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events)}),last=async t=>(await replay(t)).at(-1);
const check=(name,test)=>{test();checks.push(name)};
(async()=>{
 const p=copy(e.projection51),g=copy(e.geometry52),a=copy(e.geometryAttach);p.requestId='1';a.requestId='2';g.requestId='3';
 const baseline=[{kind:'topology',frame:{viewProtocol:1,kind:'view-topology',revision:'1',views:[scope]}},native(e.attached),native(p),native({protocolVersion:3,kind:'host-geometry-negotiate'}),native(a),native(g)],ready=await last(baseline);assert(ready.shell.available);
 const noScope=await last([native(e.attached)]);traces.noScope=noScope;
 check('missing scope suppresses actual projection send but retains allocated expected ID',()=>{assert.equal(noScope.submitted,null);assert.equal(noScope.requests.length,0);assert.equal(noScope.attemptedRequests[0].kind,'projection-request');assert(noScope.correlation.legacy)});
 findings.push({kind:'read-stranding',cause:'missing-live-scope',expected:noScope.correlation.legacy});
 const later=await last([native(e.attached),native({protocolVersion:3,kind:'host-refresh'})]);
 check('refresh without scope cannot discharge never-submitted expected read',()=>{assert.equal(later.submitted,null);assert.equal(later.correlation.legacy,noScope.correlation.legacy);assert(!later.shell.available)});
 // Fill inventory with actual projection refreshes and admitted synthetic observation responses.
 let capacity=[...baseline],row=ready;
 while(row.batchCount<16){capacity.push(native({protocolVersion:3,kind:'host-refresh'}));row=await last(capacity);assert(row.submitted);const np=copy(p),ng=copy(g);np.requestId=row.correlation.legacy;ng.requestId=row.correlation.geometry;capacity.push(native(np),native(ng));row=await last(capacity);assert(row.shell.available)}
 for(const operation of ['minimize','restore-geometry']){
  const blocked=await last([...capacity,{kind:'direct-native-begin',operation,incarnation:'1'}]);traces[operation]=blocked;
  check(operation+' real reducer issues Pending but full inventory sends nothing',()=>{assert.equal(blocked.batchCount,16);assert.equal(blocked.submitted,null);assert.equal(blocked.requests.length,0);assert.equal(blocked.attemptedRequests[0].kind,'window-effect');assert.equal(blocked.issued.length,1);assert.equal(blocked.unresolvedFull[0].status,'Pending');assert.equal(blocked.shell.effects.transaction.status,'Pending')});
  const after=await last([...capacity,{kind:'direct-native-begin',operation,incarnation:'1'},native({protocolVersion:3,kind:'host-refresh'})]);
  check(operation+' ordinary refresh preserves original never-sent Pending barrier',()=>{assert.deepEqual(after.issued,blocked.issued);assert.deepEqual(after.unresolvedFull,blocked.unresolvedFull);assert(!after.shell.available);assert.equal(after.submitted,null)});
  findings.push({kind:'operation-stranding',cause:'inventory-16',protocol:operation==='minimize'?1:2,issued:blocked.issued});
 }
 for(const [name,extra] of [['request-count',{registerCopies:17}],['UTF8-byte-bound',{registerFocus:'😀'.repeat(40000)}]]){
  const blocked=await last([...baseline,{kind:'direct-native-begin',operation:'minimize',incarnation:'1',...extra}]);traces[name]=blocked;
  check(name+' registration-only stress suppresses transport and retains actual Pending key',()=>{assert.equal(blocked.submitted,null);assert.equal(blocked.requests.length,0);assert.equal(blocked.issued.length,1);assert.equal(blocked.unresolvedFull[0].status,'Pending')});
  const next=await last([...baseline,{kind:'direct-native-begin',operation:'minimize',incarnation:'1',...extra},native({protocolVersion:3,kind:'host-refresh'})]);
  check(name+' exhaustion remains latched after refused registration',()=>{assert.equal(next.submitted,null);assert.deepEqual(next.issued,blocked.issued)});
 }
 const notification=[...capacity,native({protocolVersion:3,kind:'host-refresh'})],readBlocked=await last(notification);traces.readCapacity=readBlocked;
 check('full inventory strands both newly allocated read slots before forwarding',()=>{assert.equal(readBlocked.submitted,null);assert(readBlocked.correlation.legacy&&readBlocked.correlation.geometry);assert.equal(readBlocked.attemptedRequests.length,2)});
 const quiet=await last([...notification,native({protocolVersion:3,kind:'host-refresh'})]);
 check('subsequent notification does not replace never-sent read IDs',()=>{assert.deepEqual(quiet.correlation,readBlocked.correlation);assert.equal(quiet.requests.length,0)});
 // Menu stage1 reserves local intent; no native key exists yet. Full inventory refuses its paired observations.
 const openedTrace=[...capacity,{kind:'action',action:{viewProtocol:1,kind:'view-action',scope,action:{surfaceProtocol:2,kind:'surface-context',surface:'bar',publication:row.frame.publication,lease:row.frame.lease,id:'bar:group:application:elm-maximize-probe',trigger:'pointer',x:227,y:21}}}],opened=await last(openedTrace),control=opened.frame.popup.find(x=>x.label==='Restore'&&x.enabled);assert(control);
 const prepared=await last([...openedTrace,{kind:'action',action:{viewProtocol:1,kind:'view-action',scope,action:{surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:opened.frame.publication,lease:opened.frame.lease,id:control.id}}}]);traces.menuPrepared=prepared;
 check('menu local reservation survives paired-read non-submission with no native issued key',()=>{assert.equal(prepared.submitted,null);assert(prepared.preparedToken);assert.equal(prepared.outstanding,1);assert.equal(prepared.registry,0);assert.equal(prepared.issued.length,0);assert.equal(prepared.attemptedRequests.length,2)});
 const expired=await last([...openedTrace,{kind:'action',action:{viewProtocol:1,kind:'view-action',scope,action:{surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:opened.frame.publication,lease:opened.frame.lease,id:control.id}}},{kind:'prepared-deadline',token:prepared.preparedToken}]);
 check('menu prepared deadline retires local-only intent but transport remains exhausted',()=>{assert.equal(expired.outstanding,0);assert.equal(expired.preparedToken,null);assert.equal(expired.registry,0);assert.equal(expired.submitted,null)});
 fs.writeFileSync(out,JSON.stringify({passed:true,checks,findings,traces,scope:'Actual compiled controller; known local non-submission evidence, no native certificate/receipt manufactured; request-count and UTF8 tests stress only register boundary',nativeAcceptance:false,usabilityAcceptance:false},null,2)+'\n');clearTimeout(timer);
})().catch(err=>{fs.writeFileSync(out,JSON.stringify({passed:false,checks,findings,traces,error:String(err)},null,2)+'\n');clearTimeout(timer);console.error(err.stack);process.exitCode=1});
