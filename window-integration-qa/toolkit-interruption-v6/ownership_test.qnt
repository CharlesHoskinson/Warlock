module ownership_test {
 import ownership.* from "./ownership"
 action check(p:bool):bool=all{assert(p),s'=s}
 run idleExactUniqueOwnerTest=init.then(retire(1)).then(check(s.success and not(s.retired) and allProps))
 run pendingExactUniqueOwnerTest=init.then(reset(0,1,true,0)).then(retire(1)).then(check(s.success and s.retired and not(s.pending) and allProps))
 run exactHeldCurrentGeometryTest=init.then(reset(0,1,false,1)).then(retire(1)).then(check(s.success and s.retired and s.dragOwner==0 and allProps))
 run foreignDragKeepsAuthorityTest=init.then(reset(0,1,false,2)).then(retire(1)).then(check(s.success and not(s.retired) and s.dragOwner==2 and allProps))
 run staleOwnerRefusesTest=init.then(reset(0,2,true,2)).then(retire(1)).then(check(not(s.success) and not(s.retired) and s.pending and s.dragOwner==2 and allProps))
 run destroyingUniqueOwnerNeverBorrowedTest=init.then(reset(1,1,true,0)).then(retire(1)).then(check(s.success and not(s.retired) and not(s.borrowed) and s.pending and allProps))
 run destroyedUniqueOwnerNeverBorrowedTest=init.then(reset(2,1,true,0)).then(retire(1)).then(check(s.success and not(s.retired) and not(s.borrowed) and allProps))
 run scopedBorrowEndsTest=init.then(reset(0,1,true,0)).then(retire(1)).then(finishBorrow).then(check(not(s.borrowed) and not(s.pending) and allProps))
 run replacementIdentityNeverAdoptedTest=init.then(reset(2,1,true,0)).then(reset(0,2,true,0)).then(retire(1)).then(check(not(s.success) and s.pending and allProps))
}
