module scoped_elm_realm_tests_v2 {
 import scoped_elm_realm_v2.* from "./scoped_elm_realm_v2"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run wrongFloorCannotRevoke=init.then(fire(WrongFloor)).then(check(not(s.closing) and s.known and s.commands==[]))
 run scopedSeedRetainsKnownJob=init.then(fire(Seed)).then(check(s.held and s.known and s.closing and s.commands==["cancel"]))
 run prematureCompletionCannotRemove=init.then(fire(Seed)).then(fire(Complete)).then(check(s.held and s.known and s.processed==0))
 run terminalAckBeforeScopedReadiness=init.then(fire(Seed)).then(fire(Terminal)).then(check(s.commands==["acknowledge","detach-ready"] and s.ready))
 run readinessAfterAlreadySettledJob=init.then(fire(Quarantine)).then(fire(Terminal)).then(fire(Seed)).then(check(s.commands==["detach-ready"] and s.ready))
 run exactScopedCompletionRemovesOnce=init.then(fire(Seed)).then(fire(Terminal)).then(fire(Complete)).then(check(not(s.held) and s.processed==1 and s.commands==["detach-delivery-ack"]))
 run completionGapCannotAdvance=init.then(fire(Seed)).then(fire(Terminal)).then(fire(Gap)).then(check(s.held and s.processed==0 and s.commands==[]))
 run changedEntryCannotAdvance=init.then(fire(Seed)).then(fire(Terminal)).then(fire(WrongEntry)).then(check(s.held and s.commands==[]))
 run changedFactCannotReack=init.then(fire(Seed)).then(fire(Terminal)).then(fire(Complete)).then(fire(ChangedComplete)).then(check(s.processed==1 and s.commands==[]))
 run lostProcessingAckRepeatsExactAck=init.then(fire(Seed)).then(fire(Terminal)).then(fire(Complete)).then(fire(Complete)).then(check(s.commands==["detach-delivery-ack"] and not(s.held)))
 run quarantineEmitsCanonicalBindingFirst=init.then(fire(Quarantine)).then(check(s.commands==["reconcile","cancel"] and s.known))
 run repeatedQuarantineDoesNotRepeatEffects=init.then(fire(Quarantine)).then(fire(Quarantine)).then(check(s.commands==[] and s.known))
 run scopedCloseCannotRequest=init.then(fire(Seed)).then(fire(Request)).then(check(s.commands==[] and s.known))
 run oldRealmCannotSupplyTerminal=init.then(fire(Seed)).then(fire(ForeignTerminal)).then(check(s.known and not(s.ready)))
 run bareSourceCannotEnterControlledPolicy=init.then(fire(BareSource)).then(check(s.commands==[] and s.known))
 run greaterEpochCannotReplaceLiveRealm=init.then(fire(NextGrant)).then(check(s.epoch==1 and s.held))
 run foreignCloseCannotReleaseRealm=init.then(fire(Seed)).then(fire(Terminal)).then(fire(Complete)).then(fire(ForeignClose)).then(check(not(s.closed)))
 run oldSourceCannotReopenCompletedMember=init.then(fire(Seed)).then(fire(Terminal)).then(fire(Complete)).then(fire(Source)).then(check(not(s.held) and s.commands==[]))
 run strictCloseAllowsFreshEpoch=init.then(fire(Seed)).then(fire(Terminal)).then(fire(Complete)).then(fire(Close)).then(fire(NextGrant)).then(check(s.epoch==2 and not(s.held) and not(s.closing) and s.processed==0))
 run sameActiveSubjectReopensOnlyFreshEpoch=init.then(fire(Seed)).then(fire(Terminal)).then(fire(Complete)).then(fire(Close)).then(fire(NextGrant)).then(fire(OldSource)).then(check(not(s.held))).then(fire(Source)).then(fire(Request)).then(check(s.held and s.known and s.commands==["acquire"]))
}
