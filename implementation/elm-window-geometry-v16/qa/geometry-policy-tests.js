/* Independent scenario oracles for compiled Elm; no JS policy implementation. */
const assert = require('node:assert/strict');
const app = require(process.argv[2]).Elm.GeometryPolicyWorker.init({flags: null});
const fullCaps = {restoreMinimized:true,restoreGeometry:true,move:true,size:true,minimize:true,maximize:true,close:true,exitFullscreen:true};
const base = {mode:'ordinary',minimized:false,fixedSize:false,geometryEligible:true,resolution:'ready',capabilities:fullCaps};
const labels = ['Restore','Move','Size','Minimize','Maximize','Close'];
const actions = ['restore-geometry','move','size','minimize','maximize','close'];
const rows = (enabled, restored = false) => labels.map((label,index)=>({label,action:index===0&&restored?'restore-minimized':actions[index],enabled:enabled[index]}));
const exit = enabled => ({label:'Exit fullscreen',action:'exit-fullscreen',enabled});
const ordinary = rows([false,true,true,true,true,true],true);
const max = rows([true,false,false,true,false,true]);
const full = rows([false,false,false,true,false,true],true);
const mini = rows([true,false,false,false,false,true],true);
const cases = [
 ['Ordinary standard ordering',{},ordinary,exit(false),['move','size','minimize','maximize','close']],
 ['Maximized restore geometry distinct',{mode:'maximized'},max,exit(false),['restore-geometry','minimize','close']],
 ['Fullscreen explicit exit only',{mode:'fullscreen'},full,exit(true),['minimize','close','exit-fullscreen']],
 ['Minimized ordinary restore minimize',{minimized:true},mini,exit(false),['restore-minimized','close']],
 ['Minimized saved maximized restore minimize',{mode:'maximized',minimized:true},mini,exit(false),['restore-minimized','close']],
 ['Minimized saved fullscreen restore minimize',{mode:'fullscreen',minimized:true},mini,exit(false),['restore-minimized','close']],
 ['Fixed size ordinary visible disabled size and maximize',{fixedSize:true},rows([false,true,false,true,false,true],true),exit(false),['move','minimize','close']],
 ['Fixed size maximized can restore geometry',{mode:'maximized',fixedSize:true},max,exit(false),['restore-geometry','minimize','close']],
 ['Nonroot ordinary geometry visible disabled',{geometryEligible:false},rows([false,false,false,true,false,true],true),exit(false),['minimize','close']],
 ['Nonroot maximized restore geometry disabled',{mode:'maximized',geometryEligible:false},rows([false,false,false,true,false,true]),exit(false),['minimize','close']],
 ['Nonroot minimized restore minimize retained',{mode:'fullscreen',minimized:true,geometryEligible:false},mini,exit(false),['restore-minimized','close']],
 ['Nonroot fullscreen exit visible disabled',{mode:'fullscreen',geometryEligible:false},full,exit(false),['minimize','close']],
];
for (const state of ['pending','unknown']) {
 for (const nativeMode of ['ordinary','maximized','fullscreen']) {
  cases.push([`${state} blocks all mutations in ${nativeMode}`,{mode:nativeMode,resolution:state},rows([false,false,false,false,false,false],nativeMode!=='maximized'),exit(false),[]]);
 }
 cases.push([`${state} blocks minimized restoration`,{mode:'fullscreen',minimized:true,resolution:state},rows([false,false,false,false,false,false],true),exit(false),[]]);
}
for (const [cap,index] of [['move',1],['size',2],['minimize',3],['maximize',4],['close',5]]) {
 cases.push([`Unsupported ${cap} is absent`,{capabilities:{...fullCaps,[cap]:false}},ordinary.filter((_,i)=>i!==index),exit(false),['move','size','minimize','maximize','close'].filter(x=>x!==actions[index])]);
}
cases.push(['Unsupported minimized restore keeps supported Restore label disabled',{minimized:true,capabilities:{...fullCaps,restoreMinimized:false}},rows([false,false,false,false,false,true],true),exit(false),['close']]);
cases.push(['Unsupported fullscreen exit absent',{mode:'fullscreen',capabilities:{...fullCaps,exitFullscreen:false}},full,null,['minimize','close']]);
cases.push(['No implemented capabilities emits no rows',{capabilities:Object.fromEntries(Object.keys(fullCaps).map(k=>[k,false]))},[],null,[]]);
cases.push(['Nonroot supported restore geometry retained disabled',{mode:'maximized',geometryEligible:false,capabilities:{...fullCaps,move:false,size:false,maximize:false}},[rows([false,false,false,true,false,true])[0],rows([false,false,false,true,false,true])[3],rows([false,false,false,true,false,true])[5]],exit(false),['minimize','close']]);


