// Contract model for ARC024/architecture-024 and DEL014/delivery-014;
// source correspondence only, not observed execution or original acceptance.
// Source: withPeerNetwork obtains fd0 socket identity, kernel credentials,
// pidfd and netns FD before Main.enterPrivateNetwork; Owner adopts fd0 and
// checks the held witness before binding loopback and starting the engine.
// Root observed post-unshare /proc/peer/ns/net EACCES in the earlier source;
// the held pre-transition namespace FD is intended to avoid that lookup.
// The backend peer and selected UI process are different principals. Approved,
// selectedCurrent and bindingCurrent abstract external bootstrap/session authority;
// this model does not prove that Owner itself authenticates an approved sender.
// Kernel PID incarnation/liveness and namespace type checks are atomic here;
// time, descriptor ownership and cleanup are abstract and need real tests.
// No browser claim mints a witness; no cross-UID acceptance follows from mapping.
// Backend must remain in captured net namespace; a pidfd does not pin later
// membership. No external interface mutation after verification is assumed.
module ui_private_network {
 type Phase = Fresh | Isolated | Adopted | Verified | Running | Stopped
 type Peer = Approved | Foreign | Reused
 type State = { phase: Phase, peer: Peer, claimedPeer: Peer, witness: bool, retiredWitness: bool, socketMatches: bool, peerAlive: bool, peerOpen: bool, ownIds: bool, maps: bool,
   changedNs: bool, loopback: bool, cloexec: bool, unixPeer: bool,
   procReadable: bool, differentNs: bool, selectedCurrent: bool,
   bindingCurrent: bool, deadlineLive: bool, revoked: bool, sent: int,
   lastSafe: bool, failed: bool }
 var s: State
 pure def helperWitness(x: State): bool = x.witness and x.socketMatches and x.peerAlive and x.peerOpen and x.procReadable and x.differentNs and x.loopback
 pure def validWitness(x: State): bool = x.witness and x.socketMatches and x.peerAlive and x.peerOpen and x.ownIds and x.maps and x.changedNs and x.loopback and x.cloexec and x.unixPeer and x.procReadable and x.differentNs and x.peer == Approved and x.selectedCurrent and x.bindingCurrent and x.deadlineLive and not(x.revoked)
 action init: bool = s' = {phase: Fresh, peer: Approved, claimedPeer: Approved, witness: false, retiredWitness: false, socketMatches: true, peerAlive: true, peerOpen: true, ownIds: false, maps: false, changedNs: false, loopback: false, cloexec: false, unixPeer: false, procReadable: true, differentNs: true, selectedCurrent: true, bindingCurrent: true, deadlineLive: true, revoked: false, sent: 0, lastSafe: true, failed: false}
 // pidfd, namespace descriptor and socket identity captured atomically before unshare.
 action capture: bool = all {s.phase == Fresh, not(s.witness), s.peerAlive, s.socketMatches, s' = {...s, witness: true}}
 action swapSocket: bool = all {s.phase == Adopted, s' = {...s, socketMatches: false}}
 action closePeer: bool = all {s.phase == Adopted, s' = {...s, peerOpen: false}}
 action peerExit: bool = all {s.phase == Adopted, s' = {...s, peerAlive: false}}
 // Failure covers rejected root/mismatched IDs, unshare/map/ioctl failures.
 action isolate(ok: bool): bool = all {s.phase == Fresh, s.witness, s.deadlineLive, not(s.revoked),
  s' = if (ok) {...s, phase: Isolated, ownIds: true, maps: true, changedNs: true, loopback: true} else {...s, phase: Stopped, failed: true}}
 action adopt(peer: Peer, unix: bool): bool = all {s.phase == Isolated, s.deadlineLive, not(s.revoked),
  s' = if (unix) {...s, phase: Adopted, peer: peer, unixPeer: true, cloexec: true} else {...s, phase: Stopped, cloexec: true, failed: true}}
 // Untrusted JSON cannot alter the kernel peer witness.
 action claimPeer(peer: Peer): bool = all {s.phase == Adopted, s' = {...s, claimedPeer: peer}}
 // Observation is separated from engine launch so deadline/revocation can race.
 action verify: bool = all {s.phase == Adopted, s.deadlineLive, not(s.revoked),
  s' = if (helperWitness(s)) {...s, phase: Verified} else {...s, phase: Stopped, failed: true}}
 action start: bool = all {s.phase == Verified, validWitness(s), s' = {...s, phase: Running}}
 action send(binding: bool): bool = all {s.phase == Running, validWitness(s), binding,
  s' = {...s, sent: s.sent + 1, lastSafe: validWitness(s) and binding}}
 action expire: bool = all {s.deadlineLive, s' = {...s, deadlineLive: false, phase: Stopped}}
 action revoke: bool = all {not(s.revoked), s' = {...s, revoked: true, phase: Stopped}}
 action procDenied: bool = all {s.phase == Adopted, s' = {...s, procReadable: false}}
 action sameNamespace: bool = all {s.phase == Adopted, s' = {...s, differentNs: false}}
 action selectedRetired: bool = all {s.phase == Adopted or s.phase == Verified, s' = {...s, selectedCurrent: false}}
 action bindingRetired: bool = all {s.phase == Adopted or s.phase == Verified, s' = {...s, bindingCurrent: false}}
 action stop: bool = all {s.phase == Running, s' = {...s, phase: Stopped}}
 // Successful bracket exit retires the witness; close failure is not success.
 action retireWitness: bool = all {s.phase == Stopped, s.witness, s' = {...s, witness: false, retiredWitness: true}}

 val safety = (s.phase == Running implies s.witness and s.socketMatches and s.peerAlive and s.peerOpen and s.cloexec and s.ownIds and s.maps and s.changedNs and s.loopback and s.unixPeer and s.procReadable and s.differentNs and s.peer == Approved and s.selectedCurrent and s.bindingCurrent and s.deadlineLive and not(s.revoked)) and (s.sent == 0 or s.lastSafe)
 action step: bool = any {capture, swapSocket, closePeer, peerExit, isolate(true), isolate(false), adopt(Approved,true), adopt(Foreign,true), adopt(Reused,true), adopt(Approved,false), claimPeer(Approved), claimPeer(Foreign), verify, start, send(true), expire, revoke, procDenied, sameNamespace, selectedRetired, bindingRetired, stop, retireWitness}
 // Positive coverage schedule uses the identical guarded actions and init.
 // Full adversarial step remains the safety authority; this schedule only
 // samples reachability and does not establish original/native behavior.
 action conversationStep: bool = any {capture, isolate(true), adopt(Approved,true), verify, start, send(true), stop, retireWitness}
 val witnessCapture = s.witness
 val witnessRetirement = s.retiredWitness
 val witnessPeerClosed = not(s.peerOpen)
 val witnessIsolation = s.phase == Isolated
 val witnessAdopted = s.phase == Adopted
 val witnessVerified = s.phase == Verified
 val witnessRunning = s.phase == Running
 val witnessSent = s.sent > 0
 val witnessFailed = s.failed
 val witnessStopped = s.phase == Stopped
 val witnessExpired = not(s.deadlineLive)
 val witnessRevoked = s.revoked
 val witnessProcDenied = not(s.procReadable)
 val witnessSameNamespace = not(s.differentNs)
 val witnessSelectionRetired = not(s.selectedCurrent)
 val witnessBindingRetired = not(s.bindingCurrent)
}
