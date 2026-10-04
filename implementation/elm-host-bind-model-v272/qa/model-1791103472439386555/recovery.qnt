module recovery {
 type State={phase:str,instance:bool,directory:bool,lock:bool,lifetime:int,cause:str,retries:int}
 var s:State
 action init=s'={phase:"Unbound",instance:true,directory:false,lock:false,lifetime:0,cause:"Busy",retries:0}
 action attempt=s'=if(Set("Unbound","Retrying").contains(s.phase) and s.instance){...s,phase:if(s.cause=="None")"Live" else "Failed",directory:s.cause=="None",lock:s.cause=="None",lifetime:if(s.cause=="None")1 else 0} else s
 action correct=s'={...s,cause:"None"}
 action privateFailure=s'=if(s.phase=="Unbound" or s.phase=="Retrying"){...s,cause:"Public"} else s
 action retry=s'=if(s.phase=="Failed" and s.instance){...s,phase:"Retrying",retries:s.retries+1} else s
 action wrongLifetime=s'=s
 action stop=s'={...s,phase:"Stopped",instance:false,directory:false,lock:false,lifetime:0}
 action step=any{attempt,correct,privateFailure,retry,wrongLifetime,stop}
 val safety=(s.phase!="Stopped" implies s.instance) and (s.lock implies s.directory and s.lifetime==1) and (s.phase=="Failed" implies not(s.directory) and not(s.lock) and s.lifetime==0) and (s.phase=="Stopped" implies not(s.instance) and not(s.directory) and not(s.lock))
 run failedBindRetainsInstanceTest=init.then(attempt).then(all{assert(s.instance and not(s.lock) and not(s.directory) and s.phase=="Failed" and safety),s'=s})
 run correctionDoesNotAutoBindTest=init.then(attempt).then(correct).then(attempt).then(all{assert(s.phase=="Failed" and not(s.lock) and s.retries==0 and safety),s'=s})
 run explicitRetryBindsAfterCorrectionTest=init.then(attempt).then(correct).then(retry).then(attempt).then(all{assert(s.phase=="Live" and s.lock and s.retries==1 and safety),s'=s})
 run repeatedFailureRetainsInstanceTest=init.then(privateFailure).then(attempt).then(retry).then(attempt).then(all{assert(s.phase=="Failed" and s.instance and not(s.lock) and safety),s'=s})
 run wrongLifetimeCannotReplaceLiveBindingTest=init.then(correct).then(attempt).then(wrongLifetime).then(all{assert(s.phase=="Live" and s.lifetime==1 and s.lock and safety),s'=s})
 run finalCloseRetiresEverythingTest=init.then(correct).then(attempt).then(stop).then(all{assert(not(s.instance) and not(s.directory) and not(s.lock) and s.lifetime==0 and safety),s'=s})
 run stoppedHostCannotRetryTest=init.then(attempt).then(stop).then(correct).then(retry).then(attempt).then(all{assert(s.phase=="Stopped" and s.retries==0 and safety),s'=s})
 run successfulBindOwnsLifetimeTest=init.then(correct).then(attempt).then(all{assert(s.instance and s.directory and s.lock and s.lifetime==1 and safety),s'=s})
}
