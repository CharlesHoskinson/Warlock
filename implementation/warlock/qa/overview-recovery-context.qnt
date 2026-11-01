module overview_recovery_context {
  // Bounded correspondence model for the ELM-UI-007 recovery context path.
  // It models reducer-level origin/current-intent equality, workspace presence,
  // focus selection, repeated open and mutation count. It excludes compositor,
  // pointer/keyboard dispatch and assistive technology delivery.
  type Status = Ready | Pending | Refused | Unknown | Committed | Cancelled
  type Recovery = Idle | Issued | Returning

  type State = {
    currentIntent: int,
    currentStatus: Status,
    readOutstanding: bool,
    originIntent: int,
    originWorkspace: int,
    recovery: Recovery,
    workspacePresent: bool,
    overviewOpen: bool,
    selectedWorkspace: int,
    focusWorkspace: int,
    focusCommands: int,
    nativeMutations: int,
  }

  var s: State

  action init = s' = {
    currentIntent: 0,
    currentStatus: Ready,
    readOutstanding: false,
    originIntent: 0,
    originWorkspace: 0,
    recovery: Idle,
    workspacePresent: true,
    overviewOpen: false,
    selectedWorkspace: 0,
    focusWorkspace: 0,
    focusCommands: 0,
    nativeMutations: 0,
  }

  // A restore is issued from workspace 2; this accounts for the one legitimate
  // mutation in a trace. Read/reopen actions below must never increment it.
  action issueRestore = all {
    s.nativeMutations == 0,
    s' = {
    ...s,
    currentIntent: 1,
    currentStatus: Pending,
    originIntent: 1,
    originWorkspace: 2,
    recovery: Issued,
    overviewOpen: false,
    selectedWorkspace: 0,
    nativeMutations: s.nativeMutations + 1,
    },
  }

  action exactUnknown = all {
    s.recovery == Issued,
    s.currentIntent == s.originIntent,
    s' = { ...s, currentStatus: Unknown },
  }

  action exactRefusal = all {
    s.recovery == Issued,
    s.currentIntent == s.originIntent,
    s' = { ...s, currentStatus: Refused, recovery: Returning, readOutstanding: true },
  }

  // A different admitted reservation becomes the current transaction while the
  // original Refused route is waiting on its read. It is not a retry.
  action differentUnknown = all {
    s.recovery == Returning,
    s' = { ...s, currentIntent: 2, currentStatus: Unknown, recovery: Idle },
  }

  action removeWorkspace = s' = {
    ...s,
    workspacePresent: false,
    selectedWorkspace: 0,
    focusWorkspace: if (s.selectedWorkspace == 2) 0 else s.focusWorkspace,
    focusCommands: s.focusCommands + if (s.selectedWorkspace == 2) 1 else 0,
  }

  action reopen = all {
    s.recovery == Issued,
    s.currentIntent == s.originIntent,
    s.currentStatus == Unknown,
    not(s.overviewOpen),
    s' = {
      ...s,
      recovery: Idle,
      overviewOpen: true,
      selectedWorkspace: if (s.workspacePresent) s.originWorkspace else 0,
      focusWorkspace: if (s.workspacePresent) s.originWorkspace else 0,
      focusCommands: s.focusCommands + 1,
    },
  }

  // Explicit mutants provide sensitivity checks for the three reducer rules.
  action repeatOpenResetMutant = all {
    s.overviewOpen,
    s' = { ...s, selectedWorkspace: 0, focusWorkspace: 0,
      focusCommands: s.focusCommands + 1 },
  }

  action reopenMissingWorkspaceMutant = all {
    s.recovery == Issued,
    s.currentIntent == s.originIntent,
    s.currentStatus == Unknown,
    not(s.workspacePresent),
    not(s.overviewOpen),
    s' = { ...s, recovery: Idle, overviewOpen: true,
      selectedWorkspace: s.originWorkspace, focusWorkspace: 0,
      focusCommands: s.focusCommands + 1 },
  }

  action repeatedOpen = all {
    s.overviewOpen,
    s' = s,
  }

  // Sensitivity-only mutant: repeated activation emits another Focus command
  // while leaving the selected control unchanged. The production replay checks
  // full (model, effects) equality; this catches the model's narrower observer.
  action repeatedOpenExtraFocusMutant = all {
    s.overviewOpen,
    s' = { ...s, focusCommands: s.focusCommands + 1 },
  }

  // Return after Refused only while the exact refusal still owns the current
  // transaction. A different current intent cancels the old return context.
  action freshReadAfterRefusal = all {
    s.readOutstanding,
    s' = if (s.recovery == Returning and s.currentIntent == s.originIntent and s.currentStatus == Refused)
      { ...s, recovery: Idle, readOutstanding: false, overviewOpen: true,
        selectedWorkspace: if (s.workspacePresent) s.originWorkspace else 0,
        focusWorkspace: if (s.workspacePresent) s.originWorkspace else 0,
        focusCommands: s.focusCommands + 1 }
      else { ...s, recovery: Idle, readOutstanding: false },
  }

  action freshReadAfterRefusalMutant = all {
    s.readOutstanding,
    s' = { ...s, recovery: Idle, readOutstanding: false,
      overviewOpen: true, selectedWorkspace: s.originWorkspace,
      focusWorkspace: s.originWorkspace, focusCommands: s.focusCommands + 1 },
  }

  action step = any {
    issueRestore,
    exactUnknown,
    exactRefusal,
    differentUnknown,
    removeWorkspace,
    reopen,
    repeatedOpen,
    freshReadAfterRefusal,
  }

  val noReplayOnUnknownReopen =
    (s.overviewOpen and s.currentStatus == Unknown) implies s.nativeMutations == 1

  val selectedWorkspaceExists =
    s.selectedWorkspace == 0 or s.workspacePresent

  val focusMatchesSelection =
    not(s.overviewOpen) or s.focusWorkspace == s.selectedWorkspace

  val returnRequiresExactRefusal =
    s.recovery != Returning or (s.currentStatus == Refused and s.currentIntent == s.originIntent)

  val unknownWorkspaceWitness =
    s.overviewOpen and s.currentStatus == Unknown and s.selectedWorkspace == 2
      and s.focusWorkspace == 2

  val vanishedWorkspaceFallbackWitness =
    s.overviewOpen and s.currentStatus == Unknown and not(s.workspacePresent)
      and s.selectedWorkspace == 0 and s.focusWorkspace == 0

  val oldOriginReturnedAfterMismatch =
    s.overviewOpen and s.currentIntent != s.originIntent
}
