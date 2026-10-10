module workspaceNavigationTests {
 import workspaceNavigation.* from "./workspace-navigation"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run navigateEmptyDestinationTest=init.then(admit).then(reserve).then(commit).then(acknowledge).then(check(s.active==2 and s.status==Committed))
 run staleOwnerRefusesWithoutMutationTest=init.then(admit).then(reserve).then(retire).then(refuse).then(acknowledge).then(check(s.status==Refused and s.effects==0 and s.open))
 run staleContextRefusesWithoutMutationTest=init.then(admit).then(reserve).then(invalidate).then(refuse).then(acknowledge).then(check(s.status==Refused and s.active==1))
 run unresolvedWindowRefusesWithoutMutationTest=init.then(admit).then(reserve).then(windowBusy).then(refuse).then(acknowledge).then(check(s.status==Refused and s.effects==0))
 run lostAckIsUnknownUntilReadTest=init.then(admit).then(reserve).then(commit).then(lostAck).then(duplicate).then(check(s.status==Unknown and s.effects==1)).then(read).then(check(s.status==Committed and s.effects==1))
 run restartReadsOldIntentWithoutReplayTest=init.then(admit).then(reserve).then(commit).then(restart).then(duplicate).then(read).then(check(s.frontend==2 and s.status==Committed and s.effects==1))
 run hostOnlyCrashNeverSubmitsTest=init.then(admit).then(restart).then(read).then(duplicate).then(check(s.status==Unknown and s.effects==0 and not(s.broker)))
 run indeterminateCannotInferCommitFromSceneTest=init.then(admit).then(reserve).then(indeterminate).then(lostAck).then(read).then(check(s.active==2 and s.status==Unknown))
 run foreignReceiptCannotSettleTest=init.then(admit).then(reserve).then(commit).then(lostAck).then(foreign).then(check(s.status==Unknown and s.effects==1))
 run unknownCanDismissWithoutReplayTest=init.then(admit).then(reserve).then(indeterminate).then(lostAck).then(dismiss).then(read).then(duplicate).then(check(not(s.open) and s.status==Unknown and s.effects==1))
}
