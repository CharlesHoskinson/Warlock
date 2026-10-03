module observer {
  type Input = { kind: str, epoch: int, seq: int, rev: int, req: int, content: int }
  type State = { epoch: int, seq: int, rev: int, content: int, floor: int,
    request: int, pending: int, phase: str, effects: int, input: Input }
  var s: State
  pure def input(k, e, n, r, q, c) = {kind:k, epoch:e, seq:n, rev:r, req:q, content:c}
  pure def maximum(a,b) = if (a > b) a else b
  pure def issue(t, phase) = { ...t, request:t.request+1, pending:t.request+1, phase:phase, effects:1 }
  pure def block(t, n) = if (t.phase == "Gap") { ...t, floor:maximum(t.floor,n), effects:0 }
    else issue({ ...t, floor:maximum(t.floor,n) }, "Gap")
  action init = s' = {epoch:0, seq:-1, rev:-1, content:0, floor:0, request:0, pending:0,
    phase:"Detached", effects:0, input:input("init",0,0,0,0,0)}
  action attach(e) = all {
    e > 0,
    s' = if (s.epoch == e) { ...s, effects:0, input:input("attach",e,0,0,0,0) }
      else {epoch:e, seq:-1, rev:-1, content:0, floor:0, request:1, pending:1,
        phase:"Awaiting", effects:1, input:input("attach",e,0,0,0,0)}
  }
  action delta(n,r,c,e) = all {
    n >= 0, r >= 0, c >= 0, c <= 1,
    val t = { ...s, effects:0, input:input("delta",e,n,r,0,c) }
    s' = if (s.phase == "Detached" or e != s.epoch or n <= s.seq) t
      else if (s.seq == -1 or s.phase != "Coherent" or n != s.seq+1 or r < s.rev or (r == s.rev and c != s.content)) block(t,n)
      else { ...t, seq:n, rev:r, content:c, floor:n }
  }
  action snapshot(n,r,q,c,e) = all {
    n >= 0, r >= 0, c >= 0, c <= 1,
    val t = { ...s, effects:0, input:input("snapshot",e,n,r,q,c) }
    val valid = n >= s.floor and (s.seq == -1 or
      (n == s.seq and r == s.rev and c == s.content) or
      (n != s.seq and (r > s.rev or (r == s.rev and c == s.content))))
    s' = if (s.phase == "Detached" or e != s.epoch or q != s.pending or q == 0) t
      else if (valid) { ...t, seq:n, rev:r, content:c, floor:n, pending:0, phase:"Coherent" }
      else issue(t,"Gap")
  }
  action disconnect = s' = { ...s, phase:"Detached", pending:0, effects:0, input:input("disconnect",0,0,0,0,0) }
  action refresh = s' = if (s.phase == "Detached") { ...s, effects:0, input:input("refresh",0,0,0,0,0) }
    else issue({ ...s, input:input("refresh",0,0,0,0,0) },"Awaiting")
  action malformed = s' = if (s.phase == "Detached") { ...s, effects:0, input:input("malformed",0,0,0,0,0) }
    else block({ ...s, input:input("malformed",0,0,0,0,0) },s.floor)
  action noop = s' = { ...s, effects:0, input:input("noop",0,0,0,0,0) }
  val safety = s.seq <= s.floor and s.effects <= 1 and s.pending <= s.request and
    (s.phase != "Coherent" or (s.epoch > 0 and s.seq >= 0 and s.pending == 0))
  action step = any {
    attach(1), attach(2), delta(s.floor+1,maximum(s.rev,0)+1,0,s.epoch),
    delta(s.floor+2,maximum(s.rev,0)+2,1,s.epoch), delta(0,0,0,1),
    snapshot(s.floor,maximum(s.rev,0)+1,maximum(s.pending,1),0,s.epoch),
    snapshot(maximum(s.floor,1)-1,0,maximum(s.pending,1),1,s.epoch),
    snapshot(s.floor+1,maximum(s.rev,0)+1,maximum(s.request,1),1,2),
    disconnect, refresh, malformed, noop
  }
  run contiguousTest = init.then(attach(1)).then(snapshot(0,0,1,0,1)).then(delta(1,1,0,1)).then(all { assert(s.phase == "Coherent" and s.seq == 1), noop })
  run gapTest = init.then(attach(1)).then(snapshot(0,0,1,0,1)).then(delta(2,2,1,1)).then(all { assert(s.phase == "Gap" and s.seq == 0 and s.pending == 2), noop })
  run lateDeltaTest = init.then(attach(1)).then(snapshot(0,0,1,0,1)).then(delta(2,2,0,1)).then(delta(1,1,0,1)).then(all { assert(s.phase == "Gap" and s.floor == 2), noop })
  run oldResponseTest = init.then(attach(1)).then(snapshot(0,0,1,0,1)).then(delta(3,3,0,1)).then(snapshot(2,2,2,0,1)).then(snapshot(3,3,2,0,1)).then(all { assert(s.phase == "Gap" and s.pending == 3), noop })
  run recoveryTest = init.then(attach(1)).then(snapshot(0,0,1,0,1)).then(delta(3,3,0,1)).then(snapshot(2,2,2,0,1)).then(snapshot(3,3,3,0,1)).then(all { assert(s.phase == "Coherent" and s.seq == 3), noop })
  run wrongEpochTest = init.then(attach(1)).then(snapshot(0,0,1,0,1)).then(delta(1,1,1,2)).then(all { assert(s.seq == 0 and s.phase == "Coherent"), noop })
  run revisionTest = init.then(attach(1)).then(snapshot(0,7,1,0,1)).then(delta(1,6,0,1)).then(all { assert(s.phase == "Gap" and s.rev == 7), noop })
  run duplicateTest = init.then(attach(1)).then(snapshot(0,0,1,0,1)).then(delta(1,1,0,1)).then(delta(1,9,1,1)).then(all { assert(s.seq == 1 and s.rev == 1 and s.content == 0), noop })
  run rebindTest = init.then(attach(1)).then(snapshot(0,0,1,0,1)).then(attach(2)).then(snapshot(9,9,1,0,1)).then(all { assert(s.phase == "Awaiting" and s.seq == -1), noop })
  run disconnectedTest = init.then(attach(1)).then(snapshot(0,0,1,0,1)).then(disconnect).then(delta(1,1,1,1)).then(attach(1)).then(all { assert(s.phase == "Detached" and s.seq == 0), noop })
  run conflictingContentTest = init.then(attach(1)).then(snapshot(0,0,1,0,1)).then(delta(1,0,1,1)).then(all { assert(s.phase == "Gap" and s.content == 0), noop })
  run malformedTest = init.then(attach(1)).then(snapshot(0,0,1,0,1)).then(malformed).then(malformed).then(all { assert(s.phase == "Gap" and s.request == 2), noop })
}
