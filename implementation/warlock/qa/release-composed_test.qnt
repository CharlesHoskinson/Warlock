module release_composed_test {
  import release_composed.* from "./release-composed"
  run facts = init.then(cover).expect(s.coverage).then(reviewEvidence).expect(s.evidence)
    .then(lockInputs).expect(s.locked).then(establishIdentity).expect(s.identity)
  run happy = init.then(cover).then(reviewEvidence).then(lockInputs).then(establishIdentity)
    .then(review).expect(s.phase == Reviewed).then(package).expect(s.phase == Packaged)
    .then(audit).expect(s.phase == Audited).then(report).expect(s.outcome and s.auditRev == s.revision)
  run missingCoverage = init.then(reviewEvidence).then(review.fail())
  run missingEvidence = init.then(cover).then(review.fail())
  run missingLock = init.then(cover).then(reviewEvidence).then(review).then(package.fail())
  run missingIdentity = init.then(cover).then(reviewEvidence).then(lockInputs).then(review).then(package).then(audit.fail())
  run changedAfterReview = init.then(cover).then(reviewEvidence).then(lockInputs).then(review)
    .then(mutate).expect(s.revision == 1 and not(s.coverage)).then(package.fail())
  run changedAfterPackage = init.then(cover).then(reviewEvidence).then(lockInputs).then(establishIdentity)
    .then(review).then(package).then(mutate).then(audit.fail())
  run changedAfterAudit = init.then(cover).then(reviewEvidence).then(lockInputs).then(establishIdentity)
    .then(review).then(package).then(audit).then(mutate).then(report)
    .expect(s.outcome and s.auditRev != s.revision and not(s.identity))
}
