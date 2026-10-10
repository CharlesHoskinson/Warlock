module announcementOwnerTests {
  import announcementOwner.* from "./announcement-owner"
  action assertState(condition: bool): bool = all {assert(condition),s'=s}
  run refusalAnnouncesOnceTest = init.then(request(1)).then(refuse(1)).then(publish(1,s.publication)).then(assertState(s.delivered.get(1)==1 and s.focus==7))
  run repeatedReceiptCannotReannounceTest = init.then(request(1)).then(refuse(1)).then(publish(1,s.publication)).then(duplicateReceipt).then(assertState(s.sequence==1 and s.frontier==1 and s.delivered.get(1)==1))
  run ownerChangeDoesNotReplayTest = init.then(request(1)).then(refuse(1)).then(publish(1,s.publication)).then(choose(2)).then(assertState(not(canPublish(s,2,s.publication)) and s.delivered.get(1)==1))
  run popupHasOneRouteTest = init.then(popup(true)).then(request(2)).then(refuse(2)).then(assertState(not(canPublish(s,1,s.publication)) and not(canPublish(s,12,s.publication)))).then(publish(11,s.publication)).then(assertState(s.routed.get(1)==11))
  run retiredOwnerCannotReceiveTest = init.then(request(1)).then(refuse(1)).then(choose(0)).then(assertState(not(canPublish(s,1,s.publication)) and s.frontier==0))
  run newIdentitySameWordsCanAnnounceTest = init.then(request(1)).then(refuse(1)).then(publish(1,s.publication)).then(request(1)).then(refuse(1)).then(publish(1,s.publication)).then(assertState(s.delivered.get(1)==1 and s.delivered.get(2)==1))
  run staleFrameCannotDeliverTest = init.then(request(3)).then(refuse(3)).then(assertState(not(canPublish(s,1,s.publication-1)) and s.frontier==0))
  run unpermittedNotificationOnlyChangesHistoryTest = init.then(unpermittedNotification).then(assertState(s.visualNotifications==1 and s.sequence==0 and s.focus==7))
}