const minOnly = {restoreMinimized:true,restoreGeometry:false,move:false,size:false,minimize:true,maximize:false,close:true,exitFullscreen:false};
const geoOnly = {...minOnly,restoreMinimized:false,restoreGeometry:true};
for (const nativeMode of ['ordinary','maximized','fullscreen']) {
 cases.push([`Legacy MinRestore-only ${nativeMode} retains disabled Restore`,{mode:nativeMode,capabilities:minOnly},[{label:'Restore',action:'restore-minimized',enabled:false},{label:'Minimize',action:'minimize',enabled:true},{label:'Close',action:'close',enabled:true}],null,['minimize','close']]);
}
cases.push(['Legacy MinRestore-only minimized saved fullscreen restores minimize',{mode:'fullscreen',minimized:true,capabilities:minOnly},[{label:'Restore',action:'restore-minimized',enabled:true},{label:'Minimize',action:'minimize',enabled:false},{label:'Close',action:'close',enabled:true}],null,['restore-minimized','close']]);
for (const nativeMode of ['ordinary','fullscreen']) {
 cases.push([`Geometry-only ${nativeMode} Restore disabled`,{mode:nativeMode,capabilities:geoOnly},[{label:'Restore',action:'restore-geometry',enabled:false},{label:'Minimize',action:'minimize',enabled:true},{label:'Close',action:'close',enabled:true}],null,['minimize','close']]);
}
cases.push(['Geometry-only maximized Restore enabled',{mode:'maximized',capabilities:geoOnly},[{label:'Restore',action:'restore-geometry',enabled:true},{label:'Minimize',action:'minimize',enabled:true},{label:'Close',action:'close',enabled:true}],null,['restore-geometry','minimize','close']]);
cases.push(['Geometry-only minimized Restore visible but unsupported selected op disabled',{mode:'maximized',minimized:true,capabilities:geoOnly},[{label:'Restore',action:'restore-minimized',enabled:false},{label:'Minimize',action:'minimize',enabled:false},{label:'Close',action:'close',enabled:true}],null,['close']]);
cases.push(['Neither Restore capability makes Restore absent',{capabilities:{...fullCaps,restoreGeometry:false,restoreMinimized:false}},ordinary.slice(1),exit(false),['move','size','minimize','maximize','close']]);

function query(value) {
 return new Promise(resolve=>{
  const onValue=out=>{app.ports.response.unsubscribe(onValue);resolve(out);};
  app.ports.response.subscribe(onValue); app.ports.request.send(value);
 });
}
(async()=>{
 const checks=[];
 for(const [name,patch,expectedRows,expectedExit,authorized] of cases) {
  const result=await query({...base,...patch});
  assert.deepEqual(result.rows,expectedRows,name+' rows');
  assert.deepEqual(result.exitFullscreen,expectedExit,name+' fullscreen');
  assert.deepEqual(result.authorized,authorized,name+' authorization');
  checks.push({name,passed:true});
 }
 for(const [name,value] of [
  ['Invalid native mode rejected',{...base,mode:'label says maximized'}],
  ['Invalid resolution rejected',{...base,resolution:'retry'}],
  ['Missing native capabilities rejected',{...base,capabilities:{}}],
  ['Boolean mode rejected',{...base,mode:true}],
 ]) {
  assert.deepEqual(await query(value),{error:true},name);checks.push({name,passed:true});
 }
 process.stdout.write(JSON.stringify({passed:true,checks,checkCount:checks.length,nativeAcceptance:false})+'\n');
})().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1;});
