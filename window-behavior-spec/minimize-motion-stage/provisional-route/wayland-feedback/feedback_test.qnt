module feedback_test {
 import feedback.* from "./feedback"
 run presentedUsesCapturedOriginTest=init.then(fire(Request)).then(fire(Tick)).then(fire(Presented((1,1)))).then(all{assert(s.records.nth(0).x==0 and s.x==1 and allProps),fire(Tick)})
 run pendingNewSubmissionDoesNotInvalidateEarlierPresentationTest=init.then(fire(Request)).then(fire(Tick)).then(fire(Request)).then(fire(Presented((1,1)))).then(all{assert(s.accepted and s.pending.length()==1 and allProps),fire(Tick)})
 run discardedFrameHasNoOriginTest=init.then(fire(Request)).then(fire(Discard(1))).then(fire(Presented((1,1)))).then(all{assert(s.records.length()==0 and allProps),fire(Tick)})
 run oldWindowCannotPresentAfterReplacementTest=init.then(fire(Request)).then(fire(Replace)).then(fire(Presented((1,1)))).then(all{assert(s.records.length()==0 and allProps),fire(Tick)})
 run wrongOutputCannotSupplyOriginTest=init.then(fire(Request)).then(fire(Presented((1,2)))).then(all{assert(s.records.length()==0 and allProps),fire(Tick)})
 run olderFrameCannotRewindPresentedOriginTest=init.then(fire(Request)).then(fire(Tick)).then(fire(Request)).then(fire(Presented((2,1)))).then(fire(Presented((1,1)))).then(all{assert(s.records.length()==1 and s.records.nth(0).x==1 and allProps),fire(Tick)})
 run reversalCannotRelabelPriorPresentationTest=init.then(fire(Request)).then(fire(Reverse)).then(fire(Presented((1,1)))).then(all{assert(s.records.nth(0).token==1 and s.token==2 and allProps),fire(Tick)})
 run missingOrFullFeedbackCannotInventOriginTest=init.then(fire(Request)).then(fire(Request)).then(fire(Request)).then(fire(Request)).then(fire(Request)).then(fire(Presented((5,1)))).then(all{assert(s.records.length()==0 and s.pending.length()==4 and allProps),fire(Tick)})
}
