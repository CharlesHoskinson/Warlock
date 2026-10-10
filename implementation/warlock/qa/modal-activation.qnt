module modal_activation {
  // REN-015/max-modal-focus and GNO-006/hit-modal-redirect.
  // One serialized ordinary MAX seat. Modal constraints are abstract cases:
  // 0 none, 1 single, 2 nested, 3 ambiguous, 4 cyclic, 5 ineligible.
  // No claim about native graph discovery, ABI, transforms, timing, grabs,
  // lock/layers, presentation or AT. These need separate native evidence.
  type State = { constraint: int, ready: bool, parentPoint: bool,
    protected: bool, focus: int, rootOrder: List[int], modalAbove: bool,
    suppressed: bool, presses: int, releases: int,
    redirects: int, refusals: int, synthetic: int, staleMutations: int }
  var s: State
  action init = s' = { constraint: 0, ready: true, parentPoint: true,
    protected: false, focus: 1, rootOrder: [0,1], modalAbove: false,
    suppressed: false, presses: 0, releases: 0,
    redirects: 0, refusals: 0, synthetic: 0, staleMutations: 0 }
  pure def recipient(now: State): int =
    if (now.constraint == 1) 2 else if (now.constraint == 2) 3 else -1
  pure def activation(now: State): State =
    if (now.protected) now // existing native owner retains input authority
    else if (not(now.ready)) { ...now, suppressed: true, refusals: now.refusals+1 }
    else if (now.parentPoint and now.constraint != 0)
      if (recipient(now) == -1) { ...now, suppressed: true, refusals: now.refusals+1 }
      else { ...now, suppressed: true, focus: recipient(now), modalAbove: true,
        redirects: now.redirects+1 }
    else { ...now, focus: if(now.parentPoint) 0 else 1, presses: now.presses+1 }
  action constraint(kind: int): bool = s' = { ...s, constraint: kind, ready: false }
  action commit = s' = { ...s, ready: true }
  action point(parent: bool): bool = s' = { ...s, parentPoint: parent }
  action protect = s' = { ...s, protected: not(s.protected) }
  action press = all { not(s.suppressed), s.presses == s.releases, s' = activation(s) }
  action release = all { s.suppressed or s.presses > s.releases,
    s' = if (s.suppressed) { ...s, suppressed: false }
         else { ...s, releases: s.releases+1 } }
  action step = any { constraint(0),constraint(1),constraint(2),constraint(3),
    constraint(4),constraint(5),commit,point(true),point(false),protect,press,release }
  val safety = s.synthetic == 0 and s.staleMutations == 0 and s.rootOrder == [0,1]
    and s.presses-s.releases >= 0 and s.presses-s.releases <= 1
    and not(s.suppressed and s.presses != s.releases)
  val modalFocused = s.focus == 2 and s.redirects > 0
  val nestedFocused = s.focus == 3 and s.redirects > 0
  val ambiguousRefused = s.constraint == 3 and s.refusals > 0
  val ownerAfterRetirement = s.constraint == 0 and s.focus == 0 and s.redirects > 0
}
