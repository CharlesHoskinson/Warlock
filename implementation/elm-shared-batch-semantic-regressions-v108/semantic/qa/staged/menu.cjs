'use strict';
const fs=require('fs'),assert=require('assert/strict');
const app=require(process.argv[2]).Elm.MenuSurfaceReplay.init({flags:null});
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const timer=setTimeout(()=>{throw Error('Surface menu replay deadline');},15000);
function replay(events){return new Promise(resolve=>{const receive=value=>{app.ports.outgoing.unsubscribe(receive);resolve(value);};app.ports.outgoing.subscribe(receive);app.ports.incoming.send(events);});}
const stage=require('./stage.cjs')(replay);
const native=frame=>({kind:'native',frame}),owner=frame=>({kind:'owner',frame}),baseline=[owner(fixture.owner),native(fixture.attached),native(fixture.projection)];
const wire=(frame,kind,id,surface='popup')=>({surfaceProtocol:2,kind,surface,publication:frame.publication,lease:frame.lease,id});
const context=(frame,id,surface='bar',trigger='pointer')=>({kind:'action',action:{...wire(frame,'surface-context',id,surface),trigger,x:40,y:20}});
const action=(frame,id,surface='popup')=>({kind:'action',action:wire(frame,'surface-action',id,surface)});
const navigate=(frame,key)=>({kind:'action',action:{surfaceProtocol:2,kind:'surface-menu-navigation',surface:'popup',publication:frame.publication,lease:frame.lease,key}});
(async()=>{const cases=[];async function check(name,events,verify){let rows;try{rows=await replay(events);verify(rows,rows.at(-1));cases.push({name,passed:true,rows});}catch(error){cases.push({name,passed:false,error:String(error),rows});console.error(name+': '+error.stack);}}
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
await check('Escape closes current menu without native operation',[...openA,navigate(open,'Escape')],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.menu,null);assert.equal(last.requests.length,1);assert.equal(last.requests[0].kind,'projection-request');assert.deepEqual(last.focus,[]);});
const dispatched=await stage([...openA,action(open,'menu:1:1')]);
await check('Minimize closes publication before exactly one real full intent',dispatched,(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.outstanding,1);assert.equal(last.registry,1);assert.equal(last.order[0],'publish');assert.equal(last.requests.length,1);assert.deepEqual(last.requests[0],fixture.firstCommand);assert.equal(last.shell.effects.windows[0].minimized,false);});
await check('Enter uses selected enabled action exactly once',await stage([...openA,navigate(open,'Enter')]),(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.registry,1);assert.deepEqual(last.requests,[fixture.firstCommand]);});
await check('duplicate old callback cannot forward',[...dispatched,action(open,'menu:1:1')],(_,last)=>{assert.equal(last.registry,1);assert.equal(last.requests.length,0);assert.equal(last.outstanding,1);});
await check('correlated receipt clears ledger without optimistic observation',[...dispatched,native(fixture.committed)],(_,last)=>{assert.equal(last.outstanding,0);assert.equal(last.registry,0);assert.equal(last.shell.phase,'Reconciling');assert.equal(last.shell.effects.windows[0].minimized,false);});
const bContext=context(open,'bar:group:application:org.b');
const replacement=[...openA,bContext];const replaced=(await replay(replacement)).at(-1).frame;
await check('replacement menu obtains a distinct lease',replacement,(_,last)=>{assert.equal(last.frame.mode,'menu');assert.notEqual(last.frame.lease,open.lease);assert.equal(last.menu.id,2);assert.equal(last.requests.length,0);});
await check('stale dismissal cannot close replacement lease',[...replacement,{kind:'dismiss',lease:open.lease}],(_,last)=>{assert.equal(last.frame.mode,'menu');assert.equal(last.frame.publication,replaced.publication);});
await check('current native dismissal closes and requests fresh facts without operation',[...replacement,{kind:'dismiss',lease:replaced.lease}],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.requests.length,1);assert.equal(last.requests[0].kind,'projection-request');assert.deepEqual(last.focus,[]);});
const unavailable=JSON.parse(JSON.stringify(fixture.projection));unavailable.scene.windows.forEach(row=>row.available=false);
const disabledBaseline=[owner(fixture.owner),native(fixture.attached),native(unavailable)];const disabledFrame=(await replay(disabledBaseline)).at(-1).frame;
await check('unavailable bar context refuses unsupported target',[...disabledBaseline,context(disabledFrame,'bar:group:application:org.a')],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.outstanding,0);assert.equal(last.requests.length,0);});

