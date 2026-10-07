module next_intent_tests {
 import next_intent.* from "./next_intent"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run pendingCannotAdvance=init.then(fire(Advance)).then(check(s.status=="Conflict" and s.deadline==20))
 run sameIntentCannotRenew=init.then(fire(Expire)).then(fire(Retry)).then(fire(Renew)).then(check(s.status=="Conflict" and s.deadline==20 and not(s.issued)))
 run successorAfterExpiry=init.then(fire(Expire)).then(fire(Advance)).then(check(s.deadline==41 and s.previous==20 and s.publication==2))
 run successorKeepsCutoff=init.then(fire(Expire)).then(fire(Advance)).then(fire(Retry)).then(fire(Retry)).then(check(s.status=="Capacity" and s.deadline==41 and not(s.issued)))
 run actualCapacityStartsSuccessor=init.then(fire(Expire)).then(fire(Advance)).then(fire(Drain)).then(fire(Retry)).then(check(s.issued and s.deadline==41 and s.records==2))
 run partialStampRefused=init.then(fire(Expire)).then(fire(Partial)).then(check(s.status=="Conflict" and s.publication==1))
 run predecessorCannotReplay=init.then(fire(Expire)).then(fire(Advance)).then(fire(OldStamp)).then(check(s.status=="Conflict" and s.previous==20 and s.deadline==41))
 run repeatedSuccessorsBounded=init.then(fire(Expire)).then(fire(Advance)).then(fire(Expire)).then(fire(Advance)).then(check(s.deadline==62 and s.previous==41 and s.publication==3))
 run foreignOwnerRefused=init.then(fire(Expire)).then(fire(Foreign)).then(check(s.status=="Invalid" and s.deadline==20))
 run changedClockRefused=init.then(fire(Expire)).then(fire(WrongClock)).then(check(s.status=="Conflict" and s.deadline==20))
}
