module continuation_diagnostic_test {
 import continuation_diagnostic.* from "./continuation_diagnostic"
 action check(p:bool):bool=all{assert(p),prepared'=prepared,ack'=ack,observed'=observed,matched'=matched,caret'=caret,trusted'=trusted,accepted'=accepted,logs'=logs,seat'=seat,core'=core}
 run matchingOriginalOracleTest=init.then(fire(Before)).then(fire(Ack(0))).then(fire(Poll(good))).then(fire(Accept)).then(check(accepted))
 run ackNotDeliveryTest=init.then(fire(Before)).then(fire(Ack(0))).then(fire(Accept)).then(check(not(accepted)))
 run retainedNoDeliveryRefusedTest=init.then(fire(Before)).then(fire(Ack(0))).then(fire(Poll({...good,value:1}))).then(fire(Accept)).then(check(not(accepted) and logs==3))
 run wrongTextRefusedTest=init.then(fire(Before)).then(fire(Ack(0))).then(fire(Poll({...good,value:3}))).then(fire(Accept)).then(check(not(accepted)))
 run wrongCaretRefusedTest=init.then(fire(Before)).then(fire(Ack(0))).then(fire(Poll({...good,caret:1}))).then(fire(Accept)).then(check(not(accepted)))
 run missingTrustedInputRefusedTest=init.then(fire(Before)).then(fire(Ack(0))).then(fire(Poll({...good,trusted:false}))).then(fire(Accept)).then(check(not(accepted)))
 run coreAndSeatSeparateEvidenceTest=init.then(fire(Before)).then(fire(Poll({...good,seat:2}))).then(check(core==1 and seat==2 and not(accepted)))
 run absentSeatNeverRepairedFromCoreTest=init.then(fire(Before)).then(fire(Poll({...good,seat:0,surface:false}))).then(check(core==1 and seat==0 and not(accepted)))
 run staleWindowRefusedTest=init.then(fire(Before)).then(fire(Ack(0))).then(fire(Poll({...good,owner:2}))).then(fire(Accept)).then(check(not(accepted)))
 run staleSessionRefusedTest=init.then(fire(Before)).then(fire(Ack(0))).then(fire(Poll({...good,session:2}))).then(fire(Accept)).then(check(not(accepted)))
 run readErrorRevokesTest=init.then(fire(Before)).then(fire(Ack(0))).then(fire(Poll(good))).then(fire(ReadError)).then(fire(Accept)).then(check(not(accepted)))
 run lifetimeChangeRevokesTest=init.then(fire(Before)).then(fire(Ack(0))).then(fire(Poll(good))).then(fire(Change)).then(fire(Accept)).then(check(not(accepted)))
}
