// Explicit named traces; author did not execute them. Assert the pre-state and
// end at fail(): a blocked action has no successor for a later expectation.
module ui_engine_lifetime_test {
 import ui_engine_lifetime.* from "./ui-engine-lifetime"
 run directOwnedRetired = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(cancel).then(callbackDone).then(retireCallback).then(closeLife).then(observeExit).then(reap).then(cleanup).expect(s.clean and safety)
 run externalRefused = init.then(selectProvider(External)).then(refuseExternal).expect(s.setup == Refused and s.uncertain and safety).then(launch.fail())
 // The invalid external launch is a reachable counterexample to the *proposed*
 // shortcut nsExit => cleanup; cleanup itself remains disabled.
 run externalEscapeCounterexample = init.then(selectProvider(External)).then(externalSpawn).then(setupReady).then(cancel).then(closeLife).then(observeExit).then(reap).expect(s.nsExit and s.externalAlive and s.backingHeld and not(s.clean) and safety).then(cleanup.fail())
 run directNeedsQualification = init.then(selectProvider(Direct)).then(setupReady).expect(not(s.started) and safety).then(launch.fail())
 run setupFailureClosed = init.then(selectProvider(Direct)).then(setupRefused).expect(s.uncertain and s.backingHeld and safety).then(launch.fail())
 run noExitBeforeClose = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(cancel).expect(not(s.nsExit) and safety).then(observeExit.fail())
 run callbackCancelNotRetired = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(cancel).expect(s.callbackHeld and s.callbackPending and safety).then(retireCallback.fail())
 run namespaceExitNotCallback = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(cancel).then(closeLife).then(observeExit).then(reap).expect(s.nsExit and s.callbackPending and s.backingHeld and safety).then(cleanup.fail())
 run unknownCallbackQuarantine = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(cancel).then(closeLife).then(observeExit).then(reap).then(quarantine).expect(s.uncertain and s.callbackHeld and s.backingHeld and safety).then(cleanup.fail())
 run deadlineExpired = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(cancel).then(tick).then(tick).then(tick).then(callbackDone).then(retireCallback).then(closeLife).then(observeExit).then(reap).expect(s.time == d and s.uncertain and s.backingHeld and safety).then(cleanup.fail())
 run noCleanupBeforeReap = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(cancel).then(callbackDone).then(retireCallback).then(closeLife).then(observeExit).expect(s.nsExit and not(s.reaped) and s.backingHeld and safety).then(cleanup.fail())
 // Independent positive routes start from their own prefix, never after fail().
 run qualifiedDirectLaunch = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).expect(s.started and s.callbackPending and safety)
 run exitAfterLifelineClose = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(cancel).then(closeLife).then(observeExit).expect(s.nsExit and safety)
 run callbackObservedThenRetired = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(cancel).then(callbackDone).then(retireCallback).expect(not(s.callbackPending) and not(s.callbackHeld) and safety)
 run cleanupAfterReap = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(cancel).then(callbackDone).then(retireCallback).then(closeLife).then(observeExit).then(reap).then(cleanup).expect(s.reaped and s.clean and safety)
 run partialAsyncRetainsCallback = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(partialAsyncSetup).then(cancel).then(quarantine).expect(not(s.started) and s.callbackPending and s.callbackHeld and s.backingHeld and safety).then(retireCallback.fail())
 run lateCallbackAfterQuarantine = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(partialAsyncSetup).then(cancel).then(quarantine).then(callbackDone).expect(not(s.callbackPending) and s.callbackHeld and s.backingHeld and s.uncertain and safety)
 run filterDrainPreservesReserve = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(cancel).then(drainCallback).then(drainCallback).expect(s.time == d - reserve and s.callbackPending and s.backingHeld and safety).then(drainCallback.fail())
 run reserveAllowsCustodyClosure = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(cancel).then(drainCallback).then(drainCallback).then(closeLife).then(observeExit).then(reap).expect(s.nsExit and s.reaped and s.callbackPending and s.backingHeld and safety)
 run signalNotifyRequired = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(attachSignal).then(cancel).then(disconnectSignal).expect(s.notifyPending and s.signalHeld and safety).then(retireSignal.fail())
 run delayedSignalNotify = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(attachSignal).then(cancel).then(disconnectSignal).then(quarantine).then(signalNotify).expect(s.uncertain and s.signalHeld and s.backingHeld and safety)
 run signalRetiredOnce = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(attachSignal).then(cancel).then(disconnectSignal).then(signalNotify).then(retireSignal).expect(not(s.signalHeld) and s.notifierHeld and safety).then(retireSignal.fail())
 run signalExceptionQuarantined = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(attachSignal).then(cancel).then(disconnectSignal).then(quarantine).expect(s.uncertain and s.notifyPending and s.signalHeld and s.backingHeld and safety).then(cleanup.fail())
 run activeInvocationBlocksNotify = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(attachSignal).then(enterSignal).then(enterSignal).then(cancel).then(disconnectSignal).then(leaveSignal).expect(s.signalActive == 1 and s.notifyPending and s.signalHeld and safety).then(signalNotify.fail())
 run activeInvocationDrainsBeforeNotify = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(attachSignal).then(enterSignal).then(enterSignal).then(cancel).then(disconnectSignal).then(leaveSignal).then(leaveSignal).then(signalNotify).then(retireSignal).expect(s.signalActive == 0 and not(s.signalHeld) and s.notifierHeld and safety)
 run disconnectRefusesNewInvocation = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(attachSignal).then(enterSignal).then(cancel).then(disconnectSignal).expect(s.signalActive == 1 and s.notifyPending and safety).then(enterSignal.fail())
 run failedReleaseCannotRetry = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(attachSignal).then(cancel).then(disconnectSignal).then(signalNotify).then(signalReleaseFailed).expect(s.uncertain and s.signalHeld and s.notifierHeld and s.backingHeld and safety).then(retireSignal.fail())
 run notifierNotProcessRetirement = init.then(selectProvider(Direct)).then(qualifyDirect).then(setupReady).then(launch).then(attachSignal).then(cancel).then(disconnectSignal).then(signalNotify).then(retireSignal).expect(s.notifierHeld and not(s.nsExit) and not(s.reaped) and s.backingHeld and safety).then(cleanup.fail())
 // Exercise the exact guided scheduler, including signal disconnect while an
 // invocation is active; the notifier remains owned for process lifetime.
 run guidedSignalClean = init
   .then(cleanConversationStep).then(cleanConversationStep).then(cleanConversationStep)
   .then(cleanConversationStep).then(cleanConversationStep).then(cleanConversationStep)
   .expect(s.signalConnected and s.signalActive == 1 and s.signalHeld and s.notifierHeld)
   .then(cleanConversationStep).then(cleanConversationStep)
   .expect(not(s.signalConnected) and s.signalActive == 1 and s.notifyPending and s.signalHeld)
   .then(cleanConversationStep).then(cleanConversationStep).then(cleanConversationStep)
   .then(cleanConversationStep)
   .then(cleanConversationStep).then(cleanConversationStep).then(cleanConversationStep)
   .then(cleanConversationStep).then(cleanConversationStep)
   .expect(s.clean and s.nsExit and s.reaped and s.notifyDelivered and s.notifierHeld and
     not(s.signalHeld) and not(s.signalConnected) and not(s.notifyPending) and
     s.signalActive == 0 and safety)
}
