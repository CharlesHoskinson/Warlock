module local_field_publication {
  // Conditional candidate only: corresponds to sol-popup-reverse-edit-preedit-2200
  // SHA a127e308 (Popup preimage ebb12fa8). The separate source-current draft
  // retains the original loss witness; this candidate has not been executed.
  // UI-004 keyboard pin setup: Popup's owned field callbacks can arrive from
  // the preceding DOM paint in the same lease. External actions stay strict.
  // Abstract text as bounded integers; Elm event order is FIFO. Native paint,
  // input provenance, IME engines, AT and effect receipt acceptance are outside.
  // Step samples control classes 0, 5, 10; directed named traces cover all 11.
  // Same-field frames advance one counter step, a finite underapproximation;
  // field recovery permits bounded jumps. Counters are not full UInt64.
  var s: { pub: int, lease: int, domPub: int, domLease: int,
    draft: int, shown: int, acceptedPub: int, acceptedText: int, visible: bool, fieldActive: bool, pending: bool, composing: bool, beforePending: bool, baseline: int, lastPub: int, lastLease: int, effects: int, dependentEffects: int, safeEffects: int, badDependent: bool, badSafe: bool }
  action init = s' = {pub:1,lease:1,domPub:1,domLease:1,
    draft:0,shown:0,acceptedPub:1,acceptedText:0,visible:true,fieldActive:true,pending:false,composing:false,beforePending:false,baseline:0,lastPub:-1,lastLease:-1,effects:0,dependentEffects:0,safeEffects:0,badDependent:false,badSafe:false}
  // pub is the currently accepted same-lease publication, not a produced
  // frame waiting for validation. Publish accepts the previous authoritative
  // query unchanged; matching and unmatched frames are atomic actions below.
  action publish = all { s.visible, s.fieldActive, s.pub < 20,
    s' = {...s,pub:s.pub+1,acceptedPub:s.pub+1,
      pending:if (s.composing) s.pending else (s.pending and s.draft!=s.acceptedText),
      lastPub:if (not(s.composing) and s.pending and s.draft!=s.acceptedText) s.pub+1 else s.lastPub,
      lastLease:if (not(s.composing) and s.pending and s.draft!=s.acceptedText) s.lease else s.lastLease} }
  action paint = if (s.visible and s.fieldActive) s' = {...s,domPub:s.pub,domLease:s.lease,shown:s.draft} else s' = s
  // lastPub/lastLease approximate Popup.lastQuery's deduplication key;
  // they do not attest successful HTTP, backend application or mutation.
  def unsettledHere: bool = s.pending and s.lastPub>=0 and
    (s.lastLease!=s.lease or s.pub<=s.lastPub)
  action localEdit(value:int,pub:int,lease:int): bool =
    if (s.visible and s.fieldActive and lease==s.lease and pub>0 and pub<=s.pub and value>=0 and value<=4)
    s' = {...s,draft:value,
      pending:(s.composing or unsettledHere or value!=s.acceptedText),
      lastPub:if (s.composing) s.lastPub else s.pub,
      lastLease:if (s.composing) s.lastLease else s.lease}
    else s' = s
  action externalEdit(value:int,pub:int,lease:int): bool =
    if (s.visible and s.fieldActive and lease==s.lease and pub==s.pub and value>=0 and value<=4)
    s' = {...s,draft:value,
      pending:(s.composing or unsettledHere or value!=s.acceptedText),
      lastPub:if (s.composing) s.lastPub else s.pub,
      lastLease:if (s.composing) s.lastLease else s.lease}
    else s' = s
  // IDs 0..10 abstract enabled SurfaceSnapshot.pendingQueryBlocked families:
  // entry, pin, unpin, pin-left, pin-right, jump:open, previous/next page,
  // files:home, files:collection and files:open-path, respectively.
  // Surface mode and enabled status are fixture assumptions, not native grants.
  action activateClass(kind:int,pub:int,lease:int): bool =
    if (kind>=0 and kind<=10 and s.visible and s.fieldActive and lease==s.lease and pub==s.pub and not(s.pending) and not(s.composing)) s' = {...s,effects:s.effects+1,dependentEffects:s.dependentEffects+1,
      badDependent:(s.badDependent or s.pending or s.composing)}
    else s' = s
  action activate(pub:int,lease:int): bool = activateClass(0,pub,lease)
  action reopen = all { s.lease<10, s.pub<20,
    s'={...s,lease:s.lease+1,pub:s.pub+1,draft:0,acceptedPub:s.pub+1,acceptedText:0,visible:true,fieldActive:true,pending:false,composing:false,beforePending:false,baseline:0,lastPub:-1,lastLease:-1} }
  // effects counts only abstract dependent or safe activations, not query
  // Dispatches, native effects or receipts. Same mode and enabled field are
  // assumptions for publication transitions. Preedit cancellation and a
  // conditional committed value are modeled; physical IME is outside.
  // Acknowledge here means an accepted same-field publication whose query
  // matches the pending draft, not HTTP 204 or an operation receipt. A stale
  // publication or active preedit cannot clear it. The UI's refresh/close are
  // modeled as safeAction, distinct from query-dependent activation.
  action matchingPublication(value:int,pub:int,lease:int): bool =
    if (s.visible and s.fieldActive and s.pub<20 and pub==s.pub+1 and pub>s.acceptedPub and lease==s.lease and not(s.composing) and value==s.draft)
      s' = {...s,pub:pub,acceptedPub:pub,acceptedText:value,pending:false}
    else s' = s
  // Accepted newer unmatched frames update authoritative query without
  // clearing local input; while composing, even an equal query stays pending.
  // Same-field/lease validity and bounded input are explicit assumptions.
  action acceptOtherFrame(value:int,pub:int,lease:int): bool =
    if (s.visible and s.fieldActive and s.pub<20 and pub==s.pub+1 and pub>s.acceptedPub and lease==s.lease and
        value>=0 and value<=4 and (s.composing or value!=s.draft))
      s' = {...s,pub:pub,acceptedPub:pub,acceptedText:value,
        draft:if (not(s.pending) and not(s.composing)) value else s.draft,
        lastPub:if (not(s.composing) and s.pending and value!=s.draft) pub else s.lastPub,
        lastLease:if (not(s.composing) and s.pending and value!=s.draft) lease else s.lastLease}
    else s' = s
  action beginPreedit =
    if (s.visible and s.fieldActive and not(s.composing))
      s' = {...s,composing:true,beforePending:s.pending,baseline:s.draft,pending:true}
    else s' = s
  // Cancellation retains the prior pending baseline only if still unmatched;
  // otherwise the newly accepted authoritative value is shown at next paint.
  // Changed-value commit is separately abstracted by commitPreedit below.
  action endPreedit =
    if (s.composing)
      s' = {...s,composing:false,
        draft:if (s.beforePending and s.acceptedText!=s.baseline) s.baseline else s.acceptedText,
        pending:(s.beforePending and s.acceptedText!=s.baseline)}
    else s' = s
  // Conditional a127 candidate: composition-end with changed text uses
  // sendQuery. This action only models pending state, not the Dispatch wire.
  action commitPreedit(value:int): bool =
    if (s.visible and s.fieldActive and s.composing and value>=0 and value<=4 and value!=s.baseline)
      s' = {...s,composing:false,draft:value,
        pending:(unsettledHere or value!=s.acceptedText),lastPub:s.pub,lastLease:s.lease}
    else s' = s
  action safeAction(pub:int,lease:int): bool =
    if (s.visible and s.fieldActive and lease==s.lease and pub==s.pub and not(s.composing))
      s' = {...s,effects:s.effects+1,safeEffects:s.safeEffects+1,
        badSafe:(s.badSafe or s.composing)}
    else s' = s
  // Malformed presentation removes the current snapshot but retains the
  // monotonic accepted counters. A newer valid field replacement can recover;
  // a disabled/missing field or a different mode retires this modeled field.
  // Actions for other modes/disabled field focus are not represented here.
  action malformedPresentation =
    s' = {...s,visible:false,fieldActive:false,pending:false,
      composing:false,beforePending:false,lastPub:-1,lastLease:-1}
  action retireField = all {s.visible, s.fieldActive, s.pub<20,
    s' = {...s,pub:s.pub+1,acceptedPub:s.pub+1,fieldActive:false,
      pending:false,composing:false,beforePending:false,lastPub:-1,lastLease:-1} }
  action recoverField(value:int,pub:int,lease:int): bool =
    if ((not(s.visible) or not(s.fieldActive)) and pub>s.pub and pub<=20 and
        lease>=s.lease and value>=0 and value<=4)
      s' = {...s,pub:pub,acceptedPub:pub,lease:lease,visible:true,fieldActive:true,
        acceptedText:value,draft:value,pending:false,composing:false,beforePending:false,lastPub:-1,lastLease:-1}
    else s' = s
  action step = any {publish,paint,reopen,beginPreedit,endPreedit,
    malformedPresentation,retireField,recoverField(0,s.pub+1,s.lease),commitPreedit(3),
    matchingPublication(3,s.pub+1,s.lease),acceptOtherFrame(2,s.pub+1,s.lease),safeAction(s.domPub,s.domLease),
    localEdit(3,s.domPub,s.domLease),externalEdit(4,s.domPub,s.domLease),
    activate(s.domPub,s.domLease),activateClass(5,s.domPub,s.domLease),
    activateClass(10,s.domPub,s.domLease)}
  val safety = s.pub >= s.domPub and s.lease >= s.domLease and
    s.draft>=0 and s.draft<=4 and s.effects>=0 and
    s.pub==s.acceptedPub and not(s.badDependent) and not(s.badSafe) and
    s.effects==s.dependentEffects+s.safeEffects
  // Quint --witnesses uses true as reachable; these are nonzero positive goals.
  val witnessDependent = s.dependentEffects>0
  val witnessSafeWhilePending = s.safeEffects>0 and s.pending
  action check(ok:bool): bool = all { assert(ok), s'=s }
  run localPaintGapPreservesDraftTest = init.then(publish)
    .then(localEdit(3,1,1)).then(paint).then(check(s.shown==3 and s.pending and s.effects==0))
  run staleExternalEditRejectedTest = init.then(publish)
    .then(externalEdit(3,1,1)).then(paint).then(check(s.draft==0 and s.effects==0))
  run staleLocalButtonRejectedTest = init.then(publish)
    .then(activate(1,1)).then(check(s.effects==0))
  run retiredFieldCannotEditTest = init.then(reopen)
    .then(localEdit(3,1,1)).then(check(s.draft==0 and not(s.pending)))
  run futureFieldCannotEditTest = init.then(localEdit(3,2,1))
    .then(check(s.draft==0 and s.effects==0))
  run localFifoKeepsLatestDraftTest = init.then(publish)
    .then(localEdit(2,1,1)).then(localEdit(3,1,1)).then(publish)
    .then(paint).then(check(s.shown==3 and s.pending and s.effects==0))
  run currentActionStillWorksTest = init.then(publish).then(paint)
    .then(activate(2,1)).then(check(s.effects==1 and s.draft==0))
  run pendingDisablesQueryDependentActionTest = init.then(localEdit(3,1,1))
    .then(activate(1,1)).then(check(s.pending and s.effects==0))
  run matchingPublicationRestoresActionTest = init.then(localEdit(3,1,1))
    .then(matchingPublication(3,2,1)).then(activate(2,1))
    .then(check(not(s.pending) and s.acceptedText==3 and s.effects==1))
  run stalePublicationCannotAcknowledgeTest = init.then(localEdit(3,1,1))
    .then(publish).then(matchingPublication(3,1,1)).then(activate(2,1))
    .then(check(s.pending and s.effects==0))
  run wrongTextCannotAcknowledgeTest = init.then(localEdit(3,1,1))
    .then(acceptOtherFrame(2,2,1)).then(activate(2,1))
    .then(check(s.pending and s.effects==0))
  run preeditBlocksEvenSafeActionTest = init.then(beginPreedit)
    .then(safeAction(1,1)).then(matchingPublication(0,2,1))
    .then(check(s.pub==1 and s.pending and s.composing and s.effects==0))
    .then(acceptOtherFrame(0,2,1))
    .then(check(s.pub==2 and s.pending and s.composing and s.effects==0))
  run pendingAllowsSafeRefreshTest = init.then(localEdit(3,1,1))
    .then(safeAction(1,1)).then(check(s.pending and s.effects==1))
  run mismatchedNewFramePreservesPendingUntilMatchTest =
    init.then(localEdit(3,1,1)).then(acceptOtherFrame(2,2,1))
      .then(activate(2,1)).then(check(s.pending and s.draft==3 and s.acceptedText==2 and s.effects==0))
      .then(matchingPublication(3,3,1)).then(activate(3,1))
      .then(check(not(s.pending) and s.effects==1))
  run matchingFrameDuringPreeditPreservesDraftTest =
    init.then(localEdit(3,1,1)).then(beginPreedit)
      .then(acceptOtherFrame(3,2,1)).then(safeAction(2,1))
      .then(check(s.pending and s.composing and s.draft==3 and s.acceptedText==3 and s.effects==0))
  run sameTextDoesNotCreatePendingTest = init.then(localEdit(0,1,1))
      .then(activate(1,1)).then(check(not(s.pending) and s.effects==1))
  run retiredLeaseCannotAcknowledgeTest = init.then(reopen).then(localEdit(3,2,2))
      .then(publish).then(matchingPublication(3,4,1))
      .then(check(s.pending and s.pub==3 and s.lease==2 and s.effects==0))
      .then(matchingPublication(3,4,2))
      .then(check(not(s.pending) and s.pub==4))
  run cancelledPreeditRestoresUnacknowledgedQueryTest =
    init.then(localEdit(3,1,1)).then(beginPreedit).then(localEdit(4,1,1))
      .then(endPreedit).then(activate(1,1))
      .then(check(s.draft==3 and s.pending and not(s.composing) and s.effects==0))
  run cancelledPreeditOnAcknowledgedFieldRestoresActionTest =
    init.then(beginPreedit).then(localEdit(4,1,1)).then(endPreedit)
      .then(activate(1,1)).then(check(s.draft==0 and not(s.pending) and s.effects==1))
  run notYetAcceptedFutureEventRejectedTest =
    init.then(localEdit(3,2,1)).then(activate(2,1))
      .then(check(s.pub==1 and s.acceptedPub==1 and s.draft==0 and s.effects==0))
  // Candidate trace: old query 3 was dispatched; a later frame for 3
  // cannot erase newer reverted input 0. A subsequent frame with 0 clears it.
  // Query dispatch/order and backend causality are assumptions here.
  run latestRevertedDraftSurvivesOlderFrameTest =
    init.then(localEdit(3,1,1)).then(localEdit(0,1,1))
      .then(check(s.pending and s.draft==0))
      .then(acceptOtherFrame(3,2,1))
      .then(check(s.pending and s.draft==0 and s.acceptedText==3))
      .then(matchingPublication(0,3,1))
      .then(check(not(s.pending) and s.draft==0 and s.acceptedText==0))
  run malformedPendingConcealsFieldAndRejectsActionsTest =
    init.then(localEdit(3,1,1)).then(malformedPresentation)
      .then(activate(1,1)).then(safeAction(1,1)).then(localEdit(2,1,1))
      .then(check(not(s.visible) and not(s.fieldActive) and not(s.pending) and s.effects==0))
  run malformedPreeditConcealsAndClearsCompositionTest =
    init.then(beginPreedit).then(localEdit(3,1,1)).then(malformedPresentation)
      .then(check(not(s.visible) and not(s.composing) and not(s.pending)))
  run staleCannotResurrectConcealedFieldTest =
    init.then(malformedPresentation).then(recoverField(3,1,1))
      .then(check(not(s.visible) and s.pub==1))
  run freshSnapshotRecoversConcealedFieldTest =
    init.then(malformedPresentation).then(recoverField(2,2,1))
      .then(check(s.visible and s.fieldActive and s.draft==2 and not(s.pending) and s.effects==0))
  run disabledFieldRetiresPendingAndPreeditTest =
    init.then(localEdit(3,1,1)).then(beginPreedit).then(retireField)
      .then(localEdit(4,2,1)).then(activate(2,1))
      .then(check(s.visible and not(s.fieldActive) and not(s.pending) and not(s.composing) and s.effects==0))
  run EntryPendingBlockedThenMatchedAllowedTest =
    init.then(localEdit(3,1,1)).then(activateClass(0,1,1))
      .then(check(s.effects==0 and s.pending))
      .then(matchingPublication(3,2,1)).then(activateClass(0,2,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run PinPendingBlockedThenMatchedAllowedTest =
    init.then(localEdit(3,1,1)).then(activateClass(1,1,1))
      .then(check(s.effects==0 and s.pending))
      .then(matchingPublication(3,2,1)).then(activateClass(1,2,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run UnpinPendingBlockedThenMatchedAllowedTest =
    init.then(localEdit(3,1,1)).then(activateClass(2,1,1))
      .then(check(s.effects==0 and s.pending))
      .then(matchingPublication(3,2,1)).then(activateClass(2,2,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run PinLeftPendingBlockedThenMatchedAllowedTest =
    init.then(localEdit(3,1,1)).then(activateClass(3,1,1))
      .then(check(s.effects==0 and s.pending))
      .then(matchingPublication(3,2,1)).then(activateClass(3,2,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run PinRightPendingBlockedThenMatchedAllowedTest =
    init.then(localEdit(3,1,1)).then(activateClass(4,1,1))
      .then(check(s.effects==0 and s.pending))
      .then(matchingPublication(3,2,1)).then(activateClass(4,2,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run JumpPendingBlockedThenMatchedAllowedTest =
    init.then(localEdit(3,1,1)).then(activateClass(5,1,1))
      .then(check(s.effects==0 and s.pending))
      .then(matchingPublication(3,2,1)).then(activateClass(5,2,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run PagePreviousPendingBlockedThenMatchedAllowedTest =
    init.then(localEdit(3,1,1)).then(activateClass(6,1,1))
      .then(check(s.effects==0 and s.pending))
      .then(matchingPublication(3,2,1)).then(activateClass(6,2,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run PageNextPendingBlockedThenMatchedAllowedTest =
    init.then(localEdit(3,1,1)).then(activateClass(7,1,1))
      .then(check(s.effects==0 and s.pending))
      .then(matchingPublication(3,2,1)).then(activateClass(7,2,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run FilesHomePendingBlockedThenMatchedAllowedTest =
    init.then(localEdit(3,1,1)).then(activateClass(8,1,1))
      .then(check(s.effects==0 and s.pending))
      .then(matchingPublication(3,2,1)).then(activateClass(8,2,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run FilesCollectionPendingBlockedThenMatchedAllowedTest =
    init.then(localEdit(3,1,1)).then(activateClass(9,1,1))
      .then(check(s.effects==0 and s.pending))
      .then(matchingPublication(3,2,1)).then(activateClass(9,2,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run FilesOpenPathPendingBlockedThenMatchedAllowedTest =
    init.then(localEdit(3,1,1)).then(activateClass(10,1,1))
      .then(check(s.effects==0 and s.pending))
      .then(matchingPublication(3,2,1)).then(activateClass(10,2,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run EntryPreeditBlockedThenCancelAllowedTest =
    init.then(beginPreedit).then(activateClass(0,1,1))
      .then(check(s.effects==0 and s.composing))
      .then(endPreedit).then(activateClass(0,1,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run PinPreeditBlockedThenCancelAllowedTest =
    init.then(beginPreedit).then(activateClass(1,1,1))
      .then(check(s.effects==0 and s.composing))
      .then(endPreedit).then(activateClass(1,1,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run UnpinPreeditBlockedThenCancelAllowedTest =
    init.then(beginPreedit).then(activateClass(2,1,1))
      .then(check(s.effects==0 and s.composing))
      .then(endPreedit).then(activateClass(2,1,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run PinLeftPreeditBlockedThenCancelAllowedTest =
    init.then(beginPreedit).then(activateClass(3,1,1))
      .then(check(s.effects==0 and s.composing))
      .then(endPreedit).then(activateClass(3,1,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run PinRightPreeditBlockedThenCancelAllowedTest =
    init.then(beginPreedit).then(activateClass(4,1,1))
      .then(check(s.effects==0 and s.composing))
      .then(endPreedit).then(activateClass(4,1,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run JumpPreeditBlockedThenCancelAllowedTest =
    init.then(beginPreedit).then(activateClass(5,1,1))
      .then(check(s.effects==0 and s.composing))
      .then(endPreedit).then(activateClass(5,1,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run PagePreviousPreeditBlockedThenCancelAllowedTest =
    init.then(beginPreedit).then(activateClass(6,1,1))
      .then(check(s.effects==0 and s.composing))
      .then(endPreedit).then(activateClass(6,1,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run PageNextPreeditBlockedThenCancelAllowedTest =
    init.then(beginPreedit).then(activateClass(7,1,1))
      .then(check(s.effects==0 and s.composing))
      .then(endPreedit).then(activateClass(7,1,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run FilesHomePreeditBlockedThenCancelAllowedTest =
    init.then(beginPreedit).then(activateClass(8,1,1))
      .then(check(s.effects==0 and s.composing))
      .then(endPreedit).then(activateClass(8,1,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run FilesCollectionPreeditBlockedThenCancelAllowedTest =
    init.then(beginPreedit).then(activateClass(9,1,1))
      .then(check(s.effects==0 and s.composing))
      .then(endPreedit).then(activateClass(9,1,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  run FilesOpenPathPreeditBlockedThenCancelAllowedTest =
    init.then(beginPreedit).then(activateClass(10,1,1))
      .then(check(s.effects==0 and s.composing))
      .then(endPreedit).then(activateClass(10,1,1))
      .then(check(s.effects==1 and s.dependentEffects==1))
  // This deliberately unconstrained order represents a matching presentation
  // that is unrelated to the older request. The source pipeline may forbid
  // that order, which must be established independently: no causality is
  // inferred from text equality or HTTP 204 in this abstraction.
  run abstractUnrelatedMatchMayClearBeforeOlderResultTest =
    init.then(localEdit(3,1,1)).then(localEdit(0,1,1))
      .then(matchingPublication(0,2,1))
      .then(check(not(s.pending) and s.draft==0))
      .then(acceptOtherFrame(3,3,1))
      .then(check(s.draft==3))
  // Given two older-scope local query keys before preedit, the accepted
  // newer matching frame makes those keys stale for controller admission.
  // lastPub is only a key; actual queue/authority ordering is a premise.
  run newerMatchingPreeditFrameSettlesChangedCommitTest =
    init.then(localEdit(3,1,1)).then(localEdit(2,1,1))
      .then(beginPreedit).then(localEdit(3,1,1))
      .then(acceptOtherFrame(3,2,1)).then(commitPreedit(3))
      .then(check(not(s.composing) and not(s.pending) and s.draft==3 and s.acceptedText==3))
  run cancelledPreeditWithoutPriorPendingShowsNewAuthorityTest =
    init.then(beginPreedit).then(localEdit(3,1,1))
      .then(acceptOtherFrame(2,2,1)).then(endPreedit).then(paint)
      .then(check(not(s.composing) and not(s.pending) and s.draft==2 and s.shown==2 and s.acceptedText==2))
}
