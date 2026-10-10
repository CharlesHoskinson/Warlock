module overviewTransferCancelTests {
  import overviewTransferCancel.* from "./overview-transfer-cancel"
  action check(ok:bool):bool=all{assert(ok and safety),s'=s}
  run currentExactOriginReturnsFocusTest=init.then(cancel).then(check(s.open and s.transfer==0 and s.focus==7 and s.revision==2 and s.focusCommands==1))
  run nestedEscapeReturnsOriginTest=init.then(escape).then(check(s.open and s.transfer==0 and s.focus==7 and s.revision==2))
  run nextEscapeClosesOverviewTest=init.then(escape).then(escape).then(check(not(s.open) and s.transfer==0 and s.focusCommands==1 and s.revision==3))
  run previousEscapeCannotCloseReturnedOverviewTest=init.then(escape).then(all{s'=dismissed(s,1)}).then(check(s.open and s.revision==2 and s.focusCommands==1))
  run duplicateCancelIsInertTest=init.then(cancel).then(cancel).then(check(s.revision==2 and s.focusCommands==1))
  run staleCancelCannotDismissOrRefocusTest=init.then(staleCancel).then(check(s.transfer==7 and s.revision==1 and s.focusCommands==0))
  run unavailableOriginReturnsFilterTest=init.then(unavailable).then(cancel).then(check(s.transfer==0 and s.focus==2 and not(s.lastOriginEligible)))
  run reservedOriginReturnsFilterTest=init.then(reserve).then(cancel).then(check(s.focus==2 and not(s.lastOriginEligible)))
  run capabilityRemovedReturnsFilterTest=init.then(removeCapability).then(cancel).then(check(s.focus==2 and not(s.lastOriginEligible)))
  run unreadyOriginReturnsFilterTest=init.then(unready).then(cancel).then(check(s.focus==2 and not(s.lastOriginEligible)))
  run filteredOutOriginReturnsCurrentFilterTest=init.then(filterOther).then(cancel).then(check(s.focus==1 and not(s.lastOriginEligible)))
  run retiredOriginNeverSubstitutesTest=init.then(retire).then(cancel).then(check(s.focus==2 and s.live==Set(8) and not(s.lastOriginEligible)))
  run retiredWorkspaceReturnsAllTest=init.then(retireWorkspace).then(cancel).then(check(s.focus==0 and not(s.lastOriginEligible)))
  run incoherentObservationDismissesSafelyToAllTest=init.then(incoherent).then(cancel).then(check(s.transfer==0 and s.focus==0 and not(s.lastOriginEligible)))
  run allFilterReturnsExactOriginTest=init.then(filterAll).then(cancel).then(check(s.focus==7 and s.selected==0))
  run closedOverviewNeverRefocusesTest=init.then(close).then(cancel).then(check(s.focusCommands==0 and s.revision==2))
  run changedScopeNeverRemintsOldOpenerTest=init.then(replaceScope).then(cancel).then(check(s.focusCommands==0 and s.revision==2))
}
