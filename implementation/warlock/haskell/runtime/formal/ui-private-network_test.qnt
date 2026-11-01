// Failed actions end their trace; expectations describe only the preceding state.
module ui_private_network_test {
 import ui_private_network.* from "./ui-private-network"
 run approvedLoopback = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(verify).then(start).then(send(true)).expect(s.sent == 1 and safety)
 run missingWitness = init.expect(not(s.witness)).then(isolate(true).fail())
 run swappedSocket = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(swapSocket).then(verify).expect(s.failed and s.sent == 0)
 run closedPeer = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(closePeer).then(verify).expect(s.failed and s.sent == 0)
 run exitedPeer = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(peerExit).then(verify).expect(s.failed and s.sent == 0)
 run noNET = init.then(capture).then(isolate(false)).expect(s.phase == Stopped and s.failed and s.sent == 0).then(adopt(Approved,true).fail())
 run nonUnix = init.then(capture).then(isolate(true)).then(adopt(Approved,false)).expect(s.failed and s.cloexec).then(verify.fail())
 run foreignPeer = init.then(capture).then(isolate(true)).then(adopt(Foreign,true)).then(verify).expect(s.phase == Verified and s.sent == 0).then(start.fail())
 // Composed authority obligation; the helper alone does not approve a sender.
 run reusedPid = init.then(capture).then(isolate(true)).then(adopt(Reused,true)).then(verify).expect(s.phase == Verified and s.sent == 0).then(start.fail())
 run forgedApprovedClaim = init.then(capture).then(isolate(true)).then(adopt(Foreign,true)).then(claimPeer(Approved)).then(verify).expect(s.phase == Verified and s.sent == 0).then(start.fail())
 run forgedForeignClaim = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(claimPeer(Foreign)).then(verify).then(start).expect(s.phase == Running and safety)
 run procAccessDenied = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(procDenied).then(verify).expect(s.failed and s.phase == Stopped)
 run sameNetNamespace = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(sameNamespace).then(verify).expect(s.failed and s.sent == 0)
 run foreignBinding = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(verify).then(start).expect(s.sent == 0 and safety).then(send(false).fail())
 run deadlineBeforeStart = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(verify).then(expire).expect(not(s.deadlineLive) and s.sent == 0).then(start.fail())
 run deadlineAfterSend = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(verify).then(start).then(send(true)).then(expire).expect(s.sent == 1 and safety).then(send(true).fail())
 run revokedBeforeStart = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(verify).then(revoke).expect(s.revoked and s.sent == 0).then(start.fail())
 run revokedAfterSend = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(verify).then(start).then(send(true)).then(revoke).expect(s.sent == 1 and safety).then(send(true).fail())
 run retiredSelection = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(verify).then(selectedRetired).expect(s.sent == 0).then(start.fail())
 run retiredBinding = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(verify).then(bindingRetired).expect(s.sent == 0).then(start.fail())
 run normalCleanup = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(verify).then(start).then(stop).then(retireWitness).expect(not(s.witness) and safety).then(retireWitness.fail())
 run normalStop = init.then(capture).then(isolate(true)).then(adopt(Approved,true)).then(verify).then(start).then(stop).expect(s.phase == Stopped and safety).then(send(true).fail())
}
