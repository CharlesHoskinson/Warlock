// Bounded source correspondence: Profile.hs trusted profile and limits;
// Desktop.hs decodeDesktopCommit/parseRequest and gateway codec;
// Backend.hs handler/lastWrite and PinStore save. ELM-ARC-003, ELM-DEL-011.
// One abstract authenticated session, two ordered requests, one pin request ID.
// Byte counts and parser/credential predicates stand for concrete checks; this
// does not model JSON bytes, OS durability, transport timing, GUI or acceptance.
module uiNativeStream {
  type Profile = Native | Desktop
  type Method = Empty | Catalog | Pins | UnknownMethod | PathSelector
  type Outcome = None | Pending | Saved | Refused | Unknown
  type Request = { method: Method, bytes: int, schema: bool, version: int, binding: int }
  type Frame = { bytes: int, schema: bool, version: int, kind: str, kernel: bool, session: bool, first: Request, second: Request }
  type State = { profile: Profile, phase: str, frame: Frame, callbacks: int, reads: int, writes: int, durable: int, disposition: Outcome, lastId: int, pending: Method, resume: str, rejected: int }
  var s: State

  pure def request(m: Method): Request = { method: m, bytes: 100, schema: true, version: 3, binding: 1 }
  pure def frame(a: Method, b: Method): Frame = { bytes: 200, schema: true, version: 1, kind: "view-commit", kernel: true, session: true, first: request(a), second: request(b) }
  pure def validRequest(r: Request): bool = r.method == Empty or and {
    Set(Catalog, Pins).contains(r.method), r.bytes <= 8192, r.bytes > 0,
    r.schema, r.version == 3, r.binding == 1
  }
  pure def validDesktop(f: Frame): bool = and {
    f.bytes > 0, f.bytes <= 131072, f.schema, f.version == 1,
    f.kind == "view-commit", f.kernel, f.session,
    validRequest(f.first), validRequest(f.second)
  }
  pure def validLegacy(bytes: int, version: int, schema: bool, kernel: bool, session: bool): bool =
    bytes > 0 and bytes <= 65536 and Set(1, 2).contains(version) and schema and kernel and session
  // Gateway provenance is supplied by the trusted owner, not by payload text.
  pure def validGateway(bytes: int, inner: int, schema: bool, bridge: int, kind: str, version: int, binding: int, provenance: bool): bool = and {
    bytes > 0, bytes <= 1048704, inner > 0, inner <= 1048576,
    schema, bridge == 1, kind == "native-event", version == 3,
    binding == 1, provenance
  }
  action initProfile(p: Profile): bool = s' = { profile: p, phase: "idle", frame: frame(Empty, Empty), callbacks: 0, reads: 0, writes: 0, durable: 0, disposition: None, lastId: 0, pending: Empty, resume: "done", rejected: 0 }
  // profile is immutable through every transition; init is trusted selection.
  action init: bool = initProfile(Desktop)
  action initNative: bool = initProfile(Native)
  action offer(f: Frame): bool = all {
    s.phase == "idle", s.callbacks < 3, s.rejected < 3,
    s' = if (s.profile == Desktop and validDesktop(f))
      { ...s, phase: "checked", frame: f }
    else { ...s, frame: f, rejected: s.rejected + 1 }
  }
  action callback: bool = all {
    s.phase == "checked", s' = { ...s, phase: "first", callbacks: s.callbacks + 1 }
  }
  // Ordered iteration starts only after both requests passed the whole gate.
  action dispatch: bool = {
    val r = if (s.phase == "first") s.frame.first else s.frame.second
    all {
      Set("first", "second").contains(s.phase), s.reads < 3, s.writes < 3,
      s' = if (r.method == Pins and s.lastId == 0)
        { ...s, phase: "store", resume: if (s.phase == "first") "second" else "done", pending: Pins, lastId: 1, disposition: Pending, writes: s.writes + 1 }
      else if (r.method == Catalog)
        { ...s, phase: if (s.phase == "first") "second" else "done", reads: s.reads + 1 }
      else { ...s, phase: if (s.phase == "first") "second" else "done" }
    }
  }
  // A real commit is distinct from a refused or uncertain store completion.
  action complete(outcome: Outcome): bool = all {
    s.phase == "store", Set(Saved, Refused, Unknown).contains(outcome),
    s' = { ...s, phase: s.resume, pending: Empty, disposition: outcome,
      durable: if (outcome == Saved) s.durable + 1 else s.durable }
  }
  action reset: bool = all { s.phase == "done", s' = { ...s, phase: "idle" } }
  action step: bool = {
    nondet f = Set(frame(Catalog, Empty), frame(Pins, Empty), frame(Empty, Empty), frame(Catalog, UnknownMethod), frame(PathSelector, Empty), { ...frame(Catalog, Empty), kernel: false }).oneOf()
    nondet o = Set(Saved, Refused, Unknown).oneOf()
    any { offer(f), callback, dispatch, complete(o), reset }
  }
  val safety: bool = and {
    s.durable <= s.writes, s.writes <= 1,
    s.disposition == Saved implies s.durable == 1,
    s.phase == "checked" implies validDesktop(s.frame),
    Set("first", "second", "store").contains(s.phase) implies validDesktop(s.frame),
    s.pending == Pins implies s.phase == "store" and s.lastId == 1
  }
  val catalogWitness: bool = s.reads > 0
  val pinsWitness: bool = s.disposition == Saved and s.durable == 1
  val emptyWitness: bool = s.phase == "done" and s.callbacks > 0 and s.reads == 0 and s.writes == 0
  val refusalWitness: bool = s.disposition == Refused
  val badBatchWitness: bool = s.rejected > 0 and s.frame.first.method == Catalog and s.frame.second.method == UnknownMethod and s.callbacks == 0 and s.reads == 0 and s.writes == 0
  val unknownWitness: bool = s.disposition == Unknown and s.writes == 1
}
