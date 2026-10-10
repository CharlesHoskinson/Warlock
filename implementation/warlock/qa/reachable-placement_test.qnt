module reachable_placement_test {
 import reachable_placement.* from "./reachable-placement"
 action check(condition:bool):bool=all{assert(condition),s'=s}
 run smallerNegativeOriginRecoveryTest=init.then(shrink).then(recover).then(check(s.x==-360 and s.y==-44 and safety))
 run retainedOffscreenTranslationCounterexampleTest=init.then(shrink).then(check(s.y==30 and s.y>s.top+s.ah))
 run existingReachablePositionPreservedTest=init.then(check(clamp(s.x,s.left,s.aw,s.width)==s.x and clamp(s.y,s.top,s.ah,s.height)==s.y))
 run noResizeRoundTripTest=init.then(shrink).then(recover).then(returnOutput).then(check(s.width==108 and s.height==440 and s.workspace==2 and safety))
 run unchangedAreaDoesNotOverrideManualPlacementTest=init.then(shrink).then(recover).then(manual).then(unchangedArea).then(check(s.x==-500 and s.y==-200))
 run tinyUsableAreaTest=init.then(check(clamp(200,-400,10,108)==-400))
 run nonexistentUsableAreaNoOpTest=init.then(check(clamp(200,-400,0,108)==200))
 run recoveryIdempotentTest=init.then(shrink).then(recover).then(check(clamp(s.x,s.left,s.aw,s.width)==s.x and clamp(s.y,s.top,s.ah,s.height)==s.y))
}
