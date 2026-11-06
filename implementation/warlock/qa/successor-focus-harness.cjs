'use strict';
// Unexecuted test-only adapter. Original 28+650 harness remains mandatory.
// External protected launcher binds executed bytes and enforces its own limits.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const vm = require('node:vm');
const assert = (ok, message) => { if (!ok) throw new Error(message); };
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const specs = [
  {name:'SystemMenuFocusPipeline', top:['checks','confirmationFrame','cancelFrame'], checks:[
    'missingPointerObservationRefusesOpen','foreignIdleRefusesThenCurrentIdleAllows',
    'confirmationPublishesSuccessorAndFocus','cancellationPublishesSuccessorAndFocus',
    'literalFullModelsAndOrderedEffects','staleThenValid','duplicateCancelRefused',
    'unavailableNetworkDisabled','observedVolumeDisplayed']},
  {name:'SuccessorFocusReplay', top:['requirements','scope','checks'], checks:[
    'opened-current-available-snapshot','unavailable-network-refused-no-send','remaining-observed-state',
    'prompt-focus-matches-literal-successor-and-enabled-row','cancel-focus-matches-literal-successor-and-enabled-row',
    'stale-refused-then-valid-cancel','duplicate-cancel-stutters','foreign-binding-old-stamp-refused',
    'exhaustion-emits-no-focus','close-requests-current-system-opener','renderer-rejects-foreign-and-stale-then-valid']},
  {name:'SystemMenuFocusExtended', top:['checks','frame','confirmFrame','pendingFrame'], checks:[
    'sessionClosingClassifiedAndLogoutDenied','otherSessionTextLabelAndLogoutPreserved','sessionStateBoundsAndTypeRefused',
    'networkPermissionsPreserveAdmission','powerCapabilitiesPreserveAdmission','foreignNetworkCapabilityRefused','foreignPowerPermissionRefused',
    'powerCapabilityLabelsPreserved','systemMenuOpenerIntegrated','menuModeAcceptedByProductionRenderer','openingReadFocusMatchesCloseControl',
    'originalUnavailableNetworkShown','remainingStateObserved','oneExplicitVolumeChange','pendingCannotRepeat','committedCannotRepeatOldRevision',
    'unknownCannotReplay','readReconcilesChangedStateWithoutEffect','unavailableNeverSubmits','restartRequiresUIConfirmation','cancelHasNoNativeEffect',
    'confirmedRestartSubmitsOnce','directConfirmationCannotBypassPrompt','wrongReceiptCannotSettle','staleViewCannotSubmit',
    'closingFocusesOpenerWithoutNativeEffect','staleCloseRefusedThenCurrentCloseFocusesExactOpener','cancelConfirmationEmitsCloseFocus',
    'confirmationExactFullModelAndSuccessorEffect','cancellationExactFullModelAndSuccessorEffect','oldConfirmationStampRefusedThenCurrentAccepted',
    'oldRevisionRefusedThenCurrentAccepted','closedMenuRefusesConfirmation','confirmationFocusesCurrentEligibleCancel',
    'cancelTargetIsCurrentEnabledCloseControl','staleCancelCannotRefocusThenValidCancelRestoresCurrentClose','duplicateCancelCannotRefocus',
    'oldBindingStampCannotCancelForeignModel','exhaustedPresentationEmitsNoConfirmationFocus','disabledAndForeignActionsRefusedThenCurrentCloseAvailable',
    'anotherPopupRetiresSystemWithoutLosingNativeState','allControlsHaveNames']}
];
function exact(value, names, label) {
  assert(value !== null && typeof value === 'object' && !Array.isArray(value), label+' object required');
  assert(JSON.stringify(Object.keys(value).sort()) === JSON.stringify([...names].sort()), label+' fields differ');
}
function readPinned(filename) {
  const fd=fs.openSync(filename,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);
  try {
    const before=fs.fstatSync(fd,{bigint:true}); assert(before.isFile(),'not a regular file');
    const bytes=fs.readFileSync(fd); const after=fs.fstatSync(fd,{bigint:true});
    for (const key of ['dev','ino','size','mtimeNs','ctimeNs']) assert(before[key]===after[key],'file changed while read');
    const text=bytes.toString('utf8'); assert(Buffer.from(text,'utf8').equals(bytes),'invalid UTF-8');
    return {text,hash:sha(bytes)};
  } finally { fs.closeSync(fd); }
}
async function observe(spec,filename) {
  const timers=new Set(), messages=[];
  let rejectActive=null, asyncFailure=null, artifact;
  const later=(fn,ms,...args)=>{let t;t=setTimeout(()=>{timers.delete(t);try{fn(...args);}catch(e){asyncFailure=e;if(rejectActive)rejectActive(e);}},ms);timers.add(t);return t;};
  const cancel=t=>{clearTimeout(t);timers.delete(t);};
  try {
    assert(spec.checks.length>0 && new Set(spec.checks).size===spec.checks.length,'invalid check manifest');
    artifact=readPinned(filename);
    const context=vm.createContext({console:{log(){},warn(){},error(){}},setTimeout:later,clearTimeout:cancel});
    new vm.Script(artifact.text,{filename:path.basename(filename)}).runInContext(context,{timeout:10000});
    assert(context.Elm && context.Elm[spec.name] && typeof context.Elm[spec.name].init==='function','worker missing');
    const app=context.Elm[spec.name].init({flags:null});
    assert(app.ports && app.ports.outgoing && typeof app.ports.outgoing.subscribe==='function','outgoing port missing');
    await new Promise((resolve,reject)=>{
      rejectActive=reject;
      const watchdog=later(()=>reject(new Error('worker output timeout')),10000);
      app.ports.outgoing.subscribe(payload=>{
        try { messages.push(JSON.parse(JSON.stringify(payload))); if(messages.length===1) later(()=>{cancel(watchdog);resolve();},25); }
        catch(error){reject(error);}
      });
      if(asyncFailure)reject(asyncFailure);
    });
    assert(!asyncFailure && messages.length===1,'expected one output within 25ms window');
    const result=messages[0]; exact(result,spec.top,'payload'); exact(result.checks,spec.checks,'checks');
    if(spec.name==='SuccessorFocusReplay') {
      assert(JSON.stringify(result.requirements)===JSON.stringify(['ELM-UI-011','ELM-UX-024','ELM-UX-032']),'requirement identity mismatch');
      assert(result.scope==='synthetic reducer and frame only; no native or AT focus','scope mismatch');
    }
    assert(spec.checks.every(name=>result.checks[name]===true),'false or non-boolean check');
    return {name:spec.name,file:filename,sha256:artifact.hash,passed:true,payload:result};
  } catch(error) {
    return {name:spec.name,file:filename,sha256:artifact ? artifact.hash : null,passed:false,error:String(error && error.stack || error),payloads:messages};
  } finally { rejectActive=null; for(const timer of timers)clearTimeout(timer); timers.clear(); }
}
async function main() {
  assert(process.argv.length===6 && process.argv.slice(2).every(path.isAbsolute),'expected three absolute worker paths and new absolute report path');
  const results=[];
  for(let i=0;i<specs.length;i++)results.push(await observe(specs[i],process.argv[i+2]));
  const passed=results.length===3 && results.every(result=>result.passed===true);
  const report={schema:1,scope:'synthetic Elm focus checks only; not native or accessibility acceptance',settleWindowMs:25,fixtures:results,passed,originalAccepted:false,nativeAccepted:false};
  const fd=fs.openSync(process.argv[5],fs.constants.O_WRONLY|fs.constants.O_CREAT|fs.constants.O_EXCL|fs.constants.O_NOFOLLOW,0o600);
  try {fs.writeFileSync(fd,JSON.stringify(report,null,2)+'\n');} finally {fs.closeSync(fd);}
  if(!passed)process.exitCode=1;
}
main().catch(error=>{process.stderr.write(String(error && error.stack || error)+'\n');process.exitCode=1;});
