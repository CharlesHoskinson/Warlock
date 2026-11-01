'use strict';
// QA-only draft. Root compiles each actual Elm worker and supplies the five
// exact compiled JS paths. No compiler, model, GUI, VM, or native execution is
// performed by this author. Not an original-EARS acceptance by itself.
// Usage: node typed-state.cjs /abs/NotificationsReplay.js /abs/JumpListReplay.js /abs/NotificationRelevanceReplay.js /abs/RetirementProofReplay.js /abs/LocalFieldReplay.js /abs/report.json
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const manifests = Object.freeze({
  NotificationsReplay: Object.freeze([
    'notificationOpenerIntegrated','centerModeAcceptedByProductionRenderer',
    'openingReadFocusMatchesActualControl','allEntryStatesDecodeAndPreserveWireNames',
    'invalidEntryStateRefused','invokeIdentityAndWireUnchanged','dismissIdentityAndWireUnchanged',
    'dispatchedOutcomeTyped','refusedOutcomeTyped','invalidOutcomePreservesPending',
    'unknownOutcomeTypedAndPending','oneExplicitAction','pendingCannotRepeat',
    'dispatchedCannotRepeat','expiryRemovesActionsAndKeepsHistory','expiredChoiceIsInert',
    'reusedIdRejectsOldIncarnation','unknownCannotReplay',
    'explicitReadReconcilesRetiredUnknownWithoutEffect','staleViewCannotSubmit',
    'wrongReceiptCannotSettle','olderObservationCannotReviveTarget',
    'incomingExpiryNeverMovesFocus','allControlsHaveNames',
  ]),
  JumpListReplay: Object.freeze([
    'TypedActionKindsAndWireStrings','UnknownActionKindRejected','CrossKindPrefixRejected',
    'ActionKindDescriptionsPreserved',
    'LauncherHasBoundedKeyboardJumpOpener','OriginalTwoDeclaredActionsShown',
    'UnsupportedActionsAbsent','OnlyOwnedRecentActionShown','ForeignRecentNeverDispatches',
    'UnsupportedActionNeverDispatches','OneExplicitDesktopAction','OwnedRecentDispatchesOnce',
    'PopupClosesBeforeLaunch','SubmissionNeverClaimsApplicationReady',
    'UnknownPersistsWithoutReplay','ForeignApplicationCannotSettleReceipt',
    'ForeignApplicationReadCannotReplaceOpenList','RefreshOnlyReads',
    'CloseReturnsToLauncherWithoutLaunch','OtherPopupRetiresList','StaleViewCannotSubmit',
    'NativeRendererAcceptsJumpMode','AllActionsNamed',
  ]),
  NotificationRelevanceReplay: Object.freeze([
    'CurrentIdleSetupOpensNotifications','MatchedFocusedExpiryPolite','PassiveFocusCreatesNoAnnouncement','IrrelevantExpirySilent',
    'RepeatedExpirySilent','LateFocusCannotReplayExpiry','FocusedUnavailableNodeIsNotActionable',
    'PendingActionRetainsFocusWithoutAuthority','UserInvokedExpiryRelevant',
    'MatchedExpiredActionRefusalPolite','RefusalRetainsExactRequestAndTarget',
    'ReplacementCannotLosePendingExpiryIdentity','ExactNativeExpiryReasonWithoutIntermediateObservation',
    'RepeatedMatchedRefusalSilent','ForeignRefusalCannotSettle','ExpiryAndRefusalDoNotRequestFocus',
    'DndSuppressesExpiryAndRefusal','LeavingRetiredControlReleasesPlaceholder',
    'ForeignOutputCannotSupplyFocus','StalePublicationCannotSupplyFocus',
  ]),
  // Provisional source: RetirementProofReplay.elm SHA256 94f9ac8fa45a7802ad43f353efd502830340d05938fec6c44c618b0479fc905e.
  // Root must bind the final fixture source and compiled artifact hashes.
  RetirementProofReplay: Object.freeze([
    'observeProofDecodesTypedConstructorsAndNames','retireProofDecodesTypedConstructorsAndNames',
    'wrongKindRefused','wrongGrantStateRefused','wrongProtocolVersionRefused',
    'wrongRetirementProtocolRefused','extraFieldRefused','missingFieldRefused',
    'invalidOperationRefused','zeroCounterRefused','foreignBindingUnknownRefused',
    'recordBindingContextMismatchRefused','uncorrelatedAnnouncementRefused',
    'prematureReleaseWithoutBothObservationsRefused','changedOperationInReleaseProofRefused',
    'mismatchedObservationRequestOrOutputRefused','legacyUncertainOriginBlocksRelease',
    'correlatedTrackingReleaseSucceedsAndPreventsReplay',
    'owningRouteAnnounceEmitsReconciliationReadyAndRetainsTypedProof',
    'owningRouteCorrelatedReleaseClearsUnresolvedUnknown',
  ]),
  LocalFieldReplay: Object.freeze([
    'repeatedReversionRetainsPendingWithoutDispatch',
    'preeditAdvanceFirstTwoEditsDispatched',
    'preeditAdvanceHoldsDraft',
    'preeditEndMatchingAdvancedPublicationSettles',
    'reversionFirstQueryActuallyDispatched',
    'reversionToPublishedValueRetainsLatestIntent',
    'reversionSurvivesDelayedEarlierResult',
    'reversionMatchingLatestValueIsVisible',
    'unrelatedOldValueKeepsFirstPending',
    'reversionAfterUnrelatedPublicationRetainsIntent',
    'lateFirstAfterUnrelatedPublicationStillRetriesLatest',
    'localPaintGapPreservesDraft',
    'localFifoKeepsLatestValue',
    'refreshPreservesUnacknowledgedDraft',
    'matchingObservationAcknowledgesDraft',
    'staleExternalQueryStillRejected',
    'futureLocalQueryRejected',
    'zeroPublicationRejected',
    'oldLeaseLocalQueryRejected',
    'newLeaseRetiresPriorDraft',
    'replacedFieldRejectsOldLocalQuery',
    'boundedLocalQueryRejected',
    'sameLeaseLocalPreeditHeld',
    'sameLeaseLocalCommitUsesCurrentScope',
    'staleExternalCompositionStillRejected',
    'staleButtonStillRejected',
    'pendingBlocksPinJumpUnpinAndPagingTransitions',
    'pendingAllowsSafeEscapeAndRefreshTransitions',
    'composingBlocksAllNonFieldButtonsInTransition',
    'honestOverlayDisablesExactBlockedSet',
    'composingOverlayDisablesEveryNonFieldControl',
  ]),
});
function assert(ok, why) { if (!ok) throw new Error(why); }

