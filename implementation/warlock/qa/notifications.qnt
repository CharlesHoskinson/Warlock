module Notifications {
  var service: int
  var incarnation: int
  var live: bool
  var queuedService: int
  var queuedIncarnation: int
  var pending: bool
  var dispatched: Set[(int, int)]
  var counts: int
  action init = all {service'=1, incarnation'=1, live'=true, queuedService'=0, queuedIncarnation'=0, pending'=false, dispatched'=Set(), counts'=0}
  val current = queuedService == service and queuedIncarnation == incarnation and live and not(dispatched.contains((service,incarnation)))
  action capture = all {not(pending), live, queuedService'=service, queuedIncarnation'=incarnation, pending'=true, service'=service, incarnation'=incarnation, live'=live, dispatched'=dispatched, counts'=counts}
  action replace = all {incarnation'=incarnation+1, live'=true, service'=service, queuedService'=queuedService, queuedIncarnation'=queuedIncarnation, pending'=pending, dispatched'=dispatched, counts'=counts}
  action expire = all {live'=false, service'=service, incarnation'=incarnation, queuedService'=queuedService, queuedIncarnation'=queuedIncarnation, pending'=pending, dispatched'=dispatched, counts'=counts}
  action deliver = all {pending, current, live'=false, dispatched'=dispatched.union(Set((service,incarnation))), counts'=counts+1, pending'=false, service'=service, incarnation'=incarnation, queuedService'=queuedService, queuedIncarnation'=queuedIncarnation}
  action refuse = all {pending, not(current), pending'=false, live'=live, dispatched'=dispatched, counts'=counts, service'=service, incarnation'=incarnation, queuedService'=queuedService, queuedIncarnation'=queuedIncarnation}
  action unknown = all {pending, current, live'=false, dispatched'=dispatched.union(Set((service,incarnation))), counts'=counts+1, pending'=true, service'=service, incarnation'=incarnation, queuedService'=queuedService, queuedIncarnation'=queuedIncarnation}
  action restart = all {service'=service+1, incarnation'=1, live'=true, queuedService'=queuedService, queuedIncarnation'=queuedIncarnation, pending'=pending, dispatched'=dispatched, counts'=counts}
  action verify(condition: bool): bool = all {assert(condition), service'=service, incarnation'=incarnation, live'=live, queuedService'=queuedService, queuedIncarnation'=queuedIncarnation, pending'=pending, dispatched'=dispatched, counts'=counts}
  action step = any {capture,replace,expire,deliver,refuse,unknown,restart}
  val safety = counts == dispatched.size() and counts >= 0 and service > 0 and incarnation > 0
  run currentDispatchOnceTest = init.then(capture).then(deliver).then(verify(counts == 1 and not(live) and not(current)))
  run expiredQueuedRefusalTest = init.then(capture).then(expire).then(refuse).then(verify(counts == 0))
  run reusedIdRejectsOldIncarnationTest = init.then(capture).then(expire).then(replace).then(refuse).then(verify(live and incarnation == 2 and counts == 0))
  run replacementRejectsQueuedActionTest = init.then(capture).then(replace).then(refuse).then(verify(counts == 0 and live))
  run receiptLossCannotReplayTest = init.then(capture).then(unknown).then(refuse).then(verify(counts == 1 and not(live)))
  run restartRejectsOldServiceTest = init.then(capture).then(restart).then(refuse).then(verify(counts == 0 and live and service == 2))
}
