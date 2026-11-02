'use strict';
// QA-only, UNEXECUTED fixed consumer for atomic patch 23e26a42. Root must bind
// exact sources, compiler, artifacts, this executed runner and whole-process
// deadline externally. VM is a component loader, not a security boundary.
// Fixed argv: ShortcutPreferencesReplay, SnapReplay, GeometryCapabilitySequences,
// TransferReplay, AnnouncementReplay, TaskViewReplay, PinMaxReplay,
// FullscreenExitReplay absolute JS paths, followed by an absolute NEW report.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const assert = (condition, why) => { if (!condition) throw Error(why); };
const specs = Object.freeze([
  { name:'ShortcutPreferencesReplay', top:['checks','frame','savedFrame','pendingFrame','unknownFrame'], names:[
    'actualRendererAcceptsShortcutControls','defaultConflictCannotBeChosen','freeAlternateIsExplicit','undecidedCannotSubmit','oneGuardedPreferenceWrite','pendingCannotRepeat','unknownCannotRepeat','savingRetainsTypedAwaiting','unknownRetainsTypedUnconfirmed','duplicateUnknownNoStateOrEffect','unverifiedSavedIsUnconfirmed','unverifiedStoredIsUnconfirmed','unsettledReadIsUnconfirmed','unavailableReadPreservesAwaiting','unavailableReadPreservesUnconfirmed','staleReadPreservesPreferenceModel','lateSavedSettlesWithoutWrite','lateRefusalSettlesWithoutWrite','unknownRefreshOnlyReads','readReconcilesActualStoredAndNativeState','savedRequiresActualChosenNativeState','foreignReceiptCannotCommit','staleControlCannotEdit','hostRestartRestoresStoredChoiceWithoutEffects','renderedDefaultConflictDisabled','helpRemainsAvailable'] },
  { name:'SnapReplay', top:['checks','frame','scope'], names:[
    'allSixDesktopSelectionsHaveLiteralGeometryWireAndRoundTrip','seededTranslationKeepsSixGeometryRelations','fullWidthCountersRoundTripExactly','malformedPlacementFieldsRefused','changedBindingInvalidatesRetainedChooser','epochMonitorWorkspaceAndTargetChangesInvalidateExactProposal','allocatorRejectsMaxRequestWithoutMutation','allocatorRejectsMaxGenerationWithoutMutation','recoveredUnknownBlocksExactSnapReplay','exactRefusalIsTerminalWithoutClaimingPlacement','sixRegionsExactGeometryWireAndProductionIntent','unsupportedRegionRefused','invalidRectangleRefused','zeroAuthorityGenerationRefused','extraPlacementFieldRefused','actualDesktopOpensSnap','leftHalfUsesNativeWorkArea','rightHalfCompletesOddWidth','selectionHasNoNativeEffects','staleViewCannotChangeRegion','changedOutputInvalidatesPreview','changedWorkAreaInvalidatesPreview','sameScopeRevisionCanRefreshPreview','grabRetainsOnlyExistingUnchangedPreview','grabCannotAdmitNewChooser','unblockedIneligibleTargetRetiresPreview','readonlyRefreshRetainsPreview','refreshPendingDisablesRegionInput','minimizedTargetHasNoChooser','allSixRegionsAndCloseReachable','nativePlacementExplicitlyUnavailable','disabledApplyCannotResolve','outputReflowRetiresChoiceAndOnlyReads','snapUsesSharedAllocator','placementIntentRoundTripsStrictly','pendingSnapCannotAllocateAgain','staleOutputCannotSubmitPlacement','grabCannotSubmitPlacement','negotiatedSnapExposesApply','applyClosesChooserAndReadsBeforeMutation','unknownRecoveryRetainsPlacementAndBlocksReplay','sharedOutcomeGateAcceptsExactSnapShape','shellCorrelatesSnapCommittedReceipt','sameIdsDifferentPlacementCannotSettle','closeRetiresPreview'] },
  { name:'GeometryCapabilitySequences', top:['checks','scope'], names:[
    'negotiationActuallyIssued','all128CapabilitySubsetsFollowActualShellRoute','seededOrderingPreservesActualRoute','allSubsetsGateSnapAtRealAllocator','allSubsetsGateMaximizeAtRealAllocator','allSevenOperationsRespectAllCapabilitySubsets','allSevenOperationsRetainUnknownAndRefuseMismatchedReceipt','allSevenNegotiatedDecodedFactsReachAllocator','wrongFactsRequestCannotAdmitGeometry','unnegotiatedGeometryFactRefused','staleDecodedGeometryStampCannotEmitOperation','malformedCapabilitiesRefusedWithoutGrant','mismatchedRequestCannotGrant','foreignBindingCannotGrant','duplicateAttachCannotReissue','lateAttachAfterDisconnectCannotGrant'] }
  ,{"name":"TransferReplay","top":["checks","frame","chooserFrame","intent"],"names":["sharedAllocatorCreatesOneTypedTransfer","intentStrictRoundtrip","pendingNativeObservationCannotMoveMembership","wrongDestinationReceiptCannotMoveMembership","matchingCommittedReceiptReleasesMembership","refusalKeepsOriginalObservedWorkspace","unknownKeepsMembershipAndCustody","duplicateCannotSubmitAgain","unnegotiatedCannotSubmit","specialAndSameWorkspaceRejected","taskViewExposesMoveAction","emptyWorkspaceDestinationAvailable","cancelReturnsToOverviewWithoutEffect","selectionRequiresFreshObservations","staleViewCannotChooseDestination","duplicateTerminalReceiptDoesNotReplay"]},
  {"name":"AnnouncementReplay","top":["checks","settingsFrame","secondFrame","retiredFrame","launchMessage","transferMessage"],"names":["launchMatchedRefusal","launchRefusalPreservesQueryAndOpen","launchRefusalDoesNotRequestFocus","launchRefusalCorrelated","launchRepeatSilent","settingsMatchedPending","rootSettingsRefusalAnnounced","rootRepeatSilent","newRequestSameWordsGetsNewSerial","foreignSettingsRefusalIgnored","ownerRetirementDoesNotAllocateAnnouncement","transferRefusalCorrelated"]},
  {"name":"TaskViewReplay","top":["checks","frame"],"names":["cancelTransferReturnsSameCurrentEligibleMoveControl","duplicateAndStaleTransferCancellationAreInert","unavailableTransferOriginReturnsCurrentFilter","incoherentTransferOriginReturnsAlwaysAvailableAll","removedTransferCapabilityReturnsCurrentFilter","filteredOutTransferOriginNeverReceivesFocus","retiredTransferOriginNeverSubstitutes","unknownReservedTransferOriginIsNotFocusedOrReplayed","closedTransferCancelNeverRefocuses","allWorkspaceCancelStillReturnsExactOrigin","retiredTransferReturnsCurrentRetainedWorkspaceFocus","retiredTransferChooserHasVisibleBrowseAndDismissal","retiredTransferDoesNotRepeatFocus","retiredTransferAndWorkspaceReturnAll","incoherentTransferObservationCannotRetireSelection","existingUnavailableExactMemberKeepsTransferChooser","closedTransferNeverRefocuses","sameApplicationNewIncarnationNeverSubstitutes","matchedRefusalWaitsForFreshRead","exactRefusalRestoresFilteredOverview","differentUnknownDuringRefusedReadDoesNotResumeOldOrigin","restoredEligibleFamilyGetsCurrentFocus","duplicateRefusalCannotReopenOrReplay","emittedRestoreCarriesExactFullIntentKey","pendingRestoreShowsCorrelatedLabel","pendingDuplicateDispatchIsSuppressed","refusedRestoreShowsCorrelatedLabel","committedChoiceStaysClosed","unknownChoiceStaysClosedWithoutReplay","unknownRestoreShowsCorrelatedLabel","unknownRefreshUsesReadOnlyWireKinds","staleUnknownProjectionCannotSettleOrReplay","unknownReservationPersistsAcrossFreshRead","unknownReadRecoveryReopensExactWorkspaceWithoutReplay","unknownReadRecoveryRepeatedOpenPreservesWorkspaceAndFocus","unknownReadRecoveryFallsBackToAllWhenWorkspaceDisappears","unknownMissingWorkspaceOverviewOpened","unknownMissingWorkspaceSelectionCleared","unknownMissingWorkspaceFocusTargetsAll","unknownMissingWorkspaceNoMutation","foreignIntentCannotReturn","anotherInterfaceCancelsReturn","replacementAuthorityCannotReturn","retiredFamilyReturnsToAllWindows","unconfirmedTransferRetainsSourceFamilyWithoutInventingNativeOwner","emptyInventoryComesThroughExactRootReceipt","nativeActiveEmptyMarkerDoesNotNeedFocusedWindow","emptyWorkspaceOpensAndBrowsesWithoutEffects","emptyWorkspaceKeepsVisibleDismissal","emptySelectionHasExplicitNotice","emptyWorkspaceDismissalIsReadOnly","foreignGeometryCannotInventEmptyWorkspace","duplicateWorkspacePacketRejectedByRoot","differentGeometrySequenceCannotJoinInventory","retiredEmptySelectionFallsBackToAll","groupsMatchMembership","activeWorkspaceNamed","openingIsObservationOnly","workspaceBrowseIsLocal","overviewInitialAccessibleFilterSelection","overviewAccessibleFilterFollowsReadOnlyBrowse","staleSelectionInert","unavailableWorkspaceNeverActivates","retiredIdentityNeverSubstitutes","selectionRefreshesBeforeEffect","duplicateChoiceInert","dismissalDoesNotMutate","dismissalDefersDOMFocusUntilFreshRead","independentRevisionNamespacesRemainBrowsable","mixedOutputMembershipWithheld","mixedFocusMembershipWithheld","mixedMinimizedMembershipWithheld","ordinaryRendererAcceptsTaskView","offWorkspaceSelectionRequiresFreshObservation","freshObservationRestoresExactWorkspaceTwoRootOnce","staleNavigationObservationNeverMutates","retiredNavigationRootNeverSubstitutes","duplicateNavigationObservationNeverReplays"]},
  {"name":"PinMaxReplay","top":["checks","preparedProbe","uncheckedFrame","checkedFrame","pendingFrame"],"names":["PinUsesExistingGeometryAllocator","IntentRoundTripsTypedPin","PendingNeverShowsOptimisticPin","CommittedReceiptAloneNeverShowsPin","CorrelatedObservationShowsPinAndMax","ConfirmedPinnedMenuKeepsAlwaysOnTopLabel","RefusalPreservesObservedUnpinnedMax","DuplicatePendingNeverReplays","UnknownNeverReplays","LegacyMissingPinNeverGrantsAction","FullscreenPinIsRefused","UnpinPreservesTypedMaxObservation","NoPinWithoutNegotiatedCapability","ReorderedCompleteFactsIssuePreparedPin","ObservedUnpinnedCheckboxIsUnchecked","PendingCheckboxNeverShowsDesiredPin","ReceiptAloneNeverChecksPin","ObservedPinnedCheckboxIsChecked","CheckedProjectionUsesShippedStrictRenderer","PreparedPinWaitsForBothCorrelatedReads","ChangedPeerTitleRefusesPreparedPin","ChangedPeerGeometryRefusesPreparedPin","ChangedTargetPinRefusesPreparedPin","ChangedOutputRefusesPreparedPin","UncorrelatedReadRefusesPreparedPin","PreparedPinRegistersOneReceiptMapping","DifferentPinOperationCannotSettleReservation","UnknownPinRetainsReservation"]},
  {"name":"FullscreenExitReplay","top":["checks"],"names":["sevenOperationsDecode","capabilityNamesPreserveOrder","duplicateCapabilityRejected","unknownCapabilityRejected","effectsFlagMismatchRejected","fullscreenMenuEnabled","ordinaryHasNoExit","maxHasNoExit","unsupportedHasNoExit","exactTypedPending","blockedRefuses","parentedRefuses","unsupportedRefuses","maxRefuses","unknownNeverReplays","receiptCorrelates","preparedExitRegistersOnce"]}
]);
const expectedCounts = [26,45,16,16,12,78,28,17];
for (let i=0; i<specs.length; i++) {
  assert(specs[i].names.length===expectedCounts[i] && new Set(specs[i].names).size===expectedCounts[i], 'invalid fixed manifest');
}
function readRegular(filename) {
  const fd=fs.openSync(filename, fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);
  try {
    const before=fs.fstatSync(fd,{bigint:true});
    assert(before.isFile() && before.size<=16777216n, 'artifact not regular or exceeds bound');
    const bytes=fs.readFileSync(fd), after=fs.fstatSync(fd,{bigint:true});
    for (const key of ['dev','ino','size','mtimeNs','ctimeNs']) assert(before[key]===after[key], 'artifact changed during read');
    const text=bytes.toString('utf8'); assert(Buffer.from(text,'utf8').equals(bytes), 'artifact not UTF-8');
    return {text,hash:sha(bytes),identity:`${before.dev}:${before.ino}`};
  } finally { fs.closeSync(fd); }
}
function validateJson(value, realm, state, seen=new Set(), depth=0) {
  assert(depth<=128 && ++state.nodes<=100000, 'payload exceeds structural bound');
  if (value===null || typeof value==='boolean') return;
  if (typeof value==='string') { assert(value.length<=1048576, 'payload string exceeds bound'); return; }
  if (typeof value==='number') { assert(Number.isFinite(value) && !Object.is(value,-0), 'unsupported number'); return; }
  assert(typeof value==='object' && !seen.has(value), 'unsupported/cyclic payload');
  const array=Array.isArray(value), proto=Object.getPrototypeOf(value);
  assert(proto===(array?realm.array:realm.object) || (!array && proto===null), 'unexpected payload prototype');
  assert(Object.getOwnPropertySymbols(value).length===0, 'symbol field');
  const desc=Object.getOwnPropertyDescriptors(value);
  const keys=Object.keys(desc).filter(key=>!(array && key==='length'));
  if (array) assert(keys.length===value.length && keys.every((key,i)=>key===String(i)), 'sparse/extended array');
  seen.add(value);
  for (const key of keys) {
    assert(Object.hasOwn(desc[key],'value') && desc[key].enumerable, 'hidden/accessor field');
    validateJson(desc[key].value,realm,state,seen,depth+1);
  }
  seen.delete(value);
}
function exactKeys(value,names,label) {
  assert(value && typeof value==='object' && !Array.isArray(value), `${label}: expected object`);
  assert(JSON.stringify(Object.keys(value).sort())===JSON.stringify([...names].sort()), `${label}: missing or extra fields`);
}
async function observe(spec,artifact) {
  const timers=new Set(), messages=[];
  let asyncFailure=null, rejectActive=null;
  function schedule(fn,delay,...args) {
    assert(timers.size<10000, 'timer capacity');
    let timer; timer=setTimeout(()=>{ timers.delete(timer); try { fn(...args); } catch(e) { asyncFailure=e; if(rejectActive) rejectActive(e); } },delay);
    timers.add(timer); return timer;
  }
  function cancel(timer) { timers.delete(timer); clearTimeout(timer); }
  try {
    const context=vm.createContext({console:{log(){},warn(){},error(){}},setTimeout:schedule,clearTimeout:cancel});
    const realm=vm.runInContext('({object:Object.prototype,array:Array.prototype})',context);
    new vm.Script(artifact.text,{filename:spec.name+'.js'}).runInContext(context,{timeout:3000});
    assert(context.Elm && context.Elm[spec.name] && typeof context.Elm[spec.name].init==='function', 'compiled worker mismatch');
    const app=context.Elm[spec.name].init({flags:null});
    assert(app.ports && app.ports.outgoing && typeof app.ports.outgoing.subscribe==='function', 'missing outgoing port');
    await new Promise((resolve,reject)=>{
      rejectActive=reject;
      const watchdog=schedule(()=>reject(Error('worker output timeout')),3000);
      app.ports.outgoing.subscribe(value=>{
        try {
          validateJson(value,realm,{nodes:0});
          const encoded=JSON.stringify(value); assert(Buffer.byteLength(encoded,'utf8')<=4194304,'payload exceeds byte bound');
          messages.push(JSON.parse(encoded));
          if(messages.length===1) schedule(()=>{cancel(watchdog);resolve();},25);
          else reject(Error('duplicate output inside bounded 25ms window'));
        } catch(e) { reject(e); }
      });
      if(asyncFailure) reject(asyncFailure);
    });
    assert(!asyncFailure && messages.length===1, 'missing or duplicate output');
    const payload=messages[0]; exactKeys(payload,spec.top,spec.name+' payload'); exactKeys(payload.checks,spec.names,spec.name+' checks');
    if(spec.top.includes('scope')) assert(typeof payload.scope==='string' && payload.scope.length>0,'missing scope');
    for(const key of spec.top.filter(key=>key.endsWith('Frame') || key==='frame'))
      assert(payload[key] && typeof payload[key]==='object' && !Array.isArray(payload[key]),`${spec.name} ${key} must be object`);
    const checks=spec.names.map(name=>({name,passed:payload.checks[name]===true}));
    return {name:spec.name,sha256:artifact.hash,checks,payload,passed:checks.every(c=>c.passed)};
  } catch(e) { return {name:spec.name,sha256:artifact.hash,checks:[],payloads:messages,error:String(e && e.stack || e),passed:false}; }
  finally { rejectActive=null; for(const timer of timers) clearTimeout(timer); timers.clear(); }
}
async function main() {
  assert(process.argv.length===11 && process.argv.slice(2).every(path.isAbsolute), 'expected eight absolute JS paths and a new absolute report path');
  const results=[]; let setupError=null;
  try {
    const artifacts=process.argv.slice(2,10).map(readRegular);
    assert(new Set(artifacts.map(x=>x.identity)).size===8,'artifact aliases not allowed');
    for(let i=0;i<specs.length;i++) results.push(await observe(specs[i],artifacts[i]));
  } catch(error) { setupError=String(error && error.stack || error); }
  const failures=setupError===null?results.filter(r=>!r.passed).map(r=>({name:r.name,error:r.error || 'one or more named checks false'})):[{name:'setup',error:setupError}];
  const report={passed:setupError===null && results.length===8 && results.every(r=>r.passed===true),fixtures:results,failures,runnerPathSha256AtReport:readRegular(__filename).hash};
  const fd=fs.openSync(process.argv[10],fs.constants.O_WRONLY|fs.constants.O_CREAT|fs.constants.O_EXCL|fs.constants.O_NOFOLLOW,0o600);
  try {fs.writeFileSync(fd,JSON.stringify(report,null,2)+'\n');} finally {fs.closeSync(fd);}
  if(!report.passed) process.exitCode=1;
}
main().catch(error=>{process.stderr.write(String(error && error.stack || error)+'\n');process.exitCode=1;});
