module control_outbox_confirmation_tests {
 import control_outbox.* from "./control_outbox_confirmation"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run exactPacketRetriesAtSameOrdinal=init.then(fire(Offer)).then(fire(Retry)).then(check(s.pending==[1] and s.posted==[1,1]))
 run noOvertakingWhileReceiptMissing=init.then(fire(Offer)).then(fire(Offer)).then(check(s.pending==[1,2] and s.posted==[1]))
 run queueBackpressureConsumesNoOrdinal=init.then(fire(Offer)).then(fire(Offer)).then(fire(Offer)).then(check(not(s.last) and s.issued==2 and s.pending==[1,2]))
 run failedPostPreservesQueuedPacket=init.then(fire(FailPost)).then(fire(Offer)).then(fire(Retry)).then(check(not(s.last) and s.pending==[1] and s.issued==1)).then(fire(RecoverPost)).then(fire(Retry)).then(check(s.last and s.posted==[1,1,1]))
 run gapReceiptCannotReleaseQueue=init.then(fire(Offer)).then(fire(Ack2)).then(check(not(s.last) and s.pending==[1] and s.confirmed==0))
 run foreignEpochCannotReleaseQueue=init.then(fire(Offer)).then(fire(WrongEpoch)).then(check(not(s.last) and s.pending==[1]))
 run foreignBindingCannotReleaseQueue=init.then(fire(Offer)).then(fire(WrongBinding)).then(check(not(s.last) and s.pending==[1]))
 run confirmedPacketReleasesOnlyHead=init.then(fire(Offer)).then(fire(Offer)).then(fire(Ack1)).then(check(s.pending==[2] and s.posted==[1,2] and s.confirmed==1))
 run duplicateReceiptCannotAdvanceAgain=init.then(fire(Offer)).then(fire(Ack1)).then(fire(Offer)).then(fire(Ack1)).then(check(s.last and s.pending==[2] and s.confirmed==1 and s.confirmations==[1,1]))
 run finalOrdinalRetainedWithoutWrap=init.then(fire(Boundary)).then(fire(Offer)).then(fire(Offer)).then(fire(Retry)).then(check(s.issued==maximum and s.pending==[maximum] and s.posted==[maximum,maximum]))
 run emptyQueueRetriesLostConfirmation=init.then(fire(Offer)).then(fire(FailConfirmation)).then(fire(Ack1)).then(fire(Retry)).then(check(not(s.last) and s.pending==[] and s.confirmations==[1,1])).then(fire(RecoverConfirmation)).then(fire(Retry)).then(check(s.last and s.confirmations==[1,1,1]))
 run oldReceiptRepeatsLatestCompactConfirmation=init.then(fire(Offer)).then(fire(Ack1)).then(fire(Offer)).then(fire(Ack2)).then(fire(Ack1)).then(check(s.confirmed==2 and s.confirmations==[1,2,2]))
 run dataAndConfirmationRetryAreBounded=init.then(fire(Offer)).then(fire(Offer)).then(fire(Ack1)).then(fire(Retry)).then(check(s.pending==[2] and s.confirmations==[1,1] and s.posted==[1,2,2]))
}
