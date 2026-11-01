module overview_recovery_context_test {
  import overview_recovery_context.* from "./overview-recovery-context"

  run unknownReopenPreservesOriginAndDoesNotReplayTest =
    init.then(issueRestore).then(exactUnknown).then(reopen).expect(
      unknownWorkspaceWitness and noReplayOnUnknownReopen
        and selectedWorkspaceExists and focusMatchesSelection
    )

  run missingWorkspaceFallsBackToAllTest =
    init.then(issueRestore).then(exactUnknown).then(removeWorkspace).then(reopen).expect(
      vanishedWorkspaceFallbackWitness and noReplayOnUnknownReopen
        and selectedWorkspaceExists and focusMatchesSelection
    )

  run repeatedOpenIsIdempotentTest =
    init.then(issueRestore).then(exactUnknown).then(reopen).then(repeatedOpen).expect(
      unknownWorkspaceWitness and noReplayOnUnknownReopen
        and s.selectedWorkspace == 2 and s.focusWorkspace == 2
        and s.focusCommands == 1 and s.nativeMutations == 1
    )

  run unrelatedUnknownCannotResumeRefusedOriginTest =
    init.then(issueRestore).then(exactRefusal).then(differentUnknown)
      .then(freshReadAfterRefusal).expect(
        not(s.overviewOpen) and s.recovery == Idle and not(s.readOutstanding) and s.currentIntent == 2
          and s.currentStatus == Unknown and s.nativeMutations == 1
      )

  run exactRefusalStillReturnsAfterFreshReadTest =
    init.then(issueRestore).then(exactRefusal).then(freshReadAfterRefusal).expect(
      s.overviewOpen and s.selectedWorkspace == 2 and s.focusWorkspace == 2
        and s.nativeMutations == 1
    )

  run repeatedOpenResetMutantDetectedTest =
    init.then(issueRestore).then(exactUnknown).then(reopen)
      .then(repeatOpenResetMutant).expect(not(unknownWorkspaceWitness))

  run repeatedOpenExtraFocusMutantDetectedTest =
    init.then(issueRestore).then(exactUnknown).then(reopen)
      .then(repeatedOpenExtraFocusMutant).expect(not(s.focusCommands == 1))

  run missingWorkspaceRetainMutantDetectedTest =
    init.then(issueRestore).then(exactUnknown).then(removeWorkspace)
      .then(reopenMissingWorkspaceMutant).expect(not(selectedWorkspaceExists))

  run mismatchedRefusalReturnMutantDetectedTest =
    init.then(issueRestore).then(exactRefusal).then(differentUnknown)
      .then(freshReadAfterRefusalMutant).expect(oldOriginReturnedAfterMismatch)
}
