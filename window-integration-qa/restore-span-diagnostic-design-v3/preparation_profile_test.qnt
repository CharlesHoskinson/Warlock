module preparation_profile_test {
 import preparation_profile.* from "./preparation_profile"
 action check(p:bool):bool=all{assert(p),s'=s}
 action ready=init.then(fire(Install(true)))
 action done=ready.then(fire(Begin(1))).then(fire(End(1))).then(fire(Stop)).then(fire(Persist(true)))
 run actualClosedSpansCanBeCompleteTest=done.then(check(s.complete and allProps))
 run observationNeverConfersNativeAuthorityTest=done.then(check(not(s.nativeAuthority)))
 run preexistingHookRefusesTest=init.then(fire(Install(false))).then(fire(Begin(1))).then(fire(Stop)).then(fire(Persist(true))).then(check(s.fault and not(s.complete)))
 run missingReturnRemainsIncompleteTest=ready.then(fire(Begin(1))).then(fire(Stop)).then(fire(Persist(true))).then(check(not(s.complete)))
 run unmatchedReturnLatchesFaultTest=ready.then(fire(End(1))).then(fire(Stop)).then(fire(Persist(true))).then(check(s.fault and not(s.complete)))
 run lateReturnCannotRepairStoppedTraceTest=ready.then(fire(Begin(1))).then(fire(Stop)).then(fire(End(1))).then(fire(Persist(true))).then(check(not(s.complete)))
 run sourceChangeCannotBecomeCompleteTest=done.then(fire(ReplaceSource)).then(fire(Persist(true))).then(check(not(s.complete)))
 run failedPublicationCannotBecomeCompleteTest=ready.then(fire(Begin(1))).then(fire(End(1))).then(fire(Stop)).then(fire(Persist(false))).then(fire(Persist(true))).then(check(s.fault and not(s.complete)))
 run callbackFaultCannotBeClearedTest=ready.then(fire(Fault)).then(fire(Stop)).then(fire(Persist(true))).then(check(not(s.complete)))
 run duplicateStartCannotRepairTraceTest=ready.then(fire(Begin(1))).then(fire(Begin(1))).then(fire(End(1))).then(fire(Stop)).then(fire(Persist(true))).then(check(s.fault and not(s.complete)))
 run nestedSpansRemainIndependentlyBoundTest=ready.then(fire(Begin(1))).then(fire(Begin(2))).then(fire(End(2))).then(fire(End(1))).then(fire(Stop)).then(fire(Persist(true))).then(check(s.complete and allProps))
 action span(id:int):bool=fire(Begin(id)).then(fire(End(id)))
 run capacityIsDiagnosticFailureNotAcceptanceTest=ready.then(span(1)).then(span(2)).then(span(3)).then(span(4)).then(fire(Begin(5))).then(fire(Stop)).then(fire(Persist(true))).then(check(s.events==limit and s.fault and not(s.complete)))
}
