'use strict';
// Fixed bounded component RED report; synthetic data only.
const assert=require('node:assert/strict');
const {Elm}=require('../assets/workspace-owner-component-red.js');
const expected=["literalFixturePreconditions", "completeOpenedDesktopMatchesBaselinePlusLiteralChanges", "orderedOpenEffectsArePublishThenLiteralFocus", "completeClosedDesktopExceptOpaqueReturnFocus", "orderedCloseEffectsArePublishThenOneRead", "registeredOpenHasExactFocusAndNoRequests", "registeredCloseHasExactReadAndNoMutation", "matchedReadReturnsExactOriginalOpener", "duplicateReadCannotRepeatFocus", "overviewOwnerAndLiteralUnsupportedControls", "keyboardAndPointerUnsupportedCallbacksStutter", "foreignReplacementAndStaleCallbacksStutter", "foreignEnabledCloseCannotDismiss", "replacementEnabledCloseCannotDismiss", "staleEnabledCloseCannotDismiss", "validEnabledCloseAfterRefusalsWorks", "duplicateEnabledCloseCannotReapply", "policyRejectsInvalidScopesWithoutEffects", "validEscapeAfterRefusalsClosesWithoutMutation", "zeroOutputRetiresUnsupportedOwner", "returnedOutputRejectsRetiredOwner", "noOpEffectsDoNotRegisterCommand", "topologyTransitionsDoNotMutateWorkspace", "duplicateEscapeIsInert"];

let count=0, failure=null, receipt=null;
const app=Elm.WorkspaceOwnerComponentReplay.init({flags:null});
app.ports.outgoing.subscribe(value=>{count++;try{
 assert.equal(count,1);assert.deepEqual(Object.keys(value).sort(),['checkNames','checks','requirement','scenario','scope']);
 assert.equal(value.requirement,'ELM-UI-006');assert.equal(value.scenario,'workspace-management-unavailable');
 assert.equal(value.scope,'synthetic owner callbacks; local control and dismissal only');
 assert(Array.isArray(value.checkNames));assert.equal(value.checkNames.length,expected.length);
 assert.equal(new Set(value.checkNames).size,expected.length);assert.deepEqual(value.checkNames,expected);
 assert.deepEqual(Object.keys(value.checks).sort(),[...expected].sort());
 for(const name of expected)assert.equal(typeof value.checks[name],'boolean');
 const failed=expected.filter(name=>value.checks[name]!==true);assert.deepEqual(failed,['overviewOwnerAndLiteralUnsupportedControls']);
 receipt={classification:'EXPECTED_COMPONENT_RED',requirement:value.requirement,scenario:value.scenario,failed,checkNames:value.checkNames,checks:value.checks,nativeAcceptance:false,originalAcceptance:false};
 }catch(error){failure=error;}});
setTimeout(()=>{if(failure||count!==1||receipt===null){console.error(failure||'missing or duplicate output');process.exitCode=1}else process.stdout.write(JSON.stringify(receipt)+'\n')},1000);
