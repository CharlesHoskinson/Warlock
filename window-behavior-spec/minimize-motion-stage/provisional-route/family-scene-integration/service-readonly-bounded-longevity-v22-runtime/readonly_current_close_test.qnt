module readonly_current_close_test {
 import readonly_current_close.* from "./readonly_current_close"
 action check(b:bool):bool=all{assert(b),s'=s}
 run closeDuringUnwrittenAppendRefusesTest=init.then(fire(BeginAppend)).then(fire(NormalClose(true))).then(check(not(s.closed) and not(s.ackNow) and s.retained))
 run closeDuringDurableFileRefusesTest=init.then(fire(BeginAppend)).then(fire(Write(true))).then(fire(NormalClose(true))).then(check(not(s.closed) and not(s.ackNow)))
 run closeDuringPublishedUnadoptedTipRefusesTest=init.then(fire(BeginAppend)).then(fire(Write(true))).then(fire(Publish(true))).then(fire(NormalClose(true))).then(check(not(s.closed) and not(s.ackNow)))
 run completeAppendThenFullAuditClosesTest=init.then(fire(BeginAppend)).then(fire(Write(true))).then(fire(Publish(true))).then(fire(Adopt)).then(fire(NormalClose(true))).then(check(s.closed and s.ackNow and allProps))
 run actualBorrowBlocksNormalCloseTest=init.then(fire(Borrow)).then(fire(NormalClose(true))).then(check(not(s.closed))).then(fire(Release)).then(fire(NormalClose(true))).then(check(s.closed and allProps))
 run oldCorruptionOrIncompleteAuditRefusesNormalCloseTest=init.then(fire(CorruptOld)).then(fire(NormalClose(true))).then(check(not(s.closed) and not(s.ackNow)))
 run incompleteAuditNeverClosesTest=init.then(fire(NormalClose(false))).then(check(not(s.closed) and not(s.ackNow)))
 run crashNeverCountsAsNormalCompletionTest=init.then(fire(BeginAppend)).then(fire(Crash)).then(check(s.closed and not(s.ackNow) and s.retained and allProps))
}
