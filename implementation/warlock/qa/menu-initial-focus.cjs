'use strict';
// Actual compiled public Elm reducer component; no native/DOM/service evidence.
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const [image,output]=process.argv.slice(2);
if(process.argv.length!==4)throw Error('Expected compiled MenuInitialFocusReplay.js and NEW report.json');
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const names=["keyboard-open-one-exact-dom-focus","focus-in-same-current-projection-commit","focus-target-is-current-unique-close","keyboard-origin-established-before-open","pointer-open-no-dom-focus","old-open-callback-no-repeat","refresh-request-no-initial-focus","refreshed-menu-no-initial-focus","stale-publication-no-focus","stale-lease-no-focus","foreign-owner-no-focus","retired-owner-no-focus","disconnected-origin-no-focus","dismiss-does-not-immediately-restore","eligible-return-stays-exact-group","removed-return-target-refused","unavailable-return-target-refused"];
const preconditions=["current-taskbar-group-eligible","keyboard-menu-opened","pointer-menu-opened","exact-enabled-current-menu-close","menu-publication-and-lease-current"];
const report={schema:1,passed:false,nativeAcceptance:false,originalAccepted:false,classification:'not-started',imageSha256:hash(fs.readFileSync(image)),fixtureSha256:hash(fs.readFileSync(__filename))};
let settled=false;
function finish(error){if(settled)return;settled=true;clearTimeout(timer);if(error){report.error=String(error.stack??error);report.passed=false;}fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});process.exitCode=report.passed?0:1;}
const timer=setTimeout(()=>finish(Error('Fixed reducer result absent after5s')),5000);
try{
 const sandbox={console,setTimeout,clearTimeout};vm.createContext(sandbox);vm.runInContext(fs.readFileSync(image,'utf8'),sandbox,{timeout:2000});
 const app=sandbox.Elm.MenuInitialFocusReplay.init();
 app.ports.outgoing.subscribe(value=>{
  report.observed=value;
  const exact=(record,expected)=>record&&typeof record==='object'&&!Array.isArray(record)&&JSON.stringify(Object.keys(record).sort())===JSON.stringify([...expected].sort())&&Object.values(record).every(x=>typeof x==='boolean');
  if(!exact(value.preconditions,preconditions)||!exact(value.checks,names)){report.classification='fixture-shape-failed';return finish(Error('Exact fixed replay inventory differs'));}
  if(!Object.values(value.preconditions).every(Boolean)){report.classification='fixture-precondition-failed';return finish(Error('Public reducer setup did not establish the required case'));}
  report.caseCount=names.length;report.checks=names.map(name=>({name,passed:value.checks[name]}));report.failures=report.checks.filter(row=>!row.passed);
  const seeds=Array.from({length:32},(_,index)=>index), fuzz=value.seeded;
  if(!fuzz||fuzz.algorithm!=='literal-seed-modulo8-public-event-sequence'||JSON.stringify(fuzz.seeds)!==JSON.stringify(seeds)||!Array.isArray(fuzz.samples)||fuzz.samples.length!==32){report.classification='fixture-shape-failed';return finish(Error('Fixed32 public sequences missing'));}
  report.seeded=fuzz;report.seedFailures=[];
  fuzz.samples.forEach((sample,index)=>{
   const wants=index%8===0?['menu:1:close']:[],mode=index%8<=1?'menu':'closed';
   const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
   const valid=sample.seed===index&&sample.case===index%8&&sample.passed===true&&sample.mode===mode&&same(sample.focus,wants)&&same(sample.commitFocus,wants)&&same(sample.repeatFocus,[])
    &&(wants.length===0||(sample.commit&&same(sample.commit.focus,wants)&&same(sample.commit.projection,sample.projection)));
   if(!valid)report.seedFailures.push({seed:index,expectedFocus:wants,sample});
  });
  report.seedSampleCount=32;
  if(report.seedFailures.length)report.failures.push({name:'seeded-current-menu-focus-invariants',passed:false,failures:report.seedFailures.length});

  report.passed=report.failures.length===0;report.classification=report.passed?'component-pass':'semantic-red';finish();
 });
}catch(error){report.classification='execution-or-compile-image-failed';finish(error);}
