// PREPARATION DRAFT ONLY. Proposed broker/exec-PID1 contract, not current code,
// not a kernel, provider, runtime, native, or original-scenario proof.
// Correspondence: runtime/ui/Main.hs retains fd0 and owns the native protocol;
// Warlock/Ui/EngineCustody.hsc owns child/pidfd/lifeline; WebKit.hs owns GTK,
// async callbacks and signals; Warlock/Ui/ThreadNamespace.hs rejects unreadable
// or unequal current/for-children PID namespaces before GTK. Existing source
// does not yet implement this split. Compare ui-engine-lifetime.qnt separately.
//
// Finite abstraction: one broker, one engine incarnation, one helper class,
// one in-flight authenticated fragment and at most two active callbacks.
// D=3 records deadline ordering only, not a replacement for original D.
// Time advances from initial startup, never resets or starts afresh at stop. No retry or second engine incarnation is represented.
// A fragment is represented by its *observed* kernel SCM credentials, not
// pre-fork SO_PEERCRED. PID translation, uid/gid mapping, ancillary data and
// pinned executable/image identity must be independently established. `good`
// means all of those checks succeeded for this exact owned child incarnation.
// Final callback admission rechecks live custody and serializes with retirement;
// the atomic action is a proposed synchronization contract, not a kernel proof.
// Namespace/kernel termination, single waitpid owner, parent-death delivery,
// sole lifeline writer, held executable/loader compatibility, provider helper
// confinement and callback notifications are external implementation premises;
// actions represent observations and do not establish those premises.
//
// This small two-role shared-observation abstraction intentionally does not use
// Choreo: it checks lifecycle races, rather than a general RPC transport. The
// fragments have one outstanding operation because correlation is in a peer
// model. Separate actions preserve the relevant fork/exec/death, notification,
// and teardown interleavings; no arbitrary PID, group signal, or replay action.
module ui_engine_topology {
  type Namespace = Original | ChildNs | UnknownNs
  type Launch = Absent | Held | Executed | Exited
  type SignalTarget = NoSignal | OwnedPidfd
  type State = {
    brokerAlive: bool, brokerFd0: bool, privateNet: bool, brokerGtk: bool,
    brokerCurrent: Namespace, brokerChildren: Namespace,
    engineCurrent: Namespace, engineChildren: Namespace, enginePid1: bool,
    launch: Launch, imageHeld: bool, owned: bool, pidfd: bool,
    execReleased: bool, deathRegistered: bool, deathArmedBeforeLoss: bool,
    deathObserved: bool, pidfdSent: bool, signalTarget: SignalTarget,
    unrelatedAlive: bool, reapCount: int,
    lifeWriter: bool, escapedWriter: bool, lifeEof: bool,
    gtk: bool, helperAlive: bool, externalAlive: bool, providerQualified: bool,
    badFragment: bool, validFragment: bool, readonlyCallbacks: int,
    callbackPending: bool, callbackActive: int, callbackHeld: bool,
    connected: bool, notifyPending: bool, notifyDelivered: bool,
    notifierHeld: bool, backingHeld: bool,
    stop: bool, poisoned: bool, quarantine: bool, nsExit: bool,
    reaped: bool, visible: bool, clean: bool, time: int
  }
  var s: State
  pure val deadline = 3
  action init: bool = s' = {
    brokerAlive: true, brokerFd0: true, privateNet: true, brokerGtk: false,
    brokerCurrent: Original, brokerChildren: Original,
    engineCurrent: UnknownNs, engineChildren: UnknownNs, enginePid1: false,
    launch: Absent, imageHeld: false, owned: false, pidfd: false,
    execReleased: false, deathRegistered: false, deathArmedBeforeLoss: false,
    deathObserved: false, pidfdSent: false, signalTarget: NoSignal,
    unrelatedAlive: true, reapCount: 0,
    lifeWriter: false, escapedWriter: false, lifeEof: false,
    gtk: false, helperAlive: false, externalAlive: false, providerQualified: false,
    badFragment: false, validFragment: false, readonlyCallbacks: 0,
    callbackPending: false, callbackActive: 0, callbackHeld: false,
    connected: false, notifyPending: false, notifyDelivered: false,
    notifierHeld: false, backingHeld: true,
    stop: false, poisoned: false, quarantine: false, nsExit: false,
    reaped: false, visible: false, clean: false, time: 0
  }
  // Existing unshare affects caller's children, not its own thread namespace.
  action unshareForChildren: bool = all {s.brokerAlive, not(s.stop), s.time < deadline, s.launch == Absent,
    s.brokerChildren == Original, s' = {...s, brokerChildren: ChildNs}}
  // At this point the existing fail-closed guard cannot admit GTK on broker.
  // Fail closed on unreadable/equal unknown values as the production guard does.
  pure def namespaceCompatible(current: Namespace, children: Namespace): bool =
    current != UnknownNs and children != UnknownNs and current == children
  val brokerGuardAllowsGtk = namespaceCompatible(s.brokerCurrent, s.brokerChildren)
  action pinImage: bool = all {s.brokerAlive, not(s.stop), s.time < deadline,
    s.launch == Absent, not(s.imageHeld),
    s' = {...s, imageHeld: true}}
  // Kernel first child of new PID namespace; engine is held before exec so the
  // broker can capture exact ownership/pidfd. No native fd0 or listener transfer.
  action spawnHeld: bool = all {s.brokerAlive, not(s.stop), s.time < deadline,
    s.brokerChildren == ChildNs,
    s.imageHeld, s.launch == Absent,
    s' = {...s, launch: Held, engineCurrent: ChildNs, engineChildren: ChildNs,
      enginePid1: true, owned: true, lifeWriter: true}}
  action capturePidfd: bool = all {s.brokerAlive, s.launch == Held, s.owned,
    not(s.pidfd), s' = {...s, pidfd: true}}
  action registerParentDeath: bool = all {s.launch == Held, not(s.deathRegistered),
    s' = {...s, deathRegistered: true, deathArmedBeforeLoss: s.brokerAlive}}
  // This observation may occur even before PDEATHSIG registration. A caller's
  // getppid()==0 inside the child namespace is not modeled as death evidence.
  action brokerDies: bool = all {s.brokerAlive,
    s' = {...s, brokerAlive: false, lifeWriter: false}}
  // An escaped duplicate writer is an adversarial premise violation; closing the
  // broker writer alone must not generate EOF while that writer remains open.
  action leakWriter: bool = all {s.launch == Held, s.lifeWriter, not(s.escapedWriter),
    s' = {...s, escapedWriter: true}}
  action closeEscapedWriter: bool = all {s.escapedWriter,
    s' = {...s, escapedWriter: false}}
  action observeLifeEof: bool = all {s.launch != Absent, not(s.lifeWriter),
    not(s.escapedWriter), not(s.lifeEof), s' = {...s, lifeEof: true}}
  // Abstract kernel notification only when registration preceded death.
  action observeParentSignal: bool = all {not(s.brokerAlive), s.deathArmedBeforeLoss,
    not(s.deathObserved), s' = {...s, deathObserved: true}}
  // Startup is admitted only with sole writer, registered notification and a
  // live broker at release. Death can still race the following exec.
  action releaseExec: bool = all {s.brokerAlive, s.launch == Held, s.owned,
    s.pidfd, s.imageHeld, s.deathRegistered, s.lifeWriter, not(s.escapedWriter),
    not(s.poisoned), not(s.quarantine), s.time < deadline,
    s' = {...s, execReleased: true}}
  action execEngine: bool = all {s.launch == Held, s.execReleased, s.brokerAlive,
    not(s.lifeEof), not(s.poisoned), not(s.quarantine), s.time < deadline,
    s' = {...s, launch: Executed}}
  // Provider evidence is a conditional qualification input, not inferred from
  // process placement or an asserted Boolean as proof of the real provider.
  action qualifyProvider: bool = all {s.launch == Executed, not(s.providerQualified), not(s.externalAlive),
    s' = {...s, providerQualified: true}}
  // Adversarial unsupported external-provider observation: a helper outside
  // the child namespace survives local namespace exit; this is not an admitted
  // launch branch or a universal Flatpak support requirement.
  action externalSpawn: bool = all {s.launch == Executed, not(s.providerQualified),
    not(s.externalAlive), s' = {...s, externalAlive: true}}
  action gtkStart: bool = all {s.launch == Executed, s.enginePid1,
    namespaceCompatible(s.engineCurrent, s.engineChildren),
    s.providerQualified, not(s.gtk), not(s.stop), not(s.poisoned),
    not(s.quarantine), s.time < deadline,
    s' = {...s, gtk: true, helperAlive: true, callbackPending: true,
      callbackHeld: true, connected: true, notifierHeld: true}}
  // Visibility is not a cleanup receipt. Existing production facts can both
  // remain false while the UI is visible.
  action showMvp: bool = all {s.gtk, not(s.visible), not(s.stop),
    s' = {...s, visible: true}}
  // One received frame, one verification. Bad identity poisons without invoking
  // any owner callback; authenticated read-only observations cannot mutate the
  // broker's native authority or the cleanup/deadline facts.
  action receiveGoodFragment: bool = all {s.launch == Executed, s.brokerAlive,
    not(s.stop), not(s.poisoned), not(s.validFragment),
    s' = {...s, validFragment: true}}
  action receiveBadFragment: bool = all {s.launch == Executed, s.brokerAlive,
    not(s.stop), not(s.poisoned), s' = {...s, badFragment: true,
      poisoned: true, quarantine: true, stop: true}}
  action readonlyCallback: bool = all {s.validFragment, not(s.poisoned), not(s.stop),
    s.brokerAlive, s.owned, s.pidfd, s.launch == Executed, not(s.nsExit),
    s.time < deadline, s.readonlyCallbacks < 2, s' = {...s, validFragment: false,
      readonlyCallbacks: s.readonlyCallbacks + 1}}
  action requestStop: bool = all {s.launch != Absent, not(s.stop),
    s' = {...s, stop: true, lifeWriter: false}}
  action detectParentLoss: bool = all {s.launch != Absent, not(s.stop),
    (s.lifeEof or s.deathObserved), s' = {...s, stop: true, quarantine: true}}
  // pidfdStop is an owned target request, not exit/reap or helper retirement.
  action pidfdStop: bool = all {s.stop, s.owned, s.pidfd, s.launch != Exited,
    not(s.pidfdSent), s' = {...s, pidfdSent: true, signalTarget: OwnedPidfd}}
  // Namespace exit and callback retirement are independent observations. Helper
  // containment is qualified separately; escaped external helpers are outside
  // this bounded direct-provider branch, and must never be inferred dead here.
  action observeNsExit: bool = all {s.stop, s.owned, s.pidfd, not(s.nsExit),
    (s.pidfdSent or s.deathObserved or s.lifeEof),
    s' = {...s, nsExit: true, launch: Exited, helperAlive: false}}
  // Child can die without a prior stop request while a fragment is pending.
  // Discovery is an owned pidfd observation; the broker quarantines the pending
  // request as unknown and must not admit it later or replay it.
  action observeUnexpectedExit: bool = all {s.brokerAlive, s.owned, s.pidfd,
    s.launch == Executed, not(s.stop), not(s.nsExit),
    s' = {...s, nsExit: true, launch: Exited, helperAlive: false,
      stop: true, lifeWriter: false, quarantine: true}}
  // Only broker's custody owner reaps this exact direct child; no second waiter.
  action reapOwned: bool = all {s.brokerAlive, s.owned, s.pidfd, s.nsExit,
    not(s.reaped), s.reapCount == 0, s' = {...s, reaped: true, reapCount: 1}}
  action enterCallback: bool = all {s.connected, s.callbackHeld, s.callbackActive < 2,
    s' = {...s, callbackActive: s.callbackActive + 1}}
  action leaveCallback: bool = all {s.callbackActive > 0,
    s' = {...s, callbackActive: s.callbackActive - 1}}
  action callbackComplete: bool = all {s.callbackPending,
    s' = {...s, callbackPending: false}}
  action disconnectSignal: bool = all {s.stop, s.connected,
    s' = {...s, connected: false, notifyPending: true}}
  action notifyFinalizer: bool = all {s.notifyPending, s.callbackActive == 0,
    s' = {...s, notifyPending: false, notifyDelivered: true}}
  action retireCallback: bool = all {s.stop, s.callbackHeld, not(s.callbackPending),
    not(s.connected), not(s.notifyPending), s.notifyDelivered, s.callbackActive == 0,
    s' = {...s, callbackHeld: false}}
  action tick: bool = all {s.time < deadline, not(s.clean),
    s' = {...s, time: s.time + 1,
      stop: s.stop or s.time + 1 == deadline,
      lifeWriter: s.lifeWriter and s.time + 1 < deadline,
      quarantine: s.quarantine or s.time + 1 == deadline}}
  action unknownCallback: bool = all {s.stop, s.callbackHeld, not(s.quarantine),
    s' = {...s, quarantine: true}}
  action cleanup: bool = all {s.stop, s.brokerAlive, s.owned, s.pidfd,
    s.nsExit, s.reaped, s.providerQualified, not(s.helperAlive), not(s.externalAlive),
    not(s.callbackPending), not(s.callbackHeld), not(s.connected),
    not(s.notifyPending), s.callbackActive == 0, not(s.poisoned),
    not(s.quarantine), s.time < deadline,
    s' = {...s, clean: true, backingHeld: false}}
  val noBrokerGtk = not(s.brokerGtk) and s.brokerFd0 and s.privateNet
  val enginePlacement = s.gtk implies s.enginePid1 and
    s.engineCurrent == ChildNs and s.engineCurrent == s.engineChildren
  // Sentinel represents an unrelated process unaffected by modeled operations;
  // this does not model external actors or prove a real process survived.
  val unrelatedUntouched = s.unrelatedAlive
  val soleOwnedReaper = s.reapCount <= 1 and (s.reaped iff s.reapCount == 1)
  val noUnownedStop = (s.nsExit implies s.owned and s.pidfd) and
    (s.pidfdSent implies s.signalTarget == OwnedPidfd and s.owned and s.pidfd)
  val safeBacking = (s.callbackPending or s.callbackHeld or s.connected or
    s.notifyPending or s.callbackActive > 0 or s.helperAlive or s.externalAlive) implies s.backingHeld
  val noFalseClean = s.clean implies s.nsExit and s.reaped and s.providerQualified and
    not(s.helperAlive) and not(s.externalAlive) and not(s.callbackPending) and not(s.callbackHeld) and
    not(s.connected) and not(s.notifyPending) and s.callbackActive == 0 and
    not(s.quarantine) and not(s.poisoned) and s.time < deadline
  val noEarlyEof = s.lifeEof implies not(s.lifeWriter) and not(s.escapedWriter)
  val safety = noBrokerGtk and enginePlacement and noUnownedStop and unrelatedUntouched and
    soleOwnedReaper and safeBacking and
    noFalseClean and noEarlyEof and (s.quarantine implies not(s.clean))
  val witnessMismatch = s.brokerCurrent != s.brokerChildren and not(brokerGuardAllowsGtk)
  val witnessVisibleUnqualifiedCleanup = s.visible and not(s.nsExit) and not(s.clean)
  val witnessExitLateCallback = s.nsExit and s.callbackHeld and s.backingHeld and not(s.clean)
  val witnessExternalSurvives = s.nsExit and s.externalAlive and not(s.clean)
  val witnessDeathBeforeRegistration = s.launch == Held and s.owned and
    not(s.brokerAlive) and not(s.deathRegistered)
  val witnessLeakedWriter = not(s.brokerAlive) and s.escapedWriter and not(s.lifeEof)
  // State witness only: quarantine can arise for reasons other than the
  // unknownCallback action. Use the focused named trace for that action.
  val witnessUnknownQuarantine = s.quarantine and s.callbackHeld and not(s.clean)
  val witnessDeadline = s.time == deadline and s.quarantine and not(s.clean)
  val witnessClean = s.clean
  action step: bool = any {unshareForChildren, pinImage, spawnHeld, capturePidfd,
    registerParentDeath, brokerDies, leakWriter, closeEscapedWriter, observeLifeEof,
    observeParentSignal, releaseExec, execEngine, qualifyProvider, externalSpawn, gtkStart, showMvp,
    receiveGoodFragment, receiveBadFragment, readonlyCallback, requestStop,
    detectParentLoss, pidfdStop, observeNsExit, observeUnexpectedExit, reapOwned, enterCallback, leaveCallback,
    callbackComplete, disconnectSignal, notifyFinalizer, retireCallback, tick,
    unknownCallback, cleanup}

  // Conditional guided reachability only: uses the same guarded actions,
  // excludes failure and time interleavings, and does not establish liveness,
  // real teardown, or nonzero coverage by the broad step. Retain broad counts.
  action guidedCleanStep: bool =
    if (s.brokerChildren == Original) unshareForChildren
    else if (not(s.imageHeld)) pinImage
    else if (s.launch == Absent) spawnHeld
    else if (not(s.pidfd)) capturePidfd
    else if (not(s.deathRegistered)) registerParentDeath
    else if (not(s.execReleased)) releaseExec
    else if (s.launch == Held) execEngine
    else if (not(s.providerQualified)) qualifyProvider
    else if (not(s.gtk)) gtkStart
    else if (not(s.visible)) showMvp
    else if (not(s.stop)) requestStop
    else if (not(s.pidfdSent)) pidfdStop
    else if (not(s.nsExit)) observeNsExit
    else if (not(s.reaped)) reapOwned
    else if (s.callbackPending) callbackComplete
    else if (s.connected) disconnectSignal
    else if (s.notifyPending) notifyFinalizer
    else if (s.callbackHeld) retireCallback
    else if (not(s.clean)) cleanup
    else s' = s
  // Guided unsupported external-helper counterexample. It exercises the
  // unchanged adversarial transition and is not an accepted provider path.
  action guidedExternalStep: bool =
    if (s.brokerChildren == Original) unshareForChildren
    else if (not(s.imageHeld)) pinImage
    else if (s.launch == Absent) spawnHeld
    else if (not(s.pidfd)) capturePidfd
    else if (not(s.deathRegistered)) registerParentDeath
    else if (not(s.execReleased)) releaseExec
    else if (s.launch == Held) execEngine
    else if (not(s.externalAlive)) externalSpawn
    else if (not(s.stop)) requestStop
    else if (not(s.pidfdSent)) pidfdStop
    else if (not(s.nsExit)) observeNsExit
    else s' = s
  // Separately drives the specific unknownCallback action, not merely some
  // other reason the callback-held quarantine state is reachable.
  action guidedUnknownCallbackStep: bool =
    if (not(s.stop)) guidedCleanStep
    else if (not(s.quarantine)) unknownCallback
    else s' = s
}
