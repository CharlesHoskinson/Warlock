module denial_tests {
 import denials.* from "./denials"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run lockedPendingThenUnlock=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(DenyLocked)).then(fire(PendingRetire)).then(fire(PendingRetire)).then(fire(Resume)).then(fire(Request)).then(fire(Drain)).then(fire(Ack)).then(check(s.ready and s.records==0))
 run goneRetainsUntilDrain=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(DenyGone)).then(fire(Drain)).then(fire(Ack)).then(check(not(s.ready) and s.records==0))
 run outputDenialRetains=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(DenyOutput)).then(check(s.retiring and s.charged and not(s.ready)))
 run layoutDenialRetains=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(DenyLayout)).then(check(s.retiring and s.charged and not(s.ready)))
 run foreignDenialNoEffect=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(ForeignDenied)).then(check(s.ready and s.accepted))
 run staleDenialNoEffect=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(StaleDenied)).then(check(s.ready and s.accepted))
 run unknownRefusalNotSourceDenial=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(UnknownDenial)).then(check(s.ready and s.accepted))
 run duplicateDenialNoCleanupReplay=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(DenyLocked)).then(fire(RepeatDenied)).then(check(s.commands==List() and s.retiring))
 run staleScopeCannotResume=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(DenyLocked)).then(fire(StaleScope)).then(fire(Request)).then(check(not(s.ready) and s.commands==List()))
 run unknownCannotResumeAutomatically=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(Unknown)).then(fire(Resume)).then(fire(Request)).then(check(not(s.ready) and s.unknown and s.commands==List()))
 run hiddenOwnerDenialStillReleases=init.then(fire(Seed)).then(fire(Request)).then(fire(Capture)).then(fire(Close)).then(fire(DenyGone)).then(fire(Drain)).then(fire(Ack)).then(check(not(s.open) and s.records==0))
}
