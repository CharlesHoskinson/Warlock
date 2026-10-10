module menu_read_order {
  // ELM-UX-016: MenuBridge.compatiblePrepared / advancePrepared.
  // One Elm policy owner; authenticated post-close observations are atomic.
  // Each map value abstracts the COMPLETE window record, not only pin/MAX.
  // List order is presentation metadata. Missing/changed identities or facts
  // remain different maps. Native mutation, pixels, input and ABI are excluded.
  type State = {
    facts: int -> int, captured: int -> int,
    order: List[int], capturedOrder: List[int], scope: int, capturedScope: int,
    selected: bool, readReady: bool, issued: bool, unknown: bool,
    generation: int, delivered: Set[int], requests: int, rejected: int,
    unsafe: int
  }
  var s: State
  pure def compatible(now: State): bool =
    now.facts == now.captured and now.scope == now.capturedScope
  action init = s' = {
    facts: Map(1 -> 0, 2 -> 0), captured: Map(1 -> 0, 2 -> 0),
    order: [1, 2], capturedOrder: [1, 2], scope: 1, capturedScope: 1,
    selected: false, readReady: false, issued: false, unknown: false,
    generation: 0, delivered: Set(), requests: 0, rejected: 0, unsafe: 0
  }
  action captureSelection = all {
    not(s.selected) and not(s.issued) and not(s.unknown),
    s' = { ...s, captured: s.facts, capturedOrder: s.order,
      capturedScope: s.scope, selected: true, readReady: false,
      generation: s.generation + 1 }
  }
  action reorder = s' = { ...s, order: if (s.order == [1, 2]) [2, 1] else [1, 2] }
  action changeWindow(id: int): bool = s' = {
    ...s, facts: s.facts.set(id, 1 - s.facts.get(id)), readReady: false
  }
  action changeScope = s' = { ...s, scope: s.scope + 1, readReady: false }
  action staleRead = s' = s
  action currentRead = all { s.selected, s' = { ...s, readReady: true } }
  action settle = all {
    s.selected and s.readReady,
    s' = if (compatible(s)) {
      ...s, selected: false, readReady: false, issued: true,
      delivered: s.delivered.union(Set(s.generation)), requests: s.requests + 1,
      unsafe: s.unsafe + (if (s.delivered.contains(s.generation)) 1 else 0)
    } else { ...s, selected: false, readReady: false, rejected: s.rejected + 1 }
  }
  action definitive = all { s.issued and not(s.unknown), s' = { ...s, issued: false } }
  action lostOutcome = all { s.issued, s' = { ...s, unknown: true } }
  action retryUnknown = all { s.unknown, s' = s }
  action step = any {
    captureSelection, reorder, changeWindow(1), changeWindow(2), changeScope,
    staleRead, currentRead, settle, definitive, lostOutcome, retryUnknown
  }
  val safety = s.unsafe == 0 and s.requests == s.delivered.size()
    and (not(s.unknown) or s.issued) and (not(s.selected) or not(s.issued))
  val reorderedIssued = s.issued and s.order != s.capturedOrder
  val changedReadRefused = s.rejected > 0
  val unknownRetained = s.unknown and s.issued
}
