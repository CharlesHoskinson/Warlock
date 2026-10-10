module pinned_output_retirement_test {
 import pinned_output_retirement.* from "./pinned-output-retirement"
 action check(condition:bool):bool=all{assert(condition),s'=s}
 run retainedPinnedRetirementCounterexampleTest=init.then(retire).then(legacyStay).then(legacyReturn).then(check(s.workspace==1 and s.monitor==-1 and s.pinned and not(safety)))
 run retiredGapCallbackCannotReassignPinnedWorkspaceTest=init.then(retire).then(skipRetiredGapNavigation).then(check(s.workspace==2 and s.monitor==0 and s.pinned and safety))
 run pinnedSurvivingOwnerPreservesIdentityTest=init.then(retire).then(skipRetiredGapNavigation).then(migrate).then(check(s.workspace==2 and s.monitor==1 and s.pinned and safety))
 run pinnedZeroOutputReturnRecoveryTest=init.then(retire).then(skipRetiredGapNavigation).then(migrate).then(empty).then(returnOutput).then(taskbarRecovery).then(check(s.workspace==2 and s.monitor==2 and s.pinned and s.effects==1 and safety))
 run minimizedZeroOutputReturnRestoreTest=init.then(minimizedFixture).then(retire).then(skipRetiredGapNavigation).then(migrate).then(empty).then(returnOutput).then(check(s.minimized and s.workspace==2 and s.effects==0)).then(taskbarRecovery).then(check(not(s.minimized) and s.effects==1 and safety))
 run liveOwnerWorkspaceMoveKeepsExistingPinPolicyTest=init.then(moveWhileLive).then(check(s.workspace==1 and s.monitor==0 and s.pinned and safety))
 run expiredPinnedOwnerMustMigrateTest=init.then(check(not(stayPinned(true,false,false)) and not(stayPinned(true,false,true))))
 run retainedDisabledPinnedOwnerMustMigrateTest=init.then(check(not(stayPinned(true,true,false))))
 run ordinaryWindowStillMigratesTest=init.then(check(not(stayPinned(false,true,true))))
 run retainedSameOutputPinnedAdmissionRefusalTest=init.then(retire).then(skipRetiredGapNavigation).then(migrate).then(empty).then(returnOutput).then(legacyAdmissionRefusal).then(check(s.workspace==2 and s.monitor==2 and s.effects==0 and s.activeWorkspace==1))
 run pinnedSameOutputRecoveryNavigatesBeforeFocusTest=init.then(retire).then(skipRetiredGapNavigation).then(migrate).then(empty).then(returnOutput).then(taskbarRecovery).then(check(s.workspace==2 and s.monitor==2 and s.activeWorkspace==2 and s.effects==1 and s.pinned and safety))
 run otherOutputPinRecoveryRefusesWithoutTransferTest=init.then(retire).then(skipRetiredGapNavigation).then(migrate).then(empty).then(returnOutput).then(focusElsewhere).then(refuseCrossOutputPin).then(check(s.workspace==2 and s.monitor==2 and s.activeWorkspace==1 and s.effects==0 and s.pinned and safety))
}