const grouped=JSON.parse(JSON.stringify(fixture.projection));grouped.scene.windows.forEach(row=>row.application='org.grouped');
const groupBaseline=[owner(fixture.owner),native(fixture.attached),native(grouped)];const groupReady=(await replay(groupBaseline)).at(-1).frame;
const groupPicker=[...groupBaseline,context(groupReady,'bar:group:application:org.grouped')];const picker=(await replay(groupPicker)).at(-1).frame;
await check('ambiguous family context opens picker without choosing a target',groupPicker,(_,last)=>{assert.equal(last.frame.mode,'picker');assert.equal(last.menu,null);assert.equal(last.requests.length,0);});
await check('popup explicit root context replaces picker with native menu',[...groupPicker,context(picker,'family:10','popup')],(_,last)=>{assert.equal(last.frame.mode,'menu');assert.equal(last.menu.selected,1);assert.equal(last.requests.length,0);});
await check('popup ownership alias cannot substitute an unlisted root',[...groupPicker,context(picker,'family:11','popup')],(_,last)=>{assert.equal(last.frame.mode,'picker');assert.equal(last.menu,null);assert.equal(last.frame.publication,picker.publication);});
await check('stale popup scope cannot open context menu',[...groupPicker,context({...picker,lease:'0'},'family:10','popup')],(_,last)=>{assert.equal(last.frame.mode,'picker');assert.equal(last.requests.length,0);assert.equal(last.frame.publication,picker.publication);});
const unknown={...fixture.committed,status:'Unknown',reason:'No definitive outcome'};
const fresh=JSON.parse(JSON.stringify(fixture.projection));fresh.requestId='3';fresh.context.revision='2';fresh.scene.revision='2';
const unknownReady=[...dispatched,native(unknown),native(fresh)];const unknownFrame=(await replay(unknownReady)).at(-1).frame;
const reopenedUnknown=[...unknownReady,context(unknownFrame,'bar:group:application:org.a')];const unknownMenu=(await replay(reopenedUnknown)).at(-1).frame;
await check('fresh observed facts never resolve Unknown or enable menu retry',reopenedUnknown,(_,last)=>{assert.equal(last.menu.status,'unknown');assert.equal(last.outstanding,1);assert.equal(last.registry,1);assert.equal(last.frame.mode,'menu');assert(last.frame.popup.filter(row=>row.id.startsWith('menu:')).every(row=>!row.enabled));assert.equal(last.requests.length,0);});
await check('Unknown taskbar primary cannot bypass existing native menu ledger',[...reopenedUnknown,action(unknownMenu,'bar:group:application:org.a','bar')],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.registry,1);assert.equal(last.outstanding,1);});
const bOpen=[...reopenedUnknown,context(unknownMenu,'bar:group:application:org.b')];const bMenu=(await replay(bOpen)).at(-1).frame;
const bDispatch=await stage([...bOpen,action(bMenu,'menu:3:1')]);
const commandB=JSON.parse(JSON.stringify(fixture.firstCommand));commandB.intent={...commandB.intent,request:'2',generation:'2',incarnation:'20',context:{...commandB.intent.context,revision:'2'}};
await check('unrelated target obtains its own engine-generated native intent',bDispatch,(_,last)=>{assert.deepEqual(last.requests,[commandB]);assert.equal(last.registry,2);assert.equal(last.outstanding,2);assert.equal(last.frame.mode,'closed');});
const receiptB={...fixture.committed,intent:commandB.intent};
await check('B receipt then delayed A receipt reconciles original map only',[...bDispatch,native(receiptB),native(fixture.committed)],(rows,last)=>{assert.equal(rows.at(-2).registry,1);assert.equal(rows.at(-2).outstanding,1);assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.deepEqual(last.shell.effects.transaction.intent,commandB.intent);assert.equal(last.shell.effects.transaction.status,'Committed');assert.equal(last.shell.effects.windows[0].minimized,false);assert.equal(last.requests.length,0);});
const newBinding={...fixture.binding,frontend:'301'};const rebindProjection=JSON.parse(JSON.stringify(fresh));rebindProjection.binding=newBinding;rebindProjection.requestId='4';rebindProjection.context.epoch='301';rebindProjection.context.revision='3';rebindProjection.scene.revision='3';
const disconnected=[...unknownReady,native({protocolVersion:3,kind:'host-disconnected'})];const lostFrame=(await replay(disconnected)).at(-1).frame;
const rebind=[...disconnected,action(lostFrame,'bar:reconnect','bar'),native({...fixture.attached,binding:newBinding}),native(rebindProjection)];const reboundFrame=(await replay(rebind)).at(-1).frame;
const reopenedRebind=[...rebind,context(reboundFrame,'bar:group:application:org.a')];const reboundMenu=(await replay(reopenedRebind)).at(-1).frame;
await check('frontend rebind of same window never releases unresolved action',reopenedRebind,(_,last)=>{assert.equal(last.menu.status,'unknown');assert.equal(last.registry,1);assert.equal(last.outstanding,1);assert.equal(last.requests.length,0);});
await check('same target primary remains guarded after frontend replacement',[...reopenedRebind,action(reboundMenu,'bar:group:application:org.a','bar')],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.registry,1);});
await check('original full receipt resolves retained old binding once',[...reopenedRebind,native(fixture.committed),native(fixture.committed)],(_,last)=>{assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.equal(last.shell.effects.transaction.status,'Unknown');assert.equal(last.requests.length,0);});

