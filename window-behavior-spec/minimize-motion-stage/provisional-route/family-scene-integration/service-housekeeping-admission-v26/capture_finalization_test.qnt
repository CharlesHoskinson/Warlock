module capture_finalization_test {
 import capture_finalization.* from "./capture_finalization"
 action check(p:bool):bool=all{assert(p),s'=s}
 action staged=init.then(fire(Finalize)).then(fire(Stage))
 run finalizedExactInodeMayPublishTest=staged.then(fire(Return)).then(fire(Publish)).then(check(s.published and allProps))
 run stageBeforePermissionFinalizationRefusesTest=init.then(fire(Stage)).then(check(s.refused and s.staged==0 and allProps))
 run actualOldStagingCounterexampleTest=init.then(fire(OldStage)).then(check(s.staged==s.inode and not(s.finalized) and not(allProps)))
 run permissionMutationAfterStagingRefusesTest=staged.then(fire(Mutation)).then(fire(Return)).then(check(s.refused and not(s.returned) and allProps))
 run bytesMutationAfterReturnRefusesPublicationTest=staged.then(fire(Return)).then(fire(Mutation)).then(fire(Publish)).then(check(s.refused and not(s.published) and allProps))
 run duplicatePermissionFinalizationAfterStagingRefusesTest=staged.then(fire(Finalize)).then(check(s.refused and allProps))
 run noStageCannotReturnSourceTest=init.then(fire(Finalize)).then(fire(Return)).then(check(s.refused and not(s.returned) and allProps))
 run historicalPublishedWitnessSurvivesLaterMutationTest=staged.then(fire(Return)).then(fire(Publish)).then(fire(Mutation)).then(check(s.publishWitness and allProps))
}
