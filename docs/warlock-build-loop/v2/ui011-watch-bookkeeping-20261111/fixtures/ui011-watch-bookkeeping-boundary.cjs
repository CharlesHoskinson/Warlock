'use strict';
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const [image,output]=process.argv.slice(2);
if(process.argv.length!==4)throw Error('Expected fixed compiled boundary fixture and NEW report');
const hash=data=>crypto.createHash('sha256').update(data).digest('hex');
const names=["exact-singleton-completion-removes-only-one-row", "unchanged-completion-preserves-frame", "bookkeeping-proof-does-not-leave-output-boundary", "focus-payload-is-not-domain-receipt-authority", "mixed-catalog-batch-is-not-settled", "hidden-pin-batch-is-not-settled", "unknown-mixed-request-is-not-settled", "duplicate-request-batch-is-not-settled", "stored-request-base-must-match-completion", "late-preflight-unsent-disposition-is-inert", "duplicate-domain-reply-is-inert", "unknown-read-completion-grants-no-focus", "accepted-closure-removes-exact-pretransition-row", "accepted-replacement-removes-exact-pretransition-row", "unavailable-completion-grants-no-focus", "closed-scope-result-cannot-release-row", "incoming-json-cannot-create-bookkeeping-proof", "registering-an-effect-cannot-create-settlement"];
const setup=["real-public-watch-pending", "unrelated-read-batch-retained"];
const report={schema:1,passed:false,nativeAcceptance:false,originalAcceptance:false,assistiveTechnologyAcceptance:false,classification:'not-started',imageSha256:hash(fs.readFileSync(image)),fixtureSha256:hash(fs.readFileSync(__filename))};
let settled=false;
function finish(error){if(settled)return;settled=true;clearTimeout(timer);if(error){report.error=String(error.stack??error);report.passed=false;}fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});process.exitCode=report.passed?0:1;}
const timer=setTimeout(()=>finish(Error('Fixed public boundary result absent after5s')),5000);
try{
 const sandbox={console,setTimeout,clearTimeout};vm.createContext(sandbox);vm.runInContext(fs.readFileSync(image,'utf8'),sandbox,{timeout:2000});
 const app=sandbox.Elm.Ui011WatchBookkeepingBoundaryReplay.init();
 app.ports.outgoing.subscribe(value=>{
  report.observed=value;
  const exact=(record,keys)=>record&&typeof record==='object'&&!Array.isArray(record)&&JSON.stringify(Object.keys(record).sort())===JSON.stringify([...keys].sort())&&Object.values(record).every(x=>typeof x==='boolean');
  if(!exact(value.checks,names)||!exact(value.preconditions,setup)){report.classification='fixture-shape-failed';return finish(Error('Fixed inventories differ'));}
  if(!Object.values(value.preconditions).every(Boolean)){report.classification='fixture-precondition-failed';return finish(Error('Public setup failed'));}
  report.checks=names.map(name=>({name,passed:value.checks[name]}));report.failures=report.checks.filter(row=>!row.passed);
  report.caseCount=names.length;report.setupCount=setup.length;report.seedSampleCount=0;
  report.passed=report.failures.length===0;report.classification=report.passed?'component-pass':'semantic-red';finish();
 });
}catch(error){report.classification='execution-or-image-failed';finish(error);}
