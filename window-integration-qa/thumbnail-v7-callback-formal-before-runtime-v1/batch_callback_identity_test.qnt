module batch_callback_identity_test {
 import batch_callback_identity.* from "./batch_callback_identity"
 action check(v:bool):bool=all{assert(v),s'=s}
 action accepted=fire(Link(good)).then(fire(Original(true))).then(fire(Confirm(good))).then(fire(Accept))
 pure def changed(role:int,fn:int,owner:int):Binding={...good,callbacks:callbacks.set(role,{function:fn,owner:owner,source:true})}
 action refuses(p:Binding)=fire(Link(p)).then(fire(Original(true))).then(fire(Confirm(p))).then(fire(Accept)).then(check(s.refused and not(s.accepted)))
 run exactActorAndDesktopRolesAcceptTest=init.then(accepted).then(check(s.accepted))
 run frozenFinishCannotBeStageTest=init.then(refuses(changed(1,2,1)))
 run frozenStageCannotBeFinishTest=init.then(refuses(changed(2,1,1)))
 run frozenReleasableCannotBeDiscardTest=init.then(refuses(changed(3,4,1)))
 run frozenDiscardCannotBeReleasableTest=init.then(refuses(changed(4,3,1)))
 run frozenOtherMethodCannotBeDisposableTest=init.then(refuses(changed(5,4,1)))
 run frozenOtherMethodCannotBeFinisherTest=init.then(refuses(changed(6,5,2)))
 run genuineForeignBatchCannotOwnStageTest=init.then(refuses(changed(1,1,3)))
 run genuineForeignBatchCannotOwnFinishTest=init.then(refuses(changed(2,2,3)))
 run genuineForeignBatchCannotOwnDiscardTest=init.then(refuses(changed(3,3,3)))
 run genuineForeignBatchCannotOwnReleaseGuardTest=init.then(refuses(changed(4,4,3)))
 run genuineForeignBatchCannotOwnDisposeGuardTest=init.then(refuses(changed(5,5,3)))
 run genuineForeignDesktopCannotOwnFinisherTest=init.then(refuses(changed(6,6,3)))
 run missingRoleCannotAcceptTest=init.then(refuses({...good,callbacks:callbacks.remove(5)}))
 run extraRoleCannotAcceptTest=init.then(refuses({...good,callbacks:callbacks.put(7,{function:7,owner:1,source:true})}))
 run sourceEvidenceAloneCannotAcceptTest=init.then(fire(Original(true))).then(fire(Confirm(good))).then(fire(Accept)).then(check(not(s.accepted)))
 run wrongRoleAfterDiskRefusesTest=init.then(fire(Link(good))).then(fire(Confirm(changed(1,2,1)))).then(check(s.refused))
 run foreignOwnerAtTerminalRefusesTest=init.then(fire(Link(good))).then(fire(Confirm(changed(6,6,3)))).then(check(s.refused))
 run wrongModuleCannotAcceptTest=init.then(refuses({...good,moduleToken:22}))
 run wrongOwnerCannotAcceptTest=init.then(refuses({...good,ownerToken:2}))
 run refusalCannotBeClearedByCorrectRolesTest=init.then(refuses(changed(1,2,1))).then(accepted).then(check(s.refused and not(s.accepted)))
}
