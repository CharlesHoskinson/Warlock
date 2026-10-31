import assert from 'node:assert/strict';
import {registerServices} from '../index.js';
const handlers=new Map(); registerServices({registerService(kind,fn){assert(!handlers.has(kind));handlers.set(kind,fn);}});
const binding={lifetime:'1',session:'1',frontend:'1'}, request={binding,requestId:'42'};
let world={epoch:1,services:{}}, replies=[];
const ctx={signal:new AbortController().signal,readWorld:()=>structuredClone(world),transact(fn){world=fn(structuredClone(world));return true;},reply:value=>replies.push(value)};
function run(kind,extra={}) {handlers.get(kind)({...request,...extra},ctx);return replies.pop();}
for(const [kind,response] of [['catalog-request','application-catalog'],['files-request','files-snapshot'],['system-menu-request','system-menu-snapshot'],['notification-request','notification-snapshot'],['shell-settings-request','shell-settings'],['motion-preferences-request','motion-preferences'],['shortcut-preferences-request','shortcut-preferences']]) {const value=run(kind);assert.equal(value.kind,response);assert.deepEqual(value.binding,binding);assert.equal(value.requestId,'42');}
let result=run('shell-settings-write',{proposal:{schema:2,revision:'1',values:{theme:'dawn',textScale:125,effectsOff:false,reducedTransparency:false}}}); assert.equal(result.status,'Saved');assert.equal(result.snapshot.revision,'2');
result=run('shell-settings-write',{proposal:{schema:2,revision:'1',values:{theme:'night',textScale:100,effectsOff:false,reducedTransparency:false}}});assert.equal(result.status,'Refused');
result=run('motion-preferences-write',{proposal:{schema:1,revision:'1',override:'reduced'}});assert.equal(result.status,'Saved');assert.equal(world.motion,undefined);
result=run('files-open',{intent:{service:'9',revision:'1',target:'coll:documents'}});assert.equal(result.status,'Opened');assert.equal(result.snapshot.peer.target,'coll:documents');
// Home expansion must fit the observed target decoder, and refusal must leave
// a valid snapshot available to a later refresh and a subsequent request.
world={epoch:1,services:{}};
result=run('files-open',{intent:{service:'9',revision:'1',target:'~/'+ 'a'.repeat(501)}});
assert.equal(result.status,'Opened'); assert.equal(result.snapshot.peer.target.length,512);
const beforeFiles=structuredClone(result.snapshot);
result=run('files-open',{intent:{service:'9',revision:'2',target:'~/'+ 'a'.repeat(502)}});
assert.equal(result.status,'Refused'); assert.deepEqual(result.snapshot,beforeFiles);
assert.deepEqual(run('files-request').snapshot,beforeFiles);
result=run('files-open',{intent:{service:'9',revision:'2',target:'~/Documents'}});
assert.equal(result.status,'Opened'); assert.equal(result.snapshot.peer.target,'/home/demo/Documents');
assert.deepEqual(run('files-request').snapshot,result.snapshot);
result=run('system-menu-effect',{intent:{service:'9',revision:'1',operation:'volume-set',value:25}});assert.equal(result.status,'Committed');assert.equal(result.snapshot.volume.percent,25);
// Submission is not observation: each accepted operation keeps the exact facts
// and revision. Fault injection follows the host's blocked-transaction wrapper.
for (const operation of ['suspend','reboot','poweroff','session-logout']) {
  for (const policy of ['success','refusal','unknown']) {
    world={epoch:1,services:{system:{service:'9',revision:'11',volume:null,network:null,power:{suspend:'yes',reboot:'yes',poweroff:'yes'},session:{name:'Simulated session',state:'active',locked:false}}}};
    const before=structuredClone(world), intent={service:'9',revision:'11',operation,value:0};
    const faultCtx={...ctx,transact:policy==='success'?ctx.transact:()=>false,reply(value){replies.push(policy==='success'?value:{...value,status:policy==='refusal'?'Refused':'Unknown'});}};
    handlers.get('system-menu-effect')({...request,intent},faultCtx);
    const receipt=replies.pop();
    assert.equal(receipt.status,{success:'Submitted',refusal:'Refused',unknown:'Unknown'}[policy]);
    assert.equal(receipt.requestId,request.requestId); assert.deepEqual(receipt.binding,binding);
    assert.deepEqual(receipt.snapshot,before.services.system); assert.deepEqual(world,before);
  }
  world={epoch:1,services:{}};
  result=run('system-menu-effect',{intent:{service:'9',revision:'0',operation,value:0}});
  assert.equal(result.status,'Refused');
}
world={epoch:1,services:{}};
result=run('system-menu-effect',{intent:{service:'9',revision:'1',operation:'poweroff',value:0}}); assert.equal(result.status,'Refused');
console.log('Verified power and logout submission, unchanged observations, stale and unavailable refusal, and injected refusal/unknown.');
result=run('application-launch',{intent:{request:'5',lifetime:'1',generation:'1',entry:'warlock-editor'}});assert.equal(result.outcome.status,'Submitted');assert.equal(result.outcome.reason,'native-submission-accepted');assert.equal(result.outcome.intent.request,'5');
console.log(`Verified ${handlers.size} registered handlers, request identity, successful local writes, stale refusal and launch submission.`);
// A catalog supplied by the host is authoritative, including its generation.
world.services.catalog={catalogProtocol:2,lifetime:'7',generation:'8',entries:[{id:'seeded',name:'Seeded',iconHint:'',wmclass:'',genericName:'',keywords:[]}]};
result=run('application-launch',{intent:{request:'6',lifetime:'7',generation:'8',entry:'seeded'}}); assert.equal(result.outcome.status,'Submitted');
result=run('application-launch',{intent:{request:'7',lifetime:'1',generation:'1',entry:'warlock-editor'}}); assert.equal(result.outcome.status,'Refused');
result=run('taskbar-pins-write',{proposal:{revision:'1',identities:['seeded']}}); assert.equal(result.status,'Saved');
result=run('motion-profile-set',{profile:'full'}); assert.equal(result.kind,'motion-profile'); assert.equal(result.requestId,'42'); assert.equal(world.motion.profile,'full');
const shortcutProposal={fingerprint:'a'.repeat(64),preferences:{schema:1,revision:'1',choices:{applications:'alternate',system:'keep',notifications:'default'}}};
result=run('shortcut-preferences-write',{proposal:shortcutProposal}); assert.equal(result.status,'Saved'); assert.equal(result.snapshot.revision,'2'); assert.equal(result.inventory.applications.active,'alternate'); assert.equal(result.inventory.notifications.active,'default');
result=run('shortcut-preferences-write',{proposal:shortcutProposal}); assert.equal(result.status,'Refused'); assert.equal(result.inventory.applications.active,'alternate');
world={epoch:1,services:{}};
let transactions=0;
const storageOnlyCtx={...ctx,transact(fn){return ++transactions===1 ? ctx.transact(fn) : false;}};
handlers.get('shortcut-preferences-write')({...request,proposal:shortcutProposal},storageOnlyCtx);
result=replies.pop(); assert.equal(result.status,'Stored'); assert.equal(result.snapshot.revision,'2'); assert.equal(result.inventory.applications.active,'keep');
console.log('Verified seeded catalog authority, applied motion acknowledgement and effective shortcut inventory.');
// Application action identities, stale revisions, and observations remain distinct.
world={epoch:1,services:{}}; let observations=[];
const actionHandlers=new Map();
registerServices({registerService(kind,fn){actionHandlers.set(kind,fn);},dispatchInput(input){observations.push(structuredClone(input));}});
function actionRun(kind,extra={}) {actionHandlers.get(kind)({...request,...extra},ctx);return replies.pop();}
let editor=actionRun('jump-list-request',{entry:'warlock-editor'}).snapshot;
let browser=actionRun('jump-list-request',{entry:'warlock-browser'}).snapshot;
assert.equal(editor.name,'Warlock Editor'); assert.equal(browser.name,'Browser'); assert.notDeepEqual(editor.actions,browser.actions);
assert.equal(actionRun('jump-list-request',{entry:'foreign'}).snapshot.available,false);
let actionIntent={service:editor.service,revision:editor.revision,entry:editor.entry,action:editor.actions[0].id};
result=actionRun('jump-list-effect',{intent:actionIntent}); assert.equal(result.status,'Submitted'); assert.equal(result.snapshot.revision,'2'); assert.equal(observations.length,1); assert.equal(observations[0].intent.entry,'warlock-editor');
result=actionRun('jump-list-effect',{intent:actionIntent}); assert.equal(result.status,'Refused'); assert.equal(observations.length,1);
result=actionRun('jump-list-effect',{intent:{...actionIntent,entry:'foreign'}}); assert.equal(result.status,'Refused'); assert.equal(observations.length,1);
world.services.catalog={...world.services.catalog, catalogProtocol:2,lifetime:'1',generation:'2',entries:[{id:'warlock-editor',name:'Different application',iconHint:'',wmclass:'',genericName:'',keywords:[]}]};
assert.equal(actionRun('jump-list-request',{entry:'warlock-editor'}).snapshot.available,false);
console.log('Verified application-specific actions, foreign and stale refusal, catalog identity, and separate observation.');
