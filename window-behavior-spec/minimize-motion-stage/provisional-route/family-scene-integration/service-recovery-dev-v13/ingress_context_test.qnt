module ingress_context_test {
 import ingress_context.* from "./ingress_context"
 action check(p:bool):bool=all{assert(p),s'=s}
 run receiptBeforeContextRevokesOldEndpointTest=init.then(fire(Reserve)).then(fire(Commit(1))).then(check(not(s.effect)))
 run reorderedOldContextCannotRetargetLatestTest=init.then(fire(Reserve)).then(fire(Reserve)).then(fire(Context({receipt:3,consistent:true}))).then(fire(Context({receipt:2,consistent:true}))).then(check(not(s.retarget) and s.activated==3))
 run contextFailureHasNoUnvalidatedNativeSettlementTest=init.then(fire(Reserve)).then(fire(Fail(2))).then(fire(Commit(2))).then(check(not(s.effect)))
 run inconsistentNativeContextCannotStartExpansionTest=init.then(fire(Reserve)).then(fire(Context({receipt:2,consistent:false}))).then(check(not(s.retarget)))
 run staleFailureCannotCancelLatestActivationTest=init.then(fire(Reserve)).then(fire(Reserve)).then(fire(Context({receipt:3,consistent:true}))).then(fire(Fail(2))).then(check(s.activated==3))
 run freshValidatedLatestNativeCommitTest=init.then(fire(Reserve)).then(fire(Context({receipt:2,consistent:true}))).then(fire(Validate(2))).then(fire(Commit(2))).then(check(s.effect))
}
