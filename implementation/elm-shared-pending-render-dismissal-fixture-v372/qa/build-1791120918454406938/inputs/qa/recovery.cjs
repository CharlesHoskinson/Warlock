const fs=require('fs'),assert=require('assert');const {Elm}=require(process.argv[2]);
const binding={lifetime:'9007199254740993',session:'9',frontend:'2'};
const old={request:'41',generation:'43',incarnation:'7',operation:'minimize',context:{lifetime:binding.lifetime,epoch:'1',output:'3',revision:'4'}};
const attached={protocolVersion:3,kind:'attached',binding};
const recover={protocolVersion:3,kind:'host-uncertain',binding,intent:old};
const projection={protocolVersion:3,kind:'action-projection',binding,requestId:'1',context:{lifetime:binding.lifetime,epoch:'2',output:'3',revision:'5'},scene:{revision:'5',focused:null,windows:[{owner:null,application:'owned.app',available:true,incarnation:'7',label:'Window',minimized:false}]}};
const app=Elm.ShellReplay.init({flags:null});const timer=setTimeout(()=>{throw Error('Recovery replay completion deadline');},4000);
function replay(messages){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows)};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(messages)});}
(async()=>{let checks=0;const check=x=>{assert(x);checks++};
const rows=await replay([attached,recover,projection,{protocolVersion:3,kind:'effect-outcome',binding,intent:old,status:'Committed'},{kind:'user-action',operation:'minimize',incarnation:'7'}]);
check(rows[1].model.effects.transaction.status==='Unknown');check(rows[1].commands.length===0);check(rows[1].model.effects.request==='41');check(rows[1].model.phase==='Reconciling');check(!rows[1].model.available);
check(rows[2].model.effects.transaction.status==='Unknown');check(rows[2].model.phase==='Ready');check(rows[2].commands.length===0);check(rows[2].model.effects.windows[0].minimized===false);
check(rows[3].model.effects.transaction.status==='Unknown');check(rows[3].commands.length===0);
check(rows[4].commands.length===1);check(rows[4].commands[0].intent.request==='42');check(rows[4].commands[0].intent.generation==='44');check(rows[4].commands[0].intent.context.epoch==='2');
const cases=[{...recover,binding:{...binding,session:'8'}},{...recover,intent:{...old,context:{...old.context,lifetime:'8'}}},{...recover,intent:{...old,request:'0'}},{...recover,intent:{...old,operation:'close'}},{...recover,extra:true}];
for(const value of cases){const bad=await replay([attached,value]);check(bad[1].model.effects.transaction===null);check(bad[1].commands.length===0)}
const dup=await replay([attached,recover,{...recover,intent:{...old,request:'99'}},projection,recover]);check(dup[2].model.effects.request==='41');check(dup[4].model.effects.request==='41');check(dup.slice(1).every(r=>r.commands.length===0));
const early=await replay([recover,attached,projection,recover]);check(early[0].model.effects.transaction===null);check(early[3].model.effects.transaction===null);
fs.writeFileSync(process.argv[3],JSON.stringify({passed:true,checks,rows,dup,early},null,2)+'\n');clearTimeout(timer);
})().catch(e=>{console.error(e);process.exit(1)});
