module urgent_preview_quarantine_tests {
 import urgent_preview_quarantine.* from "./urgent_preview_quarantine"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run urgentQuarantineRevokesBlockedDemand=init.then(fire(Quarantine)).then(check(not(s.demand) and s.known==2 and s.deferred==["acquire:neighbor","reconcile:binding","cancel:first","cancel:neighbor"]))
 run urgentCleanupPreservesOlderAcquisition=init.then(fire(Quarantine)).then(fire(Issue)).then(fire(Retry)).then(check(s.pending==["acquire:neighbor"] and s.deferred==["reconcile:binding","cancel:first","cancel:neighbor"]))
 run repeatedQuarantineCannotGrowSafetyBatch=init.then(fire(Quarantine)).then(fire(Quarantine)).then(fire(Quarantine)).then(check(s.deferred.length()==4 and not(s.demand)))
 run foreignQuarantineCannotChangeBlockedRealm=init.then(fire(ForeignQuarantine)).then(check(not(s.closing) and s.demand and s.deferred==["acquire:neighbor"]))
 run blockedOrdinaryInputCannotEraseUrgentWork=init.then(fire(Quarantine)).then(fire(Ordinary)).then(fire(ForeignTicket)).then(check(s.pending==["acquire:first"] and s.deferred.length()==4 and s.known==2))
 run everyOriginalIntentKeepsItsOrder=init.then(fire(Quarantine)).then(fire(Issue)).then(fire(Retry)).then(fire(Issue)).then(fire(Retry)).then(check(s.pending==["reconcile:binding"])).then(fire(Issue)).then(fire(Retry)).then(check(s.pending==["cancel:first"])).then(fire(Issue)).then(fire(Retry)).then(check(s.pending==["cancel:neighbor"] and s.deferred==[] and s.known==2))
}
