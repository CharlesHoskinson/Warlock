module pinned_output_area_test {
 import pinned_output_area.* from "./pinned-output-area"
 import reachable_placement.clamp from "./reachable-placement"
 action check(condition:bool):bool=all{assert(condition),s'=s}
 run retainedPinnedExclusionCounterexampleTest=init.then(shrink).then(legacySkipPinned).then(check(s.pinned and s.y==30 and not(reachable)))
 run pinnedReachableRecoveryTest=init.then(shrink).then(recover).then(check(s.x==-360 and s.y==-32 and reachable and safety and s.effects==0))
 run pinnedMinimizeRestorePreservesPlacementTest=init.then(shrink).then(recover).then(minimize).then(restore).then(check(s.x==-360 and s.y==-32 and s.pinned and s.effects==2 and safety))
 run unchangedAreaDoesNotOverrideManualPlacementTest=init.then(shrink).then(recover).then(manual).then(unchangedArea).then(check(s.x==-500 and s.y==-200 and s.pinned and safety))
 run fullscreenRetainsExistingPathTest=init.then(check(not(eligible(true,true,false,true,true,true,true))))
 run hiddenTargetRetainsExistingPathTest=init.then(check(not(eligible(true,true,true,false,true,true,true))))
 run groupedTargetRetainsExistingPathTest=init.then(check(not(eligible(true,true,false,false,false,true,true))))
 run otherMonitorRetainsExistingPathTest=init.then(check(not(eligible(true,true,false,false,true,true,false))))
 run unmappedOrTiledTargetRetainsExistingPathTest=init.then(check(not(eligible(true,false,false,false,true,true,true)) and not(eligible(true,true,false,false,true,false,true))))
 run alreadyReachablePositionPreservedTest=init.then(check(clamp(s.x,s.left,s.aw,s.width)==s.x and clamp(s.y,s.top,s.ah,s.height)==s.y))
}
