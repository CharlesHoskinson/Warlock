module wheel_input_test {
 import wheel_input.* from "./wheel_input"
 action check(p:bool):bool=all{assert(p),s'=s}
 run authenticatedReleasedWheelSyncTest=init.then(wheel(true)).then(sync(true)).then(finish).then(check(not(s.failed) and s.accepted==1))
 run heldWheelRefusesTest=init.then(configure(true,true,true)).then(wheel(true)).then(check(s.failed and s.accepted==0))
 run unauthenticatedWheelRefusesTest=init.then(configure(false,false,true)).then(wheel(true)).then(check(s.failed))
 run keyboardWheelRefusesTest=init.then(configure(false,true,false)).then(wheel(true)).then(check(s.failed))
 run malformedLiteralRefusesTest=init.then(wheel(false)).then(check(s.failed))
 run missingSyncRefusesTest=init.then(wheel(true)).then(finish).then(check(s.failed))
 run changedLifetimeSyncRefusesTest=init.then(wheel(true)).then(sync(false)).then(check(s.failed))
 run interposedCommandRefusesTest=init.then(wheel(true)).then(other).then(check(s.failed))
 run duplicateWheelBeforeSyncRefusesTest=init.then(wheel(true)).then(wheel(true)).then(check(s.failed))
}
