// UI007 restore-pending/restore-unknown status-scroll abstraction.
// One renderer. Frame validity and ordered publications abstract Presentation;
// epochs abstract opaque decimal UInt64 identities, with 3 standing for the
// maximum. Task delivery is asynchronous and may arrive after replacement.
// Bar.step seeds first status without a task; later text changes schedule one.
// Browser focus, actual scrolling and announcement delivery are not proved.
// Candidate namespace repair: reserved raw control IDs render as distinct
// non-reserved IDs. Raw input is not rejected; browser rendering is abstracted.
module status_scroll {
  type State = { publication: int, status: int, epoch: int, visible: bool, exhausted: bool,
    pending: Set[int], control: int, reset: int, resetEpoch: int, focus: int, draft: int }
  var s: State
  action init: bool = s' = {publication: 0, status: 0, epoch: 0, visible: false, exhausted: false,
    pending: Set(), control: 0, reset: 0, resetEpoch: 0, focus: 1, draft: 1}
  // Equal text preserves epoch. When identity space is exhausted, retire the
  // target rather than reuse an identity. Invalid/stale frames do not advance.
  pure def renderedControl(control: int): int = if (control > 0 and control <= 3) 0 else control
  action frameWithControl(pub: int, text: int, control: int): bool = all {pub > s.publication, text > 0,
    if (text == s.status) s' = {...s, publication: pub, control: renderedControl(control), visible: not(s.exhausted)}
    else if (s.epoch == 0) s' = {...s, publication: pub, control: renderedControl(control), status: text, epoch: 1, visible: true}
    else if (s.epoch < 3) s' = {...s, publication: pub, control: renderedControl(control), status: text, epoch: s.epoch + 1,
      visible: true, pending: s.pending.union(Set(s.epoch + 1))}
    else s' = {...s, publication: pub, control: renderedControl(control), status: text, visible: false, exhausted: true}}
  action frame(pub: int, text: int): bool = frameWithControl(pub, text, 0)
  // Malformed Presentation clears the snapshot without allocating an epoch.
  action invalid: bool = s' = {...s, visible: false}
  // A well-formed stale publication leaves the retained snapshot untouched.
  action stale: bool = s' = s
  action task(id: int): bool = all {s.pending.contains(id),
    if (s.visible and id == s.epoch) s' = {...s, pending: s.pending.exclude(Set(id)), reset: s.reset + 1, resetEpoch: id}
    else s' = {...s, pending: s.pending.exclude(Set(id))}}
  val safety = s.epoch >= 0 and s.epoch <= 3 and not(s.pending.contains(s.control)) and s.focus == 1 and s.draft == 1 and
    (s.reset > 0 implies s.resetEpoch > 0 and s.resetEpoch <= s.epoch)
  val witnessReset = s.reset > 0
  val witnessRetired = s.exhausted and not(s.visible) and s.epoch == 3
  val witnessPending = s.pending.size() > 0
  action step: bool = any {frame(1, 1), frame(2, 1), frame(2, 2), frame(3, 1), frame(3, 3), frame(4, 2),
    frameWithControl(3, 3, 2), invalid, stale, task(1), task(2), task(3)}
}
