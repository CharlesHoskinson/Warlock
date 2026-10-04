const fs=require('fs'),assert=require('assert'),{Elm}=require(process.argv[2]);
const report=JSON.parse(fs.readFileSync(process.argv[3]));assert(report.passed);
const app=Elm.TaskbarReplay.init({flags:null}),deadline=setTimeout(()=>{throw Error('Native packet replay deadline');},4000);
function replay(scene){return new Promise(resolve=>{const cb=result=>{app.ports.outgoing.unsubscribe(cb);resolve(result);};app.ports.outgoing.subscribe(cb);app.ports.incoming.send({scene});});}
(async()=>{let checks=0,packets=[];const check=v=>{assert(v);checks++;};
for(const packet of report.taskbarPackets){const result=await replay(packet.scene);check(result.passed);check(result.groups.length===1&&result.groups[0].families.length===2);check(result.decisions[0].primary.kind==='picker');
 const rows=packet.scene.windows,byId=new Map(rows.map(w=>[w.incarnation,w]));let focused=packet.scene.focused;while(focused&&byId.get(focused).owner)focused=byId.get(focused).owner;
 check(result.groups[0].families.filter(f=>f.active).map(f=>f.root).join(',')===(focused||''));
 check(result.groups[0].families.every(f=>f.minimized===byId.get(f.root).minimized));
 check(result.decisions[0].selections.every((d,i)=>d.kind==='effect'&&d.root===result.groups[0].families[i].root&&d.operation===(result.groups[0].families[i].minimized?'restore':'activate')));
 packets.push({name:packet.name,result});}
assert.equal(checks,60);fs.writeFileSync(process.argv[4],JSON.stringify({passed:true,checks,scope:'Actual native action packets admitted by compiled Elm family/decision worker; full scene and integrated UI separate',packets},null,2)+'\n');clearTimeout(deadline);
})();
