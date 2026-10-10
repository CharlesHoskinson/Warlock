module modal_eligibility {
  // REN-018/ren-018; ModalRecipient::focusRecipient resolves native constraints
  // before leaf eligibility. Native-object traversal/ABI/input remain separate.
  // Topology: 0 singleton, 1 modal, 2 nested modal, 3 siblings, 4 cycle.
  type State = { topology: int, eligible: bool, noFocus: bool, ready: bool,
    protected: bool, focus: int, draft: str, familyAttempts: int,
    refusals: int, unrelatedClicks: int, validDecision: bool }
  var s: State
  action init = s' = { topology: 0, eligible: true, noFocus: false, ready: true,
    protected: false, focus: 9, draft: "unsaved modal draft", familyAttempts: 0,
    refusals: 0, unrelatedClicks: 0, validDecision: true }
  pure def candidate(now: State): int =
    if (not(now.ready) or now.protected or not(now.eligible) or now.noFocus or now.topology>=3) -1
    else now.topology
  pure def family(now: State): State = {
    ...now, focus: if (candidate(now)==-1) now.focus else candidate(now),
    familyAttempts: now.familyAttempts+1,
    refusals: now.refusals+(if(candidate(now)==-1) 1 else 0),
    validDecision: if(candidate(now)==-1) true
      else now.ready and not(now.protected) and now.eligible and not(now.noFocus)
        and now.topology<3 and candidate(now)==now.topology
  }
  action shape(kind: int): bool = s' = {...s,topology:kind,ready:false}
  action block = s' = {...s,eligible:not(s.eligible)}
  action noFocus = s' = {...s,noFocus:not(s.noFocus)}
  action protect = s' = {...s,protected:not(s.protected)}
  action commit = s' = {...s,ready:true}
  action focusFamily = s' = family(s)
  action clickUnrelated = s' = if(not(s.ready) or s.protected) s
    else {...s,focus:9,unrelatedClicks:s.unrelatedClicks+1}
  action step = any {shape(0),shape(1),shape(2),shape(3),shape(4),block,noFocus,protect,commit,focusFamily,clickUnrelated}
  val safety = s.validDecision and s.draft=="unsaved modal draft"
  val eligibleModalReached = s.focus==1 and s.familyAttempts>0
  val nestedModalReached = s.focus==2 and s.familyAttempts>0
  val blockedModalRefused = s.topology==1 and not(s.eligible) and s.refusals>0
  val noFocusModalRefused = s.topology==1 and s.noFocus and s.refusals>0
  val unrelatedDraftPreserved = s.topology>0 and s.focus==9 and s.unrelatedClicks>0
}
