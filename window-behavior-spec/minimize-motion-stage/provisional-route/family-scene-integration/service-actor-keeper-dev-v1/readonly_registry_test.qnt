module readonly_registry_test {
 import readonly_registry.* from "./readonly_registry"
 action check(p:bool):bool=all{assert(p),s'=s}
 action begin(id:int):bool=fire(Begin({id:id,durable:true}))
 action close(id:int):bool=fire(Close(id)).then(fire(Publish({id:id,durable:true})))
 run healthyParallelQueriesHaveDistinctRetainedRowsTest=init.then(begin(1)).then(begin(2)).then(check(s.rows.size()==2 and s.rows.forall(r=>not(r.closed))))
 run oneRefusalCannotConsumeOtherQueryDataTest=init.then(begin(1)).then(begin(2)).then(fire(Refuse(1))).then(close(2)).then(fire(Return({id:2,connectionProof:true}))).then(check(s.usable==Set(2)))
 run refusalBlocksNewConnectionUntilDurableClosureTest=init.then(begin(1)).then(fire(Refuse(1))).then(begin(2)).then(check(s.rows.size()==1)).then(fire(Close(1))).then(begin(2)).then(check(s.rows.size()==1)).then(fire(Publish({id:1,durable:true}))).then(begin(2)).then(check(s.rows.size()==2))
 run failedPublicationLatchesWholeServiceFaultTest=init.then(begin(1)).then(fire(Close(1))).then(fire(Publish({id:1,durable:false}))).then(begin(2)).then(check(s.fault and s.rows.size()==1))
 run retainedCapacityCannotForgetClosedRowsTest=init.then(begin(1)).then(close(1)).then(begin(2)).then(close(2)).then(begin(3)).then(close(3)).then(begin(4)).then(close(4)).then(begin(5)).then(check(s.rows.size()==4 and not(s.rows.exists(r=>r.id==5))))
 run completedConnectionIDCannotBeReusedTest=init.then(begin(1)).then(close(1)).then(begin(1)).then(check(s.rows.size()==1 and s.rows.forall(r=>r.closed and r.published)))
 run physicalClosureCannotReplacePublicationTest=init.then(begin(1)).then(fire(Close(1))).then(fire(Return({id:1,connectionProof:true}))).then(check(s.usable.size()==0))
 run missingPerConnectionProofCannotReturnTest=init.then(begin(1)).then(close(1)).then(fire(Return({id:1,connectionProof:false}))).then(check(s.usable.size()==0))
 run refusedRowNeverReturnsAfterPublicationTest=init.then(begin(1)).then(fire(Refuse(1))).then(close(1)).then(fire(Return({id:1,connectionProof:true}))).then(check(s.usable.size()==0))
 run registrationFaultCannotConnectTest=init.then(fire(Begin({id:1,durable:false}))).then(begin(2)).then(check(s.fault and s.rows.size()==0))
}
