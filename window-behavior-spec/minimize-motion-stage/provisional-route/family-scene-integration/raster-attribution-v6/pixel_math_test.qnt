module pixel_math_test {
 import pixel_math.* from "./pixel_math"
 action check(p:bool):bool=all{assert(p),s'=s}
 pure val transparent={r:0,a:0}
 pure val opaque={r:100,a:255}
 pure val solid={c00:opaque,c10:opaque,c01:opaque,c11:opaque}
 run texelCenterSelectsExactSampleTest=init.then(observe(solid,0,0,transparent)).then(check(s.result==opaque))
 run equalCornerWeightsAreConvexTest=init.then(observe({c00:transparent,c10:{r:255,a:255},c01:transparent,c11:{r:255,a:255}},3,3,transparent)).then(check(s.result=={r:128,a:128}))
 run transparentSourcePreservesDestinationTest=init.then(observe({c00:transparent,c10:transparent,c01:transparent,c11:transparent},1,5,opaque)).then(check(s.result==opaque))
 run opaqueSourceReplacesDestinationTest=init.then(observe(solid,1,5,{r:255,a:255})).then(check(s.result==opaque))
 run halfAlphaSourceOverHasExactNearestQuantizationTest=init.then(observe({c00:{r:10,a:128},c10:{r:10,a:128},c01:{r:10,a:128},c11:{r:10,a:128}},1,5,opaque)).then(check(s.result=={r:60,a:255}))
 run endpointClampSelectsCornerTest=init.then(observe({c00:transparent,c10:{r:20,a:64},c01:{r:64,a:128},c11:opaque},6,6,transparent)).then(check(s.result==opaque))
}
