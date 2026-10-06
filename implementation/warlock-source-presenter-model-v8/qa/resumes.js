'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path'),cp=require('node:child_process');
const {Elm}=require(path.resolve(process.argv[2]));
const events=fs.readFileSync(0,'utf8').trim().split('\n').filter(Boolean);
const concrete=cp.spawnSync(process.argv[4],[process.argv[3]],{input:events.join('\n')+'\n',encoding:'utf8',timeout:3000});
assert.equal(concrete.status,0,concrete.stderr);assert.equal(concrete.stderr,'');
const native=concrete.stdout.trim().split('\n').map(JSON.parse);assert.equal(native.length,events.length);
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),original=fixture.terminalReceipts[0].event.event.frame.job,identity='family:'+original.context.incarnation;
const app=Elm.PreviewPresenterReplay.init();let pending=null,result,scope=fixture.clientScope.scope;
const jobs=new Map(),frames=new Map(),terminals=new Map();
app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});
const send=(kind,value)=>new Promise((resolve,reject)=>{const timer=setTimeout(()=>{pending=null;reject(new Error('Actual Elm resume replay timeout'));},3000);pending=value=>{clearTimeout(timer);resolve(value);};app.ports.incoming.send({kind,value});});
const presentation=lease=>({surfaceProtocol:2,publication:String(lease),lease:String(lease),mode:'picker',status:'',bar:[],popup:[{id:identity,domId:'client',label:'Client',ariaLabel:'Client',detail:'',enabled:true}]});
function commands(rows){return rows.flatMap(row=>row.commands).map(c=>{
 const request=c.job?.request||c.frame?.job.request;
 if(c.kind==='acquire')assert.deepEqual(c.job,jobs.get(request));
 if(c.kind==='release')assert.deepEqual(c.frame,frames.get(request));
 if(c.kind==='acknowledge'){assert.deepEqual(c.job,jobs.get(request));assert.equal(c.sequence,terminals.get(request).event.sequence);}
 return c.kind;
});}
(async()=>{
 result=await send('presentation',presentation(1));
 for(let i=0;i<events.length;i++){
  const event=events[i],sample=native[i];let effects=[];
  if(event==='Reopen'){result=await send('presentation',presentation(2));effects.push(...commands(result.commands));}
  if(sample.wire.length){for(const wire of sample.wire){
   if(wire.kind==='source-seed')scope=wire.source.scope;
   if(wire.kind==='event' && wire.event.kind==='request'){
    const t=wire.event.trigger,request=String(sample.broker.floor),job={binding:t.binding,context:t.context,request,origin:t.origin,clock:t.clock,deadline:t.deadline};
    assert.deepEqual(job.binding,original.binding);assert.equal(job.clock,original.clock);
    if(request==='1')assert.deepEqual(job,original);
    else {assert.equal(request,'2');assert.equal(job.origin,'2');assert.equal(BigInt(job.deadline),BigInt(scope.now)+2000000000n);assert.notDeepEqual(job.context,original.context);}
    jobs.set(request,job);
   }
   if(wire.kind==='event' && wire.event.kind==='fence'){
    const f=wire.event.frame;assert.deepEqual(f.job,jobs.get(f.job.request));assert(!frames.has(f.job.request));
    if(f.job.request==='1')assert.equal(f.expires,fixture.terminalReceipts[0].event.event.frame.expires);
    else {assert.notEqual(f.handle,frames.get('1').handle);assert.equal(BigInt(f.expires),BigInt(f.job.deadline)+3000000000n);}
    frames.set(f.job.request,f);
   }
   if(wire.kind==='event' && wire.event.kind==='receipt')terminals.set(wire.event.event.frame.job.request,wire);
   result=await send('native',wire);effects.push(...commands(result.commands));
  }}else if(event!=='Reopen')result=await send('query',null);
  const m=result.models[0]?.model;
  for(const retained of m?.known||[])assert.deepEqual(retained,jobs.get(retained.request));
  if(m?.accepted)assert.deepEqual(m.accepted,frames.get(m.accepted.job.request));
  process.stdout.write(JSON.stringify({state:m?.state||'unavailable',known:m?.known.length||0,capturing:!!m?.job,accepted:!!m?.accepted,retiring:m?.retiring.length||0,demand:!!m?.demand,ready:m?.ready??true,commands:effects,broker:sample.broker})+'\n');
 }
})().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1;});
