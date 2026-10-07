module feedback_tests {
 import feedback.* from "./feedback"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run capacityWithoutEffects=init.then(fire(Capacity)).then(check(s.outcome=="capacity" and s.floor==2 and s.acquires==0 and s.acks==0))
 run originalExpiryShown=init.then(fire(Capacity)).then(fire(Expired)).then(check(s.outcome=="expired" and s.floor==3 and s.acquires==0))
 run duplicateAndOlderRefused=init.then(fire(Capacity)).then(fire(Duplicate)).then(fire(Older)).then(check(s.floor==2 and s.outcome=="capacity"))
 run foreignClockOwnerSubjectRefused=init.then(fire(Capacity)).then(fire(WrongClock)).then(fire(WrongOwner)).then(fire(WrongSubject)).then(check(s.floor==2 and s.outcome=="capacity"))
 run wrongStampRefused=init.then(fire(Capacity)).then(fire(WrongStamp)).then(check(s.outcome=="capacity" and s.floor==2))
 run closeRetainsFloor=init.then(fire(Capacity)).then(fire(Close)).then(fire(Reopen)).then(fire(Duplicate)).then(check(s.active and s.outcome=="" and s.floor==2))
 run issuedSeedClearsWait=init.then(fire(Capacity)).then(fire(Issue)).then(check(s.owned and s.outcome=="" and s.floor==3 and s.acquires==1))
 run lateFeedbackCannotClearOwnedWork=init.then(fire(Issue)).then(fire(Capacity)).then(fire(Expired)).then(fire(Close)).then(fire(Reopen)).then(fire(Waiting)).then(check(s.owned and s.cancelled and s.outcome=="" and s.cancels==1 and s.acks==0))
 run exactProofThenNewFeedback=init.then(fire(Issue)).then(fire(Close)).then(fire(Proof)).then(fire(Reopen)).then(fire(Waiting)).then(check(not(s.owned) and s.outcome=="waiting" and s.acquires==1 and s.cancels==1 and s.acks==1))
}
