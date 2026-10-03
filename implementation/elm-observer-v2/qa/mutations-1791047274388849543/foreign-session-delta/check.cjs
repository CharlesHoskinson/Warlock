'use strict';
const fs=require('fs'), assert=require('node:assert/strict');
const {Elm}=require(process.env.ELM_REPLAY || '../build/replay.js');
const binding={lifetime:'1',session:'2',frontend:'3'};
const window={incarnation:'9007199254740993',label:'Window',minimized:false};
const attach=(b=binding)=>({op:'attach',binding:b});
const observation=event=>({op:'observe',event});
const snapshot=(sequence='0',requestId='1',revision=sequence,windows=[window],b=binding)=>observation({protocolVersion:2,kind:'snapshot',binding:b,requestId,sequence,revision,windows});
const delta=(sequence,revision=sequence,windows=[window],b=binding)=>observation({protocolVersion:2,kind:'delta',binding:b,sequence,revision,windows});
const cases=[],checks=[];
function test(name,operations,verify){cases.push({name,operations});checks.push(verify);}
const last=c=>c.steps.at(-1);
const coherent=(c,sequence)=>{assert.equal(last(c).phase,'Coherent');assert.equal(last(c).projection.sequence,sequence);};
const gap=c=>assert.equal(last(c).phase,'Gap');
const start=[attach(),snapshot()];
test('initial-snapshot-is-correlated',start,c=>coherent(c,'0'));
test('contiguous-delta', [...start,delta('1')],c=>coherent(c,'1'));
test('gap-retains-last-coherent-projection',[...start,delta('2')],c=>{gap(c);assert.equal(last(c).projection.sequence,'0');assert.equal(last(c).floor,'2');assert.equal(last(c).effects.length,1);});
test('gap-deduplicates-recovery',[...start,delta('2'),delta('3'),delta('4')],c=>{gap(c);assert.equal(last(c).floor,'4');assert.equal(c.steps.flatMap(s=>s.effects).length,2);});
test('late-contiguous-delta-cannot-clear-gap',[...start,delta('2'),delta('1')],gap);
test('snapshot-below-observed-gap-cannot-clear',[...start,delta('3'),snapshot('2','2')],gap);
test('snapshot-at-gap-restores',[...start,delta('3'),snapshot('3','2')],c=>coherent(c,'3'));
test('replayed-old-snapshot-cannot-clear',[...start,delta('3'),snapshot('3','1')],gap);
test('snapshot-wrong-request-is-ignored',[attach(),snapshot('0','2')],c=>assert.equal(last(c).phase,'Awaiting'));
test('refresh-supersedes-request',[attach(),{op:'refresh'},snapshot('0','1'),snapshot('0','2')],c=>{assert.equal(c.steps[2].phase,'Awaiting');coherent(c,'0');});
test('duplicate-delta-idempotent',[...start,delta('1'),delta('1','1',[{...window,label:'stale'}])],c=>{coherent(c,'1');assert.equal(last(c).projection.windows[0].label,'Window');});
test('older-delta-idempotent',[...start,delta('1'),delta('0')],c=>coherent(c,'1'));
test('revision-regression-barrier',[attach(),snapshot('0','1','7'),delta('1','6')],gap);
test('equal-sequence-conflicting-snapshot-refused',[...start,{op:'refresh'},snapshot('0','2','0',[{...window,label:'conflict'}])],gap);
test('old-revision-snapshot-refused',[attach(),snapshot('0','1','7'),{op:'refresh'},snapshot('1','2','6')],gap);
for(const field of ['lifetime','session','frontend']){
 const wrong={...binding,[field]:'9'};
 test(`wrong-${field}-delta-ignored`,[...start,delta('1','1',[window],wrong)],c=>coherent(c,'0'));
 test(`wrong-${field}-snapshot-ignored`,[attach(),snapshot('0','1','0',[window],wrong)],c=>assert.equal(last(c).phase,'Awaiting'));
}
test('restart-invalidates-old-projection',[...start,attach({...binding,frontend:'4'}),snapshot('99','1'),snapshot('0','1','0',[window],{...binding,frontend:'4'})],c=>{assert.equal(c.steps[2].projection,null);assert.equal(c.steps[3].phase,'Awaiting');coherent(c,'0');});
test('duplicate-attach-does-not-reset-watermark',[...start,delta('1'),attach()],c=>coherent(c,'1'));
test('disconnect-withholds-events',[...start,{op:'disconnect'},delta('1'),snapshot('8')],c=>{assert.equal(last(c).phase,'Detached');assert.equal(last(c).projection.sequence,'0');assert.equal(last(c).effects.length,0);});
test('same-binding-cannot-reconnect',[...start,{op:'disconnect'},attach()],c=>assert.equal(last(c).phase,'Detached'));
test('delta-before-snapshot-raises-floor',[attach(),delta('8'),snapshot('0','2')],gap);
test('max-sequence-does-not-wrap',[attach(),snapshot('18446744073709551615'),delta('0')],c=>coherent(c,'18446744073709551615'));
test('lossless-neighboring-sequences',[attach(),snapshot('9007199254740992'),delta('9007199254740993'),delta('9007199254740994')],c=>coherent(c,'9007199254740994'));
test('decimal-carry',[attach(),snapshot('9999999999999999999'),delta('10000000000000000000')],c=>coherent(c,'10000000000000000000'));
test('obsolete-response-consumed-once',[...start,delta('3'),snapshot('2','2'),snapshot('3','2'),snapshot('3','3')],c=>{assert.equal(c.steps[4].phase,'Gap');coherent(c,'3');assert.equal(c.steps.flatMap(s=>s.effects).length,3);});
test('changed-pixels-require-new-revision',[...start,delta('1','0',[{...window,minimized:true}])],gap);
test('changed-snapshot-requires-new-revision',[...start,{op:'refresh'},snapshot('1','2','0',[{...window,minimized:true}])],gap);
test('architecture-010',[attach(),snapshot('10'),delta('9'),delta('12')],c=>{
 assert.equal(c.steps[2].projection.sequence,'10');gap(c);assert.equal(last(c).projection.sequence,'10');assert.equal(last(c).floor,'12');assert.equal(last(c).effects[0].kind,'read-only-snapshot');
});
test('revision-008',[attach(),snapshot('10'),delta('12','12',[{...window,incarnation:'9007199254740994'}])],c=>{
 gap(c);assert.equal(last(c).projection.windows[0].incarnation,window.incarnation);assert.equal(last(c).projection.sequence,'10');
});
const raw=snapshot().event;
const invalid=[
 ['version',{...raw,protocolVersion:1}],['kind',{...raw,kind:'focus'}],['unknown-field',{...raw,path:'/etc/passwd'}],
 ['numeric-sequence',{...raw,sequence:0}],['leading-zero',{...raw,sequence:'01'}],['negative',{...raw,sequence:'-1'}],
 ['unicode-digit',{...raw,sequence:'١'}],['overflow',{...raw,sequence:'18446744073709551616'}],
 ['numeric-incarnation',{...raw,windows:[{...window,incarnation:9007199254740992}]}],['zero-incarnation',{...raw,windows:[{...window,incarnation:'0'}]}],
 ['duplicate-incarnation',{...raw,windows:[window,window]}],['too-many-windows',{...raw,windows:Array.from({length:257},(_,i)=>({...window,incarnation:String(i+1)}))}],
 ['oversized-label',{...raw,windows:[{...window,label:'a'.repeat(257)}]}],['control-label',{...raw,windows:[{...window,label:'private\ntext'}]}],
 ['unknown-binding-field',{...raw,binding:{...binding,authority:'forged'}}],['zero-session',{...raw,binding:{...binding,session:'0'}}],['missing-field',{...raw,windows:undefined}]
];
for(const [name,event] of invalid)test(`decoder-refuses-${name}`,[...start,observation(event)],c=>{gap(c);assert.deepEqual(last(c).projection,c.steps[1].projection);});
// Deterministic generated adversarial transcripts. Oracles assert causal outcomes,
// not the reducer's implementation: omitted stream member must block later data.
let seed=610303;function random(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;}
for(let i=0;i<200;i++){
 const base=BigInt(random())+(i%2?9007199254740992n:0n), length=2+(random()%14);
 const omitted=1+(random()%(length-1)),ops=[attach(),snapshot(String(base))];
 for(let j=1;j<=length;j++)if(j!==omitted)ops.push(delta(String(base+BigInt(j))));
 ops.push(snapshot(String(base+BigInt(length)-1n),'2'));
 const barrierIndex=ops.length-1;
 ops.push(snapshot(String(base+BigInt(length)),'3'));
 test(`fuzz-gap-resync-${i}`,ops,c=>{assert.equal(c.steps[barrierIndex].phase,'Gap');coherent(c,String(base+BigInt(length)));assert.equal(c.steps.flatMap(s=>s.effects).length,3);});
}
const timer=setTimeout(()=>{throw new Error('Replay timeout');},15000);
const app=Elm.Replay.init({flags:null});
app.ports.results.subscribe(report=>{
 clearTimeout(timer);
 let passed=true;const results=[];
 if(report.error)throw new Error(report.error);
 assert.equal(report.cases.length,cases.length);
 assert.equal(report.counters.next.length,10);
 report.counters.next.forEach((row,i)=>{
 const expected=BigInt(row.value)===18446744073709551615n?null:String(BigInt(row.value)+1n);
 assert.equal(row.next,expected,'Lossless counter successor '+row.value);
 report.counters.next.forEach((other,j)=>{
 const a=BigInt(row.value),b=BigInt(other.value),order=a<b?-1:a>b?1:0;
 assert.equal(report.counters.comparisons[i][j],order,'Lossless counter comparison');
 });
 });
 report.cases.forEach((c,i)=>{let error=null;try{
   assert.equal(c.name,cases[i].name);checks[i](c);
   for(const s of c.steps)for(const effect of s.effects)assert.equal(effect.kind,'read-only-snapshot');
 }catch(e){passed=false;error=e.message;}
 results.push({name:c.name,passed:!error,...(error?{error}:{})});});
 const receipt={scope:'Compiled Elm observer: CPU replay and deterministic adversarial transcripts, no native acceptance',passed,seed:610303,testCount:results.length,counterSuccessorChecks:10,counterComparisonChecks:100,results};
 fs.writeFileSync(process.env.ELM_REPORT || 'build/elm-report.json',JSON.stringify(receipt,null,2)+'\n');
 fs.writeFileSync(process.env.ELM_TRANSCRIPTS || 'build/transcripts.json',JSON.stringify({inputs:cases,outputs:report},null,2)+'\n');
 console.log(JSON.stringify(receipt,null,2));process.exit(passed?0:1);
});
app.ports.transcripts.send(cases);
