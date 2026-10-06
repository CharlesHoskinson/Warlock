'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path'),cp=require('node:child_process');
const {Elm}=require(path.resolve(process.argv[2]));const events=fs.readFileSync(0,'utf8').trim().split('\n').filter(Boolean);
const concrete=cp.spawnSync(process.argv[4],[process.argv[3]],{input:events.join('\n')+'\n',encoding:'utf8',timeout:3000});assert.equal(concrete.status,0,concrete.stderr);assert.equal(concrete.stderr,'');
const native=concrete.stdout.trim().split('\n').map(JSON.parse);assert.equal(native.length,events.length);
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),job=fixture.terminalReceipts[0].event.event.frame.job,identity='family:'+job.context.incarnation;
const app=Elm.PreviewPresenterReplay.init();let pending=null,result,accepted=null,terminal=null;
app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});
const send=(kind,value)=>new Promise((resolve,reject)=>{const timer=setTimeout(()=>{pending=null;reject(new Error('Actual Elm Historical replay timeout'));},3000);pending=value=>{clearTimeout(timer);resolve(value);};app.ports.incoming.send({kind,value});});
const presentation=(lease,closed)=>({surfaceProtocol:2,publication:closed?'2':lease==='2'?'3':'1',lease,mode:closed?'closed':'picker',status:'',bar:[],popup:closed?[]:[{id:identity,domId:'client',label:'Client',ariaLabel:'Client',detail:'',enabled:true}]});
// Native source seed uses the actual newly admitted publication3/lease2.
function commands(rows,event){return rows.flatMap(r=>r.commands).map(c=>{
 if(c.kind==='acquire'){assert.equal(event,'Request');assert.deepEqual(c.job,job);}
 if(c.kind==='release')assert.deepEqual(c.frame,accepted);
 if(c.kind==='acknowledge'){assert.deepEqual(c.job,job);assert.equal(c.sequence,terminal.event.sequence);}
 return c.kind;
});}
(async()=>{
 result=await send('presentation',presentation('1',false));
 for(let i=0;i<events.length;i++){
  const event=events[i],sample=native[i];let effects=[];
  if(event==='Close' || event==='Reopen'){result=await send('presentation',presentation(event==='Reopen'?'2':'1',event==='Close'));effects.push(...commands(result.commands,event));}
  if(sample.wire.length){for(let wire of sample.wire){
   // Producer fixture stamps the new presentation after Close's publication2.
   if(wire.kind==='source-seed' && wire.lease==='2'){assert.equal(wire.publication,'3');}
   if(wire.kind==='event' && wire.event.kind==='fence'){accepted=wire.event.frame;assert.deepEqual(accepted.job,job);assert.equal(accepted.expires,fixture.terminalReceipts[0].event.event.frame.expires);}
   if(wire.kind==='event' && wire.event.kind==='receipt')terminal=wire;
   result=await send('native',wire);effects.push(...commands(result.commands,event));
  }}else if(event!=='Close' && event!=='Reopen')result=await send('query',null);
  const m=result.models[0]?.model;
  for(const original of m?.known||[])assert.deepEqual(original,job);
  if(m?.accepted)assert.deepEqual(m.accepted,accepted);
  if(m)assert.equal(m.nextRequest,event==='Seed'?'1':'2');
  process.stdout.write(JSON.stringify({state:m?.state||'unavailable',known:m?.known.length||0,capturing:!!m?.job,accepted:!!m?.accepted,retiring:m?.retiring.length||0,demand:!!m?.demand,ready:m?.ready??true,commands:effects,broker:sample.broker})+'\n');
 }
})().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1;});
