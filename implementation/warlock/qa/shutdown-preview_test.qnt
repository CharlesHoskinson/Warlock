module shutdown_preview_test {
  import shutdown_preview.* from "./shutdown-preview"
  run retirementClosesAfterProofTest = init.then(beginDrain).then(cancel).then(readerComplete)
    .then(release).then(acknowledge(true)).then(close)
    .then(all { assert(s.phase == 2 and safety), s' = s })
  run drainingRejectsDesktopEffectTest = init.then(beginDrain).then(desktopEffect)
    .then(all { assert(s.mutations == 0 and s.rejected == 1 and safety), s' = s })
  run drainingRejectsReacquireTest = init.then(beginDrain).then(readerComplete).then(release)
    .then(acknowledge(true)).then(acquire)
    .then(all { assert(not(s.owned) and s.readers == 0 and s.rejected == 1), s' = s })
  run heldReaderPreventsCloseTest = init.then(beginDrain).then(cancel).then(attemptEarlyClose)
    .then(all { assert(s.phase == 1 and s.owned and s.readers == 1), s' = s })
  run foreignProofCannotEmptyJournalTest = init.then(beginDrain).then(readerComplete).then(release)
    .then(acknowledge(false)).then(attemptEarlyClose)
    .then(all { assert(s.phase == 1 and s.journal), s' = s })
  run duplicateProofCannotCreateOwnershipTest = init.then(beginDrain).then(readerComplete).then(release)
    .then(acknowledge(true)).then(acknowledge(true)).then(close)
    .then(all { assert(s.phase == 2 and safety), s' = s })
}
