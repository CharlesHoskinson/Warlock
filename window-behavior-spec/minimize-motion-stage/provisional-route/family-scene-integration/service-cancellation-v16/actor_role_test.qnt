module actor_role_test {
 import actor_role.* from "./actor_role"
 action check(p:bool):bool=all{assert(p),s'=s}
 action attempt(c:Claim):bool=init.then(register(c,true)).then(release)
 run reviewedReadOnlyGateTest=attempt(validClaim).then(check(s.released))
 run reviewedRendererGateTest=attempt({...validClaim,command:Render,actualCommand:Render,role:Renderer}).then(check(s.released))
 run exactNativeEffectGateTest=attempt({...validClaim,command:Effect,actualCommand:Effect,role:Native}).then(check(s.released))
 run exactNativeExportGateTest=attempt({...validClaim,command:Export,actualCommand:Export,role:Native}).then(check(s.released))
 run nativeEffectCannotBorrowHelperRoleTest=attempt({...validClaim,command:Effect,actualCommand:Effect,role:Helper}).then(check(not(s.released)))
 run nativeExportCannotBorrowRendererRoleTest=attempt({...validClaim,command:Export,actualCommand:Export,role:Renderer}).then(check(not(s.released)))
 run unreviewedConfinedHandoffCannotRegisterTest=attempt({...validClaim,handoff:2,actualHandoff:2}).then(check(not(s.released)))
 run falseTargetArgvCannotRegisterTest=attempt({...validClaim,argv:2}).then(check(not(s.released)))
 run falseActualSourceCannotRegisterTest=attempt({...validClaim,actualSource:2}).then(check(not(s.released)))
 run durabilityFailureCannotReleaseTest=init.then(register(validClaim,false)).then(release).then(check(s.fault and not(s.released)))
}
