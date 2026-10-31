// Exercise the production scenario loader with deterministic host observations.
import {readFile, mkdtemp, writeFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const root=resolve(process.argv[2] || '.');
const dir=await mkdtemp(join(tmpdir(),'warlock-scenario-'));
try {
 const source=await readFile(join(root,'test-drive/scenarios/index.js'),'utf8');
 const modulePath=join(dir,'scenario.mjs');await writeFile(modulePath,source);
 await writeFile(join(dir,'package.json'),'{"type":"module"}');
 await writeFile(join(dir,'observation.js'),await readFile(join(root,'test-drive/scenarios/observation.js'),'utf8'));
 globalThis.fetch=async url=>({ok:true,json:async()=>JSON.parse(await readFile(join(root,'test-drive/scenarios',new URL(url).pathname.split('/').pop()),'utf8'))});
 const realSetTimeout=globalThis.setTimeout;globalThis.setTimeout=(fn,ms)=>realSetTimeout(fn,Math.min(ms,25));
 const {loadScenario}=await import(pathToFileURL(modulePath));
 const seed=JSON.parse(await readFile(join(root,'test-drive/scenarios/settings.json'),'utf8')).initialExternalFacts;
 function host(kind) {
  let snapshot={...seed,epoch:1,binding:{},presentation:{actionable:true,publication:1}},listeners=[];
  return {getSnapshot:()=>snapshot,subscribe:f=>(listeners.push(f),()=>{listeners=listeners.filter(x=>x!==f)}),invoke:async()=>{
   if(kind==='unsupported')return false;
   if(kind==='admitted')snapshot={...snapshot,popupPlacement:{open:true},presentation:{actionable:true,publication:2,mode:'settings',applied:{popup:2},controls:{popup:['settings:theme:night']}}};
   if(kind==='wrong')snapshot={...snapshot,popupPlacement:{open:true},presentation:{actionable:true,publication:2,mode:'system',applied:{popup:2},controls:{popup:['settings:theme:night']}}};
   if(kind==='stale')realSetTimeout(()=>{snapshot={...snapshot,epoch:2,popupPlacement:{open:true},presentation:{actionable:true,publication:2,mode:'settings',applied:{popup:2},controls:{popup:['settings:theme:night']}}};listeners.forEach(f=>f(snapshot))},1);
   return true;
  }};
 }
 let failures=0;
 for(const [kind,expected] of [['unsupported',false],['missing',false],['wrong',false],['stale',false],['admitted',true]]) {
  const result=await loadScenario('settings',host(kind));
  if(result.ok!==expected){console.error(`FAIL ${kind}: expected ok=${expected}, got ok=${result.ok}`);failures++;}
  else console.log(`PASS ${kind}`);
 }
 if(failures)process.exitCode=1;
} finally {await rm(dir,{recursive:true,force:true})}
