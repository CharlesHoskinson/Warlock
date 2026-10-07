'use strict';
const assert=require('node:assert/strict'),path=require('node:path'),{spawnSync}=require('node:child_process');
const {Elm}=require(path.resolve(process.argv[2]));let checks=0;
const check=(a,b)=>{assert.deepEqual(a,b);checks++;};
const app=Elm.PreviewFeedbackReplay.init();let pending=null;
app.ports.outgoing.subscribe(v=>{assert(pending);const done=pending;pending=null;done(v);});
function send(kind,value){return new Promise((resolve,reject)=>{assert.equal(pending,null);const timer=setTimeout(()=>reject(Error('Original three-second port deadline')),3000);pending=v=>{clearTimeout(timer);resolve(v);};app.ports.incoming.send({kind,value});});}
const presentation=(publication,lease,open=true)=>({surfaceProtocol:2,publication:String(publication),lease:String(lease),mode:open?'picker':'closed',status:'',bar:[],popup:open?[{id:'family:23',domId:'next-intent',label:'Client',ariaLabel:'Client',detail:'',enabled:true}]:[]});
const cmds=r=>r.commands.flatMap(x=>x.commands);
async function main(){
 const p=spawnSync(process.argv[3],[],{encoding:'utf8',timeout:5000});check(p.status,0);check(p.signal,null);assert(!p.stderr,p.stderr);const d=JSON.parse(p.stdout);check(d.passed,true);
 await send('presentation',presentation(1,1));let result;
 for(const v of d.waiting)result=await send('native',v);
 check(result.feedback[0].label,'Waiting for preview capacity');check(cmds(result),[]);
 for(const v of d.expired)result=await send('native',v);
 check(result.feedback[0].label,'Preview request expired');check(cmds(result),[]);const originalNext=result.models[0].model.nextRequest;
 await send('presentation',presentation(2,1,false));result=await send('presentation',presentation(3,2));
 check(result.feedback[0].outcome,null);
 for(const v of d.successor)result=await send('native',v);
 check(result.feedback[0].label,'Waiting for preview capacity');check(result.feedback[0].deadline,d.successor[1].deadline);check(cmds(result),[]);
 check(result.models[0].model.nextRequest,originalNext);check(result.models[0].model.known,[]);
 const current=structuredClone(result.feedback);for(const v of d.expired)result=await send('native',v);
 check(result.feedback,current);check(cmds(result),[]);
 for(const v of d.issued)result=await send('native',v);
 check(result.feedback[0].outcome,null);check(cmds(result).length,1);check(cmds(result)[0].kind,'acquire');
 check(cmds(result)[0].job.context.incarnation,'23');check(cmds(result)[0].job.deadline,d.successor[1].deadline);check(cmds(result)[0].job.request,'1');
 process.stdout.write(JSON.stringify({passed:true,checks,cControls:d.checks,nativeAcceptance:false,fullReleaseAccepted:false,scope:'Actual C/socket/Broker successor and old replay through current optimized Elm; no compositor/capture/presentation acceptance'})+'\n');
}
main().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1;});
