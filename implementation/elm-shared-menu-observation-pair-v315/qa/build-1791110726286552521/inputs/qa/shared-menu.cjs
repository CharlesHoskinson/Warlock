'use strict';
const fs=require('fs'),assert=require('assert/strict');
const app=require(process.argv[2]).Elm.SharedRecoveryReplay.init({flags:null});
const base=JSON.parse(fs.readFileSync(process.argv[3])),geo=JSON.parse(fs.readFileSync(process.argv[4]));
const copy=x=>JSON.parse(JSON.stringify(x)),native=frame=>({kind:'native',frame}),one={id:'1',generation:'1'},two={id:'2',generation:'1'};
const topology=(revision,views)=>({kind:'topology',frame:{viewProtocol:1,kind:'view-topology',revision:String(revision),views}});
const cold=[topology(1,[one,two]),native(base.attached)],ready=[...cold,native(base.projection),native({protocolVersion:3,kind:'host-geometry-negotiate'}),native(geo.attach),native(geo.facts)];
const action=(frame,id,scope=one,surface='bar')=>({kind:'action',frame:{viewProtocol:1,kind:'view-action',scope,action:{surfaceProtocol:2,kind:'surface-action',surface,publication:frame.publication,lease:frame.lease,id}}});
const context=(frame,scope=one,application='org.a')=>({kind:'action',frame:{viewProtocol:1,kind:'view-action',scope,action:{surfaceProtocol:2,kind:'surface-context',surface:'bar',publication:frame.publication,lease:frame.lease,id:'bar:group:application:'+application,trigger:'keyboard',x:0,y:0}}});
const timer=setTimeout(()=>{throw Error('Shared menu replay deadline')},15000),cases=[];
function replay(events){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows)};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events)})}
const nativeEffects=rows=>rows.flatMap(r=>r.requests).filter(x=>x.kind==='window-effect');
async function check(name,events,fn){let rows;try{rows=await replay(events);fn(rows,rows.at(-1));cases.push({name,passed:true,rows})}catch(e){cases.push({name,passed:false,error:String(e),rows});console.error(name,e.stack)}}
(async()=>{
 const bar=(await replay(ready)).at(-1).frame,opened=[...ready,context(bar)],menu=(await replay(opened)).at(-1);
 await check('registered first view opens shared menu without native effect',opened,(rows,last)=>{assert.equal(last.frame.mode,'menu');assert.deepEqual(last.projection.popupOwner,one);assert.deepEqual(last.ownerScope,{outputId:'1',providerId:'1'});assert.equal(nativeEffects(rows).length,0)});
 await check('second view receives distinct registered menu owner',[...ready,context(bar,two)],(rows,last)=>{assert.equal(last.frame.mode,'menu');assert.deepEqual(last.projection.popupOwner,two);assert.deepEqual(last.ownerScope,{outputId:'2',providerId:'1'});assert.equal(last.ownerExhausted,false);assert.equal(nativeEffects(rows).length,0)});
 await check('wrong view cannot select other views menu',[...opened,action(menu.frame,'menu:1:2',two,'popup')],(rows,last)=>{assert.equal(last.preparedToken,null);assert.equal(last.frame.publication,menu.frame.publication);assert.equal(nativeEffects(rows).length,0)});
 const selected=[...opened,action(menu.frame,'menu:1:2',one,'popup')],waiting=(await replay(selected)).at(-1);
 const p=copy(base.projection),g=copy(geo.facts);p.requestId=waiting.requests.find(x=>x.kind==='projection-request').requestId;p.context.revision=p.scene.revision='2';g.requestId=waiting.requests.find(x=>x.kind==='geometry-facts-request').requestId;g.revision='102';g.sequence='2';
 await check('selection closes shared popup before refreshed facts',selected,(rows,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.projection.popupOwner,null);assert(last.preparedToken);assert.equal(nativeEffects(rows).length,0)});
 await check('exact refreshed pair dispatches once through shared allocator',[...selected,native(p),native(g)],(rows,last)=>{assert.equal(nativeEffects(rows).length,1);assert.equal(nativeEffects(rows)[0].intent.operation,'maximize');assert.equal(last.preparedToken,null)});
 await check('duplicate refreshed pair never resubmits',[...selected,native(p),native(g),native(p),native(g)],rows=>assert.equal(nativeEffects(rows).length,1));
 const removed=[...selected,topology(2,[two])];
 await check('retired output cancels closed prepared selection',removed,(rows,last)=>{assert.equal(last.preparedToken,null);assert.deepEqual(last.ownerScope,{outputId:'2',providerId:'1'});assert.equal(last.ownerExhausted,false);assert.equal(nativeEffects(rows).length,0)});
 await check('old observation pair after output retirement cannot dispatch',[...removed,native(p),native(g)],rows=>assert.equal(nativeEffects(rows).length,0));
 await check('zero outputs cancels prepared selection without effects',[...selected,topology(2,[])],(rows,last)=>{assert.equal(last.preparedToken,null);assert.equal(last.ownerScope,null);assert.equal(nativeEffects(rows).length,0)});
 await check('replacement view generation cancels prepared selection',[...selected,topology(2,[{id:'1',generation:'2'},two])],(rows,last)=>{assert.equal(last.preparedToken,null);assert.deepEqual(last.ownerScope,{outputId:'1',providerId:'2'});assert.equal(last.ownerExhausted,false);assert.equal(nativeEffects(rows).length,0)});
 const changed=[...selected,action(waiting.frame,'bar:applications',two)];
 await check('admitted other-view action cancels original prepared authority',changed,(rows,last)=>{assert.equal(last.preparedToken,null);assert.deepEqual(last.ownerScope,{outputId:'2',providerId:'1'});assert.equal(nativeEffects(rows).length,0)});
 await check('stale old selection after owner change cannot dispatch',[...changed,action(menu.frame,'menu:1:2',one,'popup'),native(p),native(g)],rows=>assert.equal(nativeEffects(rows).length,0));
 const unknown={protocolVersion:3,kind:'host-uncertain',binding:copy(base.binding),intent:{request:'41',generation:'43',incarnation:'11',operation:'minimize',context:{lifetime:'100',epoch:'299',output:'1',revision:'1'}}};
 const blocked=[...cold,native(unknown),...ready.slice(2)],blockedBar=(await replay(blocked)).at(-1).frame,blockedOpen=[...blocked,context(blockedBar,two)],blockedMenu=(await replay(blockedOpen)).at(-1);
 await check('same-family child Unknown bars other-view staged mutation',[...blockedOpen,action(blockedMenu.frame,'menu:1:2',two,'popup')],(rows,last)=>{assert.equal(last.preparedToken,null);assert.equal(nativeEffects(rows).length,0);assert.equal(last.shell.effects.request,'41')});
 const failed=cases.filter(x=>!x.passed);fs.writeFileSync(process.argv[5],JSON.stringify({passed:failed.length===0,checks:cases.length,cases},null,2)+'\n');clearTimeout(timer);if(failed.length)process.exitCode=1;
})().catch(e=>{console.error(e.stack);clearTimeout(timer);process.exitCode=1});
