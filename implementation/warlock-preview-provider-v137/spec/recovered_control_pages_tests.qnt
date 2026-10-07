module recovered_control_pages_tests {
 import recovered_control_pages.* from "./recovered_control_pages"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run cannotInventNativeOrdinal=init.then(fire(Retain)).then(check(not(s.last) and s.through==0))
 run exactNativeTicketRetry=init.then(fire(Issue)).then(fire(Retain)).then(fire(Retry)).then(check(s.posted==[1,1] and s.pending==[1]))
 run issuedNeighborCannotOvertake=init.then(fire(Issue)).then(fire(Retain)).then(fire(Issue)).then(fire(Retain)).then(check(s.pending==[1,2] and s.posted==[1]))
 run backpressureRetainsNativeIssuance=init.then(fire(Issue)).then(fire(Retain)).then(fire(Issue)).then(fire(Retain)).then(fire(Issue)).then(fire(Retain)).then(check(not(s.last) and s.native==3 and s.through==2))
 run droppedPostRetainsExactTicket=init.then(fire(FailPost)).then(fire(Issue)).then(fire(Retain)).then(fire(Retry)).then(check(not(s.last) and s.pending==[1])).then(fire(RecoverPost)).then(fire(Retry)).then(check(s.last))
 run deliveredAdvisoryCannotDrain=init.then(fire(Issue)).then(fire(Retain)).then(fire(Advisory)).then(check(s.pending==[1] and s.delivered==0 and s.posted==[1,1]))
 run changedIssuedBytesRefuse=init.then(fire(Issue)).then(fire(Retain)).then(fire(Changed)).then(check(not(s.last) and s.pending==[1] and s.posted==[1]))
 run nativeOrdinalGapRefuses=init.then(fire(Issue)).then(fire(Gap)).then(check(not(s.last) and s.through==0))
 run futureReceiptCannotRelease=init.then(fire(Issue)).then(fire(Retain)).then(fire(Ack2)).then(check(not(s.last) and s.pending==[1]))
 run oldRealmReceiptCannotRelease=init.then(fire(Issue)).then(fire(Retain)).then(fire(WrongEpoch)).then(fire(WrongBinding)).then(check(not(s.last) and s.pending==[1]))
 run exactHeadDeliveryAdvancesNeighbor=init.then(fire(Issue)).then(fire(Retain)).then(fire(Issue)).then(fire(Retain)).then(fire(Ack1)).then(check(s.pending==[2] and s.delivered==1 and s.confirmations==[1] and s.posted==[1,2]))
 run lostConfirmationRetainedAfterQueueEmpty=init.then(fire(Issue)).then(fire(Retain)).then(fire(FailConfirm)).then(fire(Ack1)).then(fire(Retry)).then(check(not(s.last) and s.pending==[] and s.confirmations==[1,1])).then(fire(RecoverConfirm)).then(fire(Retry)).then(check(s.last and s.confirmations==[1,1,1]))
 run repeatedReceiptCannotAdvanceNeighbor=init.then(fire(Issue)).then(fire(Retain)).then(fire(Ack1)).then(fire(Issue)).then(fire(Retain)).then(fire(Ack1)).then(check(s.pending==[2] and s.delivered==1 and s.posted==[1,2]))
 run receiptMakesRoomForRetainedNativeTicket=init.then(fire(Issue)).then(fire(Retain)).then(fire(Issue)).then(fire(Retain)).then(fire(Issue)).then(fire(Retain)).then(fire(Ack1)).then(fire(Retain)).then(check(s.pending==[2,3] and s.through==3))

 run coldRecoveryDoesNotPost=init.then(fire(RecoverCold)).then(check(s.pending==[1,2] and s.posted==[] and s.confirmations==[]))
 run warmRecoveryRetainsNativePrefix=init.then(fire(RecoverWarm)).then(fire(Retry)).then(check(s.pending==[2] and s.delivered==1 and s.posted==[2] and s.confirmations==[1]))
 run emptyRecoveryRetainsConfirmation=init.then(fire(RecoverEmpty)).then(fire(Retry)).then(check(s.pending==[] and s.confirmations==[2] and s.posted==[]))
 run incompleteRecoveryDoesNotPost=init.then(fire(IncompleteRecovery)).then(check(not(s.last) and s.through==0 and s.posted==[]))
 run mixedRecoveryPrefixDoesNotPost=init.then(fire(MixedPrefixRecovery)).then(check(not(s.last) and s.through==0))
 run wrongRecoveryPositionDoesNotPost=init.then(fire(WrongPositionRecovery)).then(check(not(s.last) and s.through==0))
 run recoveryTicketGapDoesNotPost=init.then(fire(GapTicketRecovery)).then(check(not(s.last) and s.through==0))
 run foreignRecoveryEpochDoesNotPost=init.then(fire(ForeignEpochRecovery)).then(check(not(s.last) and s.through==0))
 run recoveredNeighborCannotOvertake=init.then(fire(RecoverCold)).then(fire(Retry)).then(check(s.posted==[1] and s.pending==[1,2]))
 run recoveredReceiptAdvancesOnlyHead=init.then(fire(RecoverCold)).then(fire(Retry)).then(fire(Ack1)).then(check(s.pending==[2] and s.delivered==1 and s.posted==[1,2]))
}
