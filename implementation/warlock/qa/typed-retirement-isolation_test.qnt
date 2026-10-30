module TypedRetirementIsolation_test {
  import TypedRetirementIsolation.* from "./typed-retirement-isolation"

  run brokenUnlinkBeforeSaveTest = init.then(observeProof(2)).then(observeJoin(2)).then(brokenPrepare(2)).then(brokenFinish(2)).expect(not(typedCustody) and s.entries.get(2).live and not(s.decoderHealthy) and not(s.entries.get(2).cert))
  run typedLegacyPrepareBlockedTest = init.then(observeProof(2)).then(observeJoin(2)).then(legacyPrepare(2).fail())
  run corruptRestartNoUnlinkTest = init.then(injectCollision(2)).then(restart).expect(not(s.decoderHealthy) and s.entries.get(2).file and s.entries.get(2).live).then(legacyFinish(2).fail())
  run directFinishBypassBlockedTest = init.then(injectCollision(2)).then(legacyFinish(2).fail())
  run genuineLegacyRetirementTest = init.then(observeProof(1)).then(observeJoin(1)).then(legacyPrepare(1)).then(legacyFinish(1)).then(legacyAck(1)).expect(s.entries.get(1).phase == Released and s.entries.get(1).ack and s.entries.get(2).file and s.entries.get(3).file and ackAfterRetirement)
  run corruptPeerBlocksLegacyFinishTest = init.then(observeProof(1)).then(observeJoin(1)).then(legacyPrepare(1)).then(injectCollision(2)).then(legacyFinish(1).fail())
  run wrongKeyJoinBlockedTest = init.then(observeProof(1)).then(observeJoin(2).fail())
  run wrongCertificateBlockedTest = init.then(exactTerminal(2,3).fail())
  run typedExactRetirementTest = init.then(exactTerminal(2,2)).then(typedFinish(2)).then(typedAck(2)).expect(s.entries.get(2).stage == AdmissionRetired and s.entries.get(2).ack and s.entries.get(1).file and s.entries.get(3).file and ackAfterRetirement)
  run noTypedAckBeforeCertificateTest = init.then(typedAck(2).fail())
  run noLegacyAckBeforeReleaseTest = init.then(observeProof(1)).then(observeJoin(1)).then(legacyAck(1).fail())
  run typedNotProjectedTest = init.then(observeProof(2)).then(observeJoin(2)).expect(legacyRecords(s) == Set(1) and s.entries.get(2).file and s.entries.get(2).live)
  run differentKeyIsolationTest = init.then(exactTerminal(3,3)).then(typedFinish(3)).expect(s.entries.get(2).file and s.entries.get(2).live and not(s.entries.get(2).cert) and s.entries.get(1).file and noReplay)
}
