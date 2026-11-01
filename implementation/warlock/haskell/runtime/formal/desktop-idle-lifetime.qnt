// Component scheduling model for ELM-ARC-002 / ownership-presentation.
// Proposed desktop inter-frame scheduling, not actual code,
// kernel behavior, runtime/liveness proof, native acceptance, or a new deadline.
// Correspondence: Aggregate.hs pump and withLeaderExit; Channel.hs readGate and
// receiveCredentialFrame's existing five-second read+admission limit; ingress
// serial/retirement and credential guard. Exact API and implementation remain
// in review. No tests executed by this worker.
//
// Abstract units: one absolute original D=8, frame budget F=2; these are not
// wall-clock seconds. Time only advances, never resets. First receive and all
// native receives start F immediately. min(D,F) for these represents outer
// aggregate supervision, not local Channel enforcement or a hard scheduler
// guarantee. Only desktop AFTER one delivered frame
// waits for readiness under the SAME original D. Readiness consumes no bytes or
// ancillary data. It is a hint, not authentication, acceptance or receipt.
// One ingress serial spans idle->read->admission; the channel read gate spans
// idle->frame only and is released before dispatch. External kernel fd
// validity, wakeups, credential integrity, exact child identity, close semantics,
// and scheduler behavior remain explicit implementation premises. The model
// does not assert whole-engine/provider/backing cleanup or original acceptance.
module desktop_idle_lifetime {
  type Profile = Desktop | Native
  type Phase = First | Between | Waiting | Reading | Admitting | Callback | Ended
  type State = {profile: Profile, phase: Phase, time: int, frameStart: int, frameEnd: int,
    delivered: int, effects: int, effectThisFrame: bool, callbackAdmitted: bool,
    lastDeliveryChecked: bool,
    ingressHeld: bool, readHeld: bool, open: bool,
    leaderAlive: bool, peerWriteClosed: bool, retired: bool,
    bytesReady: bool, headerStarted: bool, bodyComplete: bool,
    credentialsMatch: bool, revoke: bool, terminalUnknown: bool,
    eofObserved: bool, timeoutObserved: bool, settled: bool}
  var s: State
  pure val d = 8
  pure val f = 2
  pure def frameDeadline(t: int): int = if (t + f < d) t + f else d
  action initialize(p: Profile): bool = s' = {profile: p, phase: First, time: 0,
    frameStart: 0, frameEnd: 0, delivered: 0, effects: 0, effectThisFrame: false, callbackAdmitted: false,
    lastDeliveryChecked: false,
    ingressHeld: false, readHeld: false, open: true,
    leaderAlive: true, peerWriteClosed: false, retired: false,
    bytesReady: false, headerStarted: false, bodyComplete: false,
    credentialsMatch: true, revoke: false, terminalUnknown: false,
    eofObserved: false, timeoutObserved: false, settled: false}
  action init: bool = initialize(Desktop)
  // The first receive is immediate in BOTH profiles, preserving existing API.
  action beginFirst: bool = all {s.phase == First, s.open, not(s.retired), s.time < d,
    s' = {...s, phase: Reading, ingressHeld: true, readHeld: true,
      frameStart: s.time, frameEnd: frameDeadline(s.time)}}
  // Native remains immediate; only the desktop inter-frame route can wait.
  action beginNativeNext: bool = all {s.profile == Native, s.phase == Between,
    s.open, not(s.retired), s.leaderAlive, s.time < d,
    s' = {...s, phase: Reading, ingressHeld: true, readHeld: true,
      frameStart: s.time, frameEnd: frameDeadline(s.time), headerStarted: false, bodyComplete: false,
      effectThisFrame: false, credentialsMatch: true}}
  action beginDesktopWait: bool = all {s.profile == Desktop, s.phase == Between,
    s.delivered > 0, s.open, not(s.retired), s.leaderAlive, s.time < d,
    s' = {...s, phase: Waiting, ingressHeld: true, readHeld: true,
      bytesReady: false, headerStarted: false, bodyComplete: false,
      effectThisFrame: false, credentialsMatch: true}}
  // Environment delivers readiness without transferring payload or credentials.
  action bytesBecomeReady: bool = all {s.phase == Waiting, s.open, not(s.bytesReady),
    s.leaderAlive, not(s.retired), s.time < d, s' = {...s, bytesReady: true}}
  action startReadyFrame: bool = all {s.phase == Waiting, s.bytesReady, s.open,
    s.ingressHeld, s.readHeld, s.leaderAlive, not(s.retired), s.time < d,
    s' = {...s, phase: Reading, frameStart: s.time, frameEnd: frameDeadline(s.time)}}
  // One header and body abstract all fragments; a mismatch is never admitted.
  action header: bool = all {s.phase == Reading, s.open, not(s.headerStarted),
    not(s.retired), s.leaderAlive, s.time < s.frameEnd,
    s' = {...s, headerStarted: true}}
  action completeBody: bool = all {s.phase == Reading, s.headerStarted,
    not(s.bodyComplete), s.open, not(s.retired), s.leaderAlive, s.time < s.frameEnd,
    s' = {...s, phase: Admitting, bodyComplete: true, readHeld: false}}
  action foreignCredential: bool = all {s.phase == Reading, s.headerStarted,
    s.open, not(s.retired), s' = {...s, credentialsMatch: false}}
  action revokeAdmission: bool = all {not(s.revoke), s' = {...s, revoke: true}}
  // Admission and callback completion are distinct: retirement may publish
  // while an already-admitted callback is still running. Effects cannot be
  // rolled back merely because the callback outcome becomes uncertain.
  // This is the gate admission/permit, not necessarily callback execution:
  // scheduling can delay the action body until after the deadline.
  action beginCallback: bool = all {s.phase == Admitting, s.open, not(s.retired),
    s.leaderAlive, not(s.revoke), s.credentialsMatch, s.time < s.frameEnd,
    s.time < d, s.ingressHeld, not(s.readHeld), s.delivered < 2,
    s' = {...s, phase: Callback, callbackAdmitted: true}}
  action applyEffect: bool = all {s.phase == Callback, not(s.effectThisFrame),
    s.effects < 2, s' = {...s, effects: s.effects + 1, effectThisFrame: true}}
  // Existing scoped and boundary gates check BEFORE dispatch, then drain an
  // admitted callback. A successful callback may finish after retirement or
  // the admission deadline; that is not an on-time cleanup receipt. Do not
  // infer a post-action guard that the source does not have.
  action admit: bool = all {s.phase == Callback, s.callbackAdmitted,
    s.ingressHeld, not(s.readHeld),
    s' = {...s, phase: Between, delivered: s.delivered + 1,
      lastDeliveryChecked: s.callbackAdmitted, callbackAdmitted: false,
      ingressHeld: false, readHeld: false, bytesReady: false}}
  // Explicit exception/cancellation outcome; elapsed time or retirement alone
  // does not prove this branch, nor does it prove a blocked callback returned.
  action callbackUncertain: bool = all {s.phase == Callback, s.callbackAdmitted,
    s' = {...s, phase: Ended, open: false, ingressHeld: false, readHeld: false,
      callbackAdmitted: false, terminalUnknown: true}}
  // The existing owned leader watcher observes exit without reaping and shuts
  // down the retained peer write end. Exit itself is not close/reap proof.
  action leaderExits: bool = all {s.leaderAlive,
    s' = {...s, leaderAlive: false}}
  action shutdownOwnedPeerWrite: bool = all {not(s.leaderAlive), not(s.peerWriteClosed),
    s' = {...s, peerWriteClosed: true}}
  action observeEof: bool = all {s.peerWriteClosed, s.open, not(s.retired),
    (s.phase == Waiting or s.phase == Reading),
    s' = {...s, phase: Ended, open: false, eofObserved: true,
      ingressHeld: false, readHeld: false}}
  // Retire may race a wait/read. Publishing retire precedes wake/join; no
  // NEW admissions after publication, and no clean receipt before active owner exits.
  action publishRetirement: bool = all {not(s.retired),
    s' = {...s, retired: true}}
  // This action abstracts a confirmed wake + cancellation/join of the active
  // reader; publishing retirement alone never supplies this receipt.
  action settleRetired: bool = all {s.retired, s.phase != Callback, not(s.settled),
    s' = {...s, phase: Ended, open: false, ingressHeld: false,
      readHeld: false, settled: true}}
  action tick: bool = all {s.time < d, s' = {...s, time: s.time + 1}}
  action frameTimeout: bool = all {(s.phase == Reading or s.phase == Admitting),
    s.time >= s.frameEnd, s.open,
    s' = {...s, phase: Ended, open: false, ingressHeld: false, readHeld: false,
      timeoutObserved: true, terminalUnknown: s.headerStarted}}
  action originalDeadline: bool = all {s.time == d, s.open, s.phase != Callback,
    s' = {...s, phase: Ended, open: false, ingressHeld: false, readHeld: false,
      timeoutObserved: true, terminalUnknown: s.headerStarted}}
  action rejectCredential: bool = all {s.phase == Admitting, not(s.credentialsMatch),
    s' = {...s, phase: Ended, open: false, ingressHeld: false, readHeld: false,
      terminalUnknown: true}}
  action rejectRevoked: bool = all {s.phase == Admitting, s.revoke,
    s' = {...s, phase: Ended, open: false, ingressHeld: false, readHeld: false,
      terminalUnknown: true}}
  val ownership = ((s.phase == Waiting or s.phase == Reading) implies s.ingressHeld and s.readHeld) and
    ((s.phase == Admitting or s.phase == Callback) implies s.ingressHeld and not(s.readHeld))
  val noReadAfterRetire = s.settled implies s.retired and not(s.open) and
    not(s.ingressHeld) and not(s.readHeld) and s.phase == Ended
  // Last successful admission records the checks at that time; current next
  // frame credentials can differ without rewriting the historical receipt.
  val noFalseReceipt = s.delivered <= 2 and (s.delivered > 0 implies s.lastDeliveryChecked)
  // The bound alone does not express a nonrenewed frame budget. While a frame
  // is active, its end remains derived from the captured start; a separate
  // trace checks that header/body/tick transitions preserve both values.
  val noDeadlineBeyondD = s.time <= d and s.frameEnd <= d
  val fixedFrameBudget = (s.phase == Reading or s.phase == Admitting or s.phase == Callback)
    implies s.frameEnd == frameDeadline(s.frameStart)
  val safety = ownership and noReadAfterRetire and noFalseReceipt and noDeadlineBeyondD and fixedFrameBudget
  val witnessIdleBeyondFrameBudget = s.phase == Waiting and s.time > f and s.time < d
  val witnessSecondDelivery = s.delivered == 2
  val witnessExitWaiting = s.phase == Waiting and not(s.leaderAlive)
  val witnessRetireWaiting = s.phase == Waiting and s.retired and s.readHeld
  val witnessPartialTimeout = s.timeoutObserved and s.terminalUnknown and s.headerStarted
  action step: bool = any {beginFirst, beginNativeNext, beginDesktopWait,
    bytesBecomeReady, startReadyFrame, header, completeBody, foreignCredential,
    revokeAdmission, beginCallback, applyEffect, admit, callbackUncertain, leaderExits, shutdownOwnedPeerWrite, observeEof,
    publishRetirement, settleRetired, tick, frameTimeout, originalDeadline,
    rejectCredential, rejectRevoked}
  // Focused same-action reachability; never a substitute for broad counts or
  // liveness. Explicit time ticks below are symbolic and not real-time proof.
  action guidedIdleStep: bool =
    if (s.phase == First) beginFirst
    else if (s.phase == Reading and not(s.headerStarted)) header
    else if (s.phase == Reading) completeBody
    else if (s.phase == Admitting) beginCallback
    else if (s.phase == Callback) admit
    else if (s.phase == Between and s.delivered == 1) beginDesktopWait
    else if (s.phase == Waiting and s.time <= f) tick
    else if (s.phase == Waiting and not(s.bytesReady)) bytesBecomeReady
    else if (s.phase == Waiting) startReadyFrame
    else s' = s
  action guidedLeaderExitStep: bool =
    if (s.phase == Waiting and s.leaderAlive) leaderExits
    else if (s.phase == Waiting and not(s.peerWriteClosed)) shutdownOwnedPeerWrite
    else if (s.phase == Waiting) observeEof
    else if (s.phase == Ended) s' = s
    else guidedIdleStep
  action guidedRetirementStep: bool =
    if (s.phase == Waiting and not(s.retired)) publishRetirement
    else if (s.phase == Waiting) settleRetired
    else if (s.phase == Ended) s' = s
    else guidedIdleStep
  action guidedPartialTimeoutStep: bool =
    if (s.phase == First) beginFirst
    else if (s.phase == Reading and not(s.headerStarted)) header
    else if (s.phase == Reading and s.time < s.frameEnd) tick
    else if (s.phase == Reading) frameTimeout
    else s' = s
}
