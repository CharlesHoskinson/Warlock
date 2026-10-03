module family_scope_test {
 import family_scope.* from "./family_scope"
 run failedEnrichmentCannotAcceptSingletonTest=init.then(fire(Reserve)).then(fire(RelationFailure)).then(fire(Commit(2))).then(all{assert(s.stale and s.scope==Set(0,1) and allProps),fire(FailValidation)})
 run retryFreshEdgesRestoresEntireScopeTest=init.then(fire(Reserve)).then(fire(RelationFailure)).then(fire(FreshFamily({identity:1,epoch:2}))).then(fire(Commit(2))).then(all{assert(s.primaryMin and s.peerMin and allProps),fire(Reload)})
 run genuineFreshDetachmentDoesNotUseCachedPeerTest=init.then(fire(Reserve)).then(fire(GenuineDetached({identity:1,epoch:2}))).then(fire(Commit(2))).then(all{assert(s.scope==Set(0) and allProps),fire(Reload)})
 run rejectedNewIntentPreservesPreviouslyAcceptedIntentTest=init.then(fire(Reserve)).then(fire(RelationFailure)).then(fire(FailValidation)).then(all{assert(s.rejected and not(s.primaryMin) and not(s.intent) and allProps),fire(Commit(1))})
 run reuseCannotReceiveOldFamilyCommitTest=init.then(fire(Reserve)).then(fire(CloseReuse)).then(fire(Commit(1))).then(all{assert(s.stale and not(s.primaryMin) and allProps),fire(Reload)})
 run reuseRejectedReservationHasNoPriorIntentAuthorityTest=init.then(fire(CloseReuse)).then(fire(Reserve)).then(fire(RelationFailure)).then(fire(FailValidation)).then(all{assert(not(s.primaryMin) and not(s.queryOk) and allProps),fire(Commit(3))})
 run staleDetachmentCannotTruncateReservedScopeTest=init.then(fire(Reserve)).then(fire(GenuineDetached({identity:1,epoch:1}))).then(all{assert(s.stale and s.reserved and s.scope==Set(0,1) and allProps),fire(FreshFamily({identity:1,epoch:2}))})
 run reusedIdentityRejectsOldFreshFamilyObservationTest=init.then(fire(CloseReuse)).then(fire(Reserve)).then(fire(FreshFamily({identity:1,epoch:3}))).then(all{assert(s.stale and s.acceptedEpoch==0 and allProps),fire(RelationFailure)})
}
