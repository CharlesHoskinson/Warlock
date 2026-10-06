'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const {Elm}=require(path.resolve(process.argv[2])),fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
assert.equal(crypto.createHash('sha256').update(fs.readFileSync(fixture.sourceReport)).digest('hex'),fixture.sourceReportSHA256);
const source=fixture.clientScope,template=fixture.terminalReceipts[0].event.event.frame.job,identity='family:'+template.context.incarnation;
let checks=0;const check=(actual,expected,message)=>{assert.deepEqual(actual,expected,message);checks++;};
function worker(){const app=Elm.PreviewFeedbackReplay.init();let pending=null;app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});return(kind,value)=>new Promise((resolve,reject)=>{assert.equal(pending,null);const timer=setTimeout(()=>{pending=null;reject(Error('Original three-second feedback port deadline'));},3000);pending=value=>{clearTimeout(timer);resolve(value);};app.ports.incoming.send({kind,value});});}
const presentation=(id=identity,publication=1)=>({surfaceProtocol:2,publication:String(publication),lease:String(publication),mode:'picker',status:'',bar:[],popup:[{id,domId:'feedback',label:'Client',ariaLabel:'Client',detail:'',enabled:true}]});
const issuedSeed=(sequence=1,publication=1)=>({kind:'source-seed',publication:String(publication),lease:String(publication),identity,source:{...structuredClone(source),requestId:String(sequence),scope:{...structuredClone(source.scope),observation:String(BigInt(source.scope.observation)+BigInt(sequence)),now:String(BigInt(source.scope.now)+BigInt(sequence))}},title:'Own native source',application:'own.app'});
const local=(sequence=2,publication=1,outcome='capacity')=>({kind:'demand-feedback',identity,binding:structuredClone(template.binding),subject:template.context.incarnation,clock:template.clock,publication:String(publication),lease:String(publication),sequence:String(sequence),deadline:template.deadline,outcome});
const cmds=r=>r.commands.flatMap(v=>v.commands),state=r=>r.models[0].model,feedback=r=>r.feedback[0],wrapped=event=>({kind:'event',identity,event});
async function prepared(){const send=worker();await send('presentation',presentation());const result=await send('native',{...issuedSeed(),kind:'demand-seed'});check(cmds(result),[],'Idle local source cannot capture');check(state(result).demand,false,'Local source does not open demand');return{send,result};}
async function controls(){
 let {send,result}=await prepared();const original=state(result);result=await send('native',local());check(state(result),original,'Local feedback changes no lifecycle state');check(cmds(result),[],'Local feedback emits no effect');check(feedback(result).label,'Waiting for preview capacity','Truthful capacity label');
 const unchanged=structuredClone(result),mutations=[m=>m.extra=true,m=>delete m.clock,m=>m.binding.extra=true,m=>m.binding.session='999',m=>m.subject='999',m=>m.identity='family:999',m=>m.clock='1',m=>m.publication='2',m=>m.lease='2',m=>m.sequence='2',m=>m.sequence='1',m=>m.sequence='0',m=>m.sequence='03',m=>m.sequence=3,m=>m.sequence='18446744073709551616',m=>m.deadline='0',m=>m.deadline='01',m=>m.outcome='refused',m=>m.job=template,m=>m.receipt='1'];
 for(const mutate of mutations){const m=local(3);mutate(m);result=await send('native',m);check(result,unchanged,'Malformed, duplicate, stale or foreign feedback cannot change authority');}
 result=await send('native',local('9007199254740993',1,'expired'));check(feedback(result).floor,'9007199254740993','Lossless sequence');check(feedback(result).deadline,template.deadline,'Original cutoff preserved');check(feedback(result).label,'Preview request expired','Truthful expiration');check(state(result),original,'Expiration is not a native receipt');
 await send('presentation',{...presentation(identity,2),mode:'closed',popup:[]});result=await send('presentation',presentation(identity,3));check(feedback(result).outcome,null,'Close hides feedback');check(feedback(result).floor,'9007199254740993','Close retains anti-replay floor');result=await send('native',local('9007199254740993',3));check(feedback(result).outcome,null,'Reopen cannot replay consumed sequence');
 ({send,result}=await prepared());await send('native',local());result=await send('native',issuedSeed(3));check(feedback(result).outcome,null,'Actual issued source clears local wait');check(feedback(result).floor,'3','Actual source advances feedback floor');
 const trigger=structuredClone(template);delete trigger.request;result=await send('native',wrapped({kind:'request',trigger}));check(cmds(result),[{kind:'acquire',job:template}],'Original exact issued job');const owned=structuredClone(result);result=await send('native',local(4));check(result.models,owned.models,'Late local capacity retains capturing job');check(result.feedback,owned.feedback,'Late local capacity cannot replace local state');check(cmds(result),[],'Late local capacity emits no command');
 const frame=structuredClone(fixture.terminalReceipts[0].event.event.frame);await send('native',wrapped({kind:'offer',frame:{...frame,signaled:false}}));result=await send('native',local(5));check(feedback(result).outcome,null,'Candidate retains owned resources');await send('native',wrapped({kind:'fence',frame}));result=await send('native',local(6));check(feedback(result).outcome,null,'Accepted image retains ownership');check(state(result).accepted,frame,'Local result cannot replace accepted pixels');
 process.stdout.write(JSON.stringify({passed:true,checks,nativeAcceptance:false,fullReleaseAccepted:false})+'\n');
}
async function replay(trace){
 const {send}=await prepared();let result,active=true,publication=1,sequence=1,acquires=0,cancels=0,acks=0,known=null;const states=[];
 for(const event of trace){
  if(event==='Close'){active=false;result=await send('presentation',{...presentation(identity,publication),mode:'closed',popup:[]});}
  else if(event==='Reopen'){active=true;publication++;result=await send('presentation',presentation(identity,publication));}
  else if(event==='Issue'){sequence++;await send('native',issuedSeed(sequence,publication));const trigger=structuredClone(template);delete trigger.request;result=await send('native',wrapped({kind:'request',trigger}));}
  else if(event==='Proof'){assert(known);result=await send('native',wrapped({kind:'receipt',sequence:known.request,event:{kind:'refused',job:known}}));}
  else{
   const valid=['Capacity','Expired','Waiting','Conflict','Exhausted'].includes(event);if(valid)sequence++;
   const value=local(sequence+(valid?0:1),publication,valid?event.toLowerCase():'capacity');
   if(event==='Duplicate')value.sequence=feedback(result).floor;
   if(event==='Older')value.sequence=String(BigInt(feedback(result).floor)-1n);
   if(event==='WrongClock')value.clock='1';
   if(event==='WrongOwner')value.binding.session='999';
   if(event==='WrongSubject')value.subject='999';
   if(event==='WrongStamp')value.lease=String(publication+1);
   result=await send('native',value);
  }
  for(const command of cmds(result)){
   if(command.kind==='acquire'){assert.equal(event,'Issue');known=command.job;acquires++;}
   else if(command.kind==='cancel'){assert.deepEqual(command.job,known);cancels++;}
   else{assert.equal(command.kind,'acknowledge');assert.deepEqual(command.job,known);acks++;known=null;}
  }
  const m=state(result),f=feedback(result);states.push({active,owned:m.known.length>0,cancelled:m.cancelling.length>0,publication,sequence,floor:Number(f.floor||0),outcome:f.outcome||'',acquires,cancels,acks,history:[]});
 }
 process.stdout.write(JSON.stringify(states)+'\n');
}
async function nativeControls(binary){
 const results=[];
 for(const mode of ['normal','feedback-expire']){
  const child=spawnSync(binary,[mode],{encoding:'utf8',timeout:5000});check(child.status,0,'Actual native C fixture normal exit: '+child.stderr);check(child.signal,null,'No fixture signal');const d=JSON.parse(child.stdout);check(d.passed,true,'Actual C controls');
  const send=worker();await send('presentation',presentation('family:23'));let result;for(const value of d.waiting)result=await send('native',value);
  check(cmds(result),[],'Actual unissued native result emits no Elm effect');check(feedback(result).label,'Waiting for preview capacity','Actual C result reaches Elm label');const original=structuredClone(state(result));
  for(const value of d.retryFeedback)result=await send('native',value);
  for(const value of d.retryEvents)result=await send('native',value);
  if(mode==='feedback-expire'){check(feedback(result).label,'Preview request expired','Actual original native cutoff reaches Elm');check(cmds(result),[],'Actual expired native intent cannot Acquire or ACK');check(state(result).known,[],'No fabricated job after expiry');check(state(result).nextRequest,original.nextRequest,'Expiry cannot advance Elm request identity');}
  else{check(feedback(result).outcome,null,'Actual issued native seed clears status');check(cmds(result)[0].kind,'acquire','Actual issued native request reaches same Elm policy');check(cmds(result)[0].job.context.incarnation,'23','Only admitted third source');check(cmds(result)[0].job.deadline,d.waiting[1].deadline,'Actual native/Elm cutoff unchanged');}
  results.push({mode,checks:d.checks});
 }
 process.stdout.write(JSON.stringify({passed:true,checks,cases:results,nativeAcceptance:false,fullReleaseAccepted:false,scope:'Actual protected C/socket/Broker outputs replayed into optimized Elm; no compositor/pixels or actual native capture from this fixture'})+'\n');
}
(async()=>{if(process.argv[4]==='--replay'){let raw='';for await(const chunk of process.stdin)raw+=chunk;await replay(JSON.parse(raw));}else if(process.argv[4]==='--native')await nativeControls(process.argv[5]);else await controls();})().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1;});
