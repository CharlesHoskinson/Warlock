'use strict';
const fs=require('fs'),assert=require('assert/strict');
const app=require(process.argv[2]).Elm.MenuSurfaceReplay.init({flags:null});
const base=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),geo=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));
const clone=x=>JSON.parse(JSON.stringify(x)),native=frame=>({kind:'native',frame}),owner={kind:'owner',frame:base.owner};
const timer=setTimeout(()=>{throw Error('Recovery replay deadline');},15000);
function replay(events){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows)};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events)});}
const cold=[owner,native(base.attached)],ready=[...cold,native(base.projection)];
const unknown=(protocol=2)=>({protocolVersion:3,kind:'host-uncertain',binding:clone(base.binding),effectProtocol:protocol,intent:{...clone(geo.maxCommand.intent),request:'41',generation:'43',context:{...clone(geo.maxCommand.intent.context),epoch:'299'}}});
const action=(frame,id,surface='bar')=>({kind:'action',action:{surfaceProtocol:2,kind:'surface-action',surface,publication:frame.publication,lease:frame.lease,id}});
(async()=>{const cases=[];async function check(name,events,fn){let rows;try{rows=await replay(events);fn(rows,rows.at(-1));cases.push({name,passed:true,rows})}catch(e){cases.push({name,passed:false,error:String(e),rows});console.error(name+': '+e.stack)}}
 const frame=unknown();
 await check('cold geometry journal recovers typed Unknown without commands',[...cold,native(frame)],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.unresolved.length,1);assert.equal(last.unresolved[0].effectProtocol,2);assert.equal(last.unresolved[0].status,'Unknown');assert.equal(last.shell.effects.request,'41');assert.equal(last.shell.effects.generation,'43')});
 await check('duplicate journal frame idempotent no allocator reset',[...cold,native(frame),native(frame)],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.unresolved.length,1);assert.equal(last.shell.effects.request,'41')});
 const lower=unknown();lower.intent.request='40';lower.intent.generation='42';lower.intent.incarnation='20';
 await check('multiple recovery frames cannot move allocator backwards',[...cold,native(frame),native(lower)],(_,last)=>{assert.equal(last.unresolved.length,2);assert.equal(last.shell.effects.request,'41');assert.equal(last.shell.effects.generation,'43')});
 await check('observed geometry snapshot cannot fake settlement',[...cold,native(frame),native(base.projection),{kind:'geometry-attach'},native(geo.attach),native(geo.facts)],(_,last)=>{assert.equal(last.unresolved.length,1);assert.equal(last.unresolved[0].status,'Unknown');assert.equal(last.shell.effects.transaction.status,'Unknown');assert.equal(last.requests.length,0)});
 const recovered=[...cold,native(frame),native(base.projection)],bar=(await replay(recovered)).at(-1).frame;
 await check('recovered geometry Unknown blocks legacy same-window activation',[...recovered,action(bar,'bar:group:application:org.a')],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.shell.effects.request,'41')});
 await check('unrelated action advances shared recovered IDs',[...recovered,action(bar,'bar:group:application:org.b')],(_,last)=>{assert.equal(last.requests.length,1);assert.equal(last.requests[0].effectProtocol,1);assert.equal(last.requests[0].intent.request,'42');assert.equal(last.requests[0].intent.generation,'44')});
 const legacy=unknown(1);delete legacy.effectProtocol;legacy.intent.operation='minimize';
 await check('strict legacy recovery wire remains compatible',[...cold,native(legacy)],(_,last)=>{assert.equal(last.unresolved[0].effectProtocol,1);assert.equal(last.unresolved[0].status,'Unknown');assert.equal(last.requests.length,0)});
 for(const [name,mutate] of [['protocol bool',x=>x.effectProtocol=true],['protocol float',x=>x.effectProtocol=2.5],['unknown protocol',x=>x.effectProtocol=3],['wrong operation protocol',x=>x.effectProtocol=1],['missing geometry protocol',x=>delete x.effectProtocol],['wrong active binding',x=>x.binding.session='201'],['foreign lifetime',x=>x.intent.context.lifetime='101'],['zero request',x=>x.intent.request='0'],['overflow generation',x=>x.intent.generation='18446744073709551616'],['extra wire field',x=>x.extra=1],['extra intent field',x=>x.intent.extra=1]]){
  const bad=clone(frame);mutate(bad);await check('malformed journal rejects '+name,[...cold,native(bad)],(_,last)=>{assert.equal(last.requests.length,0);assert.deepEqual(last.unresolved,[]);assert.equal(last.shell.effects.request,'0')});
 }
 await check('unsolicited recovery after Ready cannot inject Unknown',[...ready,native(frame)],(_,last)=>{assert.deepEqual(last.unresolved,[]);assert.equal(last.requests.length,0)});
 const prior=(await replay(ready)).at(-1).frame;
 for(const reason of ['unavailable','full','busy','unverified','legacy-owner']){
  const failure={protocolVersion:3,kind:'host-recovery-failed',reason};
  const lost=[...ready,native(failure),native({protocolVersion:3,kind:'host-disconnected'})];const last=(await replay(lost)).at(-1);
  await check('typed storage explanation remains after disconnect '+reason,lost,(_,row)=>{assert.equal(row.shell.phase,'Detached');assert.equal(row.shell.available,false);assert(row.shell.recoveryFailure);assert.equal(row.requests.length,0)});
  await check('stale action preserves storage explanation '+reason,[...lost,action(prior,'bar:group:application:org.a')],(_,row)=>{assert.equal(row.shell.recoveryFailure,last.shell.recoveryFailure);assert.equal(row.shell.status,last.shell.status);assert.equal(row.requests.length,0)});
  await check('explicit reconnect exactly once '+reason,[...lost,action(last.frame,'bar:reconnect')],(_,row)=>assert.deepEqual(row.requests,[{protocolVersion:3,kind:'host-reconnect'}]));
 }
 const mark={protocolVersion:3,kind:'host-recovery-watermarks',binding:clone(base.binding),request:'42',generation:'44'};
 const marked=[...cold,native(mark),native(frame),native(base.projection)];const markedBar=(await replay(marked)).at(-1).frame;
 await check('committed B watermark survives older A recovery',marked,(_,last)=>{assert.equal(last.shell.effects.request,'42');assert.equal(last.shell.effects.generation,'44');assert.equal(last.unresolved.length,1)});
 await check('post-cold unrelated action advances all durable allocator maxima',[...marked,action(markedBar,'bar:group:application:org.b')],(_,last)=>{assert.equal(last.requests[0].intent.request,'43');assert.equal(last.requests[0].intent.generation,'45')});
 const lowerMark={...mark,request:'1',generation:'2'};
 await check('reordered watermarks cannot regress allocator',[...cold,native(mark),native(lowerMark),native(frame)],(_,last)=>{assert.equal(last.shell.effects.request,'42');assert.equal(last.shell.effects.generation,'44');assert.equal(last.requests.length,0)});
 const maximum={...mark,request:'18446744073709551615',generation:'18446744073709551615'};
 await check('exact UInt64 max restored without numeric truncation',[...cold,native(maximum)],(_,last)=>{assert.equal(last.shell.effects.request,maximum.request);assert.equal(last.shell.effects.generation,maximum.generation);assert.equal(last.requests.length,0)});
 for(const [name,mutate] of [['wrong binding',x=>x.binding.frontend='301'],['numeric request',x=>x.request=42],['Boolean generation',x=>x.generation=true],['counter overflow',x=>x.request='18446744073709551616'],['extra field',x=>x.extra=1],['missing field',x=>delete x.generation]]){
  const bad=clone(mark);mutate(bad);await check('strict allocation metadata rejects '+name,[...cold,native(bad)],(_,last)=>{assert.equal(last.shell.effects.request,'0');assert.equal(last.shell.effects.generation,'0');assert.equal(last.requests.length,0)});
 }
 await check('allocation metadata cannot mutate Ready controller',[...ready,native(mark)],(_,last)=>assert.equal(last.shell.effects.request,'0'));
 const failures=cases.filter(x=>!x.passed);fs.writeFileSync(process.argv[5],JSON.stringify({passed:failures.length===0,checks:cases.length,cases},null,2)+'\n');clearTimeout(timer);if(failures.length)process.exitCode=1;
})().catch(e=>{clearTimeout(timer);console.error(e.stack);process.exitCode=1});
