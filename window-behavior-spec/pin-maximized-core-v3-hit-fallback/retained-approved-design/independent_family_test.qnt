module independent_family_test {
 import max_pin.* from "./max_pin"
 run childExplicitPinUnpinnedAncestorTest=init.then(fire(ChildOwnPin)).then(check(not(s.windows.get(1).pinned) and s.windows.get(3).pinned and not(s.windows.get(4).pinned) and effective(3) and effective(4)))
 run ancestorPinUnpinPreservesChildOwnIntentTest=init.then(fire(ChildOwnPin)).then(pin(1)).then(unpin(1)).then(check(not(s.windows.get(1).pinned) and s.windows.get(3).pinned and effective(4) and not(s.windows.get(4).pinned)))
 run unrelatedFieldsPreservedWithComposeFamilyTest=init.then(fire(ChildOwnPin)).then(pin(1)).then(check(s.windows.get(2)==win(2) and s.windows.get(5)==win(5) and s.focus==5))
 run independentlyPinnedChildTransferDoesNotProtectDetachedNestedTest=init.then(fire(ChildOwnPin)).then(fire(ParentMove)).then(check(s.windows.get(3).pinned and effective(3) and not(effective(4)) and not(s.windows.get(1).pinned)))
}
