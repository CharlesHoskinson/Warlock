// Source-bound abstraction: Ui.Http readRequest, Ui.Policy admitRequest,
// Ui.Owner serve and Protocol.Desktop.decodeDesktopCommit. ARC024/DEL014.
// Not an HTTP parser, browser security proof, native acceptance or EARS proof.
// Fixed listener role and its origin are trusted setup; hostile non-browser
// clients can forge headers. Every predicate below abstracts concrete bytes.
// Http bounds: header <=16384 bytes, line <=2048, <=32 fields, names <=128,
// values <=4096, canonical decimal length <=131072. Policy checks exact host,
// optional matching Origin on GET and mandatory matching Origin on POST;
// Events also requires X-Warlock-Api: 1. GET has no body or content type.
// POST body limits are 131072 (commit) and 8192 (actions). Extra means bytes
// observed by the current recv, not bytes that arrive after its exact count.
// Desktop strict JSON/UTF-8/UTF-16/depth and counter decoding are represented by
// payload, count and bindings, not modeled bytewise. Two bindings abstract up to
// 16 requests; empty is legal. presentation represents whole projection/focus
// validation. No claim that reduced bounds prove actual byte boundaries.
module ui_http_admission {
  type Role = Controller | Bar | Popup
  type Route = Document | Events | Commit | Actions | Other
  type Method = Get | Post | Options | OtherMethod
  type Origin = Absent | Match | Foreign
  type Phase = Open | Framed | Dispatched | Closed
  type Result = Pending | Rejected | Served
  type Request = { role: Role, route: Route, method: Method, host: bool,
    origin: Origin, api: bool, headerSyntax: bool, duplicate: bool,
    forbidden: bool, canonicalLength: bool, declared: int, observed: int,
    contentType: bool, payload: bool, requestCount: int,
    firstBinding: bool, secondBinding: bool, presentation: bool }
  type State = { phase: Phase, result: Result, req: Request,
    records: int, scopeReads: int, documents: int, dequeues: int,
    actions: int, reservations: int, sends: int, responses: int, refusalResponses: int,
    effectSafe: bool }
  var s: State
  pure val validCommit: Request = {role: Controller, route: Commit, method: Post,
    host: true, origin: Match, api: true, headerSyntax: true, duplicate: false,
    forbidden: false, canonicalLength: true, declared: 10, observed: 10,
    contentType: true, payload: true, requestCount: 2, firstBinding: true,
    secondBinding: true, presentation: true}
  pure val validBar = {...validCommit, role: Bar, route: Actions}
  pure val validPopup = {...validBar, role: Popup}
  pure val validEvents = {...validCommit, route: Events, method: Get, origin: Absent,
    declared: 0, observed: 0, contentType: false}
  pure val validDocument = {...validEvents, route: Document, api: false}
  pure def framing(r: Request): bool = r.headerSyntax and not(r.duplicate) and
    not(r.forbidden) and r.canonicalLength and r.declared >= 0 and
    r.declared <= 131072 and r.observed == r.declared
  pure def routeOK(r: Request): bool =
    (r.method == Get and (r.route == Document or r.route == Events)) or
    (r.method == Post and ((r.role == Controller and r.route == Commit) or
      (r.role != Controller and r.route == Actions)))
  pure def policy(r: Request): bool = r.host and r.origin != Foreign and routeOK(r) and
    (if (r.method == Get) r.declared == 0 and not(r.contentType) and
       (r.route != Events or r.api)
     else r.origin == Match and r.api and r.contentType and r.declared > 0 and
       (if (r.route == Commit) r.declared <= 131072 else r.declared <= 8192))
  pure def whole(r: Request): bool = r.payload and r.requestCount >= 0 and
    r.requestCount <= 2 and (r.requestCount == 0 or r.firstBinding) and
    (r.requestCount < 2 or r.secondBinding) and r.presentation
  action init: bool = s' = {phase: Open, result: Pending, req: validCommit,
    records: 0, scopeReads: 0, documents: 0, dequeues: 0, actions: 0,
    reservations: 0, sends: 0, responses: 0, refusalResponses: 0, effectSafe: true}
  // A framing refusal has no policy dispatch. Framing includes incomplete and
  // observed excess bytes, malformed length, duplicates and forbidden TE family.
  action receive(r: Request): bool = all {s.phase == Open,
    if (framing(r)) s' = {...s, phase: Framed, req: r}
    else s' = {...s, phase: Dispatched, req: r, result: Rejected}}
  // Actual Owner records after HTTP policy and reads the selected scope before
  // payload preflight. These are real IO; only domain effects are guarded by
  // the whole decode/binding/presentation preflight. No CORS headers are sent.
  action dispatch: bool = all {s.phase == Framed,
    if (not(policy(s.req))) s' = {...s, phase: Dispatched, result: Rejected}
    else if (s.req.route == Document) s' = {...s, phase: Dispatched, result: Served,
      records: s.records + 1, documents: s.documents + 1}
    else if (s.req.route == Events) s' = {...s, phase: Dispatched, result: Served,
      records: s.records + 1, dequeues: s.dequeues + 1}
    else if (s.req.route == Commit) {
      if (whole(s.req)) s' = {...s, phase: Dispatched, result: Served,
        records: s.records + 1, scopeReads: s.scopeReads + 1,
        reservations: s.reservations + 1, sends: s.sends + 1,
        effectSafe: s.effectSafe and framing(s.req) and policy(s.req) and whole(s.req)}
      else s' = {...s, phase: Dispatched, result: Rejected,
        records: s.records + 1, scopeReads: s.scopeReads + 1}
    } else if (s.req.payload and s.req.presentation) s' = {...s, phase: Dispatched,
      result: Served, records: s.records + 1, scopeReads: s.scopeReads + 1,
      actions: s.actions + 1, effectSafe: s.effectSafe and framing(s.req) and policy(s.req)}
    else s' = {...s, phase: Dispatched, result: Rejected,
      records: s.records + 1, scopeReads: s.scopeReads + 1}}
  // Abstracts a successfully delivered response and closure. Real error paths
  // attempt a 400/403 response even for framing/policy rejection; transport
  // reads, response writes, connection cleanup and deadlines are I/O too.
  // A later request requires a fresh connection. Failed delivery/cleanup and
  // stopped-owner 503 are omitted, as are enqueue-full and failed native send.
  action close: bool = all {s.phase == Dispatched,
    s' = {...s, phase: Closed, responses: s.responses + 1,
      refusalResponses: s.refusalResponses + (if (s.result == Rejected) 1 else 0)}}
  val safety = s.effectSafe and s.reservations == s.sends and
    s.responses <= 1 and s.refusalResponses <= s.responses and s.documents <= 1 and s.dequeues <= 1 and
    s.actions <= 1 and s.sends <= 1 and
    ((not(framing(s.req)) or not(policy(s.req))) implies
      s.records == 0 and s.scopeReads == 0 and s.documents == 0 and
      s.dequeues == 0 and s.actions == 0 and s.reservations == 0 and s.sends == 0) and
    ((s.sends > 0) implies framing(s.req) and policy(s.req) and whole(s.req)) and
    ((s.dequeues > 0) implies framing(s.req) and policy(s.req) and s.req.route == Events) and
    ((s.actions > 0) implies framing(s.req) and policy(s.req) and s.req.route == Actions)
  // These are positive --witnesses predicates. The previous version used their
  // inverses as invariants and expected a counterexample; that convention is
  // incompatible with the protected runner's positive witness selection.
  val witnessCommit = s.sends > 0
  val witnessBar = s.actions > 0 and s.req.role == Bar
  val witnessPopup = s.actions > 0 and s.req.role == Popup
  val witnessRead = s.dequeues > 0
  val witnessDocument = s.documents > 0
  // Desired stricter obligation, intentionally separate from code-as-built
  // safety: malformed/binding-invalid commits currently get counted/recorded
  // and read scope before whole preflight. This predicate has a counterexample
  // in the model and must not be reported as an established invariant.
  val desiredWholeBeforeOwnerIO =
    (s.req.route == Commit and not(whole(s.req))) implies
      s.records == 0 and s.scopeReads == 0
  action step: bool = any {receive(validCommit), receive(validBar), receive(validPopup),
    receive(validEvents), receive(validDocument), receive({...validCommit, host: false}),
    receive({...validCommit, origin: Foreign}), receive({...validEvents, api: false}),
    receive({...validCommit, duplicate: true}), receive({...validCommit, forbidden: true}),
    receive({...validCommit, observed: 11}), receive({...validCommit, secondBinding: false}),
    receive({...validCommit, payload: false}), receive({...validBar, role: Controller}),
    receive({...validEvents, method: Options}), dispatch, close}
}
