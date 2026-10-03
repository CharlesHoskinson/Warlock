module family_order_test {
 import family_order.* from "./family_order"
 action check(p:bool):bool=all{assert(p),s'=s}
 run mruNestedBeforeParentCounterexampleCorrectedTest=init.then(draw).then(draw).then(draw).then(draw).then(check(s.order==List(0,3,1,2) and allProps))
 run ownerChildNestedChainTest=init.then(begin(Map(0->-1,1->0,2->1,3->2),Map(0->3,1->2,2->1,3->0))).then(draw).then(draw).then(draw).then(draw).then(check(s.order==List(0,1,2,3)))
 run nativeSiblingVectorNotFocusHistoryTest=init.then(begin(Map(0->-1,1->0,2->0,3->0),Map(0->3,1->2,2->0,3->1))).then(draw).then(draw).then(draw).then(draw).then(check(s.order==List(0,2,3,1)))
 run pinnedAncestorCannotCoverChildTest=init.then(begin(Map(0->-1,1->0,2->1,3->2),Map(0->3,1->0,2->1,3->2))).then(draw).then(draw).then(draw).then(draw).then(check(s.order==List(0,1,2,3)))
 run independentPinnedSiblingLastTest=init.then(begin(Map(0->-1,1->0,2->0,3->0),Map(0->3,1->1,2->2,3->0))).then(draw).then(draw).then(draw).then(draw).then(check(s.order==List(0,3,1,2)))
 run selectedCycleRefusesAllDrawsTest=init.then(begin(Map(0->-1,1->2,2->1,3->0),Map(0->0,1->1,2->2,3->3))).then(check(not(s.valid) and allProps))
 run ambiguousSecondRootRefusesTest=init.then(begin(Map(0->-1,1->-1,2->1,3->0),Map(0->0,1->1,2->2,3->3))).then(check(not(s.valid) and allProps))
 run exactCompleteVectorTest=init.then(draw).then(draw).then(draw).then(draw).then(check(s.order.length()==4 and exactNoDuplicate))
}
