module pixel_coverage_test {
 import pixel_coverage.* from "./pixel_coverage"
 action check(p:bool):bool=all{assert(p),s'=s}
 action configure=fire(Configure({lower:3,upper:9,uniforms:true,source:true}))
 run topLeftHalfCenterIncludedTest=init.then(configure).then(fire(Draw(1))).then(check(s.effect and s.covered))
 run bottomRightHalfCenterExcludedTest=init.then(configure).then(fire(Draw(4))).then(check(s.effect and not(s.covered) and s.preserved))
 run outsideMemberPreservesPreviousPrefixTest=init.then(configure).then(fire(Draw(0))).then(check(s.preserved and not(s.covered)))
 run interiorMemberCoveredTest=init.then(configure).then(fire(Draw(3))).then(check(s.covered and not(s.preserved)))
 run changedUniformRefusesPassTest=init.then(fire(Configure({lower:3,upper:9,uniforms:false,source:true}))).then(fire(Draw(1))).then(check(not(s.effect)))
 run wrongSourceRefusesPassTest=init.then(fire(Configure({lower:3,upper:9,uniforms:true,source:false}))).then(fire(Draw(1))).then(check(not(s.effect)))
 run reversedRectangleRefusesPassTest=init.then(fire(Configure({lower:9,upper:3,uniforms:true,source:true}))).then(fire(Draw(1))).then(check(not(s.effect)))
 run outsideOutputNeverDrawsTest=init.then(configure).then(fire(Draw(8))).then(check(not(s.effect)))
 run failureCannotContinuePassTest=init.then(configure).then(fire(Fail)).then(fire(Draw(1))).then(check(not(s.effect)))
 run clippedEmptyMemberPreservesEntireOutputTest=init.then(fire(Configure({lower:3,upper:3,uniforms:true,source:true}))).then(fire(Draw(1))).then(check(s.effect and s.preserved and not(s.covered)))
}
