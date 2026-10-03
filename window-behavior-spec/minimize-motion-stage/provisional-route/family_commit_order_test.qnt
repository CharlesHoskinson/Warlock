module family_commit_order_test {
 import family_commit_order.* from "./family_commit_order"
 run restoredOwnerAfterSnapshotMustReceiveLatestIntentTest=init.then(fire(Snapshot({identity:1,epoch:1}))).then(fire(OldOwnerRestore)).then(fire(Accept({identity:1,epoch:1}))).then(all{assert(s.snapshotOwnerMin and not(s.ownerMin) and s.plans.contains(0) and allProps),fire(Commit((0,1)))})
 run oldRestoreCannotFollowAtomicFamilyReservationTest=init.then(fire(Snapshot({identity:1,epoch:1}))).then(fire(Accept({identity:1,epoch:1}))).then(fire(OldOwnerRestore)).then(all{assert(s.stale and s.ownerMin and allProps),fire(Commit((1,1)))})
 run allThreeReachLatestMinimizeTest=init.then(fire(Snapshot({identity:1,epoch:1}))).then(fire(OldOwnerRestore)).then(fire(Accept({identity:1,epoch:1}))).then(fire(Commit((0,1)))).then(fire(Commit((1,1)))).then(fire(Commit((2,1)))).then(all{assert(s.plans==Set() and s.ownerMin and s.childMin and s.nestedMin and allProps),fire(OldOwnerRestore)})
 run reusedMemberCannotReceiveOldReservationTest=init.then(fire(Snapshot({identity:1,epoch:1}))).then(fire(Reuse)).then(fire(Accept({identity:1,epoch:1}))).then(all{assert(s.stale and not(s.accepted) and not(s.ownerMin) and allProps),fire(Commit((0,1)))})
}
