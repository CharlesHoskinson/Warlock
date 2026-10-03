module pending_direction_test {
 import pending_direction.* from "./pending_direction"
 action check(p:bool):bool=all{assert(p),s'=s}
 run pendingMinimizeThenToggleRestoresBeforeAnyContextTest=init.then(fire(Request(Minimize))).then(fire(Request(Toggle))).then(fire(Observe({receipt:2,live:true,minimized:false,active:true}))).then(check(not(s.target) and not(s.visual)))
 run twoInitialTogglesKeepVisibleNativeEndpointTest=init.then(fire(Request(Toggle))).then(fire(Request(Toggle))).then(fire(Observe({receipt:2,live:true,minimized:false,active:true}))).then(check(not(s.target) and not(s.visual)))
 run twoInitialTogglesKeepMinimizedNativeEndpointTest=init.then(fire(Request(Toggle))).then(fire(Request(Toggle))).then(fire(Observe({receipt:2,live:true,minimized:true,active:false}))).then(check(s.target and not(s.visual)))
 run pendingRestoreThenActivateMinimizesTest=init.then(fire(Request(Restore))).then(fire(Request(Activate))).then(fire(Observe({receipt:2,live:true,minimized:true,active:false}))).then(check(s.target))
 run inactiveActivateThenToggleMinimizesTest=init.then(fire(Request(Activate))).then(fire(Request(Toggle))).then(fire(Observe({receipt:2,live:true,minimized:false,active:false}))).then(check(s.target))
 run staleContextCannotResolveNewestDirectionTest=init.then(fire(Request(Minimize))).then(fire(Request(Toggle))).then(fire(Observe({receipt:1,live:true,minimized:false,active:true}))).then(check(not(s.effect)))
 run replacedIdentityCannotResolveAcceptedDirectionTest=init.then(fire(Request(Minimize))).then(fire(Observe({receipt:1,live:false,minimized:false,active:true}))).then(check(not(s.effect)))
 run retainedDisplayedVisualStillReversesOnMatchingNativeEndpointTest=init.then(fire(Held)).then(fire(Request(Restore))).then(fire(Observe({receipt:1,live:true,minimized:false,active:true}))).then(check(s.visual and not(s.target)))
 run failedDirectionDoesNotInfluenceNextToggleTest=init.then(fire(Request(Minimize))).then(fire(Fail(1))).then(fire(Request(Toggle))).then(fire(Observe({receipt:2,live:true,minimized:false,active:true}))).then(check(s.target))
}
