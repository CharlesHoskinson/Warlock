module runtime_lifecycle_test {
 import runtime_lifecycle.* from "./runtime_lifecycle"
 action check(p:bool):bool=all{assert(p),s'=s}
 run acceptedReceiptRequiresDurableJournalTest=init.then(fire(Start({lease:true,private:true,unresolved:false}))).then(fire(Receive)).then(fire(Acknowledge)).then(check(not(s.ack)))
 run journalFailureCannotCommitPreviouslyValidatedRequestTest=init.then(fire(Start({lease:true,private:true,unresolved:false}))).then(fire(Receive)).then(fire(Persist(true))).then(fire(Validate)).then(fire(JournalFail)).then(fire(Commit)).then(check(not(s.effect)))
 run unresolvedRestartCannotStartActorTest=init.then(fire(Start({lease:true,private:true,unresolved:true}))).then(check(not(s.running) and s.actors==0))
 run duplicateRuntimeLeaseCannotStartServiceTest=init.then(fire(Start({lease:false,private:true,unresolved:false}))).then(check(not(s.running)))
 run idleStopNeverStartsRuntimeTest=init.then(fire(IdleStop)).then(check(not(s.running) and s.actors==0))
}
