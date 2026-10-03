module manual_sampling_test {
 import manual_sampling.* from "./manual_sampling"
 action check(p:bool):bool=all{assert(p),s'=s}
 run exactTexelCenterTest=init.then(observe(4,4,12,6)).then(check(s.red==36*red(2,1) and s.alpha==36*alpha(2,1)))
 run lowerEdgeClampTest=init.then(observe(4,4,-3,-3)).then(check(s.red==36*red(0,0)))
 run upperEdgeClampTest=init.then(observe(4,4,21,21)).then(check(s.red==36*red(3,3)))
 run onePixelExtentTest=init.then(observe(1,1,17,-7)).then(check(s.red==36*red(0,0) and s.alpha==36*alpha(0,0)))
 run equalQuarterWeightsTest=init.then(observe(4,4,3,3)).then(check(s.taps.indices().forall(i=>s.taps.nth(i).weight==9)))
 run fractionalConvexSampleTest=init.then(observe(4,4,1,5)).then(check(allProps))
 run sourceExtentNotWindowExtentTest=init.then(observe(2,3,9,15)).then(check(s.taps.indices().forall(i=>s.taps.nth(i).x==1 and s.taps.nth(i).y==2)))
 run negativeFloorNotTruncationTest=init.then(observe(4,4,-1,1)).then(check(s.taps.nth(0).weight==5 and s.taps.nth(1).weight==25))
}
