module span_source_binding_test {
 import span_source_binding.* from "./span_source_binding"
 action check(p:bool):bool=all{assert(p),s'=s}
 action ready=init.then(fire(Select(true))).then(fire(Install(true)))
 action finish=fire(Stop).then(fire(Project(true,true,true)))
 run genuineExactCodeProjectionTest=ready.then(fire(Call(true))).then(finish).then(check(s.complete and allProps))
 run missingSymbolRefusesTest=init.then(fire(Select(false))).then(fire(Install(true))).then(finish).then(check(s.fault and not(s.complete)))
 run preexistingHookRefusesTest=init.then(fire(Select(true))).then(fire(Install(false))).then(finish).then(check(s.fault and not(s.complete)))
 run foreignSameLabelsCodeRefusesTest=ready.then(fire(Call(false))).then(finish).then(check(s.fault and not(s.complete)))
 run laterGoodCodeCannotEraseFaultTest=ready.then(fire(Call(false))).then(fire(Call(true))).then(finish).then(check(s.fault and not(s.complete)))
 run replacedCodeAfterCallRefusesTest=ready.then(fire(Call(true))).then(fire(ChangeCode)).then(finish).then(check(not(s.complete)))
 run changedSourceRefusesTest=ready.then(fire(Call(true))).then(fire(ChangeSource)).then(finish).then(check(not(s.complete)))
 run missingRawReturnRefusesTest=ready.then(fire(Stop)).then(fire(Project(false,true,true))).then(check(not(s.complete)))
 run currentCodeBindingMismatchRefusesTest=ready.then(fire(Call(true))).then(fire(Stop)).then(fire(Project(true,false,true))).then(check(not(s.complete)))
 run persistenceFailureCannotBeErasedTest=ready.then(fire(Stop)).then(fire(Project(true,true,false))).then(fire(Project(true,true,true))).then(check(s.fault and not(s.complete)))
 run projectionBeforeStopRefusesTest=ready.then(fire(Project(true,true,true))).then(finish).then(check(s.fault and not(s.complete)))
 run lateObservationHasNoEffectAuthorityTest=ready.then(fire(Call(true))).then(finish).then(fire(GrantEffect)).then(check(s.deadline==2 and not(s.nativeAuthority)))
}
