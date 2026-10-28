module release_transport_test {
  import release_transport.* from "./release-transport"
  run cleanTest = init.then(audit).expect(s.decision == 1)
  run aliasTest = init.then(alias).then(audit).expect(s.decision == 2).then(refreshAlias).then(audit).expect(s.decision == 1 and s.snapLink == 2)
  run retargetTest = init.then(retarget).then(audit).expect(s.decision == 2).then(restore).then(audit).expect(s.decision == 1)
  run escapeTest = init.then(escape).then(audit).expect(s.decision == 2).then(restore).then(audit).expect(s.decision == 1)
  run duplicateTest = init.then(duplicate).then(audit).expect(s.decision == 2).then(restore).then(audit).expect(s.decision == 1)
  run missingTest = init.then(missing).then(audit).expect(s.decision == 2).then(restore).then(audit).expect(s.decision == 1)
  run unexpectedTest = init.then(unexpected).then(audit).expect(s.decision == 2).then(restore).then(audit).expect(s.decision == 1)
  run typeTest = init.then(mismatchType).then(audit).expect(s.decision == 2).then(restore).then(audit).expect(s.decision == 1)
  run contentTest = init.then(mismatchContent).then(audit).expect(s.decision == 2).then(restore).then(audit).expect(s.decision == 1)
  run mutationAfterAuditTest = init.then(audit).then(escape).expect(s.decision == 1 and s.snapEscaped == false and s.escaped)
}