const retired=JSON.parse(JSON.stringify(fixture.projection));retired.requestId='2';retired.context.revision='2';retired.scene.revision='2';retired.scene.windows=retired.scene.windows.filter(row=>row.incarnation==='20');
await check('authoritative target retirement closes visible scoped menu',[...openA,native({protocolVersion:3,kind:'host-refresh'}),native(retired)],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.menu,null);assert.equal(last.outstanding,0);assert.equal(last.registry,0);assert.equal(last.requests.length,0);});

await check('retired menu callback cannot consume replacement target',[...replacement,action(open,'menu:1:1')],(_,last)=>{assert.equal(last.menu.id,2);assert.equal(last.frame.publication,replaced.publication);assert.equal(last.registry,0);assert.equal(last.requests.length,0);});
await check('current publication cannot forge retired menu identity',[...replacement,action(replaced,'menu:1:1')],(_,last)=>{assert.equal(last.menu.id,2);assert.equal(last.registry,0);assert.equal(last.requests.length,0);});
const pendingFrame=(await replay(dispatched)).at(-1).frame;
await check('pending engine refuses unrelated new context before approval',[...dispatched,context(pendingFrame,'bar:group:application:org.b')],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.registry,1);assert.equal(last.outstanding,1);assert.equal(last.requests.length,0);});
await check('navigation cannot originate from bar surface',[...openA,{kind:'action',action:{...navigate(open,'Enter').action,surface:'bar'}}],(_,last)=>{assert.equal(last.frame.mode,'menu');assert.equal(last.outstanding,0);assert.equal(last.requests.length,0);});
await check('visible Close control dismisses without window operation',[...openA,action(open,'control:menu-close')],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.registry,0);assert.equal(last.requests.length,1);assert.equal(last.requests[0].kind,'projection-request');assert.deepEqual(last.focus,[]);});

