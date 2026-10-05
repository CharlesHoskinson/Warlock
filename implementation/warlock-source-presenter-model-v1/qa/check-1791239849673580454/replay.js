'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path');
const {Elm}=require(path.resolve(process.argv[2]));
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const source=fixture.clientScope,identity='family:'+source.scope.context.incarnation;
const job=fixture.terminalReceipts[0].event.event.frame.job;
const app=Elm.PreviewPresenterReplay.init();let pending=null;
app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});
const send=(kind,value)=>new Promise((resolve,reject)=>{const timer=setTimeout(()=>{pending=null;reject(new Error('Actual Elm replay timeout'));},3000);pending=value=>{clearTimeout(timer);resolve(value);};app.ports.incoming.send({kind,value});});
const presentation=(closed=false)=>({surfaceProtocol:2,publication:closed?'2':'1',lease:'1',mode:closed?'closed':'picker',status:'',bar:[],popup:closed?[]:[{id:identity,domId:'native-client',label:'Client',ariaLabel:'Client',detail:'',enabled:true}]});
function project(result){const row=result.models[0],model=row?.model;return {entries:result.models.length,now:model?Number(BigInt(model.scope.now)-BigInt(source.scope.now)):0,active:row?.active||false,demand:model?.demand||false,known:model?.known.length||0,cancelling:model?.cancelling.length||0,commands:result.commands.flatMap(x=>x.commands.map(c=>{if(c.kind==='acquire'||c.kind==='cancel')assert.deepEqual(c.job,job);return c.kind;}))};}
(async()=>{
 let result=await send('presentation',presentation());process.stdout.write(JSON.stringify(project(result))+'\n');
 const events=fs.readFileSync(0,'utf8').trim().split('\n').filter(Boolean);
 for(const event of events){
  if(event==='Init')continue;
  if(event==='Close')result=await send('presentation',presentation(true));
  else if(event==='Request'){const trigger={...job};delete trigger.request;result=await send('native',{kind:'event',identity,event:{kind:'request',trigger}});}
  else {
   const observation=structuredClone(source);if(event.startsWith('Next')){observation.scope.now=String(BigInt(source.scope.now)+1n);observation.scope.observation=String(BigInt(source.scope.observation)+1n);}
   const type=event.replace('Next','');if(type==='Monitor'){observation.kind='preview-capture-probe-scope';observation.scopeKind='root-surface-commit-monitor-plane-unqualified';}
   let seed={kind:'source-seed',publication:'1',lease:'1',identity,source:observation,title:'Source',application:'warlock-child-probe'};
   if(type==='Legacy'){delete seed.source;seed.kind='seed';seed.scope=observation.scope;}
   if(event==='Malformed')observation.maximumTransferBytes='4097';
   if(event==='Foreign')observation.binding.session='999';
   if(event==='WrongStamp')seed.publication='999';
   result=await send('native',seed);
  }
  process.stdout.write(JSON.stringify(project(result))+'\n');
 }
})().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1;});
