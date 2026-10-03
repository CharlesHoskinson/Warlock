module service_restart_test {
 import service_restart.* from "./service_restart"
 action check(p:bool):bool=all{assert(p),s'=s}
 run liveOldRootCannotBeReplacedTest=init.then(replace(2,2,1,1)).then(check(not(s.accepted) and s.pid==1))
 run exactDeadRootCanRegisterFreshLifetimeTest=init.then(close).then(replace(2,2,1,1)).then(check(s.accepted and s.queries==2))
 run sameOldLifetimeCannotBeRefreshedTest=init.then(close).then(replace(1,1,1,1)).then(check(not(s.accepted)))
 run sourceReplacementCannotResetAuthorityTest=init.then(close).then(replace(2,2,2,1)).then(check(not(s.accepted)))
 run memberReplacementCannotResetAuthorityTest=init.then(close).then(replace(2,2,1,2)).then(check(not(s.accepted)))
 run reusedPidWithFreshStartCanRegisterExactNewRootTest=init.then(close).then(replace(1,2,1,1)).then(check(s.accepted and s.start==2 and s.queries==2))
}
