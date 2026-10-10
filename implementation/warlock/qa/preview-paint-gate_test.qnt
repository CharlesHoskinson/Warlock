module previewPaintGateTests {
  import previewPaintGate.* from "./preview-paint-gate"
  action check(ok:bool):bool=all{assert(ok and safety),s'=s}
  run acquireWaitsForOpportunityTest=init.then(queue(1,1)).then(check(s.dispatches==0 and s.pending==Set((1,1))))
  run paintedAcquireDispatchesOnceTest=init.then(queue(1,1)).then(paint(1)).then(paint(1)).then(check(s.dispatches==1 and s.pending==Set()))
  run cancellationBeforePaintNeverCapturesTest=init.then(queue(1,1)).then(cancel(1)).then(paint(1)).then(check(s.dispatches==0 and s.controls==1))
  run independentJobSurvivesCancellationTest=init.then(queue(1,1)).then(queue(2,2)).then(cancel(1)).then(paint(2)).then(check(s.sent==Set((2,2)) and s.dispatches==1))
  run foreignTicketCannotCaptureTest=init.then(queue(1,1)).then(paint(9)).then(check(s.dispatches==0 and s.pending==Set((1,1))))
  run controlsNeverWaitForPaintTest=init.then(queue(1,1)).then(control).then(check(s.controls==1 and s.dispatches==0 and s.pending==Set((1,1))))
  run lateCancelCannotReplayAcquireTest=init.then(queue(1,1)).then(paint(1)).then(cancel(1)).then(paint(1)).then(check(s.dispatches==1 and s.controls==1))
  run sameWindowDifferentJobKeepsFreshRequestTest=init.then(queue(1,1)).then(cancel(1)).then(queue(2,2)).then(paint(1)).then(paint(2)).then(check(s.sent==Set((2,2)) and s.dispatches==1))
}
