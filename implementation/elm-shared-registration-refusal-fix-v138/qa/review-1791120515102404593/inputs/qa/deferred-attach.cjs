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
 const notification=native({protocolVersion:3,kind:"host-refresh"});
 const attachPendingTrace=[...baseline,{kind:'direct-native-begin',operation:'minimize',incarnation:'1',mixed:false}],attachPendingOperation=await last(attachPendingTrace),attachPendingCommand=attachPendingOperation.requests.find(r=>r.kind==='window-effect');assert(attachPendingCommand);
 const attachDuringPendingTrace=[...attachPendingTrace,{kind:'geometry-attach'}],attachDuringPending=await last(attachDuringPendingTrace);assert.equal(attachDuringPending.requests[0].kind,'geometry-attach');
 const attachPendingCert=certificate(attachDuringPending,{publication:attachDuringPending.frame.publication,lease:attachDuringPending.frame.lease,closed:attachDuringPending.frame.lease}),clearedAttachTrace=[...attachDuringPendingTrace,disposition(attachPendingCert)],clearedAttach=await last(clearedAttachTrace);
 check('exact unsent attach while Pending retires old attach ID without replaying or deleting original operation',()=>{assert.equal(clearedAttach.correlation.attach,null);assert.equal(clearedAttach.requests.length,0);assert.deepEqual(clearedAttach.issued,attachPendingOperation.issued);assert.deepEqual(clearedAttach.unresolvedFull,attachPendingOperation.unresolvedFull)});
 const attachDefinitive={protocolVersion:3,kind:'effect-outcome',binding:attachPendingCommand.binding,effectProtocol:attachPendingCommand.effectProtocol,intent:attachPendingCommand.intent,status:'Committed',reason:'CPU-attach-resume',revision:attachPendingCommand.intent.context.revision,outputGeneration:attachPendingCommand.intent.context.output};
 const resumedAttach=await last([...clearedAttachTrace,native(attachDefinitive)]);
 check('definitive original operation receipt resumes required geometry attach under fresh ID',()=>{assert.deepEqual(resumedAttach.requests.map(r=>r.kind),['projection-request','geometry-attach']);assert(BigInt(resumedAttach.correlation.attach)>BigInt(attachDuringPending.correlation.attach));assert(!resumedAttach.requests.some(r=>r.kind==='window-effect'))});
 const waitingLegacyTrace=[...baseline,notification,{kind:'geometry-attach'}],waitingLegacy=await last(waitingLegacyTrace);assert(waitingLegacy.correlation.legacy);assert(waitingLegacy.correlation.attach);
 const waitingCert=certificate(waitingLegacy,{publication:waitingLegacy.frame.publication,lease:waitingLegacy.frame.lease,closed:waitingLegacy.frame.lease}),waitingClearedTrace=[...waitingLegacyTrace,disposition(waitingCert)],waitingCleared=await last(waitingClearedTrace);assert.equal(waitingCleared.correlation.attach,null);assert.equal(waitingCleared.correlation.legacy,waitingLegacy.correlation.legacy);
 const completeLegacy=copy(p);completeLegacy.requestId=waitingCleared.correlation.legacy;
 const drainedAttach=await last([...waitingClearedTrace,native(completeLegacy)]);
 check('remaining legacy read completion drains dirty bit into required fresh attach rather than stale geometry facts',()=>{assert.deepEqual(drainedAttach.requests.map(r=>r.kind),['projection-request','geometry-attach']);assert(BigInt(drainedAttach.correlation.attach)>BigInt(waitingLegacy.correlation.attach))});
 fs.writeFileSync(out,JSON.stringify({passed:true,checks,nativeAcceptance:false},null,2)+"\n");clearTimeout(timer);
})().catch(e=>{fs.writeFileSync(out,JSON.stringify({passed:false,checks,error:String(e)},null,2)+"\n");clearTimeout(timer);console.error(e.stack);process.exitCode=1});
