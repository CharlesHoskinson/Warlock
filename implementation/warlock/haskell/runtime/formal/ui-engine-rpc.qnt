// PREPARATION DRAFT: proposed broker/exec-PID1 split, not an as-built model,
// implementation, sampled result, native evidence, or original acceptance.
// Correspondence to existing source is limited: Ui.Owner owns origin/absolute
// deadline, request handling and ownerEvent failure; Ui.Native owns native
// forwarding; EngineCustody owns engine process custody. The broker RPC and
// isolated PID1 architecture below are proposed requirements, not present code.
// Abstract finite identities stand for a kernel-verified SCM credential AND a
// held pidfd tied to the actual spawned engine, not caller-supplied JSON/PID.
// FD transfer, cryptographic framing, clocks, payload contents, namespaces,
// compositor, HTTP and actual process reaping are not modeled or proved.
module ui_engine_rpc {
  type Method = Stop | Remaining | LastProjection | Topology | Dismiss | Escape | Reflow | Other
  type State = {
    origins: List[int], deadline: int, incarnation: int,
    spawned: bool, heldExec: bool, credential: bool, pidfd: bool,
    execReady: bool, providerReady: bool, poisoned: bool,
    pending: bool, replyReady: bool, pendingId: int, pendingMethod: Method, lastId: int, completedId: int,
    admitted: int, responses: int, readCalls: int, ownerEventAttempts: int,
    nativeWindowEffects: int, callbackReads: int, viewResolved: bool,
    staleViews: int, acceptedViews: int, ownerFailed: bool, expired: bool,
    oneReaper: bool, engineReaped: bool, callbacksJoined: bool,
    namespaceGone: bool, wholeCleanup: bool
  }
  var s: State

