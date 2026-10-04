module terminal {
 var s: { binding: int, active: bool, request: int, expected: int, geometry: int, retry: bool, pending: bool, deferred: bool, refused: bool, issued: int }
 action init = s' = { binding: 1, active: true, request: 59, expected: 58, geometry: 59, retry: false, pending: false, deferred: false, refused: false, issued: 0 }
 action terminal(binding: int, request: int) =
  if (s.active and binding == s.binding and request == s.expected and request > 0)
  s' = { ...s, expected: 0, retry: true } else s' = s
 val canRetry = s.active and s.retry and s.expected == 0 and not s.pending and not s.deferred and not s.refused
 action drain = if (canRetry) s' = { ...s, request: s.request + 1, expected: s.request + 1, retry: false, issued: s.issued + 1 } else s' = s
 action effectOn = s' = { ...s, pending: true }
 action effectOff = s' = { ...s, pending: false }
 action deferOn = s' = { ...s, deferred: true }
 action deferOff = s' = { ...s, deferred: false }
 action refuseOn = s' = { ...s, refused: true }
 action refuseOff = s' = { ...s, refused: false }
 action geometryDone = s' = { ...s, geometry: 0 }
 action disconnect = s' = { ...s, active: false, expected: 0, geometry: 0, retry: false }
 action step = any { terminal(1,58), terminal(2,58), terminal(1,57), drain, effectOn, effectOff, deferOn, deferOff, refuseOn, refuseOff, geometryDone, disconnect }
 val safety = (not s.retry or s.expected == 0) and s.request >= 59 and s.issued <= s.request - 59 and (s.active or (not s.retry and s.expected == 0))
 run retryProjectionOnlyTest = init.then(terminal(1,58)).then(drain).then(all { assert(s.expected == 60 and s.geometry == 59 and s.issued == 1), s' = s })
 run foreignBindingIgnoredTest = init.then(terminal(2,58)).then(drain).then(all { assert(s.expected == 58 and s.issued == 0), s' = s })
 run staleRequestIgnoredTest = init.then(terminal(1,57)).then(drain).then(all { assert(s.expected == 58 and s.issued == 0), s' = s })
 run duplicateTerminalIgnoredTest = init.then(terminal(1,58)).then(drain).then(terminal(1,58)).then(drain).then(all { assert(s.expected == 60 and s.issued == 1), s' = s })
 run pendingEffectDefersTest = init.then(effectOn).then(terminal(1,58)).then(drain).then(all { assert(s.retry and s.expected == 0 and s.issued == 0), s' = s }).then(effectOff).then(drain).then(all { assert(s.expected == 60 and s.issued == 1), s' = s })
 run dispositionDefersTest = init.then(deferOn).then(terminal(1,58)).then(drain).then(all { assert(s.retry and s.issued == 0), s' = s }).then(deferOff).then(drain).then(all { assert(s.issued == 1), s' = s })
 run transportDefersTest = init.then(refuseOn).then(terminal(1,58)).then(drain).then(all { assert(s.retry and s.issued == 0), s' = s }).then(refuseOff).then(drain).then(all { assert(s.issued == 1), s' = s })
 run disconnectRevokesTest = init.then(terminal(1,58)).then(disconnect).then(drain).then(all { assert(not s.retry and s.issued == 0), s' = s })
}
