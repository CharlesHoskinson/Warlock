// ARC024/DEL014 bounded contract, not runtime, kernel, original or native proof.
// Source: ui/Main.hs startCustody before owner, then abandonCustody; EngineCustody
// startCustody/stopCustody/cleanupIssues; WebKit checkEnvironment, compileFilter,
// runWebKitInternal. productionCleanupFacts currently leaves callback/provider
// unqualified: this model's positive path is a contract, not a present receipt.
//
// Linux unshare(CLONE_NEWPID) leaves caller PID unchanged, places subsequent
// children in new namespace, first child PID1. Kernel terminates namespace tasks
// on PID1 death. Correct kernel behavior, exact direct-spawn provider confinement,
// stable owned child/pidfd and trustworthy callback-completion observation are
// external premises requiring source/runtime qualification, not modeled proofs.
// The direct provider branch is a nondeterministic abstract evidence input;
// excluding unsupported external Flatpak routing does not establish all other
// provider variants. One external helper witnesses escape; one pending callback
// summarizes all callbacks. D=3 and reserve=1 express ordering only, not real
// microseconds. The reserve is the proposed filter-drain contract; the original
// owner deadline and the actual stopCustody margin remain authoritative.
module ui_engine_lifetime {
  type Provider = Unchecked | Direct | External
  type Setup = NotStarted | Ready | Refused
  type State = { provider: Provider, qualified: bool, setup: Setup, started: bool,
    externalAlive: bool, stopping: bool, time: int, lifeOpen: bool, pidfd: bool,
    owned: bool, nsExit: bool, reaped: bool, callbackPending: bool,
    cancelRequested: bool, callbackHeld: bool, signalConnected: bool,
    notifyPending: bool, notifyDelivered: bool, signalActive: int,
    signalHeld: bool, notifierHeld: bool, backingHeld: bool,
    uncertain: bool, clean: bool }
  var s: State
  pure val d = 3
  pure val reserve = 1
  action init: bool = s' = {provider: Unchecked, qualified: false, setup: NotStarted,
    started: false, externalAlive: false, stopping: false, time: 0, lifeOpen: false,
    pidfd: false, owned: false, nsExit: false, reaped: false, callbackPending: false,
    cancelRequested: false, callbackHeld: false, signalConnected: false,
    notifyPending: false, notifyDelivered: false, signalActive: 0,
    signalHeld: false, notifierHeld: false, backingHeld: true,
    uncertain: false, clean: false}
  // Provider selection and qualification abstract observations made outside the
  // model; an unsupported external provider is refused, not universally supported.
  action selectProvider(p: Provider): bool = all {s.provider == Unchecked, p != Unchecked,
    s' = {...s, provider: p}}
  action qualifyDirect: bool = all {s.provider == Direct, not(s.started),
    s.setup == NotStarted, s' = {...s, qualified: true}}
  action refuseExternal: bool = all {s.provider == External, s.setup == NotStarted,
    s' = {...s, setup: Refused, uncertain: true}}
  // Adversarial observation, showing what local namespace exit cannot establish.
  // This is not an authorized launch path; it represents an escaped provider.
  action externalSpawn: bool = all {s.provider == External, not(s.externalAlive),
    s' = {...s, externalAlive: true}}
  action setupReady: bool = all {s.setup == NotStarted, s.provider != Unchecked,
    s' = {...s, setup: Ready, pidfd: true, owned: true, lifeOpen: true}}
  action setupRefused: bool = all {s.setup == NotStarted,
    s' = {...s, setup: Refused, uncertain: true}}
  action launch: bool = all {s.setup == Ready, s.provider == Direct, s.qualified,
    not(s.started), not(s.callbackPending), not(s.callbackHeld), not(s.uncertain), s' = {...s, started: true,
      callbackPending: true, callbackHeld: true}}
  // Conservative partial async setup: a callback may already have escaped even
  // though the complete engine launch did not return. Its owner is retained.
  action partialAsyncSetup: bool = all {s.setup == Ready, s.provider == Direct,
    s.qualified, not(s.started), not(s.callbackPending), not(s.callbackHeld), not(s.uncertain),
    s' = {...s, callbackPending: true, callbackHeld: true}}
  action cancel: bool = all {s.setup == Ready, not(s.stopping),
    s' = {...s, stopping: true, cancelRequested: true}}
  action callbackDone: bool = all {s.callbackPending,
    s' = {...s, callbackPending: false}}
  action retireCallback: bool = all {s.stopping, not(s.callbackPending), s.callbackHeld,
    s' = {...s, callbackHeld: false}}
  // connectOwnedSignal: disconnection requests retirement; GLib finalizer
  // notification occurs after all active invocations, then attempts callback
  // release. We split notification and release to expose failure interleavings;
  // signalHeld after a failed release means release is *uncertified*, not that
  // the pointer is definitely still callable. The notifier itself is retained
  // for process lifetime, independent of local callback and namespace cleanup.
  action attachSignal: bool = all {s.started, not(s.stopping), not(s.signalHeld),
    s' = {...s, signalConnected: true, signalHeld: true, notifierHeld: true}}
  action enterSignal: bool = all {s.signalConnected, s.signalActive < 2,
    s' = {...s, signalActive: s.signalActive + 1}}
  action leaveSignal: bool = all {s.signalActive > 0,
    s' = {...s, signalActive: s.signalActive - 1}}
  action disconnectSignal: bool = all {s.stopping, s.signalConnected,
    s' = {...s, signalConnected: false, notifyPending: true}}
  action signalNotify: bool = all {s.notifyPending, s.signalActive == 0,
    s' = {...s, notifyPending: false, notifyDelivered: true}}
  action retireSignal: bool = all {s.stopping, s.signalHeld, not(s.signalConnected),
    s.notifyDelivered, not(s.notifyPending), s.signalActive == 0,
    s' = {...s, signalHeld: false}}
  action signalReleaseFailed: bool = all {s.notifyDelivered, s.signalHeld,
    not(s.uncertain), s' = {...s, notifyDelivered: false, uncertain: true}}
  action closeLife: bool = all {s.stopping, s.lifeOpen,
    s' = {...s, lifeOpen: false}}
  // Abstract receipt from owned pidfd after close/targeted termination; no raw PID.
  action observeExit: bool = all {s.stopping, not(s.lifeOpen), s.pidfd, s.owned,
    not(s.nsExit), s' = {...s, nsExit: true}}
  action reap: bool = all {s.nsExit, s.owned, not(s.reaped),
    s' = {...s, reaped: true}}
  action quarantine: bool = all {not(s.clean), not(s.uncertain),
    s' = {...s, uncertain: true}}
  // Draining is optional progress while preserving a teardown reserve. Time
  // can independently elapse via tick; neither action proves callback delivery.
  action drainCallback: bool = all {s.stopping, s.callbackPending, not(s.uncertain),
    s.time + 1 <= d - reserve, s' = {...s, time: s.time + 1}}
  action tick: bool = all {s.stopping, s.time < d, not(s.clean),
    s' = {...s, time: s.time + 1, uncertain: s.uncertain or s.time + 1 == d}}
  action cleanup: bool = all {s.stopping, s.setup == Ready, s.started,
    s.provider == Direct, s.qualified, not(s.externalAlive), s.owned, s.pidfd,
    s.nsExit, s.reaped, not(s.callbackPending), not(s.callbackHeld),
    not(s.signalConnected), not(s.notifyPending), s.signalActive == 0, not(s.signalHeld),
    not(s.uncertain), s.time < d, s' = {...s, backingHeld: false, clean: true}}
  val noUaf = (s.callbackPending implies s.callbackHeld and s.backingHeld) and
    ((s.signalConnected or s.notifyPending or s.signalActive > 0) implies
      s.signalHeld and s.notifierHeld and s.backingHeld) and
    (s.externalAlive implies s.backingHeld)
  val noFalseCleanup = s.clean implies s.setup == Ready and s.started and
    s.provider == Direct and s.qualified and not(s.externalAlive) and s.owned and
    s.pidfd and s.nsExit and s.reaped and not(s.callbackPending) and not(s.callbackHeld) and
    not(s.signalConnected) and not(s.notifyPending) and s.signalActive == 0 and not(s.signalHeld)
  val noArbitraryPid = s.nsExit implies s.pidfd and s.owned
  val deadlineSafety = s.clean implies s.time < d
  val safety = noUaf and noFalseCleanup and noArbitraryPid and
    deadlineSafety and (s.uncertain implies not(s.clean) and s.backingHeld)
  val witnessReady = s.setup == Ready
  val witnessRefused = s.setup == Refused
  val witnessExternal = s.externalAlive and s.nsExit and not(s.clean)
  val witnessExit = s.nsExit
  val witnessCallbackRetired = s.started and not(s.callbackHeld)
  val witnessClean = s.clean
  val witnessQuarantine = s.uncertain
  val witnessDeadline = s.time == d
  val witnessPartialAsync = s.callbackPending and not(s.started)
  action step: bool = any {selectProvider(Direct), selectProvider(External), qualifyDirect,
    refuseExternal, externalSpawn, setupReady, setupRefused, launch, partialAsyncSetup,
    cancel, callbackDone, retireCallback, attachSignal, enterSignal, leaveSignal,
    disconnectSignal, signalNotify, retireSignal, signalReleaseFailed, closeLife, observeExit, reap, quarantine,
    drainCallback, tick, cleanup}
  // A separate guided conversation exercises the same guarded transitions for
  // positive reachability. It excludes failures and time elapse by design and
  // is not a substitute for the broad step or evidence that real teardown meets
  // D. Keep the broad sample, including any zero clean count, reported intact.
  action cleanConversationStep: bool =
    if (s.provider == Unchecked) selectProvider(Direct)
    else if (not(s.qualified)) qualifyDirect
    else if (s.setup == NotStarted) setupReady
    else if (not(s.started)) launch
    else if (not(s.notifierHeld)) attachSignal
    else if (not(s.stopping) and s.signalActive == 0) enterSignal
    else if (not(s.stopping)) cancel
    else if (s.signalConnected) disconnectSignal
    else if (s.signalActive > 0) leaveSignal
    else if (s.notifyPending) signalNotify
    else if (s.signalHeld) retireSignal
    else if (s.callbackPending) callbackDone
    else if (s.callbackHeld) retireCallback
    else if (s.lifeOpen) closeLife
    else if (not(s.nsExit)) observeExit
    else if (not(s.reaped)) reap
    else if (not(s.clean)) cleanup
    else s' = s
}
