module new_instance_test {
  import new_instance.* from "./new-instance"
  run windowMenuLaunchTest = init.then(explicit(1,1)).then(all{
    assert(s.launches==1 and s.phase==Pending and s.origin==Closed and
      s.windowEffects==0 and windowMenuLaunch and safety),s'=s})
  run applicationActionsLaunchTest = init.then(catalog(2,2))
    .then(open(ApplicationActions)).then(explicit(3,2)).then(all{
      assert(applicationActionsLaunch and s.launches==1 and safety),s'=s})
  run ordinaryActivationNeverLaunchesTest = init.then(ordinaryPrimary)
    .then(ordinaryPrimary).then(all{assert(ordinaryWithoutLaunch and
      s.windowEffects==2 and safety),s'=s})
  run staleViewAndIdentityTest = init.then(explicit(0,1)).then(explicit(1,2))
    .then(all{assert(s.launches==0 and s.origin==WindowMenu and safety),s'=s})
  run catalogReplacementRejectsOldSelectionTest = init.then(catalog(2,1))
    .then(explicit(1,1)).then(explicit(2,1)).then(all{
      assert(s.launches==0 and safety),s'=s})
  run ambiguousWindowMenuTest = init.then(catalog(1,2)).then(explicit(2,1))
    .then(all{assert(s.launches==0 and safety),s'=s})
  run removedCatalogIdentityTest = init.then(catalog(0,0)).then(explicit(2,1))
    .then(all{assert(s.launches==0 and safety),s'=s})
  run pendingDuplicateTest = init.then(explicit(1,1)).then(explicit(1,1))
    .then(explicit(2,1)).then(all{assert(s.launches==1 and s.phase==Pending and safety),s'=s})
  run unknownNeverReplaysTest = init.then(explicit(1,1)).then(receipt(1,Unknown))
    .then(catalog(1,1)).then(open(ApplicationActions)).then(explicit(5,1))
    .then(receipt(1,Submitted)).then(all{
      assert(unknownRetained and s.launches==1 and safety),s'=s})
  run refusalHasNoFallbackLaunchTest = init.then(explicit(1,1))
    .then(receipt(1,Refused)).then(ordinaryPrimary).then(all{
      assert(s.launches==1 and s.phase==Refused and s.windowEffects==1 and safety),s'=s})
  run unavailableTest = init.then(unavailable).then(explicit(2,1))
    .then(all{assert(s.launches==0 and safety),s'=s})
  run staleReceiptTest = init.then(explicit(1,1)).then(receipt(0,Submitted))
    .then(all{assert(s.phase==Pending and s.launches==1 and safety),s'=s})
}
