module persistent_atlas_test {
 import persistent_atlas.* from "./persistent_atlas"
 action check(p:bool):bool=all{assert(p),s'=s}
 run exactPersistentPairSurvivesActorReloadTest=init.then(fire(Stage(original))).then(fire(Publish(original))).then(fire(Read)).then(check(s.provided and s.source.pixels==101))
 run oldCaptureAfterReuseCannotProvideNewIdentityPixelsTest=init.then(fire(Reuse)).then(fire(Stage(original))).then(fire(Publish(original))).then(fire(Read)).then(check(not(s.provided)))
 run compositorRestartWithSameNativeNumbersRejectsOldPixelsTest=init.then(fire(Stage(original))).then(fire(Publish(original))).then(fire(Restart)).then(fire(Read)).then(check(not(s.provided)))
 run metadataCommitBeforeImmutableImageCannotPublishTest=init.then(fire(Publish(original))).then(fire(Read)).then(check(not(s.provided)))
 run interruptedNewPublicationRetainsOldCompletePairTest=init.then(fire(Stage(original))).then(fire(Publish(original))).then(fire(Stage({...original,pixels:102}))).then(fire(Read)).then(check(s.provided and s.source.pixels==101))
 run geometryDriftRejectsRetainedAtlasTest=init.then(fire(Stage(original))).then(fire(Publish(original))).then(fire(Move)).then(fire(Read)).then(check(not(s.provided)))
 run completeJanitorRetainsLiveMinimizedPairTest=init.then(fire(Stage(original))).then(fire(Publish(original))).then(fire(Stage({...original,pixels:102}))).then(fire(Prune)).then(fire(Read)).then(check(s.provided and s.images==Set(original)))
 run closedIdentityJanitorDeletesOnlyOwnedPairTest=init.then(fire(Stage(original))).then(fire(Publish(original))).then(fire(Reuse)).then(fire(Prune)).then(check(s.images==Set() and s.pointer==Empty))
}
