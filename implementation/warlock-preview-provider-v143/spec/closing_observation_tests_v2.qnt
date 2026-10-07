module closing_observation_tests_v2 {
 import closing_observation_v2.* from "./closing_observation"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 action drained=release.then(physicalDone).then(independentDrain)
 run rapidLegacyCounterexample=init.then(close).then(reopen).then(drained).then(pulse(false)).then(pulse(false)).then(check(s.dutiesSettled and s.closing and not(s.detached) and not(s.observed) and s.pollStamp==1))
 run stickyPendingObservation=init.then(close).then(reopen).then(drained).then(pulse(true)).then(check(s.detached and s.observed and s.pollStamp==0))
 run originalClosedPopupObservation=init.then(close).then(drained).then(pulse(false)).then(check(s.detached and s.pollStamp==0))
 run heldReaderStillBlocks=init.then(close).then(reopen).then(physicalDone).then(independentDrain).then(pulse(true)).then(check(s.reader and s.jobs and not(s.dutiesSettled) and not(s.detached)))
 run readerCloseIsNotNativeSettlement=init.then(close).then(reopen).then(release).then(pulse(true)).then(check(not(s.reader) and s.jobs and not(s.dutiesSettled) and not(s.detached)))
 run emptyJobListIsNotRetirement=init.then(close).then(reopen).then(release).then(physicalDone).then(pulse(true)).then(check(not(s.jobs) and not(s.dutiesSettled) and not(s.detached)))
 run unknownKeepsOriginalDuty=init.then(close).then(reopen).then(fault).then(drained).then(pulse(true)).then(check(s.unknown and not(s.dutiesSettled) and not(s.detached)))
 run laterIntentCannotRestoreClosingStamps=init.then(close).then(pulse(true)).then(reopen).then(pulse(true)).then(check(s.closing and s.pollStamp==0 and s.observed))
}
