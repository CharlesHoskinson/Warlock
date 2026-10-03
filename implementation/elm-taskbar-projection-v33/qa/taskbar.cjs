const fs=require('fs'),assert=require('assert');const app=require(process.argv[2]).Elm.TaskbarReplay.init({flags:null});
const timer=setTimeout(()=>{throw new Error('Taskbar replay deadline');},15000);
const window=(id,extra={})=>({incarnation:String(id),label:'Window '+id,minimized:false,owner:null,application:'owned.app',available:true,...extra});
const scene=(windows,focused=null)=>({revision:'4',focused,windows});
function replay(value){return new Promise(resolve=>{const cb=out=>{app.ports.outgoing.unsubscribe(cb);resolve(out);};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(value);});}
(async()=>{
 const cases=[];
 async function check(name,value,verify){const out=await replay(value);verify(out);cases.push({name,passed:true});}
 const primary=out=>out.decisions[0].primary;
 await check('zero-pinned-launch',{scene:scene([]),pinned:true},o=>{assert(o.passed);assert.equal(o.zero.kind,'launch');});
 await check('zero-unpinned-unavailable',{scene:scene([])},o=>assert.equal(o.zero.kind,'unavailable'));
 await check('single-inactive-activate',{scene:scene([window(1)])},o=>assert.deepEqual(primary(o),{kind:'effect',operation:'activate',root:'1'}));
 await check('single-active-minimize',{scene:scene([window(1)],'1')},o=>assert.equal(primary(o).operation,'minimize'));
 await check('single-minimized-restore',{scene:scene([window(1,{minimized:true})])},o=>assert.equal(primary(o).operation,'restore'));
 await check('multiple-always-picker',{scene:scene([window(1),window(2)],'1')},o=>{assert.equal(primary(o).kind,'picker');assert(o.decisions[0].selections.every(s=>s.operation==='activate'));});
 await check('transient-does-not-add-family',{scene:scene([window(1),window(2,{owner:'1',application:'dialog.app'})],'2')},o=>{assert.equal(o.groups[0].families.length,1);assert.equal(primary(o).operation,'minimize');assert.equal(o.groups[0].families[0].root,'1');});
 await check('different-application-roots-separate',{scene:scene([window(1),window(2,{application:'other.app'})])},o=>assert.equal(o.groups.length,2));
 await check('empty-hints-separate-anonymous-roots',{scene:scene([window(1,{application:''}),window(2,{application:''})])},o=>assert.equal(o.groups.length,2));
 await check('unavailable-child-disables-family',{scene:scene([window(1),window(2,{owner:'1',available:false})])},o=>assert.equal(primary(o).kind,'unavailable'));
 await check('picker-restores-only-minimized-family',{scene:scene([window(1,{minimized:true}),window(2)],'2')},o=>{assert.equal(primary(o).kind,'picker');assert.equal(o.decisions[0].selections[0].operation,'restore');assert.equal(o.decisions[0].selections[1].operation,'activate');});
 for(const [name,windows,focus] of [
  ['missing-parent',[window(1,{owner:'7'})],null],['self-parent',[window(1,{owner:'1'})],null],['cycle',[window(1,{owner:'2'}),window(2,{owner:'1'})],null],
  ['duplicate',[window(1),window(1)],null],['unknown-focus',[window(1)],'7'],['minimized-focus',[window(1,{minimized:true})],'1'],['mixed-family-minimize',[window(1,{minimized:true}),window(2,{owner:'1'})],null],
  ['application-control-character',[window(1,{application:'bad\napp'})],null],['oversized-application',[window(1,{application:'x'.repeat(257)})],null],['oversized-window-list',Array.from({length:257},(_,i)=>window(i+1)),null]
 ])await check(name,{scene:scene(windows,focus)},o=>assert.equal(o.passed,false));
 for(let seed=1;seed<=64;seed++){
  const roots=Array.from({length:1+seed%7},(_,i)=>window(i*10+1,{application:'app.'+(i%3)}));
  const children=roots.map(w=>window(Number(w.incarnation)+1,{owner:w.incarnation,application:'dialog'}));
  const rows=[...roots,...children];const a=await replay({scene:scene(rows)}),b=await replay({scene:scene([...rows].reverse())});assert(a.passed&&b.passed);assert.deepEqual(a.groups,b.groups);assert.deepEqual(a.decisions,b.decisions);cases.push({name:'stack-permutation-'+seed,passed:true});
 }
 await check('lossless-family-identities',{scene:scene([window('9007199254740993'),window('18446744073709551615',{owner:'9007199254740993'})],'18446744073709551615')},o=>assert.equal(o.groups[0].families[0].root,'9007199254740993'));
 await check('capacity-boundary-256',{scene:scene(Array.from({length:256},(_,i)=>window(i+1)))},o=>{assert(o.passed);assert.equal(o.groups[0].families.length,256);});
 fs.writeFileSync(process.argv[3],JSON.stringify({passed:true,checks:cases.length,cases,scope:'Compiled family/application action decisions; launch is a planned catalog effect, not native launch acceptance'},null,2)+'\n');clearTimeout(timer);
})().catch(e=>{clearTimeout(timer);console.error(e);process.exitCode=1;});
