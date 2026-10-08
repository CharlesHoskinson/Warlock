module pickerOwnership {
  var owned: Set[int]
  var released: Set[int]
  var revoked: bool
  var reply: int
  action init = all { owned'=Set(), released'=Set(), revoked'=false, reply'=0 }
  action acquire(subject: int): bool = all {
    subject.in(Set(11,12,21)), not(subject.in(owned)), owned.size()<2,
    owned'=owned.union(Set(subject)), released'=released, revoked'=revoked, reply'=0
  }
  action descriptor(peer: int,subject: int): bool = all {
    owned'=owned, released'=released, revoked'=revoked,
    reply'=if (not(revoked) and (peer*10+subject).in(owned) and not((peer*10+subject).in(released))) peer*10+subject else 0
  }
  action consumerComplete(subject: int): bool = all {
    subject.in(owned), owned'=owned, released'=released.union(Set(subject)), revoked'=revoked, reply'=0
  }
  action retire(subject: int): bool = all {
    subject.in(owned), subject.in(released), owned'=owned.exclude(Set(subject)), released'=released.exclude(Set(subject)), revoked'=revoked, reply'=0
  }
  action revoke = all {owned'=owned,released'=released,revoked'=true,reply'=0}
  action step = any {acquire(11),acquire(12),acquire(21),descriptor(1,1),descriptor(1,2),descriptor(2,1),consumerComplete(11),consumerComplete(12),consumerComplete(21),retire(11),retire(12),retire(21),revoke}
  val safety = owned.size()<=2 and released.subseteq(owned) and (reply==0 or (reply.in(owned) and not(reply.in(released)) and not(revoked)))
  run independentFamiliesTest = init.then(acquire(11)).then(acquire(12)).then(descriptor(1,2)).then(all {assert(reply==12 and owned==Set(11,12)),owned'=owned,released'=released,revoked'=revoked,reply'=reply})
  run foreignPeerCannotBorrowTest = init.then(acquire(11)).then(descriptor(2,1)).then(all {assert(reply==0),owned'=owned,released'=released,revoked'=revoked,reply'=reply})
  run foreignSubjectCannotBorrowTest = init.then(acquire(11)).then(descriptor(1,2)).then(all {assert(reply==0),owned'=owned,released'=released,revoked'=revoked,reply'=reply})
  run familyRetirementDoesNotEraseOtherTest = init.then(acquire(11)).then(acquire(12)).then(consumerComplete(11)).then(retire(11)).then(descriptor(1,2)).then(all {assert(reply==12 and owned==Set(12)),owned'=owned,released'=released,revoked'=revoked,reply'=reply})
  run revokedDescriptorDeniedTest = init.then(acquire(11)).then(revoke).then(descriptor(1,1)).then(all {assert(reply==0 and owned==Set(11)),owned'=owned,released'=released,revoked'=revoked,reply'=reply})
  run completedConsumerCannotReadTest = init.then(acquire(11)).then(consumerComplete(11)).then(descriptor(1,1)).then(all {assert(reply==0 and owned==Set(11)),owned'=owned,released'=released,revoked'=revoked,reply'=reply})
}
