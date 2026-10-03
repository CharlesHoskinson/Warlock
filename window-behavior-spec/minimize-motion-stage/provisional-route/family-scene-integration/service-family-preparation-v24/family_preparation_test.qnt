module family_preparation_test {
 import family_preparation.* from "./family_preparation"
 action check(p:bool):bool=all{assert(p),s'=s}
 action captures=init.then(fire(Capture({id:1,exact:true}))).then(fire(Capture({id:2,exact:true}))).then(fire(Capture({id:3,exact:true})))
 action produced=captures.then(fire(BeginBatch)).then(fire(HelperClosed({normal:true,outputs:true}))).then(fire(CheckCurrent(true)))
 action published=produced.then(fire(Publish(1))).then(fire(Publish(2))).then(fire(Publish(3)))
 run completeActualFamilyCanSeedTest=published.then(fire(Seed)).then(fire(NativeReady)).then(check(s.nativeCommitted and s.launches==1 and allProps))
 run partialSourcesCannotLaunchTest=init.then(fire(Capture({id:1,exact:true}))).then(fire(BeginBatch)).then(check(s.failed and s.launches==0))
 run duplicateSourceRefusesTest=captures.then(fire(Capture({id:1,exact:true}))).then(fire(BeginBatch)).then(check(s.failed and s.launches==0))
 run wrongNativeIdentityRefusesTest=init.then(fire(Capture({id:1,exact:false}))).then(fire(BeginBatch)).then(check(s.failed and s.launches==0))
 run normalZeroWithoutOutputsCannotSeedTest=captures.then(fire(BeginBatch)).then(fire(HelperClosed({normal:true,outputs:false}))).then(fire(CheckCurrent(true))).then(fire(Seed)).then(check(s.failed and not(s.seeded)))
 run failedHelperCannotPublishTest=captures.then(fire(BeginBatch)).then(fire(HelperClosed({normal:false,outputs:true}))).then(fire(CheckCurrent(true))).then(fire(Publish(1))).then(check(s.failed and s.published==Set()))
 run everyPreviewSlotRequiredTest=produced.then(fire(Publish(1))).then(fire(Publish(2))).then(fire(Seed)).then(check(s.failed and not(s.seeded)))
 run sourceGeometryDriftCannotSeedTest=published.then(fire(CheckCurrent(false))).then(fire(Seed)).then(check(s.failed and not(s.seeded)))
 run supersededWorkCannotPublishTest=produced.then(fire(Supersede)).then(fire(Publish(1))).then(check(s.failed and s.published==Set()))
 run lateResultCannotGainNewNativeAuthorityTest=published.then(fire(Seed)).then(fire(Supersede)).then(fire(NativeReady)).then(check(not(s.nativeCommitted)))
 run unfinishedHelperRetainsMaterialTest=captures.then(fire(BeginBatch)).then(fire(Supersede)).then(fire(Dispose)).then(check(not(s.disposed) and not(s.helperGone)))
 run supersededClosedWorkCanDisposeTest=produced.then(fire(Supersede)).then(fire(Dispose)).then(check(s.disposed and allProps))
 run noPerMemberHelperLaunchMultiplicationTest=captures.then(fire(BeginBatch)).then(fire(BeginBatch)).then(check(s.launches==1 and s.failed))
 run nativeWitnessIsHistoricalAfterSupersessionTest=published.then(fire(Seed)).then(fire(NativeReady)).then(fire(Supersede)).then(check(s.nativeCommitted and s.commitWitness and not(s.current) and allProps))
}
