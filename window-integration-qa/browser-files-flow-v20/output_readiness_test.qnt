module output_readiness_test {
 import output_readiness.* from "./output_readiness"
 pure val good={reply:Exact,before:true,after:true,peer:true,eof:true,bounded:true,time:1}
 run exactReadyNoFeatureCreditTest=init.then(fire(Observe(good))).then(check(ready and not(accepted)))
 run emptyThenExactSameDeadlineTest=init.then(fire(Observe({...good,reply:Empty,time:14}))).then(fire(Observe({...good,time:14}))).then(check(ready and deadline==15 and observations==2))
 run emptyNeverReadyTest=init.then(fire(Observe({...good,reply:Empty}))).then(check(not(ready) and not(failed)))
 run deadlineNoRestartTest=init.then(fire(Observe({...good,reply:Empty,time:14}))).then(fire(Observe({...good,time:15}))).then(check(failed and not(ready) and deadline==15))
 run fallbackWrongTerminalTest=init.then(fire(Observe({...good,reply:Wrong}))).then(fire(Observe(good))).then(check(failed and not(ready)))
 run malformedTerminalTest=init.then(fire(Observe({...good,reply:Malformed}))).then(check(failed and not(ready)))
 run nonListTerminalTest=init.then(fire(Observe({...good,reply:NotList}))).then(check(failed and not(ready)))
 run missingBeforeAuthorityTest=init.then(fire(Observe({...good,before:false}))).then(check(failed and not(ready)))
 run changedAfterAuthorityTest=init.then(fire(Observe({...good,after:false}))).then(check(failed and not(ready)))
 run foreignPeerTest=init.then(fire(Observe({...good,peer:false}))).then(check(failed and not(ready)))
 run missingEOFTest=init.then(fire(Observe({...good,eof:false}))).then(check(failed and not(ready)))
 run oversizedReplyTest=init.then(fire(Observe({...good,bounded:false}))).then(check(failed and not(ready)))
 run changeRevokesReadyTest=init.then(fire(Observe(good))).then(fire(Changed)).then(check(failed and not(ready)))
 run timeCannotGoBackwardTest=init.then(fire(Tick(14))).then(fire(Observe(good))).then(check(failed and not(ready)))
 run expirationRevokesReadyTest=init.then(fire(Observe(good))).then(fire(Tick(15))).then(check(failed and not(ready)))
}
