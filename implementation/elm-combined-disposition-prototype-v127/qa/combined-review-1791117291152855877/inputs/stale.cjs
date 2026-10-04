'use strict';
const fs=require('fs'),assert=require('assert/strict'),cp=require('child_process'),path=require('path');
const app=require(process.argv[2]).Elm.BatchReplay.init({flags:null}),e=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),probe=process.argv[4],out=process.argv[5],unsafe=process.argv[6]==='ancestor';
const copy=x=>JSON.parse(JSON.stringify(x)),native=frame=>({kind:'native',frame}),scope={id:'1',generation:'1'};const checks=[];
function run(events){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows.at(-1))};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events)})}
(async()=>{
 const p=copy(e.projection51),g=copy(e.geometry52),a=copy(e.geometryAttach);p.requestId='1';a.requestId='2';g.requestId='3';
 const base=[{kind:'topology',frame:{viewProtocol:1,kind:'view-topology',revision:'1',views:[scope]}},native(e.attached),native(p),native({protocolVersion:3,kind:'host-geometry-negotiate'}),native(a),native(g)],ready=await run(base);
 const open={kind:'action',action:{viewProtocol:1,kind:'view-action',scope,action:{surfaceProtocol:2,kind:'surface-context',surface:'bar',publication:ready.frame.publication,lease:ready.frame.lease,id:'bar:group:application:elm-maximize-probe',trigger:'pointer',x:227,y:21}}};
 const opened=[...base,open],menu=await run(opened),pendingTrace=[...opened,native({protocolVersion:3,kind:'host-refresh'})],pending=await run(pendingTrace);
 const input=path.join(path.dirname(out),'stale-input.json');fs.writeFileSync(input,JSON.stringify({original:JSON.stringify(pending.submitted),binding:g.binding,gate:{publication:menu.frame.publication,lease:menu.frame.lease,closed:menu.frame.lease}}));
 const cert=JSON.parse(cp.execFileSync(probe,[input],{encoding:'utf8'}).trim().split('\n').at(-1));
 const lp=copy(p),lg=copy(g);lp.requestId=pending.correlation.legacy;lg.requestId=pending.correlation.geometry;
 const completed=[...pendingTrace,native(lp),native(lg)],current=await run(completed);assert.equal(current.frame.mode,'menu');assert.equal(current.frame.lease,menu.frame.lease);assert.equal(current.correlation.legacy,null);assert.equal(current.correlation.geometry,null);
 const after=await run([...completed,{kind:'disposition',frame:cert}]);
 if(unsafe){assert.equal(after.frame.mode,'closed');checks.push('actual frozen unsafe V104 closes newer menu from obsolete exact observation certificate')}
 else{assert.equal(after.frame.mode,'menu');assert.equal(after.frame.publication,current.frame.publication);assert.equal(after.frame.lease,current.frame.lease);assert.equal(after.submitted,null);assert.equal(after.requests.length,0);checks.push('obsolete exact observation certificate consumes record without closing current same-lease menu')}
 const select=current.frame.popup.find(r=>r.label==='Restore'&&r.enabled);assert(select);
 const selection={kind:'action',action:{viewProtocol:1,kind:'view-action',scope,action:{surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:current.frame.publication,lease:current.frame.lease,id:select.id}}};
 const staged=[...completed,selection],prepared=await run(staged);assert(prepared.preparedToken);assert.equal(prepared.frame.lease,menu.frame.lease);assert.equal(prepared.outstanding,1);
 const afterPrepared=await run([...staged,{kind:'disposition',frame:cert}]);
 if(unsafe){assert.equal(afterPrepared.preparedToken,null);checks.push('actual frozen unsafe V104 cancels newer prepared selection from obsolete same-lease observation certificate')}
 else{assert.equal(afterPrepared.preparedToken,prepared.preparedToken);assert.deepEqual(afterPrepared.correlation,prepared.correlation);assert.equal(afterPrepared.outstanding,1);assert.equal(afterPrepared.registry,0);assert.equal(afterPrepared.requests.length,0);checks.push('obsolete exact certificate cannot cancel newer same-lease prepared selection or consume its read IDs')}
 fs.writeFileSync(out,JSON.stringify({passed:true,unsafeAncestorFailureDemonstrated:unsafe,nativeAcceptance:false,checks,current,after,prepared,afterPrepared},null,2)+'\n');
})().catch(error=>{fs.writeFileSync(out,JSON.stringify({passed:false,error:String(error),checks},null,2)+'\n');console.error(error.stack);process.exitCode=1});
