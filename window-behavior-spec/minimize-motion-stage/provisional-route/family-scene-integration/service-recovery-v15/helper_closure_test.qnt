module helper_closure_test {
 import helper_closure.* from "./helper_closure"
 action check(p:bool):bool=all{assert(p),s'=s}
 action gated=fire(Reserve).then(fire(Gate({exact:true,isolated:true,noEscape:true})))
 action registered=gated.then(fire(Register({peer:true,descriptor:true})))
 action released=registered.then(fire(Publish)).then(fire(Release))
 run unjournaledJobCannotExecTest=init.then(registered).then(fire(Release)).then(check(not(s.released)))
 run wrongKernelPeerCannotRegisterTest=init.then(gated).then(fire(Register({peer:false,descriptor:true}))).then(fire(Publish)).then(fire(Release)).then(check(not(s.released)))
 run numericPIDWithoutDescriptorCannotExecTest=init.then(gated).then(fire(Register({peer:true,descriptor:false}))).then(fire(Publish)).then(fire(Release)).then(check(not(s.released)))
 run escapableGroupCannotExecTest=init.then(fire(Reserve)).then(fire(Gate({exact:true,isolated:true,noEscape:false}))).then(fire(Register({peer:true,descriptor:true}))).then(fire(Publish)).then(fire(Release)).then(check(not(s.released)))
 run leaderExitDoesNotCloseDescendantsTest=init.then(released).then(fire(LeaderExit)).then(fire(Terminal)).then(fire(Delete)).then(check(not(s.terminal) and not(s.deleted)))
 run exactKeeperClosesAfterLeaderExitTest=init.then(released).then(fire(LeaderExit)).then(fire(ServiceDeath)).then(fire(Signal)).then(fire(Terminal)).then(fire(Delete)).then(check(s.deleted and allProps))
 run missingKeeperCannotAuthorizeDeletionTest=init.then(released).then(fire(ServiceDeath)).then(fire(KeeperDeath)).then(fire(Signal)).then(fire(Terminal)).then(fire(Delete)).then(check(not(s.deleted) and not(s.signaled)))
 run inheritedPolicyRefusesEscapeTest=init.then(released).then(fire(Escape)).then(check(not(s.escaped) and allProps))
 run exitedEntireGroupCanCloseNormallyTest=init.then(released).then(fire(LeaderExit)).then(fire(DescendantExit)).then(fire(Terminal)).then(fire(Delete)).then(check(s.deleted and allProps))
}
