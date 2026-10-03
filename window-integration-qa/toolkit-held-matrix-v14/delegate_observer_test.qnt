module delegate_observer_test {
 import delegate_observer.* from "./delegate_observer"
 action check(p:bool):bool=all{assert(p),s'=s}
 action start=init.then(gate).then(bootstrap(true)).then(exec(true))
 action finish=exited(true).then(waited(true))
 run exactOwnedSuccessfulWriteWaitTest=start.then(enter(true,true,true)).then(result(true)).then(finish).then(check(s.accepted and not(s.mutation)))
 run unauthorizedSourceRefusesTest=init.then(authorize(false,true,true)).then(gate).then(bootstrap(true)).then(exec(true)).then(finish).then(check(not(s.accepted)))
 run unrelatedChildRefusesTest=init.then(authorize(true,false,true)).then(gate).then(bootstrap(true)).then(exec(true)).then(finish).then(check(not(s.accepted)))
 run changedSourceRefusesTest=init.then(authorize(true,true,false)).then(gate).then(bootstrap(true)).then(exec(true)).then(finish).then(check(not(s.accepted)))
 run unknownStopCannotNormalizeNormalExitTest=start.then(unknown).then(detach).then(finish).then(check(s.error and not(s.accepted)))
 run genuineSignalForwardDoesNotMutateSyscallTest=start.then(signal(true)).then(finish).then(check(s.forwards==1 and not(s.mutation)))
 run nonzeroDelegateExitRemainsFailTest=start.then(exited(false)).then(waited(true)).then(check(not(s.accepted)))
 run incompleteWritePayloadRefusesTest=start.then(enter(false,true,true)).then(result(true)).then(finish).then(check(not(s.accepted)))
 run oversizedWriteRefusesTest=start.then(enter(true,false,true)).then(finish).then(check(not(s.accepted)))
 run unknownFdRoutingRefusesTest=start.then(enter(true,true,false)).then(finish).then(check(not(s.accepted)))
 run unpairedSyscallReturnRefusesTest=start.then(result(true)).then(finish).then(check(not(s.accepted)))
 run pendingWriteCannotInferTerminalReceiptTest=start.then(enter(true,true,true)).then(finish).then(check(not(s.accepted)))
 run malformedExecRefusesTest=init.then(gate).then(bootstrap(true)).then(exec(false)).then(finish).then(check(not(s.accepted)))
 run wrongWaitCannotSupplyNormalTerminalTest=start.then(exited(true)).then(waited(false)).then(check(not(s.accepted)))
 run detachAfterObserverErrorRetainsFailureTest=start.then(enter(false,true,true)).then(detach).then(finish).then(check(s.error and not(s.accepted)))
 run actualWaitEndsSamplingTest=start.then(finish).then(step).then(check(s.accepted and not(s.error)))
}
