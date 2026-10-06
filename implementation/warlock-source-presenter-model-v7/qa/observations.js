'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path'),cp=require('node:child_process');
const {Elm}=require(path.resolve(process.argv[2]));
const events=fs.readFileSync(0,'utf8').trim().split('\n').filter(Boolean);
const concrete=cp.spawnSync(process.argv[4],[process.argv[3]],{input:events.join('\n')+'\n',encoding:'utf8',timeout:3000});
assert.equal(concrete.status,0,concrete.stderr);assert.equal(concrete.stderr,'');
const native=concrete.stdout.trim().split('\n').map(JSON.parse);assert.equal(native.length,events.length);
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),job=fixture.terminalReceipts[0].event.event.frame.job;
const identity='family:'+job.context.incarnation;
const app=Elm.PreviewPresenterReplay.init();let pending=null,accepted=null,terminal=null,result;
app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});
const send=(kind,value)=>new Promise((resolve,reject)=>{const timer=setTimeout(()=>{pending=null;reject(new Error('Actual Elm observation replay timeout'));},3000);pending=value=>{clearTimeout(timer);resolve(value);};app.ports.incoming.send({kind,value});});
const presentation=closed=>({surfaceProtocol:2,publication:closed?'2':'1',lease:'1',mode:closed?'closed':'picker',status:'',bar:[],popup:closed?[]:[{id:identity,domId:'client',label:'Client',ariaLabel:'Client',detail:'',enabled:true}]});
function project(broker,commands){const row=result.models[0],m=row?.model;return {state:m?.state||'unavailable',known:m?.known.length||0,capturing:!!m?.job,accepted:!!m?.accepted,retiring:m?.retiring.length||0,demand:!!m?.demand,commands:commands.map(c=>{if(c.kind==='acquire')assert.deepEqual(c.job,job);if(c.kind==='release')assert.deepEqual(c.frame,accepted);if(c.kind==='acknowledge'){assert.deepEqual(c.job,job);assert.equal(c.sequence,terminal.event.sequence);}return c.kind;}),broker};}
(async()=>{
 result=await send('presentation',presentation(false));
 for(let i=0;i<events.length;i++){
  const event=events[i],sample=native[i];let commands=[];
  if(event==='Close')result=await send('presentation',presentation(true));
  else if(sample.wire.length){for(const wire of sample.wire){
   if(wire.kind==='event' && wire.event.kind==='fence')accepted=wire.event.frame;
   if(wire.kind==='event' && wire.event.kind==='receipt')terminal=wire;
   result=await send('native',wire);commands.push(...result.commands.flatMap(row=>row.commands));
  }} else result=await send('query',null);
  for(const retained of result.models){for(const original of retained.model.known)assert.deepEqual(original,job);if(retained.model.accepted)assert.deepEqual(retained.model.accepted,accepted);}
  process.stdout.write(JSON.stringify(project(sample.broker,commands))+'\n');
 }
})().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1;});
