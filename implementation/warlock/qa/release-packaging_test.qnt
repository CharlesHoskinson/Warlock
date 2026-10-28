module release_packaging_test {
  import release_packaging.* from "./release-packaging"
  run happyTest = init.then(lockCheck).then(verifyInitial).then(stage).then(review).then(verifyAgain).then(makeManifest).then(makeArchive).then(audit).expect(s.phase == Done and s.audited)
  run oldTest = init.then(ageLock).then(refuse).expect(s.phase == Refused and not(s.output)).then(recover).then(lockCheck).expect(s.phase == Locked)
  run inputTest = init.then(lockCheck).then(mutateInput).then(refuse).then(recover).then(lockCheck).then(verifyInitial).expect(s.phase == Verified)
  run unknownTest = init.then(lockCheck).then(verifyInitial).then(stage).then(introduceUnknown).then(refuse).expect(s.phase == Refused)
  run unmappedTest = init.then(lockCheck).then(verifyInitial).then(stage).then(introduceUnmapped).then(refuse).expect(s.phase == Refused)
  run reviewRaceTest = init.then(lockCheck).then(verifyInitial).then(stage).then(review).then(mutatePayload).then(verifyAgain).then(makeManifest).then(makeArchive).then(refuse).expect(s.phase == Refused)
  run archiveRaceTest = init.then(lockCheck).then(verifyInitial).then(stage).then(review).then(verifyAgain).then(makeManifest).then(makeArchive).then(mutatePayload).then(refuse).expect(s.phase == Refused)
  run lateInputTest = init.then(lockCheck).then(verifyInitial).then(stage).then(review).then(verifyAgain).then(makeManifest).then(makeArchive).then(mutateInput).then(refuse).expect(s.phase == Refused)
  run oldBlockedTest = init.then(ageLock).then(lockCheck.fail())
  run staleBlockedTest = init.then(lockCheck).then(mutateInput).then(verifyInitial.fail())
  run unknownBlockedTest = init.then(lockCheck).then(verifyInitial).then(stage).then(introduceUnknown).then(review.fail())
  run unmappedBlockedTest = init.then(lockCheck).then(verifyInitial).then(stage).then(introduceUnmapped).then(review.fail())
  run reviewedMutationBlockedTest = init.then(lockCheck).then(verifyInitial).then(stage).then(review).then(mutatePayload).then(verifyAgain).then(makeManifest).then(makeArchive).then(audit.fail())
  run metadataRaceTest = init.then(lockCheck).then(verifyInitial).then(stage).then(review).then(verifyAgain).then(makeManifest).then(mutateMetadata).then(makeArchive).then(audit.fail())
}
