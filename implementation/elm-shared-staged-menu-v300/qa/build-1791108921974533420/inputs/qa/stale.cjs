const fs=require('fs'),assert=require('assert');const {Elm}=require(process.argv[2]);
const binding={lifetime:'71',session:'2',frontend:'3'};
const attached={protocolVersion:3,kind:'attached',binding};
const projection={protocolVersion:3,kind:'action-projection',binding,requestId:'1',context:{lifetime:'71',epoch:'3',output:'5',revision:'6'},scene:{revision:'6',focused:null,windows:[{owner:null,application:'owned.app',available:true,incarnation:'4',label:'Window',minimized:false}]}};
const app=Elm.ShellReplay.init({flags:null});const timer=setTimeout(()=>{throw Error('Stale failure replay deadline');},4000);
function replay(messages){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows)};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(messages)});}
(async()=>{let checks=0,transcripts=[];const check=(x,name)=>{assert(x,name);checks++};
for(const reason of ['unavailable','full','busy','unverified','legacy-owner']){
 for(const stamp of [{binding,output:'5',revision:'5'},{binding:{...binding,session:'1'},output:'5',revision:'6'},{binding,output:'4',revision:'6'}]){
  const rows=await replay([attached,projection,{protocolVersion:3,kind:'host-recovery-failed',reason},{kind:'user-action',operation:'minimize',incarnation:'4',stamp}]);transcripts.push(rows);
  check(rows[3].model.status===rows[2].model.status,'stale action preserves '+reason+' explanation');check(rows[3].commands.length===0,'stale action never emits effect');check(rows[3].model.phase==='Detached','stale action remains detached');
 }
}
// A stale click while connected still explains that the displayed list changed.
const ready=await replay([attached,projection,{kind:'user-action',operation:'minimize',incarnation:'4',stamp:{binding,output:'5',revision:'5'}}]);
check(ready[2].model.status==='Window list changed. Choose again.','ready stale action notice retained');check(ready[2].commands.length===0,'ready stale action emits no effect');
fs.writeFileSync(process.argv[3],JSON.stringify({passed:true,checks,transcripts,ready},null,2)+'\n');clearTimeout(timer);
})().catch(e=>{console.error(e);process.exit(1)});
