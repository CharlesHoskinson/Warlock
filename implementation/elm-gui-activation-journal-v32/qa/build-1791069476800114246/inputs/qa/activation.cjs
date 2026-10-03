const fs=require('fs');const assert=require('assert');const Elm=require(process.argv[2]).Elm;
const deadline=setTimeout(()=>{throw new Error('Activation replay deadline');},15000);
const context={lifetime:'9007199254740993',epoch:'2',output:'3',revision:'4'};
const identity='18446744073709551615';
function snapshot(minimized){return {kind:'snapshot',context,scene:{revision:'4',windows:[{incarnation:identity,label:'Owned window',minimized}]}};}
const begin={kind:'begin',operation:'activate',incarnation:identity};
function receipt(status,operation='activate'){return {kind:'receipt',intent:{request:'1',generation:'1',incarnation:identity,operation,context},status};}
function replay(messages){return new Promise(resolve=>{const app=Elm.Replay.init({flags:null});const receive=rows=>{app.ports.outgoing.unsubscribe(receive);resolve(rows);};app.ports.outgoing.subscribe(receive);app.ports.incoming.send(messages);});}
(async()=>{
 const cases=[];
 async function check(name,messages,verify){const rows=await replay(messages);verify(rows);cases.push({name,passed:true});}
 await check('visible-activation-is-typed-pending',[snapshot(false),begin],r=>{assert.equal(r[1].model.transaction.status,'Pending');assert.equal(r[1].effect.intent.operation,'activate');assert.equal(r[1].effect.intent.incarnation,identity);assert.equal(r[1].model.windows[0].minimized,false);});
 await check('minimized-activation-refused-without-restore',[snapshot(true),begin],r=>{assert(r[1].error);assert.equal(r[1].effect,null);assert.equal(r[1].model.windows[0].minimized,true);});
 await check('activation-receipt-preserves-observed-state',[snapshot(false),begin,receipt('Committed')],r=>{assert.equal(r[2].model.transaction.status,'Committed');assert.equal(r[2].model.windows[0].minimized,false);});
 for(const status of ['Refused','Cancelled','Unknown'])await check('activation-terminal-'+status,[snapshot(false),begin,receipt(status)],r=>assert.equal(r[2].model.transaction.status,status));
 await check('different-operation-receipt-refused',[snapshot(false),begin,receipt('Committed','minimize')],r=>{assert(r[2].error);assert.equal(r[2].model.transaction.status,'Pending');});
 await check('pending-activation-not-overwritten',[snapshot(false),begin,{kind:'begin',operation:'minimize',incarnation:identity}],r=>{assert(r[2].error);assert.equal(r[2].model.transaction.intent.operation,'activate');assert.equal(r[2].effect,null);});
 await check('activation-disconnect-is-unknown',[snapshot(false),begin,{kind:'disconnect'},receipt('Committed')],r=>{assert.equal(r[2].model.transaction.status,'Unknown');assert(r[3].error);assert.equal(r[3].model.transaction.status,'Unknown');});
 await check('reconnection-does-not-replay-activation',[snapshot(false),begin,{kind:'disconnect'},snapshot(false)],r=>{assert.equal(r[3].model.transaction.status,'Unknown');assert.equal(r[3].effect,null);});
 await check('already-terminal-activation-receipt-refused',[snapshot(false),begin,receipt('Committed'),receipt('Committed')],r=>{assert(r[3].error);assert.equal(r[3].model.transaction.status,'Committed');});
 await check('unmapped-activation-refused',[snapshot(false),{...begin,incarnation:'7'}],r=>{assert(r[1].error);assert.equal(r[1].effect,null);});
 for(const operation of ['Activate','activate ','focus',null,3])await check('invalid-operation-'+JSON.stringify(operation),[snapshot(false),{...begin,operation}],r=>{assert(r[1].error);assert.equal(r[1].effect,null);});
 fs.writeFileSync(process.argv[3],JSON.stringify({passed:true,checks:cases.length,cases,scope:'Compiled pure typed activation transaction behavior; native focus/pixels/GUI are separate'},null,2)+'\n');clearTimeout(deadline);
})().catch(e=>{clearTimeout(deadline);console.error(e);process.exitCode=1;});
