const fs=require('fs'),assert=require('assert');const {Elm}=require(process.argv[2]);
const binding={lifetime:'71',session:'2',frontend:'3'};
const attached={protocolVersion:3,kind:'attached',binding};
const projection={protocolVersion:3,kind:'action-projection',binding,requestId:'1',context:{lifetime:'71',epoch:'3',output:'5',revision:'6'},scene:{revision:'6',focused:null,windows:[{owner:null,application:'owned.app',available:true,incarnation:'4',label:'Window',minimized:false}]}};
const app=Elm.ShellReplay.init({flags:null});const timer=setTimeout(()=>{throw Error('Storage replay completion deadline');},4000);
function replay(messages){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows)};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(messages)});}
(async()=>{let checks=0,transcripts=[];const check=x=>{assert(x);checks++};
for(const [reason,notice] of [['unavailable','Restore access'],['full','Free space'],['busy','Close it'],['unverified','Repair it'],['legacy-owner','Complete migration']]){
 const failure={protocolVersion:3,kind:'host-recovery-failed',reason};
 const rows=await replay([failure,{protocolVersion:3,kind:'host-disconnected'},{kind:'user-refresh'},{kind:'user-reconnect'},{kind:'user-reconnect'}]);transcripts.push(rows);
 check(rows[0].model.phase==='Detached'&&!rows[0].model.available);check(rows[0].model.status.includes(notice));check(rows[0].commands.length===0);
 check(rows[1].model.status===rows[0].model.status);check(rows[2].commands.length===0);check(rows[3].commands.length===1&&rows[3].commands[0].kind==='host-reconnect');check(rows[4].commands.length===0);
}
for(const bad of [{protocolVersion:2,kind:'host-recovery-failed',reason:'full'},{protocolVersion:3,kind:'host-recovery-failed',reason:'invented'},{protocolVersion:3,kind:'host-recovery-failed',reason:'full',extra:true}]){
 const rows=await replay([attached,projection,bad]);check(rows[2].model.phase==='Ready');check(rows[2].model.recoveryFailure===null);check(rows[2].commands.length===0);
}
const failed={protocolVersion:3,kind:'host-recovery-failed',reason:'unavailable'};
const fresh={...binding,session:'3',frontend:'4'};
const rows=await replay([attached,projection,{kind:'user-action',operation:'minimize',incarnation:'4'},failed,{protocolVersion:3,kind:'host-disconnected'},{kind:'user-action',operation:'restore',incarnation:'4'},{kind:'user-reconnect'},{protocolVersion:3,kind:'attached',binding:fresh},{...projection,binding:fresh,requestId:'2',context:{...projection.context,epoch:'4'}}]);
check(rows[2].model.effects.transaction.status==='Pending');check(rows[3].model.effects.transaction.status==='Unknown');check(!rows[3].model.available);check(rows[4].model.status.includes('Restore access'));check(rows[5].commands.length===0);check(rows[6].commands[0].kind==='host-reconnect');check(rows[7].model.recoveryFailure===null);check(rows[7].commands[0].kind==='projection-request');check(rows[8].model.phase==='Ready');check(rows[8].model.effects.transaction.status==='Unknown');check(rows[8].commands.length===0);
fs.writeFileSync(process.argv[3],JSON.stringify({passed:true,checks,transcripts,rows},null,2)+'\n');clearTimeout(timer);
})().catch(e=>{console.error(e);process.exit(1)});
