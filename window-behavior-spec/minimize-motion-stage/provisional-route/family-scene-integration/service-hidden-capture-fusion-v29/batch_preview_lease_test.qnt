module batch_preview_lease_test {
 import batch_preview_lease.* from "./batch_preview_lease"
 action check(p:bool):bool=all{assert(p),s'=s}
 action staged=init.then(fire(Stage(1))).then(fire(Stage(2))).then(fire(Stage(3)))
 action launched=staged.then(fire(Launch))
 action closed=launched.then(fire(Returned({closed:true,outputs:true})))
 run oneCompleteBatchPublishesTest=closed.then(fire(Publish)).then(fire(Dispose)).then(check(s.published and s.disposed and allProps))
 run liveHelperRefusesSourceReleaseTest=launched.then(fire(Release(1))).then(check(s.pending==Set(1,2,3) and s.refused))
 run uncertainClosureRetainsSourcesTest=launched.then(fire(Returned({closed:false,outputs:true}))).then(fire(Release(1))).then(fire(Dispose)).then(check(s.uncertain and not(s.disposed) and s.pending==Set(1,2,3)))
 run noOutputDespiteClosedHelperRefusesPublishTest=launched.then(fire(Returned({closed:true,outputs:false}))).then(fire(Publish)).then(check(not(s.published) and s.refused))
 run supersededResultCannotPublishTest=closed.then(fire(Current(false))).then(fire(Publish)).then(check(not(s.published) and s.pending==Set(1,2,3)))
 run closedFailedBatchCanReleaseTest=launched.then(fire(Returned({closed:true,outputs:false}))).then(fire(Release(1))).then(fire(Release(2))).then(fire(Release(3))).then(fire(Dispose)).then(check(s.disposed and allProps))
 run abandonedPartialCaptureCanReleaseTest=init.then(fire(Stage(1))).then(fire(Release(1))).then(fire(Dispose)).then(check(s.disposed and allProps))
 run duplicateEpochRefusesTest=staged.then(fire(Stage(1))).then(check(s.refused and s.pending==Set(1,2,3)))
 run pendingEpochRefusesDisposeTest=staged.then(fire(Dispose)).then(check(not(s.disposed) and s.refused))
 run partialFamilyRefusesLaunchTest=init.then(fire(Stage(1))).then(fire(Launch)).then(check(not(s.active) and s.launches==0 and s.refused))
}
