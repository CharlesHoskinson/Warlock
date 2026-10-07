module uri_callback_lifetime_tests {
 import uri_callback_lifetime.* from "uri_callback_lifetime_v2"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run currentOpenReads=init.then(fire(Open)).then(fire(Read)).then(check(s.last==1 and s.reader and s.physical))
 run destroyedOwnerDeniesOpen=init.then(fire(DestroyEndpoint)).then(fire(Open)).then(check(s.last== -1 and not(s.physical) and not(s.reader)))
 run heldReaderRetainsPhysicalStorage=init.then(fire(Open)).then(fire(DestroyEndpoint)).then(check(s.physical and s.reader and not(s.allowed)))
 run destructionRevokesExistingReader=init.then(fire(Open)).then(fire(DestroyEndpoint)).then(fire(Read)).then(check(s.last== -1 and s.physical))
 run lastReaderCloseReleasesStorage=init.then(fire(Open)).then(fire(DestroyEndpoint)).then(fire(CloseReader)).then(check(not(s.physical) and not(s.reader)))
 run replacementDeniesOldCapability=init.then(fire(ReplaceReceiver)).then(fire(Open)).then(check(s.epoch==2 and s.last== -1 and not(s.reader)))
 run replacementRevokesExistingReader=init.then(fire(Open)).then(fire(ReplaceReceiver)).then(fire(Read)).then(check(s.reader and s.last== -1))
 run trustedReplacementRebindRestoresRoute=init.then(fire(ReplaceReceiver)).then(fire(Bind)).then(fire(Open)).then(check(s.allowed and s.reader and s.readerEpoch==2))
 run idempotentBindKeepsCurrentRealm=init.then(fire(Bind)).then(check(s.last==1 and s.epoch==1 and s.allowed))
 run clearRetainsMonotonicFrontier=init.then(fire(Clear)).then(fire(Bind)).then(check(s.last== -1 and not(s.allowed) and s.through==1))
 run clearKeepsExistingReaderAuthority=init.then(fire(Open)).then(fire(Clear)).then(fire(Read)).then(check(s.last==1 and s.reader and not(s.allowed)))
 run freshRealmAfterDestroyedOwner=init.then(fire(DestroyEndpoint)).then(fire(NewRealm)).then(fire(Bind)).then(fire(Open)).then(check(s.epoch==2 and s.reader and s.allowed))
 run expiryDeniesNewRead=init.then(fire(Expire)).then(fire(Open)).then(check(s.last== -1 and not(s.reader) and s.physical))
 run expiryRetainsExistingStorage=init.then(fire(Open)).then(fire(Expire)).then(fire(Read)).then(check(s.last== -1 and s.reader and s.physical))
 run foreignBindingKeepsOriginalRoute=init.then(fire(ForeignBind)).then(fire(Open)).then(check(s.last==1 and s.allowed and s.epoch==1))
 run contextReferenceSurvivesOwnerDrop=init.then(fire(DropOwner)).then(fire(Open)).then(fire(Read)).then(check(not(s.owner) and s.last==1 and s.reader))
}