const focusOnly=JSON.parse(JSON.stringify(fixture.projection));focusOnly.requestId='2';focusOnly.context.revision='2';focusOnly.scene.revision='2';focusOnly.scene.focused='10';
const focusRefresh=[...openA,native({protocolVersion:3,kind:'host-refresh'}),native(focusOnly)];const focusMenu=(await replay(focusRefresh)).at(-1).frame;
await check('focus-only native revision refreshes provider with new menu ID and lease',focusRefresh,(_,last)=>{assert.equal(last.frame.mode,'menu');assert.equal(last.menu.id,2);assert.equal(last.menu.selected,1);assert.notEqual(last.frame.lease,open.lease);assert.equal(last.outstanding,0);assert.equal(last.registry,0);assert.equal(last.requests.length,0);});
await check('pre-focus old menu action remains retired',[...focusRefresh,action(open,'menu:1:1')],(_,last)=>{assert.equal(last.menu.id,2);assert.equal(last.frame.publication,focusMenu.publication);assert.equal(last.requests.length,0);assert.equal(last.registry,0);});
const focusedCommand=JSON.parse(JSON.stringify(fixture.firstCommand));focusedCommand.intent.context.revision='2';
await check('refreshed focus menu sends actual fresh context once',await stage([...focusRefresh,action(focusMenu,'menu:2:1')]),(_,last)=>{assert.deepEqual(last.requests,[focusedCommand]);assert.equal(last.frame.mode,'closed');assert.equal(last.registry,1);});
const changedActions=JSON.parse(JSON.stringify(focusOnly));changedActions.scene.focused=null;changedActions.scene.windows.filter(row=>row.incarnation==='10'||row.incarnation==='11').forEach(row=>row.minimized=true);
await check('changed capability table closes old ready menu instead of refreshing',[...openA,native({protocolVersion:3,kind:'host-refresh'}),native(changedActions)],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.menu,null);assert.equal(last.registry,0);assert.equal(last.requests.length,0);});

const withoutOwner=[native(fixture.attached),native(fixture.projection)];const unownedFrame=(await replay(withoutOwner)).at(-1).frame;
await check('native owner scope is required before window menu capability',[...withoutOwner,context(unownedFrame,'bar:group:application:org.a')],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.registry,0);assert.equal(last.requests.length,0);});
for(const [name,change] of [['zero output',{outputId:'0'}],['zero provider',{providerId:'0'}],['numeric output',{outputId:1}],['noncanonical',{outputId:'01'}],['overflow',{outputId:'18446744073709551616'}],['extra authority',{exec:'/bin/sh'}],['wrong protocol',{surfaceProtocol:3}],['wrong kind',{kind:'configure'}]]){
 const malformed=[owner({...fixture.owner,...change}),...withoutOwner];const untrustedFrame=(await replay(malformed)).at(-1).frame;
 await check('malformed native owner scope cannot grant menu '+name,[...malformed,context(untrustedFrame,'bar:group:application:org.a')],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.outstanding,0);assert.equal(last.requests.length,0);});
}
await check('duplicate exact registered owner leaves publication and menu unchanged',[...openA,owner(fixture.owner)],(_,last)=>{assert.equal(last.frame.publication,open.publication);assert.equal(last.menu.id,1);assert.equal(last.frame.mode,'menu');assert.equal(last.requests.length,0);});
const conflictingOwner={...fixture.owner,outputId:'2'};
const ownerConflict=[...openA,owner(conflictingOwner)];const failedOwnerFrame=(await replay(ownerConflict)).at(-1).frame;
await check('conflicting immutable owner closes menu and cannot be restored',[...ownerConflict,owner(fixture.owner),context(failedOwnerFrame,'bar:group:application:org.a')],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.menu,null);assert.equal(last.registry,0);assert.equal(last.requests.length,0);});
await check('owner conflict retains an already forwarded receipt mapping',[...dispatched,owner(conflictingOwner),native(fixture.committed)],(_,last)=>{assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.equal(last.frame.mode,'closed');assert.equal(last.requests.filter(row=>row.kind==='window-effect').length,0);});
const otherGeneration=JSON.parse(JSON.stringify(fixture.projection));otherGeneration.context.output='23';
const topologyBaseline=[owner(fixture.owner),native(fixture.attached),native(otherGeneration)];const topologyFrame=(await replay(topologyBaseline)).at(-1).frame;
const topologyOpen=[...topologyBaseline,context(topologyFrame,'bar:group:application:org.a')];const topologyMenu=(await replay(topologyOpen)).at(-1).frame;
const generationCommand=JSON.parse(JSON.stringify(fixture.firstCommand));generationCommand.intent.context.output='23';
await check('topology generation remains separate from registered output identity',await stage([...topologyOpen,action(topologyMenu,'menu:1:1')]),(_,last)=>{assert.deepEqual(last.requests,[generationCommand]);assert.deepEqual(last.providerScope,{outputId:'1',providerId:'1'});assert.deepEqual(last.ownerScope,{outputId:'1',providerId:'1'});assert.equal(last.registry,1);assert.equal(last.outstanding,1);assert.equal(last.frame.mode,'closed');});

