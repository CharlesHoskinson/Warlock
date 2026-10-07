module combined_recovery_tests {
 import combined_recovery.* from "./combined_recovery"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 action lost={fire(ClosePreview).then(fire(AdmitWindow)).then(fire(NativeWindowCommit)).then(fire(LoseReceipt)).then(fire(RendererFailure))}
 action retired=lost.then(fire(CloseReader)).then(fire(NativeStrictClose)).then(fire(Recovery))
 action restarted=retired.then(fire(Restart)).then(fire(Scene))
 action released=restarted.then(fire(WindowBindingRetired)).then(fire(ReleaseReservation))
 run rendererDeathDoesNotCloseReader=init.then(lost).then(fire(NativeStrictClose)).then(fire(Recovery)).then(fire(Restart)).then(check(s.reader and s.oldUnknown and s.host==1 and not(s.recovery)))
 run readerCloseDoesNotInferStrictNativeProof=init.then(lost).then(fire(CloseReader)).then(fire(Recovery)).then(check(not(s.reader or s.closed or s.recovery)))
 run knownPreviewCanRetireWithWindowUnknown=init.then(retired).then(check(s.closed and s.recovery and s.oldUnknown and s.historyUnknown))
 run previewUnknownStillBlocksRestart=init.then(lost).then(fire(PreviewUnknown)).then(fire(CloseReader)).then(fire(NativeStrictClose)).then(fire(Recovery)).then(fire(Restart)).then(check(s.previewUnknown and s.oldUnknown and s.host==1 and not(s.closed or s.recovery)))
 run unreadAdmissionStillRecoversAsUnknown=init.then(fire(ClosePreview)).then(fire(AdmitWindow)).then(fire(LoseReceipt)).then(fire(RendererFailure)).then(fire(CloseReader)).then(fire(NativeStrictClose)).then(fire(Recovery)).then(fire(Restart)).then(check(s.host==2 and s.oldUnknown and not(s.nativeWindowCommitted)))
 run nativeRetirementDoesNotSettleWindowOutcome=init.then(released).then(check(s.reservationReleased and s.oldUnknown and s.historyUnknown))
 run newCommandRequiresCurrentSceneAndReservationProof=init.then(retired).then(fire(Restart)).then(fire(ExplicitNewCommand)).then(fire(Scene)).then(fire(ExplicitNewCommand)).then(check(not(s.newCommand) and s.request==1 and s.generation==1))
 run explicitAdvancedCommandPreservesHistoricalUnknown=init.then(released).then(fire(ExplicitNewCommand)).then(check(s.newCommand and s.request==2 and s.generation==2 and s.historyUnknown))
 run automaticReplayIsNotAnAllowedTransition=init.then(restarted).then(fire(RetryOldWindow)).then(check(s.replays==0 and s.request==1 and s.oldUnknown))
 run freshPreviewUsesFreshOwnerSameLifetime=init.then(released).then(fire(ExplicitNewCommand)).then(fire(FreshCapture)).then(fire(CloseFreshReader)).then(fire(FreshStrictClose)).then(check(s.freshClosed and s.freshOwner==2 and s.lifetime==1 and s.historyUnknown))
 run earlyRestartMutationRejected=init.then(lost).then(check(not(safe(unsafeRestart(s)))))
 run erasedUnknownMutationRejected=init.then(released).then(check(not(safe(unsafeEraseHistory(s)))))
 run automaticReplayMutationRejected=init.then(restarted).then(check(not(safe(unsafeReplay(s)))))
 run reusedNativeOwnerMutationRejected=init.then(restarted).then(check(not(safe(unsafeReuseOwner(s)))))
}
