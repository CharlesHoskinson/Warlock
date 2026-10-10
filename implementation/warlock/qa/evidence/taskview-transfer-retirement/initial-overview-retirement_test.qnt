module overviewRetirementTests {
 import overviewRetirement.* from "./overview-retirement"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run exactRetirementReturnsRetainedFilterTest=init.then(retireMember).then(sync).then(check(s.open and s.transfer==0 and s.selected==2 and s.focus==2 and s.mutations==0))
 run retiredWorkspaceReturnsAllTest=init.then(retireWorkspace).then(sync).then(check(s.open and s.selected==0 and s.transfer==0 and s.focus==0))
 run incoherentObservationDoesNotRetireTest=init.then(incoherentRetirement).then(sync).then(check(s.transfer==7 and s.focusCommands==0))
 run laterCoherenceAllowsRetirementTest=init.then(incoherentRetirement).then(sync).then(becomeCoherent).then(sync).then(check(s.transfer==0 and s.focus==2 and s.focusCommands==1))
 run existingExactMemberRetainsChooserTest=init.then(sync).then(check(s.transfer==7 and s.focusCommands==0))
 run duplicateReconciliationNeverRefocusesTest=init.then(retireMember).then(sync).then(sync).then(check(s.transfer==0 and s.focusCommands==1))
 run closedOverviewDoesNotRefocusTest=init.then(close).then(retireMember).then(sync).then(check(not(s.open) and s.focusCommands==0))
 run newIncarnationNeverSubstitutesTest=init.then(replace).then(sync).then(check(s.transfer==0 and s.live==Set(8) and s.mutations==0 and s.focusCommands==0))
}
