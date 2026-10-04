const fs=require('fs'),assert=require('assert');
const {Elm}=require(process.argv[2]);
const binding={lifetime:'9007199254740993',session:'8',frontend:'1'},fresh={...binding,session:'9'};
const stamp={binding,output:'3',revision:'4'};
const attach=b=>({protocolVersion:3,kind:'attached',binding:b});
const projection=(b,requestId,revision='4',output='3',focused=null)=>({protocolVersion:3,kind:'action-projection',binding:b,requestId,context:{lifetime:b.lifetime,epoch:b.frontend,output,revision},scene:{revision,focused,windows:[{incarnation:'7',owner:null,application:'owned.app',available:true,label:'Owned',minimized:false}]}});
const act=s=>({kind:'user-action',operation:'activate',incarnation:'7',stamp:s});
const app=Elm.ShellReplay.init({flags:null});
const deadline=setTimeout(()=>{throw Error('Displayed scope replay deadline');},4000);
function replay(messages){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows);};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(messages);});}
(async()=>{
 const base=[attach(binding),projection(binding,'1')],results=[];
 async function check(name,messages,allowed=false){const rows=await replay(messages),last=rows.at(-1);assert.equal(last.commands.length,allowed?1:0,name);if(allowed)assert.equal(last.commands[0].kind,'window-effect');else assert.equal(last.model.effects.transaction,null,name);results.push({name,rows});}
 await check('current displayed scope acts', [...base,act(stamp)],true);
 await check('old session cannot alias reused incarnation', [...base,{kind:'host-disconnected'},{kind:'user-reconnect'},attach(fresh),projection(fresh,'2'),act(stamp)]);
 await check('new session explicit selection acts', [...base,{kind:'host-disconnected'},{kind:'user-reconnect'},attach(fresh),projection(fresh,'2'),act({...stamp,binding:fresh})],true);
 await check('old native focus revision cannot toggle new state',[...base,{kind:'user-refresh'},projection(binding,'2','5','3','7'),act(stamp)]);
 await check('old output scope cannot select after transfer',[...base,{kind:'user-refresh'},projection(binding,'2','5','4'),act(stamp)]);
 await check('detached queued selection has no effect',[...base,{kind:'host-disconnected'},act(stamp)]);
 await check('awaiting replacement snapshot has no effect',[...base,{kind:'user-refresh'},act(stamp)]);
 for(const bad of [null,{...stamp,revision:'0'},{...stamp,output:'03'},{...stamp,extra:true},{...stamp,binding:{...binding,frontend:'2'}},{...stamp,binding:{...binding,lifetime:'5'}}])await check('malformed or mismatched explicit stamp '+JSON.stringify(bad),[...base,act(bad)]);
 const pending=await replay([...base,act(stamp),act(stamp)]);assert.equal(pending.at(-1).commands.length,0);assert.equal(pending.at(-1).model.effects.transaction.status,'Pending');results.push({name:'duplicate click while Pending emits nothing',rows:pending});
 fs.writeFileSync(process.argv[3],JSON.stringify({passed:true,checks:results.length,scope:'Compiled Shell replay; actual pointer queues and native taskbar acceptance remain separate',results},null,2)+'\n');clearTimeout(deadline);
})();