const escapeClose=[...openA,navigate(open,'Escape')];
const closeObservation=JSON.parse(JSON.stringify(fixture.projection));closeObservation.requestId='2';closeObservation.context.revision='2';closeObservation.scene.revision='2';
await check('fresh live same-output facts restore menu group opener focus',[...escapeClose,native(closeObservation)],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.focus.length,1);assert(last.focus[0].endsWith(':application:org.a'));assert.equal(last.requests.length,0);});
const movedOutput=JSON.parse(JSON.stringify(closeObservation));movedOutput.context.output='2';
await check('changed native topology cancels menu opener focus',[...escapeClose,native(movedOutput)],(_,last)=>{assert.deepEqual(last.focus,[]);assert.equal(last.frame.mode,'closed');assert.equal(last.requests.length,0);});
const goneOpener=JSON.parse(JSON.stringify(closeObservation));goneOpener.scene.windows=goneOpener.scene.windows.filter(row=>row.incarnation==='20');
await check('retired menu target cannot receive returned opener focus',[...escapeClose,native(goneOpener)],(_,last)=>{assert.deepEqual(last.focus,[]);assert.equal(last.frame.mode,'closed');assert.equal(last.requests.length,0);});

const foreignScope={...fixture.owner,outputId:'777',providerId:'42'};
const foreignBase=[owner(foreignScope),native(fixture.attached),native(fixture.projection)];const foreignFrame=(await replay(foreignBase)).at(-1).frame;
const foreignOpen=[...foreignBase,context(foreignFrame,'bar:group:application:org.a')];
await check('registered non1 scope remains exact through fresh capability revision',[...foreignOpen,native({protocolVersion:3,kind:'host-refresh'}),native(focusOnly)],(_,last)=>{assert.equal(last.menu.id,2);assert.deepEqual(last.providerScope,{outputId:'777',providerId:'42'});assert.deepEqual(last.ownerScope,{outputId:'777',providerId:'42'});assert.equal(last.requests.length,0);});
await check('malformed owner after valid admission cannot replace or retire scope',[...openA,owner({...fixture.owner,exec:'/bin/sh'})],(_,last)=>{assert.equal(last.frame.publication,open.publication);assert.equal(last.menu.id,1);assert.deepEqual(last.ownerScope,{outputId:'1',providerId:'1'});assert.equal(last.ownerExhausted,false);assert.equal(last.requests.length,0);});
const providerConflict=[...openA,owner({...fixture.owner,providerId:'2'})];const providerFailed=(await replay(providerConflict)).at(-1).frame;
await check('changed provider identity permanently closes registered owner',[...providerConflict,owner(fixture.owner),context(providerFailed,'bar:group:application:org.a')],(_,last)=>{assert.equal(last.ownerExhausted,true);assert.equal(last.frame.mode,'closed');assert.equal(last.menu,null);assert.equal(last.requests.length,0);});
await check('new application invocation cancels pending menu opener focus',[...escapeClose,{kind:'open'},native(closeObservation)],(_,last)=>{assert.equal(last.frame.mode,'applications');assert.deepEqual(last.focus,[]);assert.equal(last.requests.length,0);});
const reflow=lease=>({kind:'reflow',lease});
const reflowA=[...openA,reflow(open.lease)];const reflowFrame=(await replay(reflowA)).at(-1).frame;
await check('current menu reflow retires publication and native lease before reread',reflowA,(_,last)=>{assert.notEqual(last.frame.publication,open.publication);assert.notEqual(last.frame.lease,open.lease);assert.deepEqual(last.requests.map(row=>row.kind),['projection-request']);assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.equal(last.shell.phase,'Reconciling');assert(last.frame.popup.filter(row=>row.id.startsWith('menu:')).every(row=>!row.enabled));assert(last.frame.popup.find(row=>row.id==='control:menu-close').enabled);});
await check('old callback cannot send across native reflow',[...reflowA,action(open,'menu:1:1')],(_,last)=>{assert.equal(last.frame.publication,reflowFrame.publication);assert.equal(last.registry,0);assert.equal(last.requests.length,0);});
await check('duplicate stale reflow lease never repeats refresh',[...reflowA,reflow(open.lease)],(_,last)=>{assert.equal(last.frame.publication,reflowFrame.publication);assert.equal(last.frame.lease,reflowFrame.lease);assert.equal(last.requests.length,0);});
await check('closed presentation reflow cannot alter pending original operation',[...dispatched,reflow(open.lease)],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.outstanding,1);assert.equal(last.registry,1);assert.equal(last.requests.length,0);assert.equal(last.shell.effects.transaction.status,'Pending');});
const unknownReflow=[...reopenedUnknown,reflow(unknownMenu.lease)];const unknownReflowFrame=(await replay(unknownReflow)).at(-1).frame;
await check('Unknown survives reflow without replaying a native operation',unknownReflow,(_,last)=>{assert.equal(last.registry,1);assert.equal(last.outstanding,1);assert.equal(last.requests.filter(row=>row.kind==='window-effect').length,0);});
const reflowWrong={...fixture.committed,intent:{...fixture.committed.intent,context:{...fixture.committed.intent.context,output:'2'}}};
await check('wrong full receipt binding cannot reconcile after reflow',[...unknownReflow,native(reflowWrong)],(_,last)=>{assert.equal(last.registry,1);assert.equal(last.outstanding,1);assert.equal(last.requests.length,0);});
await check('original bound receipt still resolves exactly once after reflow',[...unknownReflow,native(fixture.committed),native(fixture.committed)],(_,last)=>{assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.equal(last.requests.filter(row=>row.kind==='window-effect').length,0);});

