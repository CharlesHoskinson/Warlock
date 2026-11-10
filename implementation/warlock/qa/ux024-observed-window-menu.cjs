'use strict';
// Public compiled Elm reducer only. No native endpoint, service or GUI evidence.
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const [image,output]=process.argv.slice(2);
if(process.argv.length!==4)throw Error('Expected Ux024ObservedWindowMenuReplay.js and NEW report.json');
const hash=data=>crypto.createHash('sha256').update(data).digest('hex');
const names=["attachment-is-application-only", "capability-emits-one-bound-read", "read-only-does-not-enable-native-actions", "actual-observed-group-is-inspectable", "actual-context-opens-inspection-menu", "inspection-shows-real-title", "inspection-shows-real-appid", "inspection-has-refresh-and-close", "inspection-no-enabled-native-effect", "keyboard-open-focuses-current-close", "pointer-open-does-not-focus", "escape-closes-and-reads-once", "fresh-exact-incarnation-restores-once", "same-application-replacement-cannot-restore", "removed-origin-cannot-restore", "unknown-cannot-restore", "pending-read-disables-inspection", "wrong-request-cannot-settle", "foreign-binding-cannot-publish", "foreign-owner-generation-cannot-publish", "detached-reply-cannot-revive", "transport-refusal-cannot-open", "reconciliation-full-cannot-open", "retired-presentation-view-cannot-restore", "absent-capability-remains-unavailable", "empty-capability-remains-unavailable", "malformed-capability-grants-nothing", "all-routes-preserve-no-effects", "inspection-declared-keyboard-order", "inspection-information-cannot-activate"];
const preconditions=["actual-presentation-view-one", "baseline-local-attachment-valid", "no-fabricated-catalog"];
const report={schema:1,passed:false,nativeAcceptance:false,providerAcceptance:false,classification:'not-started',imageSha256:hash(fs.readFileSync(image)),fixtureSha256:hash(fs.readFileSync(__filename))};
let settled=false;
function finish(error){if(settled)return;settled=true;clearTimeout(timer);if(error){report.error=String(error.stack??error);report.passed=false;}fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});process.exitCode=report.passed?0:1;}
const timer=setTimeout(()=>finish(Error('Fixed public result absent after5s')),5000);
try{
 const sandbox={console,setTimeout,clearTimeout};vm.createContext(sandbox);vm.runInContext(fs.readFileSync(image,'utf8'),sandbox,{timeout:2000});
 const app=sandbox.Elm.Ux024ObservedWindowMenuReplay.init();
 app.ports.outgoing.subscribe(value=>{
  report.observed=value;
  const exact=(record,keys)=>record&&typeof record==='object'&&!Array.isArray(record)&&JSON.stringify(Object.keys(record).sort())===JSON.stringify([...keys].sort())&&Object.values(record).every(x=>typeof x==='boolean');
  if(!exact(value.checks,names)||!exact(value.preconditions,preconditions)){report.classification='fixture-shape-failed';return finish(Error('Fixed inventories differ'));}
  if(!Object.values(value.preconditions).every(Boolean)){report.classification='fixture-precondition-failed';return finish(Error('Public setup failed'));}
  report.checks=names.map(name=>({name,passed:value.checks[name]}));report.failures=report.checks.filter(row=>!row.passed);
  const seeds=Array.from({length:32},(_,n)=>n),fuzz=value.seeded;
  if(!fuzz||JSON.stringify(fuzz.seeds)!==JSON.stringify(seeds)||!Array.isArray(fuzz.samples)||fuzz.samples.length!==32){report.classification='fixture-shape-failed';return finish(Error('Fixed32 sequences absent'));}
  report.seedFailures=fuzz.samples.filter((sample,index)=>sample.seed!==index||sample.variant!==index%8||sample.eligibleGroup!==(index%8===0)||sample.noMutation!==true||sample.noFocus!==true||sample.nativeAvailable!==false);
  report.caseCount=names.length;report.seedSampleCount=32;report.passed=report.failures.length===0&&report.seedFailures.length===0;report.classification=report.passed?'component-pass':'semantic-red';finish();
 });
}catch(error){report.classification='execution-or-image-failed';finish(error);}
