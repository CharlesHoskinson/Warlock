module process_evidence_test {
 import process_evidence.* from "./process_evidence"
 run strictPositiveTest = init.then(observe(true,true,true,true,true,true,true)).expect(accepted)
 run incompleteRefusedTest = init.then(observe(false,true,true,true,true,true,true)).expect(not(accepted))
 run staleRefusedTest = init.then(observe(true,false,true,true,true,true,true)).expect(not(accepted))
 run unownedRefusedTest = init.then(observe(true,true,false,true,true,true,true)).expect(not(accepted))
 run unknownRoleRefusedTest = init.then(observe(true,true,true,false,true,true,true)).expect(not(accepted))
 run noSandboxRefusedTest = init.then(observe(true,true,true,true,false,true,true)).expect(not(accepted))
 run privilegeRefusedTest = init.then(observe(true,true,true,true,true,false,true)).expect(not(accepted))
 run hostNetworkRefusedTest = init.then(observe(true,true,true,true,true,true,false)).expect(not(accepted))
}
