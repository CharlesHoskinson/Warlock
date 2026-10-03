module readonly_startup_test {
 import readonly_startup.* from "./readonly_startup"
 val p={owner:2,root:1,source:1,pointer:1,complete:true,durable:true}
 action check(b:bool):bool=all{assert(b),s'=s}
 action lease=fire(Lease(2))
 action seal=lease.then(fire(Seal(p)))
 action helper=seal.then(fire(PublishHelper(p)))
 run helperFirstPublicationPreservesExactLineageTest=init.then(helper).then(check(s.diskPointer==1 and not(s.bound) and not(s.bytes) and allProps))
 run crashAfterHelperBeforeReaderRecoversLineageTest=init.then(helper).then(fire(Crash)).then(fire(Lease(3))).then(fire(ValidatePending({...p,owner:3}))).then(fire(Bind({...p,owner:3}))).then(fire(Query)).then(check(s.bytes and s.oldRetained and allProps))
 run missingSealCannotPublishHelperTest=init.then(lease).then(fire(PublishHelper(p))).then(check(s.fault and not(s.helperPublished)))
 run wrongPointerCannotPublishHelperTest=init.then(seal).then(fire(PublishHelper({...p,pointer:2}))).then(check(s.fault and s.diskPointer==0))
 run malformedPendingLineageRefusesBeforeNativeRecoveryTest=init.then(helper).then(fire(Crash)).then(fire(Lease(3))).then(fire(ValidatePending({...p,owner:3,complete:false}))).then(fire(NativeRecover(true))).then(check(s.fault and not(s.nativeGuard)))
 run unvalidatedPendingCannotStartNativeRecoveryTest=init.then(helper).then(fire(Crash)).then(fire(Lease(3))).then(fire(NativeRecover(true))).then(check(s.fault and not(s.nativeGuard)))
 run dataLineageCannotWaiveNativeClosureTest=init.then(helper).then(fire(Crash)).then(fire(Lease(3))).then(fire(ValidatePending({...p,owner:3}))).then(fire(NativeRecover(false))).then(check(s.fault and not(s.nativeGuard)))
 run everyInvalidOwnerRootSourcePointerDurabilityRefusesTest=init.then(helper).then(fire(Crash)).then(fire(Lease(3))).then(all{nondet n=Set(1,2,3,4,5).oneOf();fire(ValidatePending({...p,owner:if(n==1)2 else 3,root:if(n==2)2 else 1,source:if(n==3)2 else 1,pointer:if(n==4)2 else 1,durable:n!=5}))}).then(check(s.fault and not(s.validated)))
}
