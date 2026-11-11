"use strict";
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const [image,output]=process.argv.slice(2);if(process.argv.length!==4)throw Error('Expected compiled image and NEW output');
const names=["minimize-retires-current-scope", "minimize-restores-current-eligible-group", "minimize-does-not-select-applications-fallback", "current-incarnation-remains-observed", "duplicate-reply-cannot-refocus", "foreign-binding-cannot-retire", "wrong-base-cannot-retire", "unknown-cannot-retire-or-focus", "unrelated-minimize-preserves-scope", "title-change-preserves-scope", "already-minimized-is-not-new-minimize", "replacement-never-restores-old-group", "no-restore-activate-or-mutation", "no-watch-rearm-after-retirement"],setup=["current-group-eligible", "keyboard-menu-open", "one-correlated-watch", "actual-reducer-minimized-state", "same-group-current-eligible"];
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const report={schema:1,passed:false,nativeAcceptance:false,originalAcceptance:false,assistiveTechnologyAcceptance:false,providerAcceptance:false,imageSha256:sha(fs.readFileSync(image)),fixtureSha256:sha(fs.readFileSync(__filename))};
let done=false;const finish=error=>{if(done)return;done=true;clearTimeout(timer);if(error){report.passed=false;report.error=String(error.stack||error);}fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});process.exitCode=report.passed?0:1;};
const timer=setTimeout(()=>finish(Error('Fixed result missing')),5000);
try{const sandbox={console,setTimeout,clearTimeout};vm.createContext(sandbox);vm.runInContext(fs.readFileSync(image,'utf8'),sandbox,{timeout:2000});sandbox.Elm.Ui011OpenerMinimizeReplay.init().ports.outgoing.subscribe(value=>{
report.observed=value;
const exact=(obj,keys)=>obj&&JSON.stringify(Object.keys(obj).sort())===JSON.stringify([...keys].sort())&&Object.values(obj).every(x=>typeof x==='boolean');
if(!exact(value.preconditions,setup)||!exact(value.checks,names)||!Object.values(value.preconditions).every(Boolean)){report.classification='fixture-shape-or-setup-failed';return finish(Error('Fixed setup/inventory failed'));}
report.checks=names.map(name=>({name,passed:value.checks[name]}));report.failures=report.checks.filter(row=>!row.passed);
if(!Array.isArray(value.seeded)||value.seeded.length!==32){report.classification='fixture-shape-failed';return finish(Error('Fixed32 missing'));}
report.seedFailures=value.seeded.filter((row,index)=>row.seed!==index||row.prepared!==true||row.scopeMatches!==true||row.noMutation!==true||!Array.isArray(row.actualFocus)||!Array.isArray(row.expectedFocus)||row.expectedFocus.length!==(index%4===0?1:0)||JSON.stringify(row.actualFocus)!==JSON.stringify(row.expectedFocus));
report.caseCount=names.length;report.setupCount=setup.length;report.seedSampleCount=32;report.passed=!report.failures.length&&!report.seedFailures.length;report.classification=report.passed?'component-pass':'semantic-red';finish();});}catch(error){report.classification='execution-or-image-failed';finish(error);}
