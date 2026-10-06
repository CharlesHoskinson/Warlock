'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {Elm}=require(path.resolve(process.argv[2])),fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
assert.equal(crypto.createHash('sha256').update(fs.readFileSync(fixture.sourceReport)).digest('hex'),fixture.sourceReportSHA256);
const source=fixture.clientScope,template=fixture.terminalReceipts[0].event.event.frame.job,identity='family:'+template.context.incarnation;
const original=JSON.parse(fs.readFileSync(fixture.sourceReport,'utf8'));assert.deepEqual(source,original.providerReport.clientScope);
const job=n=>({...structuredClone(template),request:String(n)});
const wrapped=event=>({kind:'event',identity,event});
function worker(){const app=Elm.PreviewPresenterReplay.init();let pending=null;app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});return(kind,value)=>new Promise((resolve,reject)=>{assert.equal(pending,null);const timer=setTimeout(()=>{pending=null;reject(Error('Original three-second Elm receipt replay deadline'));},3000);pending=v=>{clearTimeout(timer);resolve(v);};app.ports.incoming.send({kind,value});});}
(async()=>{
 let input='';for await(const chunk of process.stdin)input+=chunk;const trace=JSON.parse(input),send=worker();
 await send('presentation',{surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[{id:identity,domId:'receipt',label:'Client',ariaLabel:'Client',detail:'',enabled:true}]});
 let result=await send('native',{kind:'source-seed',publication:'1',lease:'1',identity,source,title:'Native',application:'own.client'});
 let lastJob=0,lastSeq=0,acks=0;const states=[];
 for(const event of trace){
  const m=result.models[0].model,next=Number(m.nextRequest),known=m.known.length?Number(m.known[0].request):0;let value,target=0,sequence=0;
  if(event==='Issue'){const trigger=structuredClone(template);delete trigger.request;value=wrapped({kind:'request',trigger});}
  else{
   if(event==='KnownProof'){target=known;sequence=known;}
   else if(event==='Future'){target=next;sequence=next;}
   else if(event==='Repeat' || event==='AlteredSeq' || event==='AlteredJob'){target=lastJob;sequence=lastSeq+(event==='AlteredSeq'?100:0);}
   else if(event==='WrongKnown'){target=known;sequence=known;}else throw Error('Explicit receipt action '+event);
   const emittedJob=job(target);if(event==='AlteredJob' || event==='WrongKnown')emittedJob.deadline=String(BigInt(emittedJob.deadline)+1n);
   value=wrapped({kind:'receipt',sequence:String(sequence),event:{kind:'refused',job:emittedJob}});
  }
  result=await send('native',value);const commands=result.commands.flatMap(row=>row.commands);let ack=0;
  for(const command of commands){
   if(command.kind==='acquire'){assert(event==='Issue');assert.deepEqual(command.job,job(next));}
   else{assert.equal(command.kind,'acknowledge');assert.deepEqual(command.job,value.event.event.job);assert.equal(command.sequence,value.event.sequence);ack=Number(command.job.request);acks++;lastJob=ack;lastSeq=Number(command.sequence);}
  }
  const state=result.models[0].model;assert(state.known.length<=1);
  states.push({nextRequest:Number(state.nextRequest),known:state.known.length?Number(state.known[0].request):0,lastJob,lastSeq,acks,ack,history:[]});
 }
 process.stdout.write(JSON.stringify(states)+'\n');
})().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1;});
