module popup_location_reflow_test {
  import popup_location_reflow.* from "./popup-location-reflow"
  run locationPreservesPolicyTest = init.then(location(640)).then(all{
    assert(s.open and s.ready and s.choice==10 and s.lease==1 and s.inputLease==0 and s.observations==0 and safety),s'=s})
  run growAndShrinkTest = init.then(location(640)).then(currentReflow(1,1))
    .then(location(480)).then(currentReflow(1,2)).then(all{assert(grownAndShrunk and s.lease==3 and safety),s'=s})
  run retiredLeaseTest = init.then(location(640)).then(currentReflow(1,1))
    .then(rejectedCallback(1,1)).then(all{assert(resizedAndReflowed and s.lease==2 and s.reflows==1 and safety),s'=s})
  run foreignScopeTest = init.then(location(640)).then(rejectedCallback(2,1))
    .then(all{assert(s.lease==1 and s.inputLease==0 and s.reflows==0 and safety),s'=s})
  run changedGenerationRetiresTest = init.then(replace).then(rejectedCallback(1,1))
    .then(all{assert(replacementRetired and s.reflows==0 and safety),s'=s})
  run refusalCannotRestoreRegistrationTest = init.then(refuse).then(fullTopology)
    .then(all{assert(refusalRetained and s.observations==1 and safety),s'=s})
  run exhaustedCannotReopenTest = init.then(exhaust).then(fullTopology).then(rejectedCallback(1,1))
    .then(all{assert(s.exhausted and not(s.open) and s.reflows==0 and safety),s'=s})
  run unreadyKeepsReconciliationTest = init.then(unready).then(fullTopology)
    .then(all{assert(not(s.ready) and s.observations==1 and safety),s'=s})
}