await check('awaiting reflow Enter cannot prepare or dispatch an operation',[...reflowA,navigate(reflowFrame,'Enter')],(_,last)=>{assert.equal(last.registry,0);assert.equal(last.outstanding,0);assert.equal(last.frame.publication,reflowFrame.publication);assert.equal(last.requests.length,0);});
const unchangedObservation=JSON.parse(JSON.stringify(fixture.projection));unchangedObservation.requestId='2';
const authorizedReflow=[...reflowA,native(unchangedObservation)];const reflowReadyFrame=(await replay(authorizedReflow)).at(-1).frame;
await check('same exact freshly observed authority re-enables retained menu',authorizedReflow,(_,last)=>{assert.equal(last.menu.id,1);assert.equal(last.frame.mode,'menu');assert.equal(last.frame.lease,reflowFrame.lease);assert(last.frame.popup.find(row=>row.id==='menu:1:1').enabled);assert.equal(last.requests.length,0);});
await check('fresh authorized post-reflow action dispatches once',await stage([...authorizedReflow,action(reflowReadyFrame,'menu:1:1')]),(_,last)=>{assert.deepEqual(last.requests,[fixture.firstCommand]);assert.equal(last.frame.mode,'closed');assert.equal(last.registry,1);});
const passed=cases.every(row=>row.passed);fs.writeFileSync(process.argv[4],JSON.stringify({passed,checks:cases.length,cases,scope:'Compiled production visible menu controller; synthetic native facts; native gesture authority qualified separately'},null,2)+'\n');clearTimeout(timer);if(!passed)process.exitCode=1;
})().catch(error=>{clearTimeout(timer);console.error(error.stack);process.exitCode=1;});
