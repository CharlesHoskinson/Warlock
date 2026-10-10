module notificationAnnouncementTests {
  import notificationAnnouncements.* from "./notification-announcements"
  action assertState(condition: bool): bool = all {assert(condition),s'=s}
  run ordinaryArrivalIsPoliteTest = init.then(arrival(false)).then(assertState(s.sequence==1 and s.counts.get(1)==1 and not(s.interrupt.get(1)) and s.focus==7))
  run dndRetainsHistoryWithoutSpeechTest = init.then(dnd(true)).then(arrival(false)).then(assertState(s.history.contains(1) and s.sequence==0 and s.counts.get(1)==0))
  run criticalNeedsExplicitConsentTest = init.then(arrival(true)).then(assertState(s.counts.get(1)==1 and not(s.interrupt.get(1))))
  run optedInCriticalCanInterruptTest = init.then(optIn(true)).then(arrival(true)).then(assertState(s.interrupt.get(1) and s.counts.get(1)==1 and s.focus==7))
  run optInDoesNotEscalateOrdinaryTest = init.then(optIn(true)).then(arrival(false)).then(assertState(not(s.interrupt.get(1))))
  run dndSuppressesOptedInCriticalTest = init.then(optIn(true)).then(dnd(true)).then(arrival(true)).then(assertState(s.history.contains(1) and s.sequence==0 and not(s.interrupt.get(1))))
  run duplicateObservationCannotReplayTest = init.then(arrival(false)).then(duplicateObservation).then(assertState(s.sequence==1 and s.counts.get(1)==1))
  run turningDndOffDoesNotReplayHistoryTest = init.then(dnd(true)).then(arrival(false)).then(dnd(false)).then(assertState(s.sequence==0 and s.counts.get(1)==0)).then(arrival(false)).then(assertState(s.sequence==1 and s.counts.get(2)==1))
  run optInCannotReplayPastCriticalTest = init.then(arrival(true)).then(optIn(true)).then(assertState(s.sequence==1 and not(s.interrupt.get(1))))
  run existingHistoryIsBaselineOnlyTest = init.then(baseline).then(assertState(s.history.contains(1) and s.sequence==0)).then(arrival(false)).then(assertState(s.counts.get(2)==1 and s.sequence==1))
}
