module receipt_visual_test {
 import receipt_visual.* from "./receipt_visual"
 action check(p:bool):bool=all{assert(p),s'=s}
 run queuesVisualBeforeBlockedContextTest=init.then(fire(Reserve(true))).then(check(s.queued and s.visual==2 and s.context==0))
 run provisionalNeverCommitsTest=init.then(fire(Reserve(true))).then(fire(Commit(2))).then(check(not(s.effect)))
 run oldCallbackCannotCommitTest=init.then(fire(Reserve(true))).then(fire(Commit(1))).then(check(not(s.effect)))
 run thirdReceiptBeforeSecondContextTest=init.then(fire(Reserve(true))).then(fire(Reserve(true))).then(fire(Context({receipt:2,sameContext:true}))).then(check(s.visual==3 and s.context==0))
 run changedContextCancelsVisualTest=init.then(fire(Reserve(true))).then(fire(Context({receipt:2,sameContext:false}))).then(fire(Validate(2))).then(fire(Commit(2))).then(check(s.visual==0 and not(s.effect)))
 run currentContextAndFreshValidationGrantNativeTest=init.then(fire(Reserve(true))).then(fire(Context({receipt:2,sameContext:true}))).then(fire(Validate(2))).then(fire(Commit(2))).then(check(s.effect))
}
