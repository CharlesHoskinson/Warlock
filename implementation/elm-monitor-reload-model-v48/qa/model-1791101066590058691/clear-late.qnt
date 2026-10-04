// Single event-loop reload dispatch, excluding actual monitor/render/DRM behavior.
module reload {
  type State = {requested:int, applied:int, captured:int, pending:bool, queued:int, running:bool, live:bool}
  var s: State
  action init = s' = {requested:0, applied:0, captured:0, pending:false, queued:0, running:false, live:true}
  action request = s' = if (s.live) {...s, requested:s.requested+1, pending:true,
                                      queued:if (s.pending) s.queued else s.queued+1} else s
  action idle = s' = if (s.queued>0 and not(s.running)) {
    ...s, queued:s.queued-1, pending:if (s.live) false else s.pending,
    running:s.live and s.pending, captured:if (s.live and s.pending) s.requested else s.captured
  } else s
  action render = s' = if (s.live and s.pending and not(s.running)) {
    ...s, pending:false, running:true, captured:s.requested
  } else s
  action complete = s' = if (s.running) {...s, applied:s.captured, running:false, pending:false} else s
  action stop = s' = {...s, live:false, running:false}
  action step = any {request, idle, render, complete, stop}
  val safety = s.applied<=s.requested and s.captured<=s.requested and s.queued>=0 and
               (s.pending and s.live implies s.queued>0) and (s.running implies s.live)
  run coalescedRequestsTest = init.then(request).then(request).then(request).then(all{assert(s.queued==1 and s.requested==3),s'=s})
  run noParentFrameNeededTest = init.then(request).then(idle).then(complete).then(all{assert(s.applied==1 and not(s.pending) and s.queued==0),s'=s})
  run renderWinsNoDuplicateTest = init.then(request).then(render).then(complete).then(idle).then(all{assert(s.applied==1 and s.queued==0 and not(s.running)),s'=s})
  run reentrantRequestSurvivesTest = init.then(request).then(idle).then(request).then(complete).then(all{assert(s.pending and s.queued==1 and s.applied==1),s'=s}).then(idle).then(complete).then(all{assert(s.applied==2 and not(s.pending)),s'=s})
  run renderReentrancySurvivesTest = init.then(request).then(render).then(request).then(complete).then(idle).then(complete).then(idle).then(all{assert(s.applied==2 and not(s.pending) and s.queued==0),s'=s})
  run stoppedTaskCannotApplyTest = init.then(request).then(stop).then(idle).then(complete).then(all{assert(s.applied==0 and not(s.running)),s'=s})
}
