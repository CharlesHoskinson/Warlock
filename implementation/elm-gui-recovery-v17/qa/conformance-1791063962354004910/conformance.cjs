const fs=require('fs'),path=require('path'),assert=require('assert');
const {Elm}=require(process.argv[2]),app=Elm.ShellReplay.init({flags:null});
const deadline=setTimeout(()=>{throw new Error('Model replay deadline');},10000);
const big=x=>Number(x['#bigint']),binding=n=>({lifetime:'9007199254740993',session:String(n+8),frontend:'1'});
function replay(messages){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows);};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(messages);});}
(async()=>{
 let traces=0,transitions=0;const receipts=[];
 const directory=process.argv[3],files=fs.readdirSync(directory).filter(f=>f.endsWith('.itf.json'));assert(files.length===9);
 for(const file of files){
  const states=JSON.parse(fs.readFileSync(path.join(directory,file))).states,messages=[],positions=[],intents=new Map();let revision=4,lastContext=null;
  for(let i=1;i<states.length;i++){
   const {s,e}=states[i],before=states[i-1].s;if(e.kind==='assert')continue;
   let message;
   if(e.kind==='attach')message={protocolVersion:3,kind:'attached',binding:binding(big(e.binding))};
   else if(e.kind==='refresh')message={kind:'user-refresh'};
   else if(e.kind==='reconnect')message={kind:'user-reconnect'};
   else if(e.kind==='disconnect')message={kind:'host-disconnected'};
   else if(e.kind==='snapshot'){
    const context={lifetime:'9007199254740993',epoch:'1',output:'3',revision:String(++revision)};
    message={protocolVersion:3,kind:'action-projection',binding:binding(big(e.binding)),requestId:String(big(e.request)),context,scene:{revision:context.revision,windows:[{incarnation:'7',label:'Window',minimized:big(e.minimized)===1}]}};
    if(before.phase!=='Detached'&&big(before.binding)===big(e.binding)&&big(before.expected)===big(e.request)&&big(e.request)>0)lastContext=context;
   }else if(e.kind==='begin'){
    const operation=big(before.observed)===1?'restore':'minimize';message={kind:'user-action',operation,incarnation:'7'};
    if(big(s.counter)>big(before.counter))intents.set(big(s.counter),{request:String(big(s.counter)),generation:String(big(s.counter)),incarnation:'7',operation,context:lastContext});
   }else if(e.kind==='receipt'){
    const request=big(e.request),intent=intents.get(request)||{request:String(Math.max(1,request)),generation:String(Math.max(1,request)),incarnation:'7',operation:'minimize',context:lastContext||{lifetime:'9007199254740993',epoch:'1',output:'3',revision:'4'}};
    // Out-of-range request zero must remain mismatched, rather than rounding it
    // into a valid live transaction identity for the test translation.
    const correlated=request>0?intent:{...intent,incarnation:'99'};
    message={protocolVersion:3,kind:'effect-outcome',binding:binding(big(e.binding)),intent:correlated,status:e.status};
   }else throw new Error(e.kind);
   positions.push({row:messages.length,index:i});messages.push(message);
  }
  const rows=await replay(messages);
  for(const position of positions){const expected=states[position.index].s,actual=rows[position.row].model;
   assert.equal(actual.phase,expected.phase,`${file}:${position.index}:phase`);
   assert.equal(actual.request,String(big(expected.request)),`${file}:${position.index}:request`);
   assert.equal(actual.reconnecting,expected.reconnecting,`${file}:${position.index}:reconnect`);
   assert.equal(actual.effects.request,String(big(expected.counter)),`${file}:${position.index}:intent`);
   assert.equal(actual.effects.transaction?actual.effects.transaction.status:'Idle',expected.status,`${file}:${position.index}:status`);
   assert.equal(actual.effects.windows===null?-1:(actual.effects.windows[0].minimized?1:0),big(expected.observed),`${file}:${position.index}:observed`);
   assert.equal(actual.available,expected.phase==='Ready'&&expected.status!=='Pending');transitions++;
  }
  receipts.push({file,messages,rows});traces++;
 }
 fs.writeFileSync(process.argv[4],JSON.stringify({passed:true,traces,transitions,receipts},null,2)+'\n');clearTimeout(deadline);
})();
