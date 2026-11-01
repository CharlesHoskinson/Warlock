// Proposed application-only startup boundary, not a claim that the new
// application-attached route has landed or that any native effect is qualified.
// Existing Protocol.Identity binding has three nonzero counters; Desktop v3
// request/reply and Shell's Binding.replaces are the source anchors. Backend
// attachment emission is a proposed authenticated-credential-ingress seam.
// Two distinct positive counter values abstract UInt64; no byte parser, actual
// credential authentication, persistence, clock or compositor is modeled.
// Desired recovery retains the unknown pin disposition across reconnect; the
// current Desktop resets Pins.initial on disconnect/rebind, then requires a
// fresh snapshot before writing. This difference needs source-route review;
// it is not evidence that the retained-disposition behavior is implemented.
module ui_standalone_bootstrap {
  type Binding = { lifetime: int, session: int, frontend: int }
  type Phase = Offline | AwaitCommit | AwaitAttachment | Application | Lost
  type PinPhase = PinIdle | PinPending | PinUnknown | PinSaved
  type State = { phase: Phase, current: Binding, previous: Binding, hadPrevious: bool,
    attempts: int, authenticated: bool, catalogPending: bool, catalogReady: bool,
    pin: PinPhase, nextRequest: int, catalogRequest: int, pinRequest: int,
    nativeAuthority: bool, projectionIssued: bool, nativeEffectIssued: bool }
  var s: State
  pure val first: Binding = {lifetime: 1, session: 1, frontend: 1}
  pure val nextBinding: Binding = {lifetime: 1, session: 2, frontend: 1}
  pure def valid(b: Binding): bool = b.lifetime > 0 and b.session > 0 and b.frontend > 0
  pure def replaces(b: Binding, old: Binding): bool = b.lifetime != old.lifetime or b.session != old.session or b.frontend > old.frontend
  action init: bool = s' = {phase: Offline, current: first, previous: first, hadPrevious: false,
    attempts: 0, authenticated: false, catalogPending: false, catalogReady: false,
    pin: PinIdle, nextRequest: 0, catalogRequest: 0, pinRequest: 0,
    nativeAuthority: false, projectionIssued: false, nativeEffectIssued: false}
  // Backend session and authentication represent already-approved custody, not
  // HTTP Origin or self-asserted identity. This finite abstraction requires a
  // different session counter after loss even if lifetime also changes; that
  // is a conservative subset of Shell's full Binding.replaces relation.
  action connect(b: Binding, authenticated: bool): bool = all {
    Set(Offline, Lost).contains(s.phase), authenticated, valid(b),
    not(s.hadPrevious) or (b.session != s.previous.session and replaces(b, s.previous)),
    s' = {...s, phase: AwaitCommit, current: b, previous: b, hadPrevious: true,
      attempts: 0, authenticated: true, catalogPending: false, catalogReady: false,
      pin: if (s.pin == PinUnknown) PinUnknown else PinIdle, catalogRequest: 0, pinRequest: 0}
  }
  // One attempted attachment per approved session, after a valid whole commit;
  // transport uncertainty loses the session and is not retried.
  action wholeCommit(binding: Binding, version: int, validWhole: bool): bool = all {
    s.phase == AwaitCommit, s.authenticated, binding == s.current, version == 3, validWhole,
    s.attempts == 0, s' = {...s, phase: AwaitAttachment, attempts: 1}
  }
  action attachment(binding: Binding, version: int, exactFields: bool, emptyNative: bool): bool = all {
    s.phase == AwaitAttachment, s.authenticated, binding == s.current, version == 3,
    exactFields, emptyNative, s.attempts == 1, s' = {...s, phase: Application}
  }
  action lose: bool = all {Set(AwaitCommit, AwaitAttachment, Application).contains(s.phase),
    s' = {...s, phase: Lost, authenticated: false, catalogPending: false,
      pin: if (s.pin == PinPending) PinUnknown else s.pin}}
  action requestCatalog: bool = all {s.phase == Application, not(s.catalogPending),
    s' = {...s, nextRequest: s.nextRequest + 1, catalogRequest: s.nextRequest + 1, catalogPending: true}}
  action receiveCatalog(binding: Binding, version: int, request: int): bool = all {
    s.phase == Application, s.catalogPending, binding == s.current, version == 3, request == s.catalogRequest,
    s' = {...s, catalogPending: false, catalogReady: true}}
  action savePin: bool = all {s.phase == Application, s.catalogReady, s.pin == PinIdle,
    s' = {...s, nextRequest: s.nextRequest + 1, pinRequest: s.nextRequest + 1, pin: PinPending}}
  action receivePin(binding: Binding, version: int, request: int, confirmed: bool): bool = all {
    s.phase == Application, s.pin == PinPending, binding == s.current, version == 3, request == s.pinRequest,
    s' = {...s, pin: if (confirmed) PinSaved else PinUnknown}}
  // Shell.available guards Act; application attachment does not provide the
  // separate native authority needed for an effect. A real native attachment
  // and its issuance path are intentionally outside this application model.
  action issueNativeEffect: bool = all {s.phase == Application, s.nativeAuthority,
    s' = {...s, nativeEffectIssued: true}}
  // A fresh catalog read can reconcile an unknown result, but cannot replay it.
  action reconcilePin(binding: Binding, version: int, request: int, snapshotAvailable: bool): bool = all {
    s.phase == Application, s.pin == PinUnknown, s.catalogPending, binding == s.current,
    version == 3, request == s.catalogRequest, snapshotAvailable,
    s' = {...s, pin: PinIdle, catalogPending: false, catalogReady: true}}
  val safety = not(s.nativeAuthority) and not(s.projectionIssued) and not(s.nativeEffectIssued) and
    (s.phase == Application implies s.authenticated and s.attempts == 1 and valid(s.current)) and
    (s.catalogPending implies s.phase == Application and s.catalogRequest > 0) and
    (s.pin == PinPending implies s.phase == Application and s.pinRequest > 0) and s.attempts <= 1
  val witnessAttachment = s.phase == Application
  val witnessCatalog = s.catalogReady
  val witnessPin = s.pin == PinSaved
  val witnessUnknown = s.pin == PinUnknown
  val witnessReconnect = s.phase == Application and s.current.session == 2
  action step: bool = any { connect(first, true), connect(nextBinding, true), connect(first, false),
    wholeCommit(first, 3, true), wholeCommit(nextBinding, 3, true), wholeCommit(first, 2, true),
    attachment(first, 3, true, true), attachment(nextBinding, 3, true, true), attachment(first, 3, true, false),
    lose, requestCatalog, receiveCatalog(first, 3, 1), receiveCatalog(nextBinding, 3, 1),
    savePin, receivePin(first, 3, 2, true), receivePin(first, 3, 2, false), issueNativeEffect,
    reconcilePin(first, 3, 3, true) }
}
