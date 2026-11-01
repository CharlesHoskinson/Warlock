module action_feedback_priority_test {
  import action_feedback_priority.* from "./action-feedback-priority"

  run pendingRetainsWorkspaceAndActionTest = init.then(pending).expect(
    s.overviewOpen and s.workspaceNotice and s.rendered == CombinedFeedback
      and renderedMatchesPolicy and actionFeedbackKeepsPriority
      and liveRegionMatchesRenderedState
  )

  run pendingWithoutWorkspaceNoticeTest = init.then(pendingWithoutWorkspaceNotice).expect(
    s.overviewOpen and not(s.workspaceNotice) and s.rendered == WindowFeedback
      and renderedMatchesPolicy and actionFeedbackKeepsPriority
      and liveRegionMatchesRenderedState
  )

  run refusedRetainsWorkspaceAndActionTest = init.then(refused).expect(
    s.overviewOpen and s.workspaceNotice and s.rendered == CombinedFeedback
      and renderedMatchesPolicy and actionFeedbackKeepsPriority
      and liveRegionMatchesRenderedState
  )

  run unknownRetainsWorkspaceAndActionTest = init.then(unknown).expect(
    s.overviewOpen and s.workspaceNotice and s.rendered == CombinedFeedback
      and renderedMatchesPolicy and actionFeedbackKeepsPriority
      and liveRegionMatchesRenderedState
  )

  run committedReturnsToOverviewTest = init.then(committed).expect(
    s.overviewOpen and s.workspaceNotice and s.rendered == OverviewGuidance
      and renderedMatchesPolicy and actionFeedbackKeepsPriority
      and liveRegionMatchesRenderedState
  )

  run cancelledReturnsToOverviewTest = init.then(cancelled).expect(
    s.overviewOpen and s.workspaceNotice and s.rendered == OverviewGuidance
      and renderedMatchesPolicy and actionFeedbackKeepsPriority
      and liveRegionMatchesRenderedState
  )

  run closedOverviewHidesProjectionTest = init.then(closeOverview).expect(
    s.status == Pending and not(s.overviewOpen) and s.rendered == Empty
      and renderedMatchesPolicy and liveRegionMatchesRenderedState
  )

  // The negative tests exercise the same properties against explicit faulty
  // transitions. A tautological projection-only predicate could not pass them.
  run wrongPriorityMutantIsDetectedTest = init.then(pendingPriorityMutant).expect(
    not(renderedMatchesPolicy) and not(actionFeedbackKeepsPriority)
  )

  run disabledLiveRegionMutantIsDetectedTest = init.then(pendingLiveRegionMutant).expect(
    renderedMatchesPolicy and not(liveRegionMatchesRenderedState)
  )
}
