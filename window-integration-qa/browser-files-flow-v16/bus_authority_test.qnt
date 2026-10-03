module bus_authority_test {
 import bus_authority.* from "./bus_authority"
 pure val good={preExecSelectors:true,sameExec:true,sameLifetime:true,ownedScope:true,privateDaemon:true,sameSocket:true,realClientPid:true,realClientUid:true}
 run ownedPositiveTest=init.then(observe(good)).expect(accepted and allProps)
 run preexecMismatchTest=init.then(observe(good.with("preExecSelectors",false))).expect(not(accepted))
 run execMismatchTest=init.then(observe(good.with("sameExec",false))).expect(not(accepted))
 run lifetimeMismatchTest=init.then(observe(good.with("sameLifetime",false))).expect(not(accepted))
 run scopeMismatchTest=init.then(observe(good.with("ownedScope",false))).expect(not(accepted))
 run foreignDaemonTest=init.then(observe(good.with("privateDaemon",false))).expect(not(accepted))
 run replacedSocketTest=init.then(observe(good.with("sameSocket",false))).expect(not(accepted))
 run foreignBusClientTest=init.then(observe(good.with("realClientPid",false))).expect(not(accepted))
 run foreignClientUidTest=init.then(observe(good.with("realClientUid",false))).expect(not(accepted))
}
