// Source proposal only: shared GLib owner and one HTTP slot; never executed by author.
module http_owner {
  type ElmPhase = Idle | Connecting | Available | Failed | Retired
  type CookiePhase = CookieIdle | CookiePending | CookieCancel | CookieDone
  type RequestPhase = Empty | Reading | Detached | Closed
  type Event = DidBeginCookie | DidCancelCookie | DidCompleteCookie | DidFailCookie | DidStartConnect | DidAdmit | DidTick | DidChunk | DidCallbackEnter | DidCallbackDone | DidDetach | DidCloseOwned | DidCleanup | DidExpire | DidOverflow | DidAbortRequest | DidFinishRequest | DidElmTimeout | DidRetireElm | DidNewElm | DidStopListening | DidFreeOwner
  type State = {
    events: Set[Event],
    elm: ElmPhase, generation: int, requestGeneration: int,
    cookie: CookiePhase, cookieGeneration: int, cookieInstalled: bool,
    listening: bool, stopping: bool, freed: bool,
    request: RequestPhase, handlersAttached: bool, retained: bool,
    clock: int, deadline: int, bytes: int, callbacks: int,
    closeCount: int, serverReplyGeneration: int, nativeOps: Set[int]
  }
  var s: State
  action init: bool = all {
    s' = { events: Set(), elm: Idle, generation: 1, requestGeneration: 0,
      cookie: CookieIdle, cookieGeneration: 0, cookieInstalled: false,
      listening: true, stopping: false, freed: false, request: Empty,
      handlersAttached: false, retained: false, clock: 0, deadline: 0,
      bytes: 0, callbacks: 0, closeCount: 0, serverReplyGeneration: 0,
      nativeOps: Set() },
  }
  action beginCookie: bool = all {
    s.cookie == CookieIdle, s.elm != Retired, not(s.stopping), not(s.freed),
    s' = { ...s, events: s.events.union(Set(DidBeginCookie)), cookie: CookiePending, cookieGeneration: s.generation, callbacks: s.callbacks + 1 },
  }
  action cancelCookie: bool = all {
    s.cookie == CookiePending,
    s' = { ...s, events: s.events.union(Set(DidCancelCookie)), cookie: CookieCancel },
  }
  action completeCookie: bool = all {
    s.cookie == CookiePending or s.cookie == CookieCancel,
    s' = { ...s, events: s.events.union(Set(DidCompleteCookie)), cookie: CookieDone, callbacks: s.callbacks - 1,
      cookieInstalled: s.cookie == CookiePending and s.cookieGeneration == s.generation and s.elm != Retired and not(s.stopping) },
  }
  action failCookie: bool = all {
    s.cookie == CookiePending or s.cookie == CookieCancel,
    s' = { ...s, events: s.events.union(Set(DidFailCookie)), cookie: CookieDone, callbacks: s.callbacks - 1, cookieInstalled: false },
  }
  action startConnect: bool = all {
    s.elm == Idle, s.cookieInstalled, not(s.stopping), not(s.freed),
    s' = { ...s, events: s.events.union(Set(DidStartConnect)), elm: Connecting },
  }
  // Boolean authentication facts abstract exact checks, not parser or secret security.
  action admit(hostOk: bool, originOk: bool, cookieOk: bool): bool = all {
    s.elm == Connecting, s.listening, not(s.stopping), s.request == Empty,
    hostOk, originOk, cookieOk, s.cookieInstalled,
    s' = { ...s, events: s.events.union(Set(DidAdmit)), request: Reading, requestGeneration: s.generation,
      deadline: s.clock + 3, bytes: 0, handlersAttached: true, retained: true },
  }
  action tick: bool = all { s.clock < 8, s' = { ...s, events: s.events.union(Set(DidTick)), clock: s.clock + 1 } }
  action chunk: bool = all {
    s.request == Reading, s.clock < s.deadline, s.bytes < 2,
    s' = { ...s, events: s.events.union(Set(DidChunk)), bytes: s.bytes + 1 },
  }
  // Entering a callback retains a live owner until callback completion.
  action callbackEnter: bool = all {
    s.request == Reading, s.handlersAttached, not(s.freed),
    s' = { ...s, events: s.events.union(Set(DidCallbackEnter)), callbacks: s.callbacks + 1 },
  }
  action callbackDone: bool = all {
    s.callbacks > 0, s.cookie != CookiePending, s.cookie != CookieCancel,
    s' = { ...s, events: s.events.union(Set(DidCallbackDone)), callbacks: s.callbacks - 1 },
  }
  // Detach and take a reference in one owner/lock section; no interleaving there.
  action detach: bool = all {
    s.request == Reading, s.retained,
    s' = { ...s, events: s.events.union(Set(DidDetach)), request: Detached, handlersAttached: false },
  }
  // Close after leaving that section. A detached request can close once only.
  action closeOwned: bool = all {
    s.request == Detached, s.retained,
    s' = { ...s, events: s.events.union(Set(DidCloseOwned)), request: Closed, closeCount: s.closeCount + 1 },
  }
  action cleanup: bool = all {
    s.request == Closed, s.callbacks == 0,
    s' = { ...s, events: s.events.union(Set(DidCleanup)), request: Empty, retained: false, requestGeneration: 0, bytes: 0, deadline: 0 },
  }
  action expire: bool = all {
    s.request == Reading, s.clock >= s.deadline,
    s' = { ...s, events: s.events.union(Set(DidExpire)), request: Detached, handlersAttached: false,
      elm: if (s.elm == Connecting and s.requestGeneration == s.generation) Failed else s.elm },
  }
  action overflow: bool = all {
    s.request == Reading, s.bytes == 2,
    s' = { ...s, events: s.events.union(Set(DidOverflow)), request: Detached, handlersAttached: false,
      elm: if (s.elm == Connecting and s.requestGeneration == s.generation) Failed else s.elm },
  }
  action abortRequest: bool = all {
    s.request == Reading,
    s' = { ...s, events: s.events.union(Set(DidAbortRequest)), request: Detached, handlersAttached: false,
      elm: if (s.elm == Connecting and s.requestGeneration == s.generation) Failed else s.elm },
  }
  action finishRequest: bool = all {
    s.request == Reading, s.clock < s.deadline,
    s' = { ...s, events: s.events.union(Set(DidFinishRequest)), request: Detached, handlersAttached: false,
      serverReplyGeneration: s.requestGeneration,
      elm: if (s.elm == Connecting and s.requestGeneration == s.generation) Available else s.elm },
  }
  action elmTimeout: bool = all {
    s.elm == Connecting, not(s.freed),
    s' = { ...s, events: s.events.union(Set(DidElmTimeout)), elm: Failed },
  }
  action retireElm: bool = all {
    s.elm != Retired, not(s.freed),
    s' = { ...s, events: s.events.union(Set(DidRetireElm)), elm: Retired, generation: s.generation + 1, cookieInstalled: false },
  }
  action newElm: bool = all {
    s.elm == Retired, s.cookie == CookieDone, s.callbacks == 0, not(s.freed),
    s' = { ...s, events: s.events.union(Set(DidNewElm)), elm: Idle, cookie: CookieIdle, cookieInstalled: false },
  }
  // stopListening only closes listener, not any already owned request.
  action stopListening: bool = all {
    not(s.stopping),
    s' = { ...s, events: s.events.union(Set(DidStopListening)), listening: false, stopping: true },
  }
  // Terminal destruction of this shared owner; listener stop alone is not destruction.
  action freeOwner: bool = all {
    s.stopping, s.request == Empty, s.callbacks == 0,
    s.cookie != CookiePending, s.cookie != CookieCancel, not(s.freed),
    s' = { ...s, events: s.events.union(Set(DidFreeOwner)), freed: true },
  }
  action step: bool = any {
    beginCookie, cancelCookie, completeCookie, failCookie, startConnect,
    admit(true, true, true), admit(false, true, true), admit(true, false, true), admit(true, true, false),
    tick, chunk, callbackEnter, callbackDone, detach, closeOwned, cleanup,
    expire, overflow, abortRequest, finishRequest, elmTimeout, retireElm, newElm,
    stopListening, freeOwner,
  }
  val noNativeAuthority = s.nativeOps == Set()
  val noFreeWithOwnedWork = s.freed implies (s.callbacks == 0 and s.request == Empty)
  val ownedWhileActive = (s.request != Empty) implies s.retained
  val closedHasNoHandlers = (s.request == Detached or s.request == Closed) implies not(s.handlersAttached)
  val stoppedHasNoListener = s.stopping implies not(s.listening)
  val retiredHasNoCookie = (s.elm == Retired) implies not(s.cookieInstalled)
  val availableIsCurrent = (s.elm == Available) implies s.serverReplyGeneration == s.generation
  val reachedBeginCookie = s.events.contains(DidBeginCookie)
  val reachedCancelCookie = s.events.contains(DidCancelCookie)
  val reachedCompleteCookie = s.events.contains(DidCompleteCookie)
  val reachedFailCookie = s.events.contains(DidFailCookie)
  val reachedStartConnect = s.events.contains(DidStartConnect)
  val reachedAdmit = s.events.contains(DidAdmit)
  val reachedTick = s.events.contains(DidTick)
  val reachedChunk = s.events.contains(DidChunk)
  val reachedCallbackEnter = s.events.contains(DidCallbackEnter)
  val reachedCallbackDone = s.events.contains(DidCallbackDone)
  val reachedDetach = s.events.contains(DidDetach)
  val reachedCloseOwned = s.events.contains(DidCloseOwned)
  val reachedCleanup = s.events.contains(DidCleanup)
  val reachedExpire = s.events.contains(DidExpire)
  val reachedOverflow = s.events.contains(DidOverflow)
  val reachedAbortRequest = s.events.contains(DidAbortRequest)
  val reachedFinishRequest = s.events.contains(DidFinishRequest)
  val reachedElmTimeout = s.events.contains(DidElmTimeout)
  val reachedRetireElm = s.events.contains(DidRetireElm)
  val reachedNewElm = s.events.contains(DidNewElm)
  val reachedStopListening = s.events.contains(DidStopListening)
  val reachedFreeOwner = s.events.contains(DidFreeOwner)
}
