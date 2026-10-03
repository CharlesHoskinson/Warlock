module frontend_test {
 import frontend.* from "./frontend"
 pure val good={peer:true,eof:true,frame:true,ok:true,accepted:true,completedFalse:true,receiptValid:true}
 run invalidIdentityRefusedTest=init.then(fire(Validate(false))).then(fire(Send)).expect(phase==Refused and sends==0 and allProps)
 run verifiedAcceptedTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Reply(good))).then(fire(CommitLog(true))).expect(phase==Accepted and accepted and sends==1 and allProps)
 run noEofUnknownNoRetryTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Reply(good.with("eof",false)))).then(fire(Retry)).then(fire(Send)).expect(phase==Uncertain and not(accepted) and sends==1 and allProps)
 run disconnectedNoFallbackTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Disconnect)).then(fire(Retry)).then(fire(Send)).expect(phase==Uncertain and sends==1 and allProps)
 run explicitRejectedTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Reply(good.with("ok",false).with("accepted",false)))).expect(phase==Rejected and not(accepted) and sends==1 and allProps)
 run ambiguousReceiptTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Reply(good.with("receiptValid",false)))).expect(phase==Uncertain and not(accepted) and sends==1 and allProps)
 run postReceiptIdentityFaultTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Reply(good))).then(fire(Disconnect)).expect(phase==Uncertain and verifiedReceipt and not(accepted) and allProps)
 run postReceiptLogFaultTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Reply(good))).then(fire(CommitLog(false))).then(fire(Send)).expect(phase==Uncertain and verifiedReceipt and sends==1 and allProps)
 run duplicateAcceptedNoSendTest=init.then(fire(Validate(true))).then(fire(Send)).then(fire(Reply(good))).then(fire(CommitLog(true))).then(fire(Send)).expect(phase==Accepted and sends==1 and allProps)
}
