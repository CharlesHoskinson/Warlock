module workspaceInventoryTests {
 import workspaceInventory.* from "./workspace-inventory"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run currentEmptyWorkspaceCanBeBrowsedTest=init.then(request).then(current).then(show).then(browseEmpty).then(check(s.selected==2 and s.active==2 and s.effects==0))
 run foreignCannotPopulateInventoryTest=init.then(request).then(foreign).then(check(s.inventory==0 and s.listed==Set() and s.expected==1))
 run malformedCannotPopulateInventoryTest=init.then(request).then(malformed).then(check(s.inventory==0 and s.expected==1))
 run selectedRetirementFallsBackToAllTest=init.then(request).then(current).then(show).then(browseEmpty).then(request).then(current).then(check(s.open and s.selected==0 and not(s.listed.contains(2))))
 run replacementCannotReuseInventoryTest=init.then(request).then(current).then(show).then(browseEmpty).then(replace).then(check(not(s.open) and s.listed==Set() and s.active==0))
 run dismissIsObservationOnlyTest=init.then(request).then(current).then(show).then(browseEmpty).then(dismiss).then(check(not(s.open) and s.effects==0))
}
