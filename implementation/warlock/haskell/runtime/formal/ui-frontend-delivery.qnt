// ARC024 / DEL014 source abstraction: UiHttp.elm, HttpMain.elm,
// HttpBar.elm, HttpPopup.elm, Presentation.elm and Popup.elm.
// One fixed root per instance; roles never come from wire input. A single
// serialized root is modeled, with up to 16 retained posts (one active).
// Requests and full-width counters are opaque, distinct atoms; no float or
// arithmetic encoding. Network callbacks may be late, lost, or reordered.
// Frames and controls below are a deliberately small valid-frame abstraction;
// popup frames keep the same application/files field and mode while their
// lease is unchanged and that field is enabled. Focus target is a separate
// atom. Receipt abstracts a matching authenticated policy receipt; its wire
// validation and correlation are assumptions, not proved by this model.
// focused records an issued Browser.Dom.focus target, not successful DOM focus.
// Malformed decoding, actual networking, DOM, AT, IME and native effects are
// outside this model. No fairness, wall clock or physical delivery assumed.
module ui_frontend_delivery {
  type Role = Controller | Renderer
  type Kind = NativeEvent | ViewTopology | ViewAction | ViewDisposition | ViewDismiss | ViewEscape | ViewReflow | Presentation | Announcements | Focus | Other
  type Status = Empty204 | Body200 | OtherResponse | TransportError
  type Knowledge = Idle | Waiting | Unknown | Confirmed
  type Surface = Bar | Popup
  type Atom = Zero | First | Next | HugeA | HugeB
  type State = { role: Role, active: bool, pending: int, polling: bool, failed: bool,
    sent: int, completed: int, lost: int, delivered: int, policy: Knowledge,
    nativeAck: int, publication: Atom, lease: Atom, surface: Surface,
    target: Atom, enabled: bool, focusOnly: bool, composing: bool,
    focused: Atom, focusCount: int }
  var s: State
  pure def allowed(role: Role, kind: Kind): bool =
    if (role == Controller) Set(NativeEvent, ViewTopology, ViewAction, ViewDisposition, ViewDismiss, ViewEscape, ViewReflow).contains(kind)
    else Set(Presentation, Announcements, Focus).contains(kind)
  action init(role: Role): bool = s' = {role: role, active: false, pending: 0, polling: true, failed: false,
    sent: 0, completed: 0, lost: 0, delivered: 0, policy: Idle, nativeAck: 0,
    publication: Zero, lease: Zero, surface: Popup, target: Zero, enabled: false,
    focusOnly: false, composing: false, focused: Zero, focusCount: 0}
  action initController: bool = init(Controller)
  action initRenderer: bool = init(Renderer)
  pure def rank(a: Atom): int = if (a == Zero) 0 else if (a == First) 1 else if (a == Next) 2 else if (a == HugeA) 3 else 4
  // The actual failed path retains queued values, cancels both trackers and
  // ignores all later callbacks. Policy's correlated request becomes Unknown.
  pure def lose(x: State): State = {...x, failed: true, lost: x.lost + 1,
    policy: if (x.policy == Waiting) Unknown else x.policy}
  action enqueue: bool = all {not(s.failed),
    if (s.pending + (if (s.active) 1 else 0) >= 16) s' = lose(s)
    else if (s.active) s' = {...s, pending: s.pending + 1}
    else s' = {...s, active: true, sent: s.sent + 1}}
  action policyRequest: bool = all {s.role == Controller, not(s.failed), s.policy == Idle,
    s' = {...s, policy: Waiting}}
  action posted(status: Status): bool = all {not(s.failed), s.active,
    if (status != Empty204) s' = lose(s)
    else if (s.pending > 0) s' = {...s, pending: s.pending - 1, sent: s.sent + 1, completed: s.completed + 1}
    else s' = {...s, active: false, completed: s.completed + 1}}
  action polled(status: Status, kind: Kind): bool = all {not(s.failed), s.polling,
    if (status == Empty204) s' = {...s, polling: false}
    else if (status == Body200 and allowed(s.role, kind)) s' = {...s, delivered: s.delivered + 1}
    else s' = lose(s)}
  // Empty event polls schedule one delayed Poll; nonempty polls immediately
  // start the next request. A cancelled delayed Poll cannot restart transport.
  action pollTick: bool = all {not(s.failed), not(s.polling), s' = {...s, polling: true}}
  action stop: bool = all {not(s.failed), s' = lose(s)}
  // A callback after cancellation cannot resurrect or dispatch anything.
  action lateCallback: bool = all {s.failed, s' = s}
  // This separate correlated source receipt is the ONLY modeled ACK path.
  action receipt: bool = all {s.role == Controller, not(s.failed), s.policy == Waiting,
    s' = {...s, policy: Confirmed, nativeAck: s.nativeAck + 1}}
  // Distinct publications represent monotone accepted frames. Equal leases
  // preserve popup composition only when the field remains eligible.
  action frame(pub: Atom, lease: Atom, surface: Surface, target: Atom, targetEnabled: bool, focusOnly: bool): bool = all {
    s.role == Renderer, rank(pub) > rank(s.publication), rank(lease) >= rank(s.lease), target != Zero,
    s' = {...s, publication: pub, lease: lease, surface: surface, target: target,
      enabled: targetEnabled, focusOnly: focusOnly,
      composing: s.composing and lease == s.lease and surface == Popup and targetEnabled}}
  action preedit: bool = all {s.role == Renderer, s.surface == Popup, s.publication != Zero, s.enabled,
    s' = {...s, composing: true}}
  action endPreedit: bool = all {s.role == Renderer, s.composing, s' = {...s, composing: false}}
  action focus(pub: Atom, lease: Atom, surface: Surface, target: Atom): bool = all {
    s.role == Renderer, s.publication != Zero, pub == s.publication, lease == s.lease, surface == s.surface,
    target == s.target, (s.enabled or s.focusOnly), not(surface == Popup and s.composing),
    s' = {...s, focused: target, focusCount: s.focusCount + 1}}
  val safety = s.pending >= 0 and s.pending + (if (s.active) 1 else 0) <= 16 and
    s.completed <= s.sent and s.nativeAck <= 1 and
    (s.nativeAck == 1 implies s.policy == Confirmed) and
    (s.failed implies s.lost == 1) and (s.policy == Unknown implies s.nativeAck == 0)
  val witnessDelivery = s.completed > 0
  val witnessReceipt = s.nativeAck > 0
  val witnessUnknown = s.policy == Unknown
  val witnessFocus = s.focusCount > 0
  val witnessPreedit = s.composing
  val witnessGateway = s.delivered > 0
  action step: bool = any {enqueue, policyRequest, posted(Empty204), posted(Body200), posted(TransportError),
    polled(Empty204, Other), polled(Body200, NativeEvent), polled(Body200, Focus), polled(OtherResponse, Other),
    pollTick, stop, lateCallback, receipt, frame(First, First, Popup, HugeA, true, false),
    frame(Next, First, Popup, HugeB, false, true), preedit, endPreedit,
    focus(First, First, Popup, HugeA), focus(Next, First, Popup, HugeB)}
}