// Validate full port payload before JSON serialization so unsupported values,
// accessors, hidden properties, cycles and sparse arrays cannot disappear.
function checkJson(value, where, ancestors, realm) {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return;
  if (typeof value === 'number') { assert(Number.isFinite(value) && !Object.is(value, -0), `${where}: unsupported number`); return; }
  assert(typeof value === 'object' && !ancestors.has(value), `${where}: unsupported or cyclic`);
  const proto = Object.getPrototypeOf(value);
  assert(proto === (Array.isArray(value) ? realm.array : realm.object) || (!Array.isArray(value) && proto === null), `${where}: unsupported prototype`);
  assert(Object.getOwnPropertySymbols(value).length === 0, `${where}: symbol property`);
  ancestors.add(value);
  try {
    const desc = Object.getOwnPropertyDescriptors(value);
    const keys = Object.keys(desc).filter(key => !(Array.isArray(value) && key === 'length'));
    if (Array.isArray(value)) assert(keys.length === value.length && keys.every((key, i) => key === String(i)), `${where}: sparse or extended array`);
    for (const key of keys) {
      assert('value' in desc[key] && desc[key].enumerable, `${where}.${key}: hidden/accessor property`);
      checkJson(desc[key].value, `${where}.${key}`, ancestors, realm);
    }
  } finally { ancestors.delete(value); }
}

