module gesture_capture_test {
 import gesture_capture.* from "./gesture_capture"
 action check(p:bool):bool=all{assert(p),s'=s}
 run currentGeometryAfterRetirementTest=init.then(reserve).then(retire(0)).then(retire(1)).then(retire(2)).then(refresh).then(capture(0)).then(check(s.sourceGeometry==7 and allProps))
 run partialRetirementCannotCaptureTest=init.then(reserve).then(retire(0)).then(check(s.retired!=s.scope and s.captured==Set()))
 run refusalPreservesZeroCapturesTest=init.then(reserve).then(retire(0)).then(refusal).then(check(allProps and s.captured==Set()))
 run obsoleteWorkerCannotReserveTest=init.then(newer).then(check(s.worker!=s.receipt and s.retired==Set()))
 run missingCapabilityCannotRetireTest=init.then(reserve).then(unavailable).then(check(not(s.capable) and s.retired==Set() and s.captured==Set()))
 run freshScopeReplacementCannotAuthorizeCaptureTest=init.then(reserve).then(retire(0)).then(retire(1)).then(retire(2)).then(replace).then(check(s.fresh!=s.scope and s.captured==Set()))
}
