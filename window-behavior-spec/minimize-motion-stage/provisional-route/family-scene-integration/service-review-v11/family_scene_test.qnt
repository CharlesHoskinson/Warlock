module family_scene_test {
 import family_scene.* from "./family_scene"
 action check(condition:bool):bool=all{assert(condition),s'=s}
 val proof={epoch:1,ids:List(1,2),scope:Set(0,1),complete:true,edges:true,detached:false}
 val frame={epoch:1,output:0,generation:1,scope:Set(0,1),ids:List(1,2),versions:List(11,22)}
 run fullSceneBothOutputsCommitTest=init.then(fire(Present(frame))).then(fire(Present({...frame,output:1}))).then(fire(Commit)).then(check(s.committed and allProps))
 run reserveImmediatelyRevokesNativeAuthorityTest=init.then(fire(Present(frame))).then(fire(Present({...frame,output:1}))).then(fire(Reserve)).then(fire(Commit)).then(check(not(s.committed) and s.versions==List(11,22) and allProps))
 run unvalidatedProvisionalSceneMovesWithoutAuthorityTest=init.then(fire(Reserve)).then(fire(Present({...frame,epoch:2}))).then(fire(Present({...frame,epoch:2,output:1}))).then(fire(Commit)).then(check(s.presented==Set(0,1) and not(s.committed) and allProps))
 run rapidThirdRejectsSecondMetadataTest=init.then(fire(Reserve)).then(fire(Reserve)).then(fire(Validate({...proof,epoch:2}))).then(check(s.epoch==3 and not(s.validated) and allProps))
 run incompleteFamilyCannotBecomeSingletonTest=init.then(fire(Reserve)).then(fire(Validate({...proof,epoch:2,complete:false,scope:Set(0),detached:true}))).then(check(not(s.validated) and s.scope==Set(0,1) and allProps))
 run successfulSingletonNeedsExplicitDetachmentTest=init.then(fire(Reserve)).then(fire(Validate({...proof,epoch:2,scope:Set(0)}))).then(check(not(s.validated))).then(fire(Validate({...proof,epoch:2,scope:Set(0),detached:true}))).then(check(s.validated and s.scope==Set(0) and allProps))
 run missingPeerPresentationCannotCommitTest=init.then(fire(Present(frame))).then(fire(Commit)).then(check(not(s.committed) and allProps))
 run peerReuseClearsPixelAndNativeAuthorityTest=init.then(fire(Replace(1))).then(fire(Present(frame))).then(fire(Commit)).then(check(s.versions.nth(1)==0 and not(s.committed) and allProps))
 run retiredOutputCannotSupplyEndpointTest=init.then(fire(OutputChange)).then(fire(Present(frame))).then(fire(Commit)).then(check(not(s.committed) and s.presented==Set() and allProps))
}
