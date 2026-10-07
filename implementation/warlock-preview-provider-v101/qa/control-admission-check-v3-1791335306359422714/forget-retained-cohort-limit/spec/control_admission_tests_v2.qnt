module control_admission_tests {
 import control_admission.* from "./control_admission_v2"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run receiverEnrollmentPrecedesJob=init.then(fire(EmptyRead)).then(check(s.epoch==1 and s.members==0 and s.records==0))
 run originalEpochSurvivesAdmission=init.then(fire(Admit)).then(check(s.epoch==1 and s.members==1 and s.jobs==1 and s.reserved==8))
 run capacityRefusesBeforeNativeIntent=init.then(fire(Low)).then(fire(Admit)).then(check(s.last==0 and s.jobs==0 and s.intents==0 and s.slots==0 and s.reserved==1))
 run foreignReceiverCannotAdmit=init.then(fire(ForeignReceiver)).then(check(s.last== -1 and s.jobs==0 and s.groups==1))
 run foreignEpochCannotAdmit=init.then(fire(ForeignEpoch)).then(check(s.last== -1 and s.jobs==0 and s.groups==1))
 run foreignBindingCannotAdmit=init.then(fire(ForeignBinding)).then(check(s.last== -1 and s.jobs==0 and s.groups==1))
 run exceptionKeepsUnknownCleanup=init.then(fire(ThrowAfterIssue)).then(check(s.last== -1 and s.pending and s.jobs==1 and s.records==1 and s.reserved==8))
 run missingReturnedJobCannotRollback=init.then(fire(HideIssuedJob)).then(check(s.last== -1 and s.pending and s.jobs==1 and s.records==1 and s.reserved==8))
 run unknownRetryCannotIssueAgain=init.then(fire(ThrowAfterIssue)).then(fire(Retry)).then(check(s.last==0 and s.records==1 and s.reserved==8 and s.groups==3))
 run closedReceiverPreservesObligations=init.then(fire(Admit)).then(fire(CloseView)).then(fire(Admit)).then(check(s.last== -1 and s.jobs==1 and s.reserved==8 and s.epoch==0))
 run repeatedEnrollmentCannotReset=init.then(fire(Admit)).then(fire(RepeatEnrollment)).then(check(s.last==0 and s.epoch==1 and s.members==1 and s.jobs==1))
 run retainedCohortBoundPrecedesNinthJob=init.then(fire(Admit)).then(fire(Admit)).then(fire(Admit)).then(fire(Admit)).then(fire(Admit)).then(fire(Admit)).then(fire(Admit)).then(fire(Admit)).then(fire(Admit)).then(check(s.last==0 and s.jobs==8 and s.intents==8 and s.slots==8 and s.reserved==57))
 run replacementEpochCannotReplayOriginal=init.then(fire(Admit)).then(fire(CloseView)).then(fire(ReplaceView)).then(fire(Admit)).then(check(s.last== -1 and s.epoch==2 and s.jobs==1 and s.reserved==8 and s.members==0))
 run foreignBrokerCannotIssue=init.then(fire(ForeignBroker)).then(check(s.last== -1 and s.jobs==0 and s.groups==1))
 run singleManagerOwnsOriginalQuota=init.then(fire(SecondManager)).then(check(s.last== -1 and s.reserved==1 and s.groups==1 and s.jobs==0))
}
