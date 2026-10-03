const fs=require('node:fs'),assert=require('node:assert/strict');
const app=require(process.env.ELM_REPLAY).Elm.Replay.init({flags:null});
function replay(messages){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows)};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(messages)})}
const base={lifetime:'9007199254740993',epoch:'2',output:'3',revision:'4'};
const big=n=>n['#bigint'];
const identity=authority=>(9007199254740992n+BigInt(authority)).toString();
function snapshot(st,revision){return {kind:'snapshot',context:{...base,lifetime:identity(big(st.authority)),revision:String(revision)},scene:{revision:String(revision),locked:false,windows:[{id:'8',owner:null,mapped:true,minimized:st.observedMinimized,member:true,modal:false,inputAtProbe:true}],order:st.observedMinimized?[]:['8'],focused:st.observedMinimized?null:'8'}}}
(async()=>{
 let traces=0,transitions=0,receipts=[];
 const files=fs.readdirSync(process.env.QUINT_TRACES).filter(f=>f.endsWith('.itf.json'));
 assert.equal(files.filter(f=>f.startsWith('named-')).length,9);assert(files.some(f=>f.startsWith('sample-')));
 for(const file of files){const states=JSON.parse(fs.readFileSync(process.env.QUINT_TRACES+'/'+file)).states;let revision=4;const messages=[snapshot(states[0].s,revision)],positions=[{i:0,row:0}];let latestIntent=null;
 for(let i=1;i<states.length;i++){const {s,e}=states[i],prev=states[i-1].s;
 if(e.kind==='assert')continue;
 if(e.kind==='begin'){const operation=prev.observedMinimized?'restore':'minimize';messages.push({kind:'begin',operation,incarnation:'8'});if(prev.connected&&prev.status!=='Pending')latestIntent={request:big(s.request),generation:big(s.request),incarnation:'8',operation,context:{...base,lifetime:identity(big(s.authority)),revision:String(revision)}}}
 else if(e.kind==='disconnect')messages.push({kind:'disconnect'});
 else if(e.kind==='rebind')messages.push(snapshot(s,++revision));
 else if(e.kind==='scene'){if(!prev.connected)continue;messages.push(snapshot(s,++revision));}
 else if(e.kind==='receipt'){const intent=latestIntent?JSON.parse(JSON.stringify(latestIntent)):{request:'1',generation:'1',incarnation:'8',operation:'minimize',context:base};intent.request=big(e.request)==='0'?'1':big(e.request);intent.context.lifetime=identity(big(e.authority));messages.push({kind:'receipt',intent,status:e.status})}
 else throw Error('Unknown model action '+e.kind);
 positions.push({i,row:messages.length-1});
 }
 const rows=await replay(messages);
 for(const {i,row} of positions){const expected=states[i].s,actual=rows[row].model;assert.equal(actual.connected,expected.connected,`${file}:${i}:connected`);assert.equal(actual.request,big(expected.request),`${file}:${i}:request`);assert.equal(actual.transaction?.status||'Idle',expected.status,`${file}:${i}:status`);assert.deepEqual(actual.paint,expected.observedMinimized?[]:['8'],`${file}:${i}:paint`);transitions++}
 traces++;receipts.push({file,messages,rows});
 }
 fs.writeFileSync(process.env.CONFORMANCE_REPORT,JSON.stringify({passed:true,traces,statesCompared:transitions,receipts},null,2)+'\n');console.log(traces+' Quint action journals replayed into compiled Elm');
})().catch(e=>{console.error(e);process.exitCode=1});
