const assert=require('node:assert/strict');const fs=require('node:fs');
const app=require(process.env.ELM_REPLAY).Elm.Replay.init({flags:null});
const clone=x=>JSON.parse(JSON.stringify(x));let count=0, transcripts=[];
function replay(messages){return new Promise(resolve=>{const receive=result=>{app.ports.outgoing.unsubscribe(receive);transcripts.push({messages,result});resolve(result)};app.ports.outgoing.subscribe(receive);app.ports.incoming.send(messages)})}
const context={lifetime:'9007199254740993',epoch:'2',output:'3',revision:'4'};
function snapshot(minimized=false,revision='4',ctx={}) {return {kind:'snapshot',context:{...context,revision,...ctx},scene:{revision,locked:false,windows:[{id:'8',owner:null,mapped:true,minimized,member:true,modal:false,inputAtProbe:true}],order:minimized?[]:['8'],focused:minimized?null:'8'}}}
const begin={kind:'begin',operation:'minimize',incarnation:'8'};
const intent={request:'1',generation:'1',incarnation:'8',operation:'minimize',context};
const receipt=status=>({kind:'receipt',intent:clone(intent),status});
function check(name,test){count++;try{test()}catch(e){e.message=name+': '+e.message;throw e}}
(async()=>{
 let rows=await replay([snapshot(),begin,receipt('Committed')]);
 check('identity tuple',()=>assert.deepEqual(rows[1].effect,{kind:'window-effect',protocol:1,intent}));
 check('pending does not hide',()=>assert.deepEqual(rows[1].model.paint,['8']));
 check('receipt does not hide',()=>assert.deepEqual(rows[2].model.paint,['8']));
 check('committed distinguished',()=>assert.equal(rows[2].model.transaction.status,'Committed'));
 rows=await replay([snapshot(),begin,receipt('Committed'),snapshot(true,'5'),{...begin,operation:'restore'}]);
 check('native minimized scene hides',()=>assert.deepEqual(rows[3].model.paint,[]));
 check('restore generation and revision',()=>{assert.equal(rows[4].effect.intent.operation,'restore');assert.equal(rows[4].effect.intent.request,'2');assert.equal(rows[4].effect.intent.generation,'2');assert.equal(rows[4].effect.intent.context.revision,'5')});
 for(const status of ['Refused','Cancelled']){rows=await replay([snapshot(),begin,receipt(status)]);check(status,()=>{assert.equal(rows[2].model.transaction.status,status);assert.deepEqual(rows[2].model.paint,['8'])})}
 rows=await replay([snapshot(),begin,{kind:'disconnect'},receipt('Committed'),begin,snapshot(),receipt('Committed')]);
 check('disconnect unknown',()=>assert.equal(rows[2].model.transaction.status,'Unknown'));
 check('late outcome remains unknown',()=>assert.equal(rows[3].model.transaction.status,'Unknown'));
 check('disconnect suppresses effects',()=>assert.equal(rows[4].effect,null));
 check('exact resync allowed',()=>assert.equal(rows[5].model.connected,true));
 check('resync never recommits old request',()=>assert.equal(rows[6].model.transaction.status,'Unknown'));
 for(const field of ['request','generation','incarnation','operation']){let changed=receipt('Committed');changed.intent[field]=field==='operation'?'restore':'99';rows=await replay([snapshot(),begin,changed]);check('mismatch '+field,()=>assert.equal(rows[2].model.transaction.status,'Pending'))}
 for(const field of ['lifetime','epoch','output','revision']){let changed=receipt('Committed');changed.intent.context[field]='99';rows=await replay([snapshot(),begin,changed]);check('mismatch '+field,()=>assert.equal(rows[2].model.transaction.status,'Pending'))}
 for(const field of ['lifetime','epoch','output']){rows=await replay([snapshot(),begin,snapshot(false,'5',{[field]:'99'}),receipt('Committed')]);check('authority changed '+field,()=>assert.equal(rows[3].model.transaction.status,'Unknown'))}
 rows=await replay([snapshot(),begin,begin]);check('single pending bound',()=>{assert.equal(rows[2].effect,null);assert.equal(rows[2].model.request,'1')});
 rows=await replay([snapshot(),{...begin,incarnation:'9'}]);check('unknown incarnation',()=>assert.equal(rows[1].effect,null));
 rows=await replay([snapshot(true),begin]);check('already minimized',()=>assert.equal(rows[1].effect,null));
 rows=await replay([snapshot(),{...begin,operation:'restore'}]);check('already restored',()=>assert.equal(rows[1].effect,null));
 rows=await replay([snapshot(),begin,receipt('Refused'),receipt('Committed')]);check('terminal cannot change',()=>assert.equal(rows[3].model.transaction.status,'Refused'));
 rows=await replay([snapshot(),begin,snapshot(false,'5'),receipt('Committed')]);check('new scene revision does not miscorrelate receipt',()=>assert.equal(rows[3].model.transaction.status,'Committed'));
 rows=await replay([snapshot(false,'5'),{kind:'disconnect'},snapshot(false,'4')]);check('resync cannot rewind',()=>assert.equal(rows[2].model.connected,false));
 let malformed=snapshot();malformed.scene.windows[0].minimized=null;rows=await replay([malformed,begin]);check('unknown minimization refuses bind',()=>assert.equal(rows[1].effect,null));
 for(const value of [0,8,'08','-1','18446744073709551616']){rows=await replay([snapshot(),{...begin,incarnation:value}]);check('bad counter '+value,()=>assert.equal(rows[1].effect,null))}
 rows=await replay([snapshot(),{...begin,workspace:'special:win-minimized'}]);check('scratchpad parameter rejected',()=>assert.equal(rows[1].effect,null));
 rows=await replay([snapshot(),begin,{...receipt('Committed'),extra:true}]);check('receipt extra field rejected',()=>assert.equal(rows[2].model.transaction.status,'Pending'));
 // Deterministic adversarial receipt field mutations retain independent expected
 // results, including every authority-bearing field and high canonical counters.
 for(let i=0;i<160;i++){let changed=receipt(['Committed','Refused','Cancelled'][i%3]);const fields=['request','generation','incarnation','lifetime','epoch','output','revision'];let f=fields[i%fields.length];let target=['request','generation','incarnation'].includes(f)?changed.intent:changed.intent.context;target[f]=(BigInt(target[f])+BigInt(i+1)).toString();rows=await replay([snapshot(),begin,changed]);check('fuzz-correlated-'+i,()=>assert.equal(rows[2].model.transaction.status,'Pending'))}
 fs.writeFileSync(process.env.ELM_REPORT,JSON.stringify({passed:true,checks:count,transcripts},null,2)+'\n');console.log(count+' compiled Elm effect checks passed');
})().catch(e=>{console.error(e);process.exitCode=1});
