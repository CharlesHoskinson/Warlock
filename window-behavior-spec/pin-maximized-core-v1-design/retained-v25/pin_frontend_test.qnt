module pin_frontend_test {
 import pin_frontend.* from "./pin_frontend"
 run actualCapturedOwnerTest=init.then(menu).then(fire(Invoke)).then(fire(Execute)).then(check(s.pinned.contains(1)and s.lastWrite==1))
 run noCaptureNoInvokeTest=init.then(fire(Open(1))).then(fire(Invoke)).then(fire(Execute)).then(check(not(s.queued)and s.lastWrite==0))
 run noAuthorityCaptureTest=init.then(fire(Open(1))).then(fire(Capture({nonce:1,token:{owner:1,generation:1,epoch:1},authority:false}))).then(check(not(s.ready)))
 run refocusNeverRedirectsTest=init.then(menu).then(fire(Focus(2))).then(fire(Invoke)).then(fire(Execute)).then(check(s.pinned==Set(1,2)))
 run dismissedNoActionTest=init.then(menu).then(fire(Dismiss)).then(fire(Invoke)).then(fire(Execute)).then(check(s.lastWrite==0))
 run oldMenuReplyCannotEnableNewTest=init.then(fire(Open(1))).then(fire(Open(1))).then(fire(Capture({nonce:1,token:{owner:1,generation:1,epoch:1},authority:true}))).then(check(not(s.ready)))
 run wrongMemberReplyNoActionTest=init.then(fire(Open(2))).then(fire(Capture({nonce:1,token:{owner:1,generation:1,epoch:1},authority:true}))).then(check(not(s.ready)))
 run oldLifetimeNoWriteTest=init.then(menu).then(fire(Invoke)).then(fire(Close)).then(fire(NewLifetime)).then(fire(Execute)).then(check(s.lastWrite==0 and not(s.pinned.contains(1))))
 run reloadNoWriteTest=init.then(menu).then(fire(Invoke)).then(fire(Reload)).then(fire(Execute)).then(check(s.lastWrite==0))
 run duplicateInvokeOneSendTest=init.then(menu).then(fire(Invoke)).then(fire(Invoke)).then(fire(Execute)).then(fire(Execute)).then(check(s.pinned==Set(1,2)and s.lastWrite==0))
 run failureAckNoRetryTest=init.then(menu).then(fire(Invoke)).then(fire(Execute)).then(fire(Ack(false))).then(fire(Execute)).then(check(not(s.complete)and s.lastWrite==0 and s.pinned==Set(1,2)))
 run actualCompleteTest=init.then(menu).then(fire(Invoke)).then(fire(Execute)).then(fire(Ack(true))).then(check(s.complete))
}
