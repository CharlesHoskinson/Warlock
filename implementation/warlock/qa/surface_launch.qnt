// Abstract transport admission only; see README for boundaries and source mapping.
module surface_launch {
  type Batch = { mode: str, publication: int, lease: int, requests: List[str], valid: bool }
  type State = {
    publication: int, lease: int, closed: int, queued: int, active: int, ready: bool,
    phase: str, batch: Batch, beforePublication: int, beforeLease: int, beforeQueue: int,
    preflightRefused: bool, committed: bool, popupFailed: bool, enqueued: bool, retired: bool, loadSet: bool,
  }
  var s: State
  pure def batch(mode: str, pub: int, lease: int, requests: List[str]): Batch =
    { mode: mode, publication: pub, lease: lease, requests: requests, valid: true }
  pure def frameAdmitted(s: State, b: Batch): bool =
    Set("closed", "applications", "menu", "other").contains(b.mode) and
    b.publication > s.publication and b.lease >= s.lease and
    (b.mode == "closed" or (b.lease > 0 and b.lease > s.closed))
  pure def baseAdmitted(s: State, b: Batch): bool =
    b.valid and frameAdmitted(s, b) and s.queued >= 0 and s.active >= 0 and
    b.requests.length() <= 16 and b.requests.length() + s.queued + s.active <= 16 and
    b.requests.indices().forall(i => s.ready or b.requests.nth(i) == "host-reconnect") and
    (b.requests.select(r => r == "host-reconnect").length() == 0 or b.requests.length() == 1)
  pure def blockedWhenOpen(r: str): bool =
    Set("application-launch", "workspace-navigation", "window-effect", "files-open", "jump-list-effect").contains(r)
  pure def oldAdmission(s: State, b: Batch): bool =
    baseAdmitted(s, b) and (b.mode == "closed" or b.requests.indices().forall(i => not(blockedWhenOpen(b.requests.nth(i)))))
  pure def candidateAdmission(s: State, b: Batch): bool =
    baseAdmitted(s, b) and (b.mode == "closed" or b.requests.indices().forall(i => not(blockedWhenOpen(b.requests.nth(i)))) or
      (b.mode == "applications" and b.requests == List("application-launch")))
  // surface_action uses equality to the live gate, unlike frame admission's increasing publication.
  pure def viewCurrent(s: State, publication: int, lease: int): bool =
    publication == s.publication and lease == s.lease and lease > s.closed

  action init: bool = s' = {
    publication: 0, lease: 0, closed: 0, queued: 0, active: 0, ready: true,
    phase: "idle", batch: batch("closed", 0, 0, List()),
    beforePublication: 0, beforeLease: 0, beforeQueue: 0,
    preflightRefused: false, committed: false, popupFailed: false, enqueued: false, retired: false, loadSet: false,
  }
  // Explicit environment load: abstracts other already-queued/active requests.
  action setLoad(queued: int, active: int, ready: bool): bool = all {
    s.phase == "idle", queued >= 0, active >= 0, active <= 1, queued + active <= 16,
    s' = { ...s, queued: queued, active: active, ready: ready, loadSet: true },
  }
  action preflightAccept(b: Batch): bool = all {
    s.phase == "idle", candidateAdmission(s, b),
    s' = { ...s, phase: "preflight", batch: b,
      beforePublication: s.publication, beforeLease: s.lease, beforeQueue: s.queued,
      preflightRefused: false, committed: false, popupFailed: false, enqueued: false },
  }
  action preflightReject(b: Batch): bool = all {
    s.phase == "idle", not(candidateAdmission(s, b)),
    s' = { ...s, phase: "rejected", batch: b,
      beforePublication: s.publication, beforeLease: s.lease, beforeQueue: s.queued,
      preflightRefused: true, committed: false, popupFailed: false, enqueued: false },
  }
  // Admission-batch success is assumed here. Failure and its backend effects are outside scope.
  action commitFrame: bool = all {
    s.phase == "preflight",
    s' = { ...s, phase: "frame", publication: s.batch.publication,
      lease: s.batch.lease, committed: true },
  }
  action popupFail: bool = all {
    s.phase == "frame", s.batch.mode != "closed",
    s' = { ...s, phase: "popupFailed", popupFailed: true },
  }
  // Abstract complete queue insertion, after popup opening succeeds if needed.
  // No claim about later backend execution or durable batch certificates.
  action enqueue: bool = all {
    s.phase == "frame", s.batch.requests.select(r => r == "host-reconnect").length() == 0,
    s' = { ...s, phase: "done", queued: s.queued + s.batch.requests.length(), enqueued: true },
  }
  // Popup hide retires the current open lease; gate history is not reset.
  action retirePopup: bool = all {
    s.phase == "done", s.batch.mode != "closed", s.lease > s.closed,
    s' = { ...s, phase: "idle", closed: s.lease, retired: true,
      preflightRefused: false, committed: false, popupFailed: false, enqueued: false },
  }
  val queueBound: bool = s.queued >= 0 and s.active >= 0 and s.queued + s.active <= 16
  val refusalPreservesGateAndQueue: bool = s.preflightRefused implies
    (s.publication == s.beforePublication and s.lease == s.beforeLease and s.queued == s.beforeQueue and not(s.enqueued))
  val popupFailureAfterCommit: bool = s.popupFailed implies
    (s.committed and s.publication == s.batch.publication and s.lease == s.batch.lease and s.queued == s.beforeQueue and not(s.enqueued))
  val queueBatchComplete: bool = s.enqueued implies s.queued == s.beforeQueue + s.batch.requests.length()
  val safety: bool = queueBound and refusalPreservesGateAndQueue and popupFailureAfterCommit and queueBatchComplete
  val reachedAppsLaunch: bool = s.enqueued and s.batch.mode == "applications" and s.batch.requests == List("application-launch")
  val reachedRejected: bool = s.preflightRefused
  val reachedFrame: bool = s.committed
  val reachedPopupFailure: bool = s.popupFailed
  val reachedEnqueue: bool = s.enqueued
  val reachedRetire: bool = s.retired
  val reachedLoad: bool = s.loadSet
  action step: bool = {
    nondet mode = Set("closed", "applications", "menu", "other").oneOf()
    nondet requests = Set(List("application-launch"), List("application-launch", "window-effect"), List("projection-request")).oneOf()
    val b = batch(mode, s.publication + 1, s.lease + 1, requests)
    any { setLoad(15, 1, false), preflightAccept(b), preflightReject(b), commitFrame, popupFail, enqueue, retirePopup }
  }
}
