module frontend_test {
 import frontend.* from "./frontend"
 run invalidIdentityRefusedTest=init.then(fire(Validate(false))).then(fire(Send)).then(all{assert(phase==Refused and sends==0 and allProps),fire(Retry)})
 run verifiedAcceptedTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Reply({peer:true,eof:true,frame:true,ok:true,accepted:true}))).then(all{assert(phase==Accepted and accepted and sends==1 and allProps),fire(Retry)})
 run noEofUnknownNoRetryTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Reply({peer:true,eof:false,frame:true,ok:true,accepted:true}))).then(fire(Retry)).then(fire(Send)).then(all{assert(phase==Uncertain and not(accepted) and sends==1 and allProps),fire(Retry)})
 run disconnectedNoFallbackTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Disconnect)).then(fire(Retry)).then(fire(Send)).then(all{assert(phase==Uncertain and sends==1 and allProps),fire(Retry)})
 run explicitRejectedTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Reply({peer:true,eof:true,frame:true,ok:false,accepted:false}))).then(all{assert(phase==Rejected and not(accepted) and sends==1 and allProps),fire(Retry)})
 run duplicateAcceptedNoSendTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Reply({peer:true,eof:true,frame:true,ok:true,accepted:true}))).then(fire(Send)).then(all{assert(phase==Accepted and sends==1 and allProps),fire(Retry)})
}
