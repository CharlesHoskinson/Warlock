module retirement_tests {
 import retirement.* from "./retirement"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run liveOwnedActive=init.then(fire(Birth)).then(fire(QueryFirst)).then(check(s.status=="Active"))
 run minimizedStillOwned=init.then(fire(Birth)).then(fire(MinimizeFirst)).then(fire(QueryFirst)).then(check(s.status=="Active" and s.minimized))
 run destroyedPermanentlyRetired=init.then(fire(Birth)).then(fire(CloseFirst)).then(fire(QueryFirst)).then(check(s.status=="Retired"))
 run futureBeforeBirth=init.then(fire(QueryFirst)).then(check(s.status=="Future" and s.issued==0))
 run futureBeyondFrontier=init.then(fire(Birth)).then(fire(QueryFuture)).then(check(s.status=="Future"))
 run oldIdentityCannotReappear=init.then(fire(Birth)).then(fire(CloseFirst)).then(fire(Birth)).then(fire(QueryFirst)).then(check(s.status=="Retired" and s.owned==Set(2)))
 run zeroIdentityInvalid=init.then(fire(QueryZero)).then(check(s.status=="Invalid" and s.issued==0))
 run incoherentOwnerInvalid=init.then(fire(Birth)).then(fire(QueryIncoherent)).then(check(s.status=="Invalid" and s.owned==Set(1)))
}
