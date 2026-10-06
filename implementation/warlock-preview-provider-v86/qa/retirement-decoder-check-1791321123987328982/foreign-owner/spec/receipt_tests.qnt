module receipt_tests {
 import receipt.* from "./receipt"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run knownProofSettlesExactJob=init.then(fire(Issue)).then(fire(KnownProof)).then(check(s.known==0 and s.ack==1 and s.nextRequest==2))
 run futureAfterOriginalFinal=init.then(fire(Issue)).then(fire(KnownProof)).then(fire(Future)).then(check(s.ack==0 and s.acks==1 and s.nextRequest==2))
 run exactReplayRetriesAck=init.then(fire(Issue)).then(fire(KnownProof)).then(fire(Repeat)).then(check(s.ack==1 and s.acks==2 and s.known==0))
 run replayPreservesNewKnown=init.then(fire(Issue)).then(fire(KnownProof)).then(fire(Issue)).then(fire(Repeat)).then(check(s.ack==1 and s.known==2 and s.nextRequest==3))
 run alteredSequenceRefused=init.then(fire(Issue)).then(fire(KnownProof)).then(fire(AlteredSeq)).then(check(s.ack==0 and s.acks==1))
 run alteredJobRefused=init.then(fire(Issue)).then(fire(KnownProof)).then(fire(AlteredJob)).then(check(s.ack==0 and s.acks==1))
 run wrongKnownProofRetainsJob=init.then(fire(Issue)).then(fire(WrongKnown)).then(check(s.known==1 and s.ack==0 and s.nextRequest==2))
 run futureWhileKnownRetained=init.then(fire(Issue)).then(fire(Future)).then(check(s.known==1 and s.ack==0 and s.acks==0))
}
