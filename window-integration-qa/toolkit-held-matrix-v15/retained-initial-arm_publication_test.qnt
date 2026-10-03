module arm_publication_test {
 import arm_publication.* from "./arm_publication"
 run originalQuietProposalSpawnImmediateRefusalTest=init.then(fire(Propose)).then(fire(Spawn)).then(fire(Acquire)).then(fire(OriginalImmediate)).then(assert(s.failed and s.published==0))
 run quietProposalSpawnReleasesLockWithoutAuthorityTest=init.then(fire(Propose)).then(fire(Spawn)).then(fire(Acquire)).then(fire(Recheck)).then(assert(not(s.locked) and s.published==0 and not(s.failed)))
 run exactHelperFinishesThenSinglePublicationTest=init.then(fire(Propose)).then(fire(Spawn)).then(fire(Acquire)).then(fire(Recheck)).then(fire(Finish)).then(fire(Propose)).then(fire(Acquire)).then(fire(Recheck)).then(assert(s.published==1 and allProps))
 run configChangeHardRefusalTest=init.then(fire(Propose)).then(fire(ConfigChanged)).then(fire(Acquire)).then(fire(Recheck)).then(assert(s.failed and s.published==0))
 run authorityChangeHardRefusalTest=init.then(fire(Propose)).then(fire(AuthorityChanged)).then(fire(Acquire)).then(fire(Recheck)).then(assert(s.failed and s.published==0))
 run actualNonzeroTerminalNeverRetriesTest=init.then(fire(Spawn)).then(fire(BadTerminal)).then(fire(Finish)).then(fire(Propose)).then(assert(s.failed and s.published==0))
 run malformedHelperNeverPublishesTest=init.then(fire(Malformed)).then(fire(Propose)).then(fire(Acquire)).then(fire(Recheck)).then(assert(s.failed and s.published==0))
 run finishCannotProgressUnderLogLockTest=init.then(fire(Propose)).then(fire(Spawn)).then(fire(Acquire)).then(fire(Finish)).then(assert(s.helpers==1)).then(fire(Recheck)).then(fire(Finish)).then(assert(s.helpers==0 and not(s.locked)))
 run multiplePendingHelpersAllMustCloseTest=init.then(fire(Spawn)).then(fire(Spawn)).then(fire(Finish)).then(fire(Propose)).then(assert(not(s.proposed))).then(fire(Finish)).then(fire(Propose)).then(fire(Acquire)).then(fire(Recheck)).then(assert(s.published==1))
 run originalAbsoluteDeadlineNeverResetsTest=init.then(fire(Spawn)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Finish)).then(fire(Propose)).then(assert(s.failed and s.deadline==8 and s.published==0))
 run repeatedProposeCannotDoublePublishTest=init.then(fire(Propose)).then(fire(Acquire)).then(fire(Recheck)).then(fire(Propose)).then(fire(Acquire)).then(fire(Recheck)).then(assert(s.published==1))
 run noPublicationBeforeLockedCurrentRecheckTest=init.then(fire(Propose)).then(assert(s.published==0)).then(fire(Acquire)).then(assert(s.published==0)).then(fire(Recheck)).then(assert(s.published==1))
}
