'use strict';
// Public compiled Elm reducer only. No native endpoint, service or GUI evidence.
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const [image,output]=process.argv.slice(2);
if(process.argv.length!==4)throw Error('Expected Ui011WindowWatchBatchReplay.js and NEW report.json');
const hash=data=>crypto.createHash('sha256').update(data).digest('hex');
const names=["explicit-watch-capability-is-admitted", "legacy-read-only-menu-does-not-watch", "keyboard-scope-arms-one-backpressure-timer", "timer-sends-one-bound-watch-with-base", "duplicate-timer-cannot-issue-second-watch", "pending-watch-preserves-open-menu-frame", "unchanged-preserves-frame-stamp-and-focus", "unchanged-only-rearms-no-publication", "successor-watch-request-is-distinct", "closed-origin-automatically-restores-fallback", "replacement-never-receives-old-focus", "same-origin-title-change-preserves-menu", "other-window-change-preserves-menu", "counter-only-changed-cannot-retire", "changed-reply-settles-once", "unknown-stops-watch-no-fallback", "unavailable-stops-watch-no-fallback", "wrong-request-cannot-restore", "wrong-base-cannot-restore", "foreign-binding-cannot-restore", "foreign-owner-cannot-restore", "closed-scope-ignores-late-watch", "closed-scope-ignores-old-timer", "superseded-presentation-ignores-watch", "detached-scope-ignores-watch", "pointer-scope-does-not-arm", "watch-never-issues-native-mutation"];
const preconditions=["existing-read-route-admitted", "existing-menu-route-opens", "actual-view-one"];
const quotaNames=["forty-correlated-watch-requests-issued", "forty-correlated-watch-replies-rearm", "unchanged-quota-sixteen-never-exceeded", "menu-and-group-remain-current-after-forty", "unchanged-replies-do-not-publish-or-focus", "read-only-watch-never-mutates", "request-ids-never-replayed", "closed-opener-after-forty-restores-current-fallback", "replacement-after-forty-never-inherits-old-focus", "closure-reply-cannot-replay-focus", "foreign-binding-does-not-retire-current-batch", "foreign-request-does-not-retire-current-batch", "stale-base-does-not-retire-current-batch", "foreign-owner-does-not-retire-current-batch", "duplicate-prior-result-does-not-retire-next-batch", "malformed-result-does-not-retire-current-batch", "invalid-unchanged-payload-does-not-retire-current-batch"];
const quotaPreconditions=["public-watch-route-ready", "initial-read-batch-is-retained", "public-menu-opens"];
const report={schema:1,passed:false,nativeAcceptance:false,originalAcceptance:false,assistiveTechnologyAcceptance:false,providerAcceptance:false,classification:'not-started',imageSha256:hash(fs.readFileSync(image)),fixtureSha256:hash(fs.readFileSync(__filename))};
let settled=false;
function finish(error){if(settled)return;settled=true;clearTimeout(timer);if(error){report.error=String(error.stack??error);report.passed=false;}fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});process.exitCode=report.passed?0:1;}
const timer=setTimeout(()=>finish(Error('Fixed public result absent after5s')),5000);
try{
 const sandbox={console,setTimeout,clearTimeout};vm.createContext(sandbox);vm.runInContext(fs.readFileSync(image,'utf8'),sandbox,{timeout:2000});
 const app=sandbox.Elm.Ui011WindowWatchBatchReplay.init();
 app.ports.outgoing.subscribe(value=>{
  report.observed=value;
  const legacy=value.legacy,quota=value.quota;
  const exact=(record,keys)=>record&&typeof record==='object'&&!Array.isArray(record)&&JSON.stringify(Object.keys(record).sort())===JSON.stringify([...keys].sort())&&Object.values(record).every(x=>typeof x==='boolean');
  if(!exact(legacy.checks,names)||!exact(legacy.preconditions,preconditions)){report.classification='fixture-shape-failed';return finish(Error('Fixed inventories differ'));}
  if(!Object.values(legacy.preconditions).every(Boolean)){report.classification='fixture-precondition-failed';return finish(Error('Public setup failed'));}
  report.checks=names.map(name=>({name,passed:legacy.checks[name]}));report.failures=report.checks.filter(row=>!row.passed);
  const seeds=Array.from({length:32},(_,n)=>n),fuzz=legacy.seeded;
  if(!fuzz||JSON.stringify(fuzz.seeds)!==JSON.stringify(seeds)||!Array.isArray(fuzz.samples)||fuzz.samples.length!==32){report.classification='fixture-shape-failed';return finish(Error('Fixed32 sequences absent'));}
  report.seedFailures=fuzz.samples.filter((sample,index)=>sample.seed!==index||sample.variant!==index%8||sample.contractReady!==true||sample.expectedEligible!==true||sample.preservedScope!==true||sample.once!==true||sample.noMutation!==true||!Array.isArray(sample.actualFocus)||!Array.isArray(sample.expectedFocus)||sample.expectedFocus.length!==([1,2].includes(index%8)?1:0)||JSON.stringify(sample.actualFocus)!==JSON.stringify(sample.expectedFocus));
  report.legacyCaseCount=names.length;
  report.legacySeedFailures=report.seedFailures;
  if(!quota||!exact(quota.checks,quotaNames)||!exact(quota.preconditions,quotaPreconditions)){report.classification='fixture-shape-failed';return finish(Error('Fixed quota inventories differ'));}
  if(!Object.values(quota.preconditions).every(Boolean)){report.classification='fixture-precondition-failed';return finish(Error('Public quota setup failed'));}
  report.checks.push(...quotaNames.map(name=>({name,passed:quota.checks[name]})));
  report.failures=report.checks.filter(row=>!row.passed);
  if(!Array.isArray(quota.seeded)||quota.seeded.length!==32){report.classification='fixture-shape-failed';return finish(Error('Fixed32 quota sequences absent'));}
  report.quotaSeedFailures=quota.seeded.filter((sample,index)=>sample.seed!==index||sample.cycles!==17+index||sample.issued!==sample.cycles||sample.completed!==sample.cycles||sample.preserved!==true||!Number.isInteger(sample.maximumPending)||sample.maximumPending>16||sample.noMutation!==true||sample.closed!==true||sample.once!==true||!Array.isArray(sample.actualFocus)||!Array.isArray(sample.expectedFocus)||sample.expectedFocus.length!==1||JSON.stringify(sample.actualFocus)!==JSON.stringify(sample.expectedFocus));
  report.seedFailures=[...report.legacySeedFailures,...report.quotaSeedFailures];
  report.caseCount=names.length+quotaNames.length;
  report.seedSampleCount=64;
  report.setupCount=preconditions.length+quotaPreconditions.length;
  report.passed=report.failures.length===0&&report.seedFailures.length===0;
  report.classification=report.passed?'component-pass':legacy.contractReady===false?'watch-capability-or-scheduling-red':'watch-batch-liveness-red';
  finish();
 });
}catch(error){report.classification='execution-or-image-failed';finish(error);}
