module pins_save_lifecycle_test {
  import pins_save_lifecycle.* from "./pins-save-lifecycle"

  run rBeforeWTest = init.then(readStart).then(intent(2))
    .then(readResult(1, true, 1, 1))
    .expect(s.phase == "Saving" and s.write == 2 and s.base == 1 and s.proposal == 2 and s.order == 1 and s.sent == Set(2))
    .then(saved(2, 2, 2)).expect(s.phase == "Idle" and s.order == 2 and s.revision == 2 and s.saved == Set(2))

  run wBeforeRReceiptOrderedTest = init.then(intent(2)).then(readStart)
    .then(saved(1, 2, 2)).then(readResult(2, true, 2, 2))
    .expect(s.phase == "Idle" and s.order == 2 and s.sent == Set(1) and s.revision == 2)

  run unknownOldRThenNewRTest = init.then(readStart).then(intent(2))
    .then(unknown(2)).then(readResult(1, true, 2, 2))
    .expect(s.phase == "Unknown" and s.write == 2 and s.order == 1 and s.recovery == 0)
    .then(readStart).then(unknown(2)).expect(s.recovery == 3 and s.sent == Set(2))
    .then(readResult(3, true, 2, 2)).expect(s.phase == "Idle" and s.order == 2 and s.recovered == Set(2) and s.saved == Set())
    .then(intent(1)).expect(s.phase == "Saving" and s.write == 4 and s.sent == Set(2, 4))

  run wrongDuplicateOutcomeTest = init.then(intent(2)).then(saved(2, 2, 2))
    .then(saved(1, 1, 2)).then(saved(1, 2, 1))
    .expect(s.phase == "Unknown" and s.write == 1 and s.proposal == 2 and s.order == 1 and s.sent == Set(1))
    .then(saved(1, 2, 2)).then(saved(1, 3, 2)).then(unknown(1))
    .expect(s.phase == "Idle" and s.revision == 2 and s.saved == Set(1) and s.sent == Set(1))

  run lowerNoneHigherReadWhileSavingTest = init.then(intent(2)).then(saved(1, 2, 2))
    .then(intent(1)).then(readStart).then(readResult(3, true, 1, 1))
    .then(readStart).then(readResult(4, false, 2, 1))
    .then(readStart).then(readResult(5, true, 2, 1))
    .then(readStart).then(readResult(6, true, 3, 1))
    .expect(s.phase == "Saving" and s.write == 2 and s.base == 2 and s.proposal == 1 and s.revision == 2 and s.order == 2 and s.available and s.sent == Set(1, 2))

  run lateSavedAfterRecoveryDoesNotRewindTest = init.then(intent(2)).then(unknown(1))
    .then(readStart).then(readResult(2, true, 2, 2)).then(intent(1))
    .then(saved(1, 3, 2)).expect(s.phase == "Saving" and s.write == 3 and s.base == 2 and s.proposal == 1 and s.revision == 2 and s.order == 2 and s.sent == Set(1, 3))

  run refusalAndInvalidBoundaryTest = init.then(intent(2)).then(invalidInput)
    .expect(s.phase == "Saving" and s.write == 1 and s.sent == Set(1))
    .then(refused(1)).expect(s.phase == "Idle" and s.order == 1 and s.sent == Set(1))
    .then(intent(2)).expect(s.write == 2 and s.sent == Set(1, 2))

  run staleRecoveryRequiresNewReadTest = init.then(intent(2)).then(saved(1, 2, 2))
    .then(intent(1)).then(unknown(2)).then(readStart).then(readResult(3, true, 1, 1))
    .expect(s.phase == "Unknown" and s.recovery == 0 and s.write == 2)
    .then(readStart).then(readResult(4, true, 2, 2)).expect(s.phase == "Idle" and s.order == 2 and s.saved == Set(1) and s.recovered == Set(2))

  run unavailableRecoveryRequiresFreshObservationTest = init.then(intent(2)).then(unknown(1))
    .then(readStart).then(readResult(2, false, 1, 1))
    .expect(s.phase == "Idle" and not(s.available) and s.sent == Set(1))
    .then(readStart).then(readResult(3, true, 1, 1)).then(intent(2))
    .expect(s.phase == "Saving" and s.write == 4 and s.sent == Set(1, 4))

  run readIssuedWhileSavingNotRecoveryTest = init.then(intent(2)).then(readStart)
    .then(unknown(1)).then(readResult(2, true, 2, 2))
    .expect(s.phase == "Unknown" and s.write == 1 and s.order == 1 and s.recovery == 0)
    .then(readStart).then(readResult(3, true, 2, 2)).expect(s.phase == "Idle" and s.recovered == Set(1))

  run invalidSavedPreservesRegisteredRecoveryTest = init.then(intent(2))
    .then(saved(1, 1, 2)).expect(s.phase == "Unknown" and s.write == 1 and s.recovery == 0 and s.order == 1)
    .then(readStart).then(saved(1, 2, 1)).then(nullSavedProof(1)).then(unknown(1))
    .expect(s.phase == "Unknown" and s.recovery == 2 and s.write == 1 and s.sent == Set(1) and s.saved == Set())
    .then(readResult(2, true, 2, 2)).expect(s.phase == "Idle" and s.recovered == Set(1) and s.saved == Set())

  run nullableProofForeignRequestIsInertTest = init.then(intent(2)).then(nullSavedProof(2))
    .expect(s.phase == "Saving" and s.write == 1 and s.proposal == 2 and s.sent == Set(1))
    .then(nullSavedProof(1)).expect(s.phase == "Unknown" and s.write == 1 and s.order == 1 and s.saved == Set())
}
