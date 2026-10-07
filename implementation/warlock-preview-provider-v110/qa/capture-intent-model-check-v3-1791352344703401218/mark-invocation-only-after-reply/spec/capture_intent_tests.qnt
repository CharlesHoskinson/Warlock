module capture_intent_tests {
 import capture_intent.* from "./capture_intent"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run originalIntentSurvivesCaptureError=init.then(fire(Acquire)).then(check(s.intent and s.last==3 and s.captures==1))
 run cancelledUnknownKeepsExactOriginalWire=init.then(fire(Acquire)).then(fire(Cancel)).then(check(s.wireUnchanged and s.intent))
 run rawRetryCannotCaptureAgain=init.then(fire(Acquire)).then(fire(RawRetry)).then(check(s.captures==1 and s.last== -1))
 run cancellationBeforeCaptureHasFinalProof=init.then(fire(Cancel)).then(fire(Acquire)).then(check(s.terminal and s.charge==0 and s.captures==0))
 run cancellationAfterUnknownRetainsCharge=init.then(fire(Acquire)).then(fire(Cancel)).then(check(s.charge==4096 and not(s.terminal)))
 run controlConfirmationIsNoPhysicalProof=init.then(fire(Acquire)).then(fire(Cancel)).then(fire(Confirm)).then(check(s.confirmed==2 and s.charge==4096))
 run originalTicketRetryDoesNotReplayCapture=init.then(fire(Acquire)).then(fire(Acquire)).then(check(s.last==2 and s.issued==1 and s.captures==1))
 run oldTicketAfterCancelCannotReinvoke=init.then(fire(Acquire)).then(fire(Cancel)).then(fire(Acquire)).then(check(s.last==0 and s.captures==1))
 run wrongOriginalJobCannotIssueTicket=init.then(fire(BadJob)).then(check(s.last== -1 and s.issued==0 and s.captures==0))
 run foreignReceiverCannotAcquire=init.then(fire(ForeignReceiver)).then(check(s.last== -1 and s.issued==0))
 run pollingCannotInventUnknownCleanup=init.then(fire(Acquire)).then(fire(Cancel)).then(fire(Poll)).then(check(s.charge==4096 and not(s.terminal)))
 run bindingCloseRetainsUnknownAttempt=init.then(fire(Acquire)).then(fire(Cancel)).then(fire(Confirm)).then(fire(Close)).then(check(not(s.closed) and s.intent))
 run originalDeadlineNeverExtended=init.then(fire(Acquire)).then(fire(RawRetry)).then(fire(Poll)).then(check(s.deadlineUnchanged))
 run confirmedPrefixNeverResetsOriginalCapture=init.then(fire(Acquire)).then(fire(Confirm)).then(fire(Acquire)).then(check(s.confirmed==1 and s.captures==1 and s.issued==1))
}
