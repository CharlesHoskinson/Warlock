module release_provenance_test {
  import release_provenance.* from "./release-provenance"
  run completeReviewTest = init.then(review).then(all { assert(s.decision == 1 and safety), s' = s })
  run sourceRefusalRecoveryTest = init.then(mutateSource).then(review).then(all { assert(s.decision == 2), s' = s }).then(restore).then(review).then(all { assert(s.decision == 1 and s.refused), s' = s })
  run noticeRefusalTest = init.then(mutateNotice).then(review).then(all { assert(s.decision == 2), s' = s })
  run unknownDispositionTest = init.then(all { s' = { ...s, disposition: 0 } }).then(review).then(all { assert(s.decision == 2), s' = s })
  run missingApplicabilityTest = init.then(all { s' = { ...s, hasNotice: false, applicability: 0 } }).then(review).then(all { assert(s.decision == 2), s' = s })
  run reviewedNoNoticeTest = init.then(all { s' = { ...s, hasNotice: false, applicability: 1 } }).then(review).then(all { assert(s.decision == 1), s' = s })
  run staleDecisionTest = init.then(review).then(mutateSource).then(all { assert(s.decision == 1 and s.source != s.pinnedSource and safety), s' = s }).then(review).then(all { assert(s.decision == 2), s' = s })
}