async function observe(name, filename, messages) {
  const expected = manifests[name];
  assert(Array.isArray(expected) && expected.length > 0 && new Set(expected).size === expected.length,
    `${name}: exact source-derived check manifest is missing`);
  const bytes = fs.readFileSync(filename);
  const code = bytes.toString('utf8');
  assert(Buffer.from(code, 'utf8').equals(bytes), `${name}: JS not canonical UTF-8`);
  const context = vm.createContext({ console: { log() {}, warn() {}, error() {} }, setTimeout, clearTimeout });
  const realm = vm.runInContext('({object: Object.prototype, array: Array.prototype})', context);
  new vm.Script(code, { filename: path.basename(filename) }).runInContext(context, { timeout: 10000 });
  assert(context.Elm && context.Elm[name] && typeof context.Elm[name].init === 'function', `${name}: worker not found`);
  const app = context.Elm[name].init({ flags: null });
  assert(app.ports && app.ports.outgoing && typeof app.ports.outgoing.subscribe === 'function', `${name}: outgoing port missing`);
  await new Promise((resolve, reject) => {
    const watchdog = setTimeout(() => reject(new Error(`${name}: output timeout`)), 10000);
    app.ports.outgoing.subscribe(payload => {
      try {
        checkJson(payload, '$', new Set(), realm);
        messages.push(JSON.parse(JSON.stringify(payload)));
        if (messages.length === 1) setTimeout(() => { clearTimeout(watchdog); resolve(); }, 25);
      } catch (error) {
        // Unsupported payloads cannot be safely rendered as JSON; retain the
        // explicit diagnostic and any previously captured complete payloads.
        messages.push({ unsupportedPayload: true, error: String(error && error.message || error) });
        clearTimeout(watchdog); reject(error);
      }
    });
  });
  assert(messages.length === 1, `${name}: expected exactly one worker output, got ${messages.length}`);
  const payload = messages[0];
  const checks = payload && payload.checks;
  const actual = checks && typeof checks === 'object' && !Array.isArray(checks) ? Object.keys(checks).sort() : [];
  const sorted = [...expected].sort();
  const missing = sorted.filter(key => !actual.includes(key));
  const extra = actual.filter(key => !sorted.includes(key));
  const failed = sorted.filter(key => !checks || checks[key] !== true);
  const failures = [...missing.map(key => `missing check: ${key}`),
    ...extra.map(key => `unexpected check: ${key}`), ...failed.filter(key => !missing.includes(key)).map(key => `check is not true: ${key}`)];
  return { name, file: filename, sha256: hash(bytes), checks: sorted.map(key => ({name: key, passed: !!checks && checks[key] === true})),
    failures, payload, passed: failures.length === 0 };
}

async function main() {
  assert(process.argv.length === 8 && process.argv.slice(2).every(path.isAbsolute), 'expected five absolute worker paths and an absolute report path');
  const names = ['NotificationsReplay','JumpListReplay','NotificationRelevanceReplay','RetirementProofReplay','LocalFieldReplay'];
  const fixtures = [];
  for (let i = 0; i < names.length; i++) {
    const messages = [];
    const filename = path.resolve(process.argv[i + 2]);
    try { fixtures.push(await observe(names[i], filename, messages)); }
    catch (error) { fixtures.push({ name: names[i], file: filename, passed: false, checks: [], payloads: messages,
      failures: [String(error && error.stack || error)] }); }
  }
  const checks = fixtures.flatMap(fixture => fixture.checks.map(row => ({fixture: fixture.name, ...row})));
  const failures = fixtures.flatMap(fixture => fixture.failures.map(reason => ({fixture: fixture.name, reason})));
  const passed = fixtures.length === 5 && fixtures.every(fixture => fixture.passed === true) && checks.length > 0 && checks.every(row => row.passed === true) && failures.length === 0;
  fs.writeFileSync(process.argv[7], JSON.stringify({ schema: 1, scope: 'compiled Elm worker controls only; not native or whole-EARS acceptance',
    runnerSha256: hash(fs.readFileSync(__filename)), fixtures, checks, failures, passed }, null, 2) + '\n');
  if (!passed) process.exitCode = 1;
}
main().catch(error => { process.stderr.write(`typed-state: ${error && error.stack || error}\n`); process.exitCode = 1; });
