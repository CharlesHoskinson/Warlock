// One local editor, two abstract routes: Keep=0, Alternate=1, Default=2.
// Other route fixed; counters stay below uint64 exhaustion. Bound read/write
// deliveries are separate from requests. No native/storage atomicity, crash
// durability, changing frontend binding, GUI or native effect proof is claimed.
module ShortcutDraft {
  type Phase = Editing | Waiting | Unknown
  type Audit = { read: bool, preserve: bool, a: int, b: int, submitted: int, revision: int }
  type Facts = { revision: int, a: int, b: int, nativeA: int, nativeB: int,
    defaultA: bool, defaultB: bool, alternateA: bool, alternateB: bool }
  type State = { phase: Phase, binding: int, revision: int, storedA: int, storedB: int,
    draftA: int, draftB: int, nativeA: int, nativeB: int,
    conflictA: bool, conflictB: bool, inventory: bool, defaultA: bool, defaultB: bool,
    alternateA: bool, alternateB: bool, expectedRequest: int, nextRequest: int,
    submitted: int, pendingRequest: int, pendingA: int, pendingB: int, audit: Audit }
  var s: State
  pure def dirty(x: State): bool = x.draftA != x.storedA or x.draftB != x.storedB
  pure def allowed(choice: int, normal: bool, alternate: bool): bool =
    choice == 0 or (choice == 1 and alternate) or (choice == 2 and normal)
  pure def quiet(x: State): State = {...x, audit: {...x.audit, read: false}}
  pure def readBase(x: State): State = {...x, expectedRequest: 0,
    audit: {read: true, preserve: dirty(x) or x.phase != Editing or x.conflictA or x.conflictB,
      a: x.draftA, b: x.draftB, submitted: x.submitted, revision: x.revision}}
  // Intended pure read contract, independent of the request guard in Desktop.
  pure def observed(x: State, f: Facts): State = {
    val base = readBase(x)
    val keep = dirty(x) or x.phase != Editing or x.conflictA or x.conflictB
    val a = if (keep) x.draftA else f.a
    val b = if (keep) x.draftB else f.b
    val settled = x.phase != Editing and f.a == x.pendingA and f.b == x.pendingB
      and f.nativeA == x.pendingA and f.nativeB == x.pendingB
    if (f.revision < x.revision) base else
      {...base, revision: f.revision, storedA: f.a, storedB: f.b,
        draftA: a, draftB: b, nativeA: f.nativeA, nativeB: f.nativeB,
        inventory: true, defaultA: f.defaultA, defaultB: f.defaultB,
        alternateA: f.alternateA, alternateB: f.alternateB,
        conflictA: not(settled) and keep and ((x.conflictA and not(a == f.a and a == f.nativeA)) or (x.storedA != f.a and a != f.a)),
        conflictB: not(settled) and keep and ((x.conflictB and not(b == f.b and b == f.nativeB)) or (x.storedB != f.b and b != f.b)),
        phase: if (settled) Editing else x.phase}
  }
  pure def facts(x: State): Facts = {revision: x.revision, a: x.storedA, b: x.storedB,
    nativeA: x.nativeA, nativeB: x.nativeB, defaultA: x.defaultA, defaultB: x.defaultB,
    alternateA: x.alternateA, alternateB: x.alternateB}
  pure def matches(x: State, binding: int, request: int): bool =
    x.phase != Editing and binding == x.binding and request == x.pendingRequest
  action init = s' = {phase: Editing, binding: 1, revision: 1, storedA: 0, storedB: 0,
    draftA: 0, draftB: 0, nativeA: 0, nativeB: 0, conflictA: false, conflictB: false,
    inventory: true, defaultA: true, defaultB: true, alternateA: true, alternateB: true,
    expectedRequest: 0, nextRequest: 0, submitted: 0, pendingRequest: 0, pendingA: 0, pendingB: 0,
    audit: {read: false, preserve: false, a: 0, b: 0, submitted: 0, revision: 1}}
  val editable = s.phase == Editing and s.inventory and s.expectedRequest == 0
  val ready = editable and not(s.conflictA) and not(s.conflictB)
    and allowed(s.draftA, s.defaultA, s.alternateA) and allowed(s.draftB, s.defaultB, s.alternateB)
  val differs = dirty(s) or s.nativeA != s.draftA or s.nativeB != s.draftB
  action editA = all {editable, s.alternateA, s' = {...quiet(s), draftA: 1, conflictA: false}}
  action defaultA = all {editable, s.defaultA, s' = {...quiet(s), draftA: 2, conflictA: false}}
  action keepA = all {editable, s' = {...quiet(s), draftA: 0, conflictA: false}}
  action reaffirmB = all {editable, allowed(s.draftB, s.defaultB, s.alternateB), s.conflictB,
    s' = {...quiet(s), conflictB: false}}
  action beginRead = all {s.expectedRequest == 0,
    s' = {...quiet(s), nextRequest: s.nextRequest + 1, expectedRequest: s.nextRequest + 1}}
  // Old observe counterexample is intentionally absent from the normal step.
  action currentBug = all {s.expectedRequest > 0, dirty(s),
    s' = {...readBase(s), draftA: s.storedA, draftB: s.storedB, phase: Editing}}
  action sameRead = all {s.expectedRequest > 0, s' = observed(s, facts(s))}
  action changedRead = all {s.expectedRequest > 0,
    s' = observed(s, {...facts(s), revision: s.revision + 1, a: 2, b: 2,
      nativeA: 0, nativeB: 0, defaultA: true, defaultB: true, alternateA: true, alternateB: true})}
  action unavailableRead = all {s.expectedRequest > 0,
    s' = observed(s, {...facts(s), defaultA: false, alternateA: false, nativeA: 0})}
  action failRead = all {s.expectedRequest > 0, s' = {...readBase(s), inventory: false}}
  action staleRead = all {s.expectedRequest > 0, s.revision > 1,
    s' = observed(s, {...facts(s), revision: s.revision - 1})}
  action submit = all {ready, differs,
    s' = {...quiet(s), phase: Waiting, pendingA: s.draftA, pendingB: s.draftB,
      pendingRequest: s.nextRequest + 1, nextRequest: s.nextRequest + 1, submitted: s.submitted + 1}}
  action lose = all {s.phase == Waiting, s' = {...quiet(s), phase: Unknown}}
  action storedMismatch = all {s.expectedRequest > 0, s.phase != Editing,
    s' = observed(s, {...facts(s), revision: s.revision + 1,
      a: if (s.pendingA == 0) 1 else 0, b: s.pendingB, nativeA: s.pendingA, nativeB: s.pendingB,
      defaultA: true, defaultB: true, alternateA: true, alternateB: true})}
  action nativeMismatch = all {s.expectedRequest > 0, s.phase != Editing,
    s' = observed(s, {...facts(s), revision: s.revision + 1, a: s.pendingA, b: s.pendingB,
      nativeA: if (s.pendingA == 0) 1 else 0, nativeB: s.pendingB,
      defaultA: true, defaultB: true, alternateA: true, alternateB: true})}
  action newerPendingRead = all {s.expectedRequest > 0, s.phase != Editing,
    s' = observed(s, {...facts(s), revision: s.revision + 2, a: 2, b: 2,
      nativeA: 0, nativeB: 0, defaultA: true, defaultB: true, alternateA: true, alternateB: true})}
  action exactRead = all {s.expectedRequest > 0, s.phase != Editing,
    s' = observed(s, {...facts(s), a: s.pendingA, b: s.pendingB,
      nativeA: s.pendingA, nativeB: s.pendingB,
      defaultA: true, defaultB: true, alternateA: true, alternateB: true})}
  pure def committed(x: State, revision: int, nativeMatches: bool): Facts =
    {...facts(x), revision: revision, a: x.pendingA, b: x.pendingB,
      nativeA: if (nativeMatches) x.pendingA else x.nativeA,
      nativeB: if (nativeMatches) x.pendingB else x.nativeB,
      defaultA: true, defaultB: true, alternateA: true, alternateB: true}
  pure def outcome(x: State, f: Facts, needsNative: bool): State =
    if (f.revision < x.revision or f.a != x.pendingA or f.b != x.pendingB or
      (needsNative and (f.nativeA != x.pendingA or f.nativeB != x.pendingB))) quiet(x) else
      {...quiet(x), phase: Editing, revision: f.revision, storedA: f.a, storedB: f.b,
        nativeA: f.nativeA, nativeB: f.nativeB, inventory: true,
        defaultA: f.defaultA, defaultB: f.defaultB, alternateA: f.alternateA, alternateB: f.alternateB,
        conflictA: x.conflictA and not(f.nativeA == x.pendingA and f.nativeB == x.pendingB),
        conflictB: x.conflictB and not(f.nativeA == x.pendingA and f.nativeB == x.pendingB)}
  action storedReceipt(binding: int, request: int, f: Facts): bool = all {matches(s, binding, request), s' = outcome(s, f, false)}
  action savedReceipt(binding: int, request: int, f: Facts): bool = all {matches(s, binding, request), s' = outcome(s, f, true)}
  action refusedReceipt(binding: int, request: int): bool = all {matches(s, binding, request), s' = {...quiet(s), phase: Editing}}
  action ignoredWrite(binding: int, request: int): bool = all {not(matches(s, binding, request)), s' = quiet(s)}
  action foreignWrite = ignoredWrite(s.binding + 1, s.pendingRequest)
  action wrongWrite = ignoredWrite(s.binding, s.pendingRequest + 1)
  action foreignRead = all {s.expectedRequest > 0, s' = s} // rejected before observe
  action staleStored = all {s.revision > 1, storedReceipt(s.binding, s.pendingRequest, committed(s, s.revision - 1, false))}
  action stored = storedReceipt(s.binding, s.pendingRequest, committed(s, s.revision, false))
  action staleSaved = all {s.revision > 1, savedReceipt(s.binding, s.pendingRequest, committed(s, s.revision - 1, true))}
  action saved = savedReceipt(s.binding, s.pendingRequest, committed(s, s.revision, true))
  action refused = refusedReceipt(s.binding, s.pendingRequest)
  action step = any {editA, defaultA, keepA, reaffirmB, beginRead, sameRead, changedRead,
    unavailableRead, failRead, staleRead, submit, lose, storedMismatch, nativeMismatch,
    newerPendingRead, staleStored, stored, staleSaved, saved, refused, exactRead, foreignWrite, wrongWrite, foreignRead}
  val readPreservesIntent = s.audit.read and s.audit.preserve implies s.draftA == s.audit.a and s.draftB == s.audit.b
  val readNeverSubmits = s.audit.read implies s.submitted == s.audit.submitted
  val readNeverRollsBack = s.audit.read implies s.revision >= s.audit.revision
  val pendingIntentStable = s.phase != Editing implies s.draftA == s.pendingA and s.draftB == s.pendingB
  val conflictBlocksSave = (s.conflictA or s.conflictB) implies not(ready)
  val pendingBlocksSave = s.phase != Editing implies not(ready)
}
