'use strict';
const fs=require('fs'),assert=require('assert/strict');
const app=require(process.argv[2]).Elm.MenuSurfaceReplay.init({flags:null});
const evidence=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),copy=x=>JSON.parse(JSON.stringify(x)),native=frame=>({kind:'native',frame});
const timer=setTimeout(()=>{throw Error('Retirement CPU replay deadline')},20000);
function replay(events){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows)};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events)})}
const commit=row=>({surfaceProtocol:2,kind:'surface-commit',frame:row.frame,requests:row.requests,focus:row.focus});
(async()=>{
 const p=copy(evidence.projection51),g=copy(evidence.geometry52),attached=copy(evidence.geometryAttach);
 p.requestId='1';attached.requestId='2';g.requestId='3';
 const baseline=[{kind:'owner',frame:{surfaceProtocol:2,kind:'surface-owner',outputId:'1',providerId:'1'}},native(evidence.attached),native(p),native({protocolVersion:3,kind:'host-geometry-negotiate'}),native(attached),native(g)];
 const ready=(await replay(baseline)).at(-1);assert(ready.shell.available);assert.equal(ready.geometry.revision,evidence.geometry52.revision);
 const context={kind:'action',action:{surfaceProtocol:2,kind:'surface-context',surface:'bar',publication:ready.frame.publication,lease:ready.frame.lease,id:'bar:group:application:elm-maximize-probe',trigger:'pointer',x:227,y:21}};
 const opened=[...baseline,context],menu=(await replay(opened)).at(-1);assert.equal(menu.frame.mode,'menu');assert.equal(menu.requests.length,0);
 const notification=native({protocolVersion:3,kind:'host-refresh'}),refresh=[...opened,notification],pending=(await replay(refresh)).at(-1);
 assert.equal(pending.frame.mode,'menu');assert.equal(pending.frame.lease,menu.frame.lease);assert.deepEqual(pending.requests.map(x=>x.kind),['projection-request','geometry-facts-request']);
 const lost=[...refresh,{kind:'dismiss',lease:menu.frame.lease}],closed=(await replay(lost)).at(-1);
 assert.equal(closed.frame.mode,'closed');assert.equal(closed.requests.length,0);assert.equal(closed.correlation.legacy,pending.requests[0].requestId);assert.equal(closed.correlation.geometry,pending.requests[1].requestId);
 const stranded=[...lost,notification,...Array(20).fill(notification)],rows=await replay(stranded),last=rows.at(-1);
 assert.equal(last.requests.length,0);assert.equal(last.shell.available,false);assert.equal(last.shell.notificationQueued,true);assert.equal(last.correlation.deferNotifications,false);
 assert.deepEqual(last.correlation,closed.correlation);assert.equal(last.shell.effects.request,'0');assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.equal(last.menu,null);
 assert.equal(last.geometry.windows.length,1);assert.equal(last.geometry.windows[0].incarnation,'1');
 // Control only: if the missing batch's hypothetical responses existed, the
 // existing decoder admits them and drains the dirty bit with a fresh batch.
 const hypotheticalP=copy(p),hypotheticalG=copy(g);hypotheticalP.requestId=pending.requests[0].requestId;hypotheticalG.requestId=pending.requests[1].requestId;
 const control=[...stranded,native(hypotheticalP),native(hypotheticalG)],drained=(await replay(control)).at(-1);
 assert.deepEqual(drained.requests.map(x=>x.kind),['projection-request','geometry-facts-request']);
 const retiredP=copy(p),retiredG=copy(g);retiredP.requestId=drained.requests[0].requestId;retiredP.context.revision=retiredP.scene.revision=String(BigInt(p.scene.revision)+1n);retiredP.scene.focused=null;retiredP.scene.windows=[];
 retiredG.requestId=drained.requests[1].requestId;retiredG.revision=String(BigInt(g.revision)+1n);retiredG.sequence=String(BigInt(g.sequence)+1n);retiredG.facts.focused=null;retiredG.facts.windows=[];
 const recovered=(await replay([...control,native(retiredP),native(retiredG)])).at(-1);assert(recovered.shell.available);assert.equal(recovered.geometry.windows.length,0);assert.equal(recovered.menu,null);
 const output={passed:true,scope:'Actual compiled Controller ordering with exact actual producer fields and normalized initial request IDs; C preflight must establish rejected batch. Hypothetical control responses are CPU-only.',allExplicitAssertionsCompleted:true,
  opened:menu,pending,closed,stranded:last,hypotheticalControl:recovered,rows,
  nativeGate:{publication:menu.frame.publication,lease:menu.frame.lease,closed:menu.frame.lease},
  rejectedCommit:commit(pending),closedCommit:commit(closed),laterCommit:commit(last)};
 fs.writeFileSync(process.argv[4],JSON.stringify(output,null,2)+'\n');clearTimeout(timer);
})().catch(error=>{fs.writeFileSync(process.argv[4],JSON.stringify({passed:false,error:String(error)},null,2)+'\n');clearTimeout(timer);console.error(error.stack);process.exitCode=1});
