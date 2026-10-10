module notificationRelevanceTests {
 import notificationRelevance.* from "./notification-relevance"
 action assertState(condition:bool):bool=all{assert(condition),s'=s}
 run focusedExpiryRetainsFocusTest=init.then(focus(1)).then(expire(1)).then(assertState(s.expiry.get(1)==1 and s.focus==1))
 run invokedExpiryRetainsOtherFocusTest=init.then(focus(2)).then(invoke(1)).then(expire(1)).then(assertState(s.expiry.get(1)==1 and s.focus==2 and s.pending==1))
 run irrelevantExpirySilentTest=init.then(focus(2)).then(expire(1)).then(assertState(s.expiry.get(1)==0 and s.focus==2))
 run repeatedExpirySilentTest=init.then(focus(1)).then(expire(1)).then(duplicate).then(assertState(s.expiry.get(1)==1 and not(s.live.contains(1)) and s.focus==1))
 run matchedExpiredRefusalOnceTest=init.then(invoke(1)).then(expire(1)).then(refused(1)).then(duplicate).then(assertState(s.rejection.get(1)==1 and s.pending==0 and not(canRefuse(s,1))))
 run changedLiveTargetRefusalSilentTest=init.then(invoke(1)).then(refused(1)).then(assertState(s.rejection.get(1)==0))
 run foreignRequestCannotSettleTest=init.then(invoke(1)).then(foreign).then(assertState(not(canRefuse(s,2)) and s.pending==1))
 run dndSuppressesRelevantExpiryAndRefusalTest=init.then(focus(1)).then(invoke(1)).then(dnd(true)).then(expire(1)).then(refused(1)).then(assertState(s.expiry.get(1)==0 and s.rejection.get(1)==0 and s.focus==1))
 run dndOffCannotReplayTest=init.then(focus(1)).then(dnd(true)).then(expire(1)).then(dnd(false)).then(assertState(s.expiry.get(1)==0 and s.focus==1))
 run lateFocusCannotReplayExpiryTest=init.then(expire(1)).then(focus(1)).then(assertState(s.expiry.get(1)==0 and s.focus==1))
}
