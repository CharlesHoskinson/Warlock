'use strict';
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {Elm}=require(process.env.ELM_REPLAY);
const dir=process.env.QUINT_TRACES;
function decode(x){if(x&&typeof x==='object'){if('#bigint' in x)return x['#bigint'];if(Array.isArray(x))return x.map(decode);return Object.fromEntries(Object.entries(x).map(([k,v])=>[k,decode(v)]));}return x;}
const files=fs.readdirSync(dir).filter(n=>n.endsWith('.itf.json')).sort();
const binding=e=>({lifetime:'1',session:'2',frontend:e});
const windows=c=>[{incarnation:'9007199254740993',label:'Window',minimized:c==='1'}];
function operation(s){const i=s.input;
 switch(i.kind){
 case 'attach':return {op:'attach',binding:binding(i.epoch)};
 case 'delta':case 'snapshot':return {op:'observe',event:{protocolVersion:2,kind:i.kind,binding:binding(i.epoch),sequence:i.seq,revision:i.rev,windows:windows(i.content),...(i.kind==='snapshot'?{requestId:i.req}:{})}};
 case 'malformed':return {op:'observe',event:{}};
 case 'refresh':case 'disconnect':return {op:i.kind};
 default:throw Error('Unknown model input '+i.kind);
 }}
const expected=[];
const cases=files.map(name=>{const trace=decode(JSON.parse(fs.readFileSync(path.join(dir,name),'utf8')));const states=trace.states.map(s=>s.s).filter(s=>!['init','noop'].includes(s.input.kind));expected.push(states);return {name,operations:states.map(operation)};});
assert.ok(cases.length>=12,'No actual Quint test traces');
const app=Elm.Replay.init({flags:null});
const timer=setTimeout(()=>{throw Error('Conformance timed out');},15000);
app.ports.results.subscribe(report=>{
 clearTimeout(timer);assert.ok(!report.error,report.error);assert.equal(report.cases.length,cases.length);
 const rows=[];let passed=true,stepCount=0;
 report.cases.forEach((c,i)=>{let error=null;try{
 assert.equal(c.name,cases[i].name);assert.equal(c.steps.length,expected[i].length);
 c.steps.forEach((actual,j)=>{stepCount++;const model=expected[i][j];const label=c.name+' step '+j;
 assert.equal(actual.phase,model.phase,label+' phase');assert.equal(actual.floor,model.floor,label+' floor');
 assert.equal(actual.lastRequest,model.request,label+' request');assert.equal(actual.pending,model.pending==='0'?null:model.pending,label+' pending');
 assert.equal(actual.effects.length,model.effects,label+' effects');
 assert.equal(actual.projection?.sequence??'-1',model.seq,label+' sequence');
 assert.equal(actual.projection?.revision??'-1',model.rev,label+' revision');
 if(actual.projection)assert.equal(actual.projection.windows[0].minimized,model.content==='1',label+' content');
 });
 }catch(e){passed=false;error=e.message;}rows.push({name:c.name,passed:!error,...(error?{error}:{})});});
 const receipt={scope:'Quint ITF traces replayed through actual compiled Observer.update at every state transition',passed,traceCount:cases.length,stepCount,results:rows};
 fs.writeFileSync(process.env.CONFORMANCE_REPORT,JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt,null,2));process.exit(passed?0:1);
});
app.ports.transcripts.send(cases);
