'use strict';
const fs=require('fs'),assert=require('assert/strict');
const app=require(process.argv[2]).Elm.MenuSurfaceReplay.init({flags:null});
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const timer=setTimeout(()=>{throw Error('Surface menu replay deadline');},15000);
function replay(events){return new Promise(resolve=>{const receive=value=>{app.ports.outgoing.unsubscribe(receive);resolve(value);};app.ports.outgoing.subscribe(receive);app.ports.incoming.send(events);});}
const native=frame=>({kind:'native',frame}),baseline=[native(fixture.attached),native(fixture.projection)];
const wire=(frame,kind,id,surface='popup')=>({surfaceProtocol:2,kind,surface,publication:frame.publication,lease:frame.lease,id});
const context=(frame,id,surface='bar',trigger='pointer')=>({kind:'action',action:{...wire(frame,'surface-context',id,surface),trigger,x:40,y:20}});
const action=(frame,id,surface='popup')=>({kind:'action',action:wire(frame,'surface-action',id,surface)});
const navigate=(frame,key)=>({kind:'action',action:{surfaceProtocol:2,kind:'surface-menu-navigation',surface:'popup',publication:frame.publication,lease:frame.lease,key}});
(async()=>{const cases=[];async function check(name,events,verify){try{const rows=await replay(events);verify(rows,rows.at(-1));cases.push({name,passed:true,rows});}catch(error){cases.push({name,passed:false,error:String(error)});console.error(name+': '+error.stack);}}
const ready=(await replay(baseline)).at(-1).frame;
const openA=[...baseline,context(ready,'bar:group:application:org.a')];
const open=(await replay(openA)).at(-1).frame;
await check('current secondary context opens menu without native action',openA,(_,last)=>{assert.equal(last.frame.mode,'menu');assert(last.rendererAdmitted);assert.equal(last.requests.length,0);assert.equal(last.outstanding,0);assert.equal(last.registry,0);assert.equal(last.menu.selected,1);});
await check('menu presentation carries explicit disabled Restore and available Minimize',openA,(_,last)=>{assert.deepEqual(last.frame.popup.map(row=>({label:row.label,enabled:row.enabled})),[{label:'Close',enabled:true},{label:'Restore',enabled:false},{label:'Minimize',enabled:true}]);});
for(const [name,change] of [['old publication',{publication:'0'}],['old lease',{lease:'9'}],['numeric publication',{publication:1}],['unknown role',{surface:'overlay'}],['wrong protocol',{surfaceProtocol:3}],['bad trigger',{trigger:'script'}],['fractional point',{x:1.5}],['extra command',{exec:'/bin/sh'}],['unknown identity',{id:'bar:group:application:missing'}]]){
const ev=context(ready,'bar:group:application:org.a');ev.action={...ev.action,...change};
await check('invalid context '+name,[...baseline,ev],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.requests.length,0);assert.equal(last.frame.publication,ready.publication);});}
await check('keyboard context shares native provider and target',[...baseline,context(ready,'bar:group:application:org.a','bar','keyboard')],(_,last)=>{assert.equal(last.frame.mode,'menu');assert.equal(last.menu.selected,1);assert.equal(last.requests.length,0);});
await check('disabled Restore cannot allocate an operation',[...openA,action(open,'menu:1:0')],(_,last)=>{assert.equal(last.frame.mode,'menu');assert.equal(last.outstanding,0);assert.equal(last.registry,0);assert.equal(last.requests.length,0);});
for(const key of ['Home','End','ArrowUp','ArrowDown'])await check('navigation skips disabled and never sends '+key,[...openA,navigate(open,key)],(_,last)=>{assert.equal(last.menu.selected,1);assert.equal(last.frame.mode,'menu');assert.equal(last.requests.length,0);});
await check('stale navigation preserves current menu',[...openA,navigate({...open,publication:'0'},'Enter')],(_,last)=>{assert.equal(last.frame.publication,open.publication);assert.equal(last.requests.length,0);assert.equal(last.outstanding,0);});
await check('Escape closes current menu without native operation',[...openA,navigate(open,'Escape')],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.menu,null);assert.equal(last.requests.length,0);});
const dispatched=[...openA,action(open,'menu:1:1')];
await check('Minimize closes publication before exactly one real full intent',dispatched,(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.outstanding,1);assert.equal(last.registry,1);assert.equal(last.order[0],'publish');assert.equal(last.requests.length,1);assert.deepEqual(last.requests[0],fixture.firstCommand);assert.equal(last.shell.effects.windows[0].minimized,false);});
await check('Enter uses selected enabled action exactly once',[...openA,navigate(open,'Enter')],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.registry,1);assert.deepEqual(last.requests,[fixture.firstCommand]);});
await check('duplicate old callback cannot forward',[...dispatched,action(open,'menu:1:1')],(_,last)=>{assert.equal(last.registry,1);assert.equal(last.requests.length,0);assert.equal(last.outstanding,1);});
await check('correlated receipt clears ledger without optimistic observation',[...dispatched,native(fixture.committed)],(_,last)=>{assert.equal(last.outstanding,0);assert.equal(last.registry,0);assert.equal(last.shell.phase,'Reconciling');assert.equal(last.shell.effects.windows[0].minimized,false);});
const bContext=context(open,'bar:group:application:org.b');
const replacement=[...openA,bContext];const replaced=(await replay(replacement)).at(-1).frame;
await check('replacement menu obtains a distinct lease',replacement,(_,last)=>{assert.equal(last.frame.mode,'menu');assert.notEqual(last.frame.lease,open.lease);assert.equal(last.menu.id,2);assert.equal(last.requests.length,0);});
await check('stale dismissal cannot close replacement lease',[...replacement,{kind:'dismiss',lease:open.lease}],(_,last)=>{assert.equal(last.frame.mode,'menu');assert.equal(last.frame.publication,replaced.publication);});
await check('current native dismissal closes without cancel or send',[...replacement,{kind:'dismiss',lease:replaced.lease}],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.requests.length,0);});
const unavailable=JSON.parse(JSON.stringify(fixture.projection));unavailable.scene.windows.forEach(row=>row.available=false);
const disabledBaseline=[native(fixture.attached),native(unavailable)];const disabledFrame=(await replay(disabledBaseline)).at(-1).frame;
await check('unavailable bar context refuses unsupported target',[...disabledBaseline,context(disabledFrame,'bar:group:application:org.a')],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.outstanding,0);assert.equal(last.requests.length,0);});
const passed=cases.every(row=>row.passed);fs.writeFileSync(process.argv[4],JSON.stringify({passed,checks:cases.length,cases,scope:'Compiled production visible menu controller; synthetic native facts; native gesture authority qualified separately'},null,2)+'\n');clearTimeout(timer);if(!passed)process.exitCode=1;
})().catch(error=>{clearTimeout(timer);console.error(error.stack);process.exitCode=1;});
