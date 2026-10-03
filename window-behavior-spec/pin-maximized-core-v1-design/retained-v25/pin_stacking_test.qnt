module pin_stacking_test {
 import pin_stacking.* from "./pin_stacking"
 run maintainedAfterOtherRaiseTest=init.then(fire(CoreRaise(4))).then(enforce).then(check(s.complete and s.order==List(4,1,3,2)))
 run modalStillAboveOwnerTest=init.then(fire(CoreRaise(1))).then(enforce).then(check(s.complete and s.order==List(4,2,1,3)))
 run independentPinBitsUnchangedTest=init.then(enforce).then(check(s.pinned==Set(1,2)and s.focus==4))
 run noCaptureNoWriteTest=init.then(fire(Advance(true))).then(check(s.lastWrite==0 and not(s.complete)))
 run closedCaptureNoWriteTest=init.then(fire(Capture)).then(fire(Close(1))).then(fire(Advance(true))).then(check(s.lastWrite==0 and not(s.complete)))
 run reusedCaptureNoWriteTest=init.then(fire(Capture)).then(fire(Reuse(1))).then(fire(Advance(true))).then(check(s.lastWrite==0 and not(s.complete)))
 run reloadCaptureNoWriteTest=init.then(fire(Capture)).then(fire(Reload)).then(fire(Advance(true))).then(check(s.lastWrite==0 and not(s.complete)))
 run pinCallbackInvalidatesTest=init.then(fire(Capture)).then(fire(Pin({owner:2,value:false}))).then(fire(Advance(true))).then(check(s.lastWrite==0 and not(s.complete)))
 run focusCallbackInvalidatesTest=init.then(fire(Capture)).then(fire(Focus(2))).then(fire(Advance(true))).then(check(s.lastWrite==0 and not(s.complete)))
 run minimizedCaptureNoWriteTest=init.then(fire(Capture)).then(fire(Minimize(1))).then(fire(Advance(true))).then(check(s.lastWrite==0 and not(s.complete)))
 run backendRefusalNoCompleteTest=init.then(fire(Capture)).then(fire(Advance(false))).then(fire(Finish)).then(check(not(s.complete)))
 run incompletePassNoSuccessTest=init.then(fire(Capture)).then(fire(Advance(true))).then(fire(Finish)).then(check(not(s.complete)))
 run reentrantCaptureNoRestartTest=init.then(fire(Capture)).then(fire(Advance(true))).then(fire(Capture)).then(check(s.index==1))
 run coreLowerPinnedStillProtectedTest=init.then(fire(CoreLower(2))).then(enforce).then(check(s.complete and s.order==List(4,2,1,3)))
 run coreLowerDuringPassInvalidatesTest=init.then(fire(Capture)).then(fire(CoreLower(2))).then(fire(Advance(true))).then(check(s.lastWrite==0 and not(s.complete)))
}
