module ancestor_policy_test {
 import ancestor_policy.* from "./ancestor_policy"
 pure val OWNER={geometric:1,filtered:0,pointer:0,foreign:false,region:true,decoration:false,guard:false}
 run filteredOwnerRecoveredTest=init.then(fire(Click(OWNER))).then(all{assert(s.focus==3 and s.consumed and s.delivered==0),fire(Release)})
 run nestedOwnerRecoveredTest=init.then(fire(Modal(2))).then(fire(Click(OWNER))).then(all{assert(s.focus==4 and s.consumed),fire(Release)})
 run intermediateRecoveredTest=init.then(fire(Modal(2))).then(fire(Click({...OWNER,geometric:3}))).then(all{assert(s.focus==4 and s.consumed),fire(Release)})
 run underlyingPointerRecoveredTest=init.then(fire(Click({...OWNER,filtered:2,pointer:2}))).then(all{assert(s.focus==3 and s.delivered==0),fire(Release)})
 run unrelatedOccluderWinsTest=init.then(fire(Click({...OWNER,geometric:2,filtered:2,pointer:2}))).then(all{assert(s.focus==2 and not(s.consumed) and s.delivered==2),fire(Release)})
 run regionHoleRefusesTest=init.then(fire(Click({...OWNER,region:false}))).then(all{assert(s.focus==2 and not(s.consumed)),fire(Release)})
 run decorationAuthorityRecoversTest=init.then(fire(Click({...OWNER,region:false,decoration:true}))).then(all{assert(s.focus==3 and s.consumed),fire(Release)})
 run nonWindowSurfaceRefusesTest=init.then(fire(Click({...OWNER,foreign:true}))).then(all{assert(s.focus==2 and not(s.consumed)),fire(Release)})
 run guardsRefuseTest=init.then(fire(Click({...OWNER,guard:true}))).then(all{assert(s.focus==2 and not(s.consumed)),fire(Release)})
 run conflictingPointerRefusesTest=init.then(fire(Click({...OWNER,pointer:2}))).then(all{assert(s.focus==2 and not(s.consumed)),fire(Release)})
 run destroyedModalRefusesTest=init.then(fire(Modal(0))).then(fire(Click(OWNER))).then(all{assert(s.focus==2 and not(s.consumed)),fire(Release)})
 run closeBeforeReleaseConsumesTest=init.then(fire(Click(OWNER))).then(fire(Modal(0))).then(fire(Release)).then(all{assert(s.delivered==0 and not(s.consumed)),fire(Focus(2))})
}
