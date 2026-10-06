module source_tests {
 import source.* from "./source"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run clientRejectsMonitorWithOwner=init.then(fire(Client)).then(fire(Request)).then(fire(NextMonitor)).then(check(s.domain==1 and s.now==0 and s.known))
 run clientRejectsLegacyWithOwner=init.then(fire(Client)).then(fire(Request)).then(fire(NextLegacy)).then(check(s.domain==1 and s.now==0 and s.known))
 run monitorRejectsClient=init.then(fire(Monitor)).then(fire(NextClient)).then(check(s.domain==2 and s.now==0))
 run legacyRejectsTypedUpgrade=init.then(fire(Legacy)).then(fire(NextClient)).then(check(s.domain==0 and s.now==0))
 run sameClientAdmitsNewFacts=init.then(fire(Client)).then(fire(Request)).then(fire(NextClient)).then(check(s.domain==1 and s.now==1 and s.known))
 run malformedPreservesOwner=init.then(fire(Client)).then(fire(Request)).then(fire(Malformed)).then(fire(Foreign)).then(fire(WrongStamp)).then(check(s.domain==1 and s.now==0 and s.known))
 run closeRetainsOwner=init.then(fire(Client)).then(fire(Request)).then(fire(Close)).then(fire(NextMonitor)).then(check(s.domain==1 and s.known and not(s.open)))
 run closedCannotEnroll=init.then(fire(Close)).then(fire(Client)).then(fire(Request)).then(check(s.domain== -1 and not(s.known)))
}
