module ipc_guard_test {
 import ipc_guard.* from "./ipc_guard"
 action check(p:bool):bool=all{assert(p),s'=s}
 run zeroRequestPeerProofIsInsufficientTest=init.then(fire(Connect(true))).then(fire(Authorize)).then(check(not(s.authority)))
 run completeJsonWithoutEofIsInsufficientTest=init.then(fire(Connect(true))).then(fire(SendVersion)).then(fire(Receive(true))).then(fire(Authorize)).then(check(not(s.authority)))
 run invalidReplyWithEofRefusesTest=init.then(fire(Connect(true))).then(fire(SendVersion)).then(fire(Receive(false))).then(fire(ServerEOF)).then(fire(Authorize)).then(check(not(s.authority)))
 run freshPeerCompleteVersionEofAllowsGuardTest=init.then(fire(Connect(true))).then(fire(SendVersion)).then(fire(Receive(true))).then(fire(ServerEOF)).then(fire(Authorize)).then(check(s.authority))
}
