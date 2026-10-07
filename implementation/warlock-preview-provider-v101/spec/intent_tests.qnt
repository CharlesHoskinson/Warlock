module intent_tests {
 import intent.* from "./intent"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run capacityHasNoJob=init.then(fire(Retry)).then(check(s.status=="Capacity" and not(s.issued) and s.charge==64 and s.records==2))
 run retryCannotRenew=init.then(fire(Retry)).then(fire(Renew)).then(fire(Retry)).then(check(s.deadline==20 and not(s.issued) and s.status=="Capacity"))
 run expiredCapacityDoesNotRevive=init.then(fire(Retry)).then(fire(Expire)).then(fire(Drain)).then(fire(Retry)).then(check(s.status=="Expired" and not(s.issued) and s.free and s.deadline==20))
 run realCapacityReturnsOriginalJob=init.then(fire(Retry)).then(fire(Drain)).then(fire(Retry)).then(check(s.issued and s.status=="Started" and s.deadline==20 and s.records==2))
 run changedStampRefused=init.then(fire(ChangeStamp)).then(check(s.status=="Conflict" and s.deadline==20 and not(s.issued)))
 run foreignIntentRefused=init.then(fire(Foreign)).then(check(s.status=="Invalid" and not(s.issued) and s.records==2))
}