  // Distinct abstract origins encode three immutable initialization bindings;
  // 100 is one original absolute monotonic D, never renewed by reconnect.
  pure val initialOrigins = List(1, 2, 3)
  pure val originalD = 100
  pure def allowed(m: Method): bool = Set(Stop, Remaining, LastProjection, Topology, Dismiss, Escape, Reflow).contains(m)
  pure def ownerEvent(m: Method): bool = Set(Topology, Dismiss, Escape, Reflow).contains(m)
  action init: bool = s' = {origins: initialOrigins, deadline: originalD, incarnation: 1,
    spawned: false, heldExec: false, credential: false, pidfd: false,
    execReady: false, providerReady: false, poisoned: false,
    pending: false, replyReady: false, pendingId: 0, pendingMethod: Other, lastId: 0, completedId: 0,
    admitted: 0, responses: 0, readCalls: 0, ownerEventAttempts: 0,
    nativeWindowEffects: 0, callbackReads: 0, viewResolved: true,
    staleViews: 0, acceptedViews: 0, ownerFailed: false, expired: false,
    oneReaper: true, engineReaped: false, callbacksJoined: false,
    namespaceGone: false, wholeCleanup: false}

  // The actual child is held before exec until broker-owned custody is installed.
  // One reaper is an explicit environmental ownership assumption in this model.
  action spawnHeld: bool = all {not(s.spawned), not(s.poisoned), s' = {...s, spawned: true, heldExec: true}}
  action bindPeer(scmActual: bool, heldPidfdActual: bool): bool = all {
    s.spawned, s.heldExec, not(s.execReady), not(s.poisoned),
    if (scmActual and heldPidfdActual)
      s' = {...s, credential: true, pidfd: true}
    else s' = {...s, poisoned: true, heldExec: false}
  }
  action releaseExec: bool = all {s.heldExec, s.credential, s.pidfd, not(s.poisoned), s' = {...s, heldExec: false}}
  // Exec success is not provider readiness; each observation is distinct.
  action observeExec: bool = all {s.spawned, not(s.heldExec), s.credential, s.pidfd, not(s.poisoned), not(s.execReady), s' = {...s, execReady: true}}
  action observeProvider: bool = all {s.execReady, not(s.poisoned), not(s.providerReady), s' = {...s, providerReady: true}}

  // One request total may be outstanding. Frame integrity covers exact keys,
  // bounded length, typed payload and complete parse. Every invalid/stale,
  // foreign, duplicated or unsupported request poisons, rather than replays.
  // IDs are contiguous from 1; 7 abstracts the Word64 limit. Exhaustion is
  // terminal for admission: it cannot wrap to 0 or restart an incarnation.
  action request(id: int, method: Method, frame: bool, peer: bool, session: int): bool = all {
    s.execReady, not(s.poisoned),
    if (not(frame) or not(peer) or session != s.incarnation or not(allowed(method)) or
        s.pending or s.lastId == 7 or id != s.lastId + 1)
      s' = {...s, poisoned: true, pending: false, replyReady: false}
    else s' = {...s, pending: true, pendingId: id, pendingMethod: method, lastId: id,
      viewResolved: not(ownerEvent(method)), admitted: s.admitted + 1,
      readCalls: s.readCalls + (if (ownerEvent(method)) 0 else 1),
      ownerEventAttempts: s.ownerEventAttempts + (if (ownerEvent(method)) 1 else 0)}
  }
  // Ui.Owner.ownerEvent routes GUI facts into the controller queue. Stale view
  // refusal is distinct from invalid owner input and RPC framing failure. This
  // reduced disposition models that boundary, not payload/queue validation.
  action viewDisposition(current: bool, valid: bool): bool = all {
    s.pending, ownerEvent(s.pendingMethod), not(s.viewResolved), not(s.poisoned),
    if (s.expired or s.ownerFailed) s' = {...s, viewResolved: true}
    else if (not(valid) or (not(current) and s.pendingMethod == Topology)) s' = {...s, viewResolved: true, ownerFailed: true}
    else if (not(current)) s' = {...s, viewResolved: true, staleViews: s.staleViews + 1}
    else s' = {...s, viewResolved: true, acceptedViews: s.acceptedViews + 1}
  }
  // Time is abstracted as a one-way observation of the unchanged original D.
  action deadlineReached: bool = all {not(s.expired), s' = {...s, expired: true}}
  // No method grants a native-window effect: queueing GUI facts and reads are
  // not compositor authority. Unknown send never authorizes a replay.
  action response(id: int, method: Method, frame: bool, peer: bool, session: int): bool = all {
    s.execReady, not(s.poisoned),
    if (not(frame) or not(peer) or session != s.incarnation or not(s.pending) or s.replyReady or id != s.pendingId or method != s.pendingMethod)
      s' = {...s, poisoned: true, pending: false, replyReady: false}
    else all {s.viewResolved, s' = {...s, replyReady: true}}
  }
  // A constructed reply is not a sent reply. Uncertain send takes eof/poison;
  // no subsequent request is admitted while the reply is still being sent.
  action confirmReplySent: bool = all {s.pending, s.replyReady, not(s.poisoned),
    s' = {...s, pending: false, replyReady: false, completedId: s.pendingId, responses: s.responses + 1}}
  action eof: bool = all {s.spawned, not(s.poisoned), s' = {...s, poisoned: true, pending: false, replyReady: false}}
  // Callbacks are broker-originated observations, never raw native events or a
  // reverse RPC that grants engine authority or invokes native mutation.
  action readOnlyCallback(valid: bool): bool = all {s.providerReady, not(s.poisoned),
    if (valid) s' = {...s, callbackReads: s.callbackReads + 1}
    else s' = {...s, poisoned: true, pending: false, replyReady: false}}
  action reap: bool = all {s.spawned, s.oneReaper, not(s.engineReaped), s' = {...s, engineReaped: true, poisoned: true, pending: false, replyReady: false}}
  action joinCallbacks: bool = all {s.engineReaped, not(s.callbacksJoined), s' = {...s, callbacksJoined: true}}
  action removeNamespace: bool = all {s.engineReaped, not(s.namespaceGone), s' = {...s, namespaceGone: true}}
  action finishCleanup: bool = all {s.engineReaped, s.callbacksJoined, s.namespaceGone, not(s.wholeCleanup), s' = {...s, wholeCleanup: true}}

  val safety = s.origins == initialOrigins and s.deadline == originalD and s.incarnation == 1 and
    (s.execReady implies s.spawned and s.credential and s.pidfd and not(s.heldExec)) and
    (s.providerReady implies s.execReady) and
    (s.pending implies s.execReady and not(s.poisoned) and s.pendingId == s.lastId and s.pendingId > s.completedId) and
    (s.replyReady implies s.pending) and
    s.completedId <= s.lastId and s.lastId <= 7 and s.responses <= s.admitted and
    s.readCalls + s.ownerEventAttempts == s.admitted and s.nativeWindowEffects == 0 and
    s.staleViews + s.acceptedViews <= s.ownerEventAttempts and
    (s.wholeCleanup implies s.engineReaped and s.callbacksJoined and s.namespaceGone and s.oneReaper)
  val witnessRequestResponse = s.responses > 0
  val witnessOwnerEvent = s.acceptedViews > 0
  val witnessStaleView = s.staleViews > 0
  val witnessDeadline = s.expired
  val witnessCallback = s.callbackReads > 0
  val witnessPoison = s.poisoned
  val witnessCleanup = s.wholeCleanup
  // Seven methods remain available at every actual next ID. The extra branches
  // are adversarial traffic; they must never replace the positive choices.
  action step: bool = any {spawnHeld, bindPeer(true, true), bindPeer(false, true), bindPeer(true, false),
    releaseExec, observeExec, observeProvider,
    request(s.lastId + 1, Stop, true, true, 1), request(s.lastId + 1, Remaining, true, true, 1),
    request(s.lastId + 1, LastProjection, true, true, 1), request(s.lastId + 1, Topology, true, true, 1),
    request(s.lastId + 1, Dismiss, true, true, 1), request(s.lastId + 1, Escape, true, true, 1),
    request(s.lastId + 1, Reflow, true, true, 1), request(s.lastId + 1, Other, true, true, 1),
    request(1, Stop, false, true, 1), request(1, Stop, true, false, 1),
    request(1, Stop, true, true, 2), request(s.lastId, Stop, true, true, 1),
    response(s.pendingId, s.pendingMethod, true, true, 1),
    response(s.pendingId, Other, true, true, 1),
    response(1, Stop, false, true, 1), response(1, Stop, true, false, 1),
    response(1, Stop, true, true, 2),
    viewDisposition(true, true), viewDisposition(false, true), viewDisposition(true, false), deadlineReached,
    confirmReplySent, eof, readOnlyCallback(true), readOnlyCallback(false), reap, joinCallbacks, removeNamespace, finishCleanup}
  // A separate coverage driver uses the same init/actions and omits only
  // hostile traffic; it does not replace broad step or establish liveness.
  action guidedRequest(m: Method): bool = all {not(s.pending), s.lastId < 7, request(s.lastId + 1, m, true, true, 1)}
  action guidedConversationStep: bool =
    if (not(s.spawned)) spawnHeld
    else if (s.heldExec and not(s.credential)) bindPeer(true, true)
    else if (s.heldExec) releaseExec
    else if (not(s.execReady)) observeExec
    else if (not(s.providerReady)) observeProvider
    else if (s.callbackReads == 0) readOnlyCallback(true)
    else any {
    guidedRequest(Stop), guidedRequest(Remaining), guidedRequest(LastProjection), guidedRequest(Topology),
    guidedRequest(Dismiss), guidedRequest(Escape), guidedRequest(Reflow), viewDisposition(true, true),
    all {s.pendingMethod != Topology, viewDisposition(false, true)},
    all {s.pending, s.viewResolved, not(s.replyReady), response(s.pendingId, s.pendingMethod, true, true, 1)}, confirmReplySent,
    all {s.responses > 0 and s.acceptedViews > 0, reap}, joinCallbacks, removeNamespace, finishCleanup}
}
