module action_feedback_priority {
  // ELM-UI-007 restore-pending/refused/unknown presentation slice.
  // This models the overview notice choice and its live-region category, not
  // the native reducer, focus, keyboard input, assistive technology, or effect
  // dispatch. `rendered` and `liveRegion` are state so incorrect choices are
  // reachable and can falsify the properties below.
  type Status = Ready | Pending | Refused | Unknown | Cancelled | Committed
  type Projection = Empty | OverviewGuidance | WindowFeedback | CombinedFeedback
  type LiveMode = Off | Polite

  type State = {
    status: Status,
    unresolvedPending: bool,
    unresolvedUnknown: bool,
    overviewOpen: bool,
    workspaceNotice: bool,
    rendered: Projection,
    liveRegion: LiveMode,
  }

  var s: State

  pure def recoveryNeeded(state: State): bool =
    (state.unresolvedPending and state.status == Pending)
      or (state.unresolvedUnknown and state.status == Unknown)
      or state.status == Refused
      or state.status == Unknown

  pure def expectedProjection(state: State): Projection =
    if (not(state.overviewOpen)) Empty
    else if (recoveryNeeded(state))
      (if (state.workspaceNotice) CombinedFeedback else WindowFeedback)
    else OverviewGuidance

  pure def expectedLiveMode(rendered: Projection): LiveMode =
    if (rendered == Empty) Off else Polite

  action init = s' = {
    status: Ready,
    unresolvedPending: false,
    unresolvedUnknown: false,
    overviewOpen: true,
    workspaceNotice: true,
    rendered: OverviewGuidance,
    liveRegion: Polite,
  }

  action pending = s' = {
    status: Pending,
    unresolvedPending: true,
    unresolvedUnknown: false,
    overviewOpen: true,
    workspaceNotice: true,
    rendered: CombinedFeedback,
    liveRegion: Polite,
  }

  action pendingWithoutWorkspaceNotice = s' = {
    status: Pending,
    unresolvedPending: true,
    unresolvedUnknown: false,
    overviewOpen: true,
    workspaceNotice: false,
    rendered: WindowFeedback,
    liveRegion: Polite,
  }

  action refused = s' = {
    status: Refused,
    unresolvedPending: false,
    unresolvedUnknown: false,
    overviewOpen: true,
    workspaceNotice: true,
    rendered: CombinedFeedback,
    liveRegion: Polite,
  }

  action unknown = s' = {
    status: Unknown,
    unresolvedPending: false,
    unresolvedUnknown: true,
    overviewOpen: true,
    workspaceNotice: true,
    rendered: CombinedFeedback,
    liveRegion: Polite,
  }

  action committed = s' = {
    status: Committed,
    unresolvedPending: false,
    unresolvedUnknown: false,
    overviewOpen: true,
    workspaceNotice: true,
    rendered: OverviewGuidance,
    liveRegion: Polite,
  }

  action cancelled = s' = {
    status: Cancelled,
    unresolvedPending: false,
    unresolvedUnknown: false,
    overviewOpen: true,
    workspaceNotice: true,
    rendered: OverviewGuidance,
    liveRegion: Polite,
  }

  action closeOverview = s' = {
    status: Pending,
    unresolvedPending: true,
    unresolvedUnknown: false,
    overviewOpen: false,
    workspaceNotice: true,
    rendered: Empty,
    liveRegion: Off,
  }

  // Deliberate mutants: sensitivity tests prove that the properties can catch
  // a priority regression or an incorrectly disabled live region.
  action pendingPriorityMutant = s' = {
    status: Pending,
    unresolvedPending: true,
    unresolvedUnknown: false,
    overviewOpen: true,
    workspaceNotice: true,
    rendered: OverviewGuidance,
    liveRegion: Polite,
  }

  action pendingLiveRegionMutant = s' = {
    status: Pending,
    unresolvedPending: true,
    unresolvedUnknown: false,
    overviewOpen: true,
    workspaceNotice: true,
    rendered: CombinedFeedback,
    liveRegion: Off,
  }

  action step = any {
    pending,
    pendingWithoutWorkspaceNotice,
    refused,
    unknown,
    committed,
    cancelled,
    closeOverview,
  }

  val renderedMatchesPolicy = s.rendered == expectedProjection(s)

  val actionFeedbackKeepsPriority =
    (not(recoveryNeeded(s)) or not(s.overviewOpen))
      or s.rendered == WindowFeedback or s.rendered == CombinedFeedback

  val liveRegionMatchesRenderedState =
    s.liveRegion == expectedLiveMode(s.rendered)

  val pendingScenarioWitness = s.status == Pending and s.rendered == CombinedFeedback
  val pendingNoWorkspaceWitness = s.status == Pending and not(s.workspaceNotice)
    and s.rendered == WindowFeedback
  val refusedScenarioWitness = s.status == Refused and s.rendered == CombinedFeedback
  val unknownScenarioWitness = s.status == Unknown and s.rendered == CombinedFeedback
  val committedScenarioWitness = s.status == Committed and s.rendered == OverviewGuidance
  val cancelledScenarioWitness = s.status == Cancelled and s.rendered == OverviewGuidance
  val closedOverviewWitness = not(s.overviewOpen) and s.rendered == Empty
  val priorityMutantWitness = s.status == Pending and s.rendered == OverviewGuidance
  val liveRegionMutantWitness = s.status == Pending and s.rendered == CombinedFeedback
    and s.liveRegion == Off
}
