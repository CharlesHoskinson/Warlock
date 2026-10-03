module stop_contract_test {
 import stop_contract.* from "./stop_contract"
 run absentStopIsIdempotentTest=init.then(stop).then(stop).then(all{assert(ok and submitted==0 and allProps),stop})
 run liveStartupCannotReportIdleTest=init.then(configure(true,true,false,false)).then(stop).then(all{assert(not(ok) and busy and allProps),stop})
 run acceptedJournalCannotBeLostTest=init.then(configure(false,false,true,false)).then(stop).then(all{assert(not(ok) and pending and allProps),stop})
 run liveShutdownSubmitsOnceTest=init.then(configure(true,true,true,true)).then(stop).then(stop).then(all{assert(ok and submitted==1 and allProps),stop})
}
