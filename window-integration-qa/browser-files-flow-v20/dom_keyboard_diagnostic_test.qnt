module dom_keyboard_diagnostic_test {
 import dom_keyboard_diagnostic.* from "./dom_keyboard_diagnostic"
 pure val c={token:1,page:1,key:45,prevented:false}
 run sameEventCaptureBubbleTest=init.then(fire(Capture(c))).then(fire(Bubble({...c,prevented:true}))).then(check(records.get(1).bubble and records.get(1).prevented))
 run orphanBubbleNotInventedTest=init.then(fire(Bubble(c))).then(check(orphan and records==Map()))
 run newEventCannotReplaceCaptureTest=init.then(fire(Capture(c))).then(fire(Capture({...c,key:99}))).then(check(records.get(1).key==45))
 run mismatchedKeyNotJoinedTest=init.then(fire(Capture(c))).then(fire(Bubble({...c,key:99}))).then(check(not(records.get(1).bubble)))
 run stalePageBubbleNotJoinedTest=init.then(fire(Capture(c))).then(fire(Reload)).then(fire(Bubble(c))).then(check(orphan and records==Map()))
 run truncationDoesNotInventHistoryTest=init.then(fire(Capture(c))).then(fire(Truncate)).then(fire(Bubble(c))).then(check(orphan and records==Map()))
 run exhaustionStopsObserverNotOriginalVerdictTest=init.then(fire(Exhaust)).then(fire(Capture(c))).then(fire(OriginalAccept(true))).then(check(records==Map() and accepted))
 run diagnosticMatchingNeverAcceptsOriginalFeatureTest=init.then(fire(Capture(c))).then(fire(Bubble(c))).then(check(not(accepted)))
 run originalFailureNotChangedByKeyMetadataTest=init.then(fire(OriginalAccept(false))).then(fire(Capture(c))).then(fire(Bubble(c))).then(check(not(accepted)))
 run missingAndOutOfRangeTokenRefusedTest=init.then(fire(Capture({...c,token:0}))).then(fire(Capture({...c,token:65}))).then(check(records==Map()))
 run newPageSameTokenKeepsPageSeparationTest=init.then(fire(Capture(c))).then(fire(Reload)).then(fire(Capture({...c,page:2}))).then(check(records.get(1).page==2))
}
