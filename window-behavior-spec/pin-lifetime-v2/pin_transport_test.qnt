module pin_transport_test {
 import pin_transport.* from "./pin_transport"
 pure val good={eof:true,valid:true,nativeOk:true,after:true}
 run exactOneRequestTest=init.then(prepared).then(fire(Send)).then(fire(Reply(good))).then(check(success and sends==1))
 run noCaptureNoFallbackTest=init.then(fire(Guard(true))).then(fire(Send)).then(check(refused and sends==0))
 run staleOwnerRefusedTest=init.then(fire(Capture({...first,owner:2}))).then(fire(Guard(true))).then(fire(Send)).then(check(refused and sends==0))
 run staleLifetimeRefusedTest=init.then(fire(Capture(first))).then(fire(ChangeLifetime)).then(fire(Guard(true))).then(fire(Send)).then(check(refused and sends==0))
 run staleEpochRefusedTest=init.then(fire(Capture(first))).then(fire(Reload)).then(fire(Guard(true))).then(fire(Send)).then(check(refused and sends==0))
 run stalePluginRefusedTest=init.then(fire(Capture(first))).then(fire(UnloadReload)).then(fire(Guard(true))).then(fire(Send)).then(check(refused and sends==0))
 run staleCompositorRefusedTest=init.then(fire(Capture(first))).then(fire(SessionChange)).then(fire(Guard(true))).then(fire(Send)).then(check(refused and sends==0))
 run guardChangeBeforeSendRefusedTest=init.then(prepared).then(fire(ChangeAuthority)).then(fire(Send)).then(check(refused and sends==0))
 run noRetryAfterSendTest=init.then(prepared).then(fire(Send)).then(fire(Send)).then(check(sends==1 and refused))
 run missingEOFUncertainTest=init.then(prepared).then(fire(Send)).then(fire(Reply({...good,eof:false}))).then(check(uncertain and not(success)))
 run malformedResultUncertainTest=init.then(prepared).then(fire(Send)).then(fire(Reply({...good,valid:false}))).then(check(uncertain and not(success)))
 run changedAfterUncertainTest=init.then(prepared).then(fire(Send)).then(fire(Reply({...good,after:false}))).then(check(uncertain and not(success)))
 run lifecycleAfterSendUncertainTest=init.then(prepared).then(fire(Send)).then(fire(ChangeLifetime)).then(fire(Reply(good))).then(check(uncertain and not(success)))
 run nativeRefusalExplicitTest=init.then(prepared).then(fire(Send)).then(fire(Reply({...good,nativeOk:false}))).then(check(refused and not(success) and not(uncertain)))
 run uncertaintyCannotBeGreenOnLaterReplyTest=init.then(prepared).then(fire(Send)).then(fire(Reply({...good,eof:false}))).then(fire(Reply(good))).then(check(uncertain and not(success)))
}
