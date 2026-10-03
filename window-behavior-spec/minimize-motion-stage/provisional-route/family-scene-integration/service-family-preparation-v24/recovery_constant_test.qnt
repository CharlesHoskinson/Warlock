module recovery_constant_test {
 import recovery_constant.* from "./recovery_constant"
 action check(p:bool):bool=all{assert(p),s'=s}
 action owned=fire(Accept(2)).then(fire(Claim({complete:true,newer:false})))
 action prepared=owned.then(fire(Prepare(true)))
 run incompleteFamilyCannotPrepareTest=init.then(fire(Accept(2))).then(fire(Claim({complete:false,newer:false}))).then(fire(Prepare(true))).then(check(not(s.prepared)))
 run newerOwnerCannotPrepareTest=init.then(fire(Accept(2))).then(fire(Claim({complete:true,newer:true}))).then(fire(Prepare(true))).then(check(not(s.prepared)))
 run endpointMustBeDurableBeforeWriteTest=init.then(owned).then(fire(NativeWrite)).then(check(not(s.effect)))
 run crashAfterWriteCannotRetoggleEndpointTest=init.then(prepared).then(fire(NativeWrite)).then(fire(Crash)).then(fire(Reload)).then(fire(Claim({complete:true,newer:false}))).then(fire(Prepare(false))).then(fire(NativeWrite)).then(check(s.effect and s.operation and allProps))
 run crashRequiresFreshCompleteOwnershipTest=init.then(prepared).then(fire(Crash)).then(fire(Reload)).then(fire(NativeWrite)).then(check(not(s.effect)))
 run nativeWriteWithoutReturnedResultCannotClearTest=init.then(prepared).then(fire(NativeWrite)).then(fire(Endpoint(true))).then(fire(Clear)).then(check(not(s.cleared)))
 run durableResultAndObservedEndpointCanClearTest=init.then(prepared).then(fire(NativeWrite)).then(fire(DurableResult)).then(fire(Endpoint(true))).then(fire(Clear)).then(check(s.cleared and allProps))
}
