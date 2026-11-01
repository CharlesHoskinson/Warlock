// Bounded source correspondence, not native or original-scenario acceptance.
// Browser same-origin/preflight, private namespace and selected process/peer are
// assumptions. Non-browser clients can forge HTTP headers; no process auth is
// established here. Full WebKit/CSP execution and focus pub/lease are not modeled.
// Source mapping: Ui.Owner's enqueue/dequeue own per-role FIFO and atomic batch;
// presentation derives renderer rows, serve preflights before enqueue then calls
// Ui.Native.sendCommit. ownerEvent and receiveGateway are trusted producers.
// Engine return and cleanup aggregate in Ui.Owner's UiResult; UiHttp's per-role
// active/failed state represents the client transport, not server authentication.
module ui_origin {
  type Role = Controller | Bar | Popup
  type Route = Document | Events | Commit | Actions | Other
  type Method = Get | Post | Options
  type Payload = WholeCommit | BarAction | PopupAction | Invalid
  type Event = Topology | NativeGateway | ViewAction | Presentation | Announcement | Focus | UnknownSource
  type Outcome = NoneYet | Accepted | Refused | Full | Unknown
  type Request = { listener: Role, caller: Role, route: Route, method: Method,
    host: bool, origin: bool, originPresent: bool, api: bool, wellFormed: bool,
    binding: bool, payload: Payload, focusBar: bool, focusPopup: bool }
  type State = { privateNet: bool, live: bool, retired: bool, expired: bool,
    enginePassed: bool, engineCleanup: bool, clean: bool,
    controller: List[Event], bar: List[Event], popup: List[Event],
    active: Set[Role], served: Set[Role], failed: Set[Role], pendingCommit: bool,
    forwarded: int, barActions: int, popupActions: int, reads: int,
    topologyReads: int, nativeReads: int, result: Outcome, safe: bool }
  var s: State
  // Two base renderer messages fit together; three is a reduced role capacity,
  // six is a reduced aggregate byte/count proxy. Real owner: 16 items per role,
  // each <=1048704 bytes and aggregate <=16*1048704 bytes. Real UiHttp retains
  // active + pending <=16 per role; this model retains one active and no pending.
  // A commit may request at most one focus event per renderer in this finite
  // abstraction; real presentation can produce multiple validated targets.
  // Aggregate count approximates bytes only when every modeled event has equal
  // size. Neither reduced bound represents the concrete byte limit exactly.
  pure val capacity = 3
  pure val aggregate = 6
  pure val validCommit: Request = {listener: Controller, caller: Controller, route: Commit, method: Post, host: true, origin: true, originPresent: true, api: true, wellFormed: true, binding: true, payload: WholeCommit, focusBar: false, focusPopup: false}
  pure val validBar: Request = {listener: Bar, caller: Bar, route: Actions, method: Post, host: true, origin: true, originPresent: true, api: true, wellFormed: true, binding: true, payload: BarAction, focusBar: false, focusPopup: false}
  pure val validPopup: Request = {listener: Popup, caller: Popup, route: Actions, method: Post, host: true, origin: true, originPresent: true, api: true, wellFormed: true, binding: true, payload: PopupAction, focusBar: false, focusPopup: false}
  pure val validRead: Request = {listener: Controller, caller: Controller, route: Events, method: Get, host: true, origin: true, originPresent: true, api: true, wellFormed: true, binding: true, payload: Invalid, focusBar: false, focusPopup: false}
  pure def admitted(r: Request): bool = r.host and r.wellFormed and
    (not(r.originPresent) or r.origin) and
    (if (r.method == Get and r.route == Document) true
     else if (r.method == Get and r.route == Events) r.api and r.caller == r.listener
     else if (r.method == Post) r.api and r.originPresent and r.origin and r.caller == r.listener and
       ((r.listener == Controller and r.route == Commit) or (r.listener != Controller and r.route == Actions))
     else false)
  pure def payloadOK(r: Request): bool = r.binding and
    ((r.listener == Controller and r.route == Commit and r.payload == WholeCommit) or
     (r.listener == Bar and r.route == Actions and r.payload == BarAction) or
     (r.listener == Popup and r.route == Actions and r.payload == PopupAction))
  pure def allowed(role: Role, event: Event): bool =
    if (role == Controller) Set(Topology, NativeGateway, ViewAction).contains(event)
    else Set(Presentation, Announcement, Focus).contains(event)
  val total = s.controller.length() + s.bar.length() + s.popup.length()
  action init: bool = s' = {privateNet: false, live: false, retired: false, expired: false,
    enginePassed: false, engineCleanup: false, clean: false, controller: List(), bar: List(), popup: List(),
    active: Set(), served: Set(), failed: Set(), pendingCommit: false, forwarded: 0, barActions: 0, popupActions: 0,
    reads: 0, topologyReads: 0, nativeReads: 0, result: NoneYet, safe: true}
  action privateReady: bool = all {not(s.retired), not(s.expired), s' = {...s, privateNet: true}}
  action start: bool = all {s.privateNet, not(s.live), not(s.retired), not(s.expired), s' = {...s, live: true}}
  // Callback provenance comes from the trusted owner callback or native fd,
  // never an HTTP-supplied role or event-source field. Invalid or full callback
  // fails the owner; the selected scope/revision check is abstracted by current.
  action producer(event: Event, current: bool): bool = all {
    s.live, not(s.retired), not(s.expired),
    if (not(current) or not(Set(Topology, NativeGateway).contains(event)) or s.controller.length() == capacity or total == aggregate)
      s' = {...s, live: false, retired: true, result: Refused}
    else s' = {...s, controller: s.controller.append(event), result: Accepted}
  }
  // UiHttp fixed role endpoint: one active POST per root, independent roles;
  // later enqueues are omitted rather than conflated with replay.
  action issue(role: Role): bool = all {s.live, not(s.retired), not(s.expired),
    not(s.active.contains(role)), not(s.failed.contains(role)), s' = {...s, active: s.active.union(Set(role)), served: s.served.exclude(Set(role))}}
  action request(r: Request): bool = all {
    s.live, not(s.retired), not(s.expired),
    if (not(admitted(r))) s' = {...s, result: Refused}
    else if (r.route == Document) s' = {...s, result: Accepted}
    else if (r.route == Events) {
      if (r.listener == Controller and s.controller.length() > 0)
        s' = {...s, controller: s.controller.tail(), reads: s.reads + 1,
          topologyReads: s.topologyReads + (if (s.controller.head() == Topology) 1 else 0),
          nativeReads: s.nativeReads + (if (s.controller.head() == NativeGateway) 1 else 0), result: Accepted}
      else if (r.listener == Bar and s.bar.length() > 0) s' = {...s, bar: s.bar.tail(), reads: s.reads + 1, result: Accepted}
      else if (r.listener == Popup and s.popup.length() > 0) s' = {...s, popup: s.popup.tail(), reads: s.reads + 1, result: Accepted}
      else s' = {...s, result: Accepted}
    } else if (not(payloadOK(r)) or not(s.active.contains(r.listener)) or s.served.contains(r.listener)) s' = {...s, result: Refused}
    else if (r.route == Commit) {
      if (s.pendingCommit or s.bar.length() + 2 + (if (r.focusBar) 1 else 0) > capacity or s.popup.length() + 2 + (if (r.focusPopup) 1 else 0) > capacity or total + 4 + (if (r.focusBar) 1 else 0) + (if (r.focusPopup) 1 else 0) > aggregate)
        s' = {...s, live: false, retired: true, result: Full}
      else s' = {...s, bar: if (r.focusBar) s.bar.append(Presentation).append(Announcement).append(Focus) else s.bar.append(Presentation).append(Announcement),
        popup: if (r.focusPopup) s.popup.append(Presentation).append(Announcement).append(Focus) else s.popup.append(Presentation).append(Announcement), pendingCommit: true, served: s.served.union(Set(r.listener)), result: Accepted}
    } else if (s.controller.length() == capacity or total == aggregate)
      s' = {...s, live: false, retired: true, result: Full}
    else s' = {...s, controller: s.controller.append(ViewAction), served: s.served.union(Set(r.listener)), result: Accepted,
      barActions: s.barActions + (if (r.listener == Bar) 1 else 0),
      popupActions: s.popupActions + (if (r.listener == Popup) 1 else 0)}
  }
  // Reservation precedes sendCommit; a send failure retires, not a rollback.
  action sendCommit(ok: bool): bool = all {s.live, not(s.retired), not(s.expired), s.pendingCommit,
    if (ok) s' = {...s, pendingCommit: false, forwarded: s.forwarded + 1}
    else s' = {...s, pendingCommit: false, live: false, retired: true, result: Unknown}}
  // HTTP 204 only advances the transport; no native or presentation receipt.
  action ack(role: Role): bool = all {s.active.contains(role), s' = {...s, active: s.active.exclude(Set(role))}}
  action unknown(role: Role): bool = all {s.active.contains(role), s' = {...s, active: s.active.exclude(Set(role)), failed: s.failed.union(Set(role)), result: Unknown}}
  // Engine return always begins retirement; cleanup/passed are independent.
  // clean abstracts engine + native/socket closes and worker joins all confirmed.
  action engineReturn(passed: bool, cleanup: bool, otherClean: bool): bool = all {s.live, not(s.retired),
    s' = {...s, live: false, retired: true, enginePassed: passed, engineCleanup: cleanup, clean: cleanup and otherClean}}
  action deadline: bool = all {not(s.retired), not(s.expired), s' = {...s, live: false, expired: true}}
  val safety = s.controller.length() <= capacity and s.bar.length() <= capacity and s.popup.length() <= capacity and total <= aggregate and
    s.controller.foldl(true, (ok, e) => ok and allowed(Controller, e)) and s.bar.foldl(true, (ok, e) => ok and allowed(Bar, e)) and s.popup.foldl(true, (ok, e) => ok and allowed(Popup, e)) and
    s.active.intersect(s.failed).size() == 0 and (s.live implies s.privateNet and not(s.retired) and not(s.expired)) and
    (s.clean implies s.retired and s.engineCleanup)
  val witnessCommit = s.forwarded > 0
  val witnessBar = s.barActions > 0
  val witnessPopup = s.popupActions > 0
  val witnessTopology = s.topologyReads > 0
  val witnessNative = s.nativeReads > 0
  val witnessUnknown = s.failed.size() > 0
  val witnessRetired = s.retired
  val witnessFocus = s.bar.length() == 3 or s.popup.length() == 3
  action step: bool = any {privateReady, start, producer(Topology, true), producer(NativeGateway, true), producer(UnknownSource, true), producer(NativeGateway, false),
    issue(Controller), issue(Bar), issue(Popup), request(validCommit), request({...validCommit, focusBar: true}), request({...validCommit, focusPopup: true}), request(validBar), request(validPopup), request(validRead),
    request({...validCommit, caller: Bar}), request({...validRead, api: false}), request({...validCommit, host: false}),
    request({...validCommit, binding: false}), request({...validRead, method: Options}),
    sendCommit(true), sendCommit(false), ack(Controller), ack(Bar), ack(Popup), unknown(Controller), unknown(Bar), unknown(Popup),
    engineReturn(true, true, true), engineReturn(false, false, false), deadline}
}
