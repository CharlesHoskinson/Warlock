module job_control_tests {
 import job_control.* from "./job_control"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 action finish=fire(Cancel).then(fire(DeliverCancel)).then(fire(Ack)).then(fire(DeliverAck))
 run typedNativePurposePrecedesEffect=init.then(fire(Cancel)).then(check(s.issued==1 and s.records==1 and s.charge==4096 and s.invocations==0))
 run exactProposalKeepsOriginalTicket=init.then(fire(Cancel)).then(fire(Cancel)).then(check(s.issued==1 and s.tickets==1))
 run inventedProofHasNoTicket=init.then(fire(Ack)).then(check(s.last== -1 and s.issued==0 and s.reserved==8))
 run originalTerminalProofChoosesAckSlot=init.then(fire(Cancel)).then(fire(DeliverCancel)).then(fire(Ack)).then(check(s.issued==2 and s.phase==1 and s.records==1))
 run postEffectAckRetryRetainsOriginal=init.then(finish).then(fire(Ack)).then(check(s.last==1 and s.records==0 and s.issued==2))
 run duplicateTicketCannotInvokeAgain=init.then(finish).then(fire(DeliverAck)).then(check(s.last==2 and s.invocations==2))
 run unconfirmedAckCannotReleaseCredits=init.then(finish).then(fire(Resume)).then(check(s.last==0 and s.job==1 and s.tickets==2))
 run confirmedResumeKeepsNamespace=init.then(finish).then(fire(Confirm)).then(fire(Resume)).then(check(s.job==2 and s.issued==2 and s.previous==1 and s.tickets==0))
 run exactConfirmedPredecessorIsDelivered=init.then(finish).then(fire(Confirm)).then(fire(Resume)).then(fire(OldAck)).then(check(s.last==2 and s.issued==2 and s.invocations==2))
 run changedConfirmedBodyCannotSuppress=init.then(finish).then(fire(Confirm)).then(fire(Resume)).then(fire(ChangedAck)).then(check(s.last== -1 and s.issued==2))
 run wrongOriginalJobHasNoCredit=init.then(fire(WrongJob)).then(check(s.last== -1 and s.issued==0))
 run wrongFamilyHasNoCredit=init.then(fire(WrongFamily)).then(check(s.last== -1 and s.issued==0))
 run foreignReceiverHasNoCredit=init.then(fire(ForeignReceiver)).then(check(s.last== -1 and s.issued==0))
 run malformedCommandHasNoCredit=init.then(fire(Malformed)).then(check(s.last== -1 and s.issued==0))
 run predecessorStorageRemainsBounded=init.then(finish).then(fire(Confirm)).then(fire(Resume)).then(finish).then(fire(Confirm)).then(fire(Resume)).then(fire(OldAck)).then(check(s.job==3 and s.previous==2 and s.last==2 and s.issued==4))
}
