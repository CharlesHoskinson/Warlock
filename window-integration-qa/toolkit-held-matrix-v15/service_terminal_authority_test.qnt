module service_terminal_authority_test {
 import service_terminal_authority.* from "./service_terminal_authority"
 run originalAttemptedStopIsInsufficientTest=init.then(fire(FeatureEnd)).then(fire(CapturedService)).then(fire(StopAttempt)).then(fire(OriginalAfterAttempt)).then(all { s'=s, assert(s.quiesced and not(allProps)) })
 run normalExactClosedServiceCanQuiesceTest=init.then(fire(FeatureEnd)).then(fire(CapturedService)).then(fire(StopAttempt)).then(fire(NormalExit)).then(fire(ExactGone)).then(fire(ResourcesClosed)).then(fire(Quiesce)).then(all { s'=s, assert(s.quiesced and allProps) })
 run capturedLiveServiceCannotQuiesceTest=init.then(fire(FeatureEnd)).then(fire(CapturedService)).then(fire(StopAttempt)).then(fire(NormalExit)).then(fire(ResourcesClosed)).then(fire(Quiesce)).then(all { s'=s, assert(s.failed and not(s.quiesced)) })
 run exactGoneWithoutNormalExitDoesNotQuiesceTest=init.then(fire(FeatureEnd)).then(fire(CapturedService)).then(fire(ExactGone)).then(fire(ResourcesClosed)).then(fire(Quiesce)).then(all { s'=s, assert(s.failed and not(s.quiesced)) })
 run rendererResourceUnknownCannotQuiesceTest=init.then(fire(FeatureEnd)).then(fire(CapturedService)).then(fire(NormalExit)).then(fire(ExactGone)).then(fire(Quiesce)).then(all { s'=s, assert(s.failed and not(s.quiesced)) })
 run sourceRootMismatchAndUnknownExitRefuseTest=init.then(fire(FeatureEnd)).then(fire(CapturedService)).then(fire(WrongRoot)).then(fire(Quiesce)).then(all { s'=s, assert(s.failed and not(s.quiesced)) })
 run verifiedNoServiceMayQuiesceTest=init.then(fire(FeatureEnd)).then(fire(NoService)).then(fire(Quiesce)).then(all { s'=s, assert(s.quiesced and allProps) })
 run notCreatedIsInsufficientWithoutObservedAbsenceTest=init.then(fire(FeatureEnd)).then(fire(Quiesce)).then(all { s'=s, assert(s.failed and not(s.quiesced)) })
 run laterUnknownRevokesAuthorityPreservesPhysicalQuiesceTest=init.then(fire(FeatureEnd)).then(fire(CapturedService)).then(fire(NormalExit)).then(fire(ExactGone)).then(fire(ResourcesClosed)).then(fire(Quiesce)).then(fire(UnknownExit)).then(all { s'=s, assert(s.failed and s.quiesced and not(s.ackAuthority) and allProps) })
}
