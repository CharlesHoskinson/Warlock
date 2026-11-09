'use strict';
// Actual compiled public Elm reducer component; no native/DOM/service evidence.
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const [image,output]=process.argv.slice(2);
if(process.argv.length!==4)throw Error('Expected compiled MenuEscapeReplay.js and NEW report.json');
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const names=['current-menu-escape-closes','dismissal-queues-current-refresh','no-return-before-fresh-observation','eligible-origin-return-once','duplicate-escape-no-repeat-focus','stale-lease-refused','stale-publication-refused','foreign-owner-scope-refused','retired-view-refused','removed-origin-no-focus','changed-binding-or-output-no-focus','pointer-origin-no-keyboard-steal','nonmenu-close-path-preserved','unavailable-origin-no-focus','missing-close-does-nothing','wrong-surface-envelope-refused'];
const preconditions=['one-current-eligible-taskbar-group','keyboard-menu-opened-through-renderer','actual-enabled-menu-close-control','pointer-menu-opened-through-renderer','applications-other-mode-opened'];
const report={schema:1,passed:false,nativeAcceptance:false,originalAccepted:false,classification:'not-started',imageSha256:hash(fs.readFileSync(image)),fixtureSha256:hash(fs.readFileSync(__filename))};
let settled=false;
function finish(error){if(settled)return;settled=true;clearTimeout(timer);if(error){report.error=String(error.stack??error);report.passed=false;}fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});process.exitCode=report.passed?0:1;}
const timer=setTimeout(()=>finish(Error('Fixed reducer result absent after5s')),5000);
try{
 const sandbox={console,setTimeout,clearTimeout};vm.createContext(sandbox);vm.runInContext(fs.readFileSync(image,'utf8'),sandbox,{timeout:2000});
 const app=sandbox.Elm.MenuEscapeReplay.init();
 app.ports.outgoing.subscribe(value=>{
  report.observed=value;
  const exact=(record,expected)=>record&&typeof record==='object'&&!Array.isArray(record)&&JSON.stringify(Object.keys(record).sort())===JSON.stringify([...expected].sort())&&Object.values(record).every(x=>typeof x==='boolean');
  if(!exact(value.preconditions,preconditions)||!exact(value.checks,names)){report.classification='fixture-shape-failed';return finish(Error('Exact fixed replay inventory differs'));}
  if(!Object.values(value.preconditions).every(Boolean)){report.classification='fixture-precondition-failed';return finish(Error('Public reducer setup did not establish the required case'));}
  report.caseCount=names.length;report.checks=names.map(name=>({name,passed:value.checks[name]}));report.failures=report.checks.filter(row=>!row.passed);
  report.passed=report.failures.length===0;report.classification=report.passed?'component-pass':'semantic-red';finish();
 });
}catch(error){report.classification='execution-or-compile-image-failed';finish(error);}
