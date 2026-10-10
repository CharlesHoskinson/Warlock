module max_overlap {
  // ELM-REN-015/max-input-region. Two native roots, matched internal/client
  // modes abstracted as 0 ordinary / 1 MAX / 2 fullscreen. This sampled model
  // excludes ABI, Wayland commits, transforms, pixels and actual native seats.
  type State = { modes: List[int], floating: List[bool],
    hole: bool, revision: int, paintedRevision: int, painted: int,
    recipient: int, hitRevision: int, rejected: int, staleHits: int }
  var s: State
  pure def eligible(now: State, id: int): bool =
    now.floating[id] and now.modes[id] != 2 and
    (now.modes[1-id] == 0 or (now.modes[1-id] == 1 and now.floating[1-id]))
  pure def maximize(now: State, id: int): State =
    if (now.modes[id] == 1 and eligible(now,id)) now
    else if (eligible(now, id)) { ...now, modes: now.modes.replaceAt(id, 1),
      revision: now.revision + 1, recipient: -1 }
    else { ...now, rejected: now.rejected + 1 }
  action init = s' = { modes: [0, 0], floating: [true, true],
    hole: false, revision: 0, paintedRevision: -1, painted: -1,
    recipient: -1, hitRevision: -1, rejected: 0, staleHits: 0 }
  action max(id: int): bool = s' = maximize(s, id)
  action restore(id: int): bool = s' = { ...s, modes: s.modes.replaceAt(id,0),
    revision: s.revision + 1, recipient: -1 }
  action changeHole = s' = { ...s, hole: not(s.hole), revision: s.revision + 1, recipient: -1 }
  action fullscreenPeer = s' = { ...s, modes: [0,2], revision: s.revision + 1, recipient: -1 }
  action tiledMaxPeer = s' = { ...s, modes: [0,1], floating: [true,false],
    revision: s.revision + 1, recipient: -1 }
  action paint = all { s.modes == [1,1],
    s' = { ...s, painted: 1, paintedRevision: s.revision } }
  action click = all { s.modes == [1,1],
    s' = if (s.paintedRevision == s.revision) { ...s,
      recipient: if(s.hole) 0 else 1, hitRevision: s.revision }
    else { ...s, rejected: s.rejected + 1, staleHits: s.staleHits + 1 } }
  action step = any { max(0), max(1), restore(0), restore(1), changeHole,
    fullscreenPeer, tiledMaxPeer, paint, click }
  val safety = s.recipient == -1 or
    (s.painted == 1 and s.hitRevision == s.paintedRevision
      and s.hitRevision == s.revision and s.recipient == (if(s.hole) 0 else 1))
  val bothMax = s.modes == [1,1]
  val holeLower = s.hole and s.painted == 1 and s.recipient == 0
  val stalePaintRefused = s.staleHits > 0 and s.paintedRevision != s.revision
}
