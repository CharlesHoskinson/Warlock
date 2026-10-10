module taskbar_output_focus_test {
 import taskbar_output_focus.* from "./taskbar-output-focus"
 action check(condition:bool):bool=all{assert(condition),s'=s}
 run retainedRawFocusCounterexampleTest=init.then(retire).then(check(s.rawFocus and not(s.visible) and not(projectedFocus) and offer=="activate"))
 run inactiveActivationMinimizeRestoreTest=init.then(retire).then(activate).then(minimize).then(restore).then(check(restored and s.effects==3 and safety))
 run shellBarCustodyRetainsActiveFamilyTest=init.then(retire).then(activate).then(holdBar).then(check(barCustody and safety))
 run shellPopupCustodyRetainsActiveFamilyTest=init.then(retire).then(activate).then(holdPopup).then(check(popupCustody and safety))
 run barCustodyMinimizeSuccessionTest=init.then(retire).then(activate).then(holdBar).then(minimize).then(check(minimized and s.seat=="desktop" and safety))
 run popupCustodyMinimizeSuccessionTest=init.then(retire).then(activate).then(holdPopup).then(minimize).then(check(minimized and s.seat=="desktop" and safety))
 run hiddenFocusedMemberIsInactiveTest=init.then(check(not(focusProjection(true,true,true,false,true))))
 run minimizedFocusedMemberIsInactiveTest=init.then(check(not(focusProjection(true,true,false,true,true))))
 run specialWorkspaceFocusIsInactiveTest=init.then(check(not(focusProjection(true,true,false,false,false))))
 run noNativeFocusCannotInventActivityTest=init.then(check(not(focusProjection(false,true,false,false,true))))
}
