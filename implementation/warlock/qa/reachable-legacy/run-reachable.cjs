'use strict';
// Root-only fixed pure replay. CLI: node run-reachable.cjs ROOT BUNDLE PINS.json
// PINS is a reviewed JSON mapping absolute input paths to lowercase SHA256.
const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
function main(){
if(process.argv.length!==6)throw new Error('Expected fixed ROOT BUNDLE CLOSURE SHA256');
const root=fs.realpathSync(process.argv[2]), bundle=fs.realpathSync(process.argv[3]);
const pinPath=fs.realpathSync(process.argv[4]), approved=process.argv[5];
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
if(!/^[a-f0-9]{64}$/.test(approved||'') || hash(fs.readFileSync(pinPath))!==approved) throw new Error('reviewed closure hash mismatch');
const closure=JSON.parse(fs.readFileSync(pinPath,'utf8'));
if(Object.keys(closure).sort().join(',')!==['bundle','compileReceipt','elm','elmHome','files','launcher','node','profile','root','schema','toolchainManifest'].sort().join(',') || closure.schema!==1 || closure.profile!=='reachable-legacy-v2' || closure.root!==root || closure.bundle!==bundle ||
   !closure.files || typeof closure.files!=='object' || Array.isArray(closure.files)) throw new Error('invalid closure');
function regular(p){const l=fs.lstatSync(p);if(!l.isFile()||l.isSymbolicLink()||fs.realpathSync(p)!==p)throw new Error('noncanonical closure file '+p);}
function walk(directory){
  return fs.readdirSync(directory,{withFileTypes:true}).flatMap(e=>{
    const p=path.join(directory,e.name);if(e.isSymbolicLink())throw new Error('symlink in closure '+p);
    return e.isDirectory()?walk(p):e.isFile()?[p]:[];
  });
}
const src=path.join(root,'implementation/warlock/src');
const qa=path.join(root,'implementation/warlock/qa');
const baseline=path.join(qa,'http-full-subscriptions-v2');
const local=[__filename,path.join(__dirname,'reachable-observer.cjs'),path.join(__dirname,'reachable-literals.cjs')];
const sourceFiles=walk(src).filter(x=>x.endsWith('.elm'));
const baselineFiles=walk(baseline).filter(x=>x.endsWith('.cjs')||x.endsWith('.json'));
const must=[...local,...sourceFiles,...baselineFiles,path.join(root,'implementation/warlock/elm.json'),
  path.join(qa,'tea-subscriptions-cases.cjs'),path.join(qa,'tea-contract-cases.cjs'),
  path.join(root,'tools/qa_cpu.py'),path.join(root,'tools/check_arm64_cpu.py'),
  path.join(root,'tools/arm64_toolchain.py'),path.join(root,'tools/arm64-toolchain.json'),
  path.join(root,'tools/haskell-toolchain.json'),path.join(root,'tools/ui-host-toolchain.json'),
  path.join(root,'tools/elm-http-dependencies.json'),path.join(root,'tools/haskell-dependencies.json'),
  path.join(root,'window-integration-qa/qa_launch.py'),
  bundle,closure.node,closure.elm,closure.compileReceipt,closure.launcher,closure.toolchainManifest,
  ...walk(closure.elmHome)];
if(!closure.node||!closure.elm||!closure.compileReceipt||!closure.launcher||!closure.toolchainManifest||!closure.elmHome || fs.realpathSync(process.execPath)!==closure.node)throw new Error('toolchain identity mismatch');
const paths=Object.keys(closure.files);
if(new Set(paths).size!==paths.length || must.some(p=>!Object.hasOwn(closure.files,p)))throw new Error('incomplete closed dependency roster');
for(const [p,want] of Object.entries(closure.files)){
  if(!path.isAbsolute(p)||! /^[a-f0-9]{64}$/.test(want))throw new Error('invalid closure pin');
  regular(p);if(hash(fs.readFileSync(p))!==want)throw new Error('closure digest mismatch '+p);
}
const provenance=JSON.parse(fs.readFileSync(closure.compileReceipt,'utf8'));
if(provenance.schema!==1 || provenance.profile!=='reachable-legacy-v2' || provenance.bundle!==bundle ||
   provenance.bundleSha256!==closure.files[bundle] || provenance.elm!==closure.elm ||
   provenance.elmSha256!==closure.files[closure.elm] || provenance.node!==closure.node ||
   provenance.nodeSha256!==closure.files[closure.node] || provenance.toolchainManifestSha256!==closure.files[closure.toolchainManifest] || !provenance.sourceHashes ||
   sourceFiles.some(p=>provenance.sourceHashes[p]!==closure.files[p]) ||
   provenance.sourceHashes[path.join(root,'implementation/warlock/elm.json')]!==closure.files[path.join(root,'implementation/warlock/elm.json')])
  throw new Error('compiled bundle provenance mismatch');
const toolchain=JSON.parse(fs.readFileSync(closure.toolchainManifest,'utf8'));
if(toolchain.elmHome!==closure.elmHome || provenance.elmHome!==closure.elmHome || !provenance.stagedElmHome || !provenance.cacheModes)throw new Error('compile cache provenance mismatch');
function checkClosure(){
 if(hash(fs.readFileSync(pinPath))!==approved)throw new Error('closure identity changed');
 for(const [p,want]of Object.entries(closure.files)){regular(p);if(hash(fs.readFileSync(p))!==want)throw new Error('closure changed '+p);}
 for(const directory of [closure.elmHome,provenance.stagedElmHome]){
  if(fs.realpathSync(directory)!==directory)throw new Error('noncanonical cache');
  const actual=walk(directory).sort(),expected=Object.keys(closure.files).filter(p=>p.startsWith(directory+'/')).sort();
  if(JSON.stringify(actual)!==JSON.stringify(expected))throw new Error('cache inventory changed');
  for(const p of actual)if((fs.statSync(p).mode&4095)!==provenance.cacheModes[p])throw new Error('cache mode changed');
 }
}
checkClosure();
// No fixture/baseline module is loaded until the complete approved closure is checked.
const {run}=require('./reachable-observer.cjs');
const literal=require('./reachable-literals.cjs');
const source=fs.readFileSync(bundle,'utf8');
const base=require(path.join(root,'implementation/warlock/qa/http-full-subscriptions-v2/full-literals.cjs')).build(root);
function routeRemoved(kind){
 const needle='native-preview-'+kind, n=source.split(needle).length-1;
 if(n<1)throw new Error('route mutation marker missing '+kind);
 return source.split(needle).join('disabled-preview-'+kind);
}
function overlayGated(kind){
 const marker='\n_Platform_export(';const i=source.indexOf(marker);
 if(i<0||source.indexOf(marker,i+1)>=0)throw new Error('export mutation marker');
 const tag=kind==='retry'?'NativeRetry':'NativeRetirement';
 const insertion=`\nvar __legacyGateOriginal=$author$project$Popup$transition;\n$author$project$Popup$transition=F2(function(msg,m){if(msg.$===${JSON.stringify(tag)} && m.presentation.a.snapshot.$==='Just' && m.presentation.a.snapshot.a.a.mode==='closed')return _Utils_Tuple2(m,_List_Nil);return A2(__legacyGateOriginal,msg,m);});\n`;
 return source.slice(0,i)+insertion+source.slice(i);
}
// Change only the final compiled update Cmd, before main captures update.
function commandOnly(kind){
 if(!['drop','duplicate'].includes(kind))throw new Error('unknown fixed command mutation');
 const marker='var $author$project$HttpPopup$main =',i=source.indexOf(marker);
 const update=source.indexOf('var $author$project$HttpPopup$update = F2(');
 if(i<0||source.indexOf(marker,i+1)>=0||update<0||update>=i||source.includes('__reachableCommandOriginal'))throw new Error('compiled command mutation layout differs');
 const body=kind==='drop'?'_Platform_batch(_List_Nil)':'_Platform_batch(_List_fromArray([pair.b,pair.b]))';
 const insertion=`var __reachableCommandOriginal=$author$project$HttpPopup$update;\n$author$project$HttpPopup$update=F2(function(msg,m){var pair=A2(__reachableCommandOriginal,msg,m);return _Utils_Tuple2(pair.a,${body});});\n`;
 return source.slice(0,i)+insertion+source.slice(i);
}
function mustRejectCommand(kind,spec){
 const label='returned-command-'+kind,step=1,mutant=commandOnly(kind),eq=require('node:util').isDeepStrictEqual;
 try{run(mutant,spec);throw new Error('command counterfactual unexpectedly passed '+label);}
 catch(e){
  const c=e.counterexample;
  if(!c||c.name!==spec.name||c.step!==step||e.message!==`${spec.name} step ${step}: COMPLETE owning model/subscription/typed descriptions differ`)throw new Error('command counterfactual wrong failure '+label+': '+e.message);
  const actual={...c.actual},expected={...c.expected},actualCounts=actual.commandLeaves,expectedCounts=expected.commandLeaves;
  delete actual.commandLeaves;delete expected.commandLeaves;
  const counts=n=>Object.assign(Object.create(null),{Http:n,Task:0});
  const comparisons={otherFieldsEqual:eq(actual,expected),expectedCountsEqual:eq(expectedCounts,counts(1)),actualCountsEqual:eq(actualCounts,counts(kind==='drop'?0:2))};
  if(!comparisons.otherFieldsEqual||!comparisons.expectedCountsEqual||!comparisons.actualCountsEqual){
    const error=new Error('command mutation changed model/descriptions/returns or missed exact leaf discrepancy');
    error.counterexample=c;
    error.diagnostic={kind:'command-only-comparison',label,caseName:spec.name,step,comparisons,actualCounts,expectedCounts,
      actualCountsPrototypeIsNull:actualCounts!=null&&Object.getPrototypeOf(actualCounts)===null,
      expectedCountsPrototypeIsNull:expectedCounts!=null&&Object.getPrototypeOf(expectedCounts)===null};
    throw error;
  }
  return {label,caseName:spec.name,step,reason:e.message,mutantSHA256:hash(mutant),counterexample:c};
 }
}
function mustReject(mutant,spec,step,label){
 try{run(mutant,spec);throw new Error('counterfactual unexpectedly passed '+label);}
 catch(e){
  const c=e.counterexample, eq=require('node:util').isDeepStrictEqual;
  if(!c||c.name!==spec.name||c.step!==step || e.message!==`${spec.name} step ${step}: COMPLETE owning model/subscription/typed descriptions differ` || eq(c.actual,c.expected))
    throw new Error('counterfactual wrong failure '+label+': '+e.message);
  const a=c.actual.state, x=c.expected.state;
  const target=label.startsWith('retry')
    ? x.http.a.active.$==='Just' && x.http.a.active.a.id.a.a==='2' && !eq(a.http.a.active,x.http.a.active)
    : x.popup.previews.a.d.closing===true && a.popup.previews.a.d.closing===false;
  if(!target)throw new Error('counterfactual missed declared observable '+label);
  return {label,caseName:spec.name,step,reason:e.message,counterexample:c};
 }
}
const receipt=[];
for(const seed of [20261105,20261106]){
 const packet=literal.build(root,base,seed);
 if(packet.cases.length!==10 || packet.cases.reduce((n,x)=>n+x.steps.length,0)!==38)throw new Error('fixed budget mismatch');
 for(const c of packet.cases){
   if(c.root!=='HttpPopup' || c.steps[0].input.kind!=='init' || c.steps.slice(1).some(s=>s.input.kind==='given')) throw new Error('fixture must start at real Popup init without given injection');
 }
 for(const c of packet.cases)run(source,c);
 const retirement=packet.cases.find(c=>c.name==='closed-empty-retry-retirement-duplicate');
 const retry=packet.cases.find(c=>c.name==='closed-reconcile-after-correlated-http204-reoffers');
 if(!retirement || !retry || retirement.steps.length!==8 || retry.steps.length!==6) throw new Error('required observable control histories differ');
 const negatives=[
   mustReject(routeRemoved('retry'),retry,5,'retry-route-removed'),
   mustReject(routeRemoved('retirement'),retirement,3,'retirement-route-removed'),
   mustReject(overlayGated('retry'),retry,5,'retry-closed-gate'),
   mustReject(overlayGated('retirement'),retirement,3,'retirement-closed-gate')];
 const observerGuardNegatives=[mustRejectCommand('drop',retirement),mustRejectCommand('duplicate',retirement)];
 receipt.push({seed,cases:10,steps:38,wholeObservations:38,counterfactuals:4,negatives,observerGuards:2,observerGuardNegatives});
}
checkClosure();
console.log(JSON.stringify({status:'passed',profile:'reachable-legacy-pure-draft',receipt,
 hashes:{bundle:hash(source),observer:hash(fs.readFileSync(path.join(__dirname,'reachable-observer.cjs'))),
 literals:hash(fs.readFileSync(path.join(__dirname,'reachable-literals.cjs'))),closure:hash(fs.readFileSync(pinPath)),compileReceipt:hash(fs.readFileSync(closure.compileReceipt))},
 nativeAcceptance:false,originalAcceptance:false}));

}
try { main(); } catch (error) {
 console.error(JSON.stringify({status:'failed',profile:'reachable-legacy-pure-draft',error:error.stack,
   counterexample:error.counterexample||null,diagnostic:error.diagnostic||null,nativeAcceptance:false,originalAcceptance:false}));
 process.exitCode=1;
}
