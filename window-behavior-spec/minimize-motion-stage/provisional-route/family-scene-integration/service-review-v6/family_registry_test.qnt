module family_registry_test {
 import family_registry.* from "./family_registry"
 action check(p:bool):bool=all{assert(p),s'=s}
 run unknownPeerNewerReceiptBlocksOldFamilyClaimTest=init.then(fire(Reserve((0,0)))).then(fire(Reserve((1,1)))).then(fire(Claim((0,Set(0,1),true)))).then(fire(Commit(0))).then(check(not(s.effect)))
 run latestFreshScopeAtomicallyReclaimsPeersTest=init.then(fire(Reserve((0,0)))).then(fire(Claim((0,Set(0,1),true)))).then(fire(Reserve((1,1)))).then(fire(Claim((1,Set(0,1),true)))).then(fire(Commit(0))).then(check(not(s.effect))).then(fire(Commit(1))).then(check(s.effect and s.effectScope==Set(0,1)))
 run incompleteGraphCannotOwnScopeTest=init.then(fire(Reserve((0,0)))).then(fire(Claim((0,Set(0),false)))).then(fire(Commit(0))).then(check(not(s.effect)))
 run sameProcessUnrelatedIdentityDoesNotShareAuthorityTest=init.then(fire(Reserve((0,0)))).then(fire(Claim((0,Set(0),true)))).then(fire(Reserve((1,1)))).then(fire(Claim((1,Set(1),true)))).then(fire(Commit(0))).then(check(s.effectScope==Set(0))).then(fire(Commit(1))).then(check(s.effectScope==Set(1)))
 run closedOrReusedPeerRetiresWholeScopeTest=init.then(fire(Reserve((0,0)))).then(fire(Claim((0,Set(0,1),true)))).then(fire(Replace(1))).then(fire(Commit(0))).then(check(not(s.effect)))
}
