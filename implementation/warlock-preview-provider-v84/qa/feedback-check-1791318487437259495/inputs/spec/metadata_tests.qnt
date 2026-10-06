module metadata_tests {
 import metadata.* from "./metadata"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run freshMetadata=init.then(fire(Fresh)).then(check(s.revision==1 and s.visible and s.capturing and s.cancels==0))
 run staleAndForeign=init.then(fire(Fresh)).then(fire(Stale)).then(fire(Foreign)).then(check(s.revision==1 and s.cancels==0))
 run lockConceals=init.then(fire(Fresh)).then(fire(Lock)).then(check(not(s.visible) and s.cancels==1 and not(s.capturing)))
 run metadataCannotUnlock=init.then(fire(Lock)).then(fire(Fresh)).then(fire(OtherDenial)).then(check(not(s.visible) and s.revision==1 and s.cancels==1))
 run staleUnlockIgnored=init.then(fire(Lock)).then(fire(UnlockStale)).then(check(not(s.visible) and s.cancels==1))
 run freshUnlockRetainsCleanup=init.then(fire(Lock)).then(fire(UnlockFresh)).then(check(s.visible and s.cancels==1 and not(s.capturing)))
 run foreignLockIgnored=init.then(fire(ForeignLock)).then(check(s.visible and s.capturing and s.cancels==0))
 run lockedScopeConceals=init.then(fire(ObserveLocked)).then(fire(Fresh)).then(fire(UnlockStale)).then(fire(UnlockFresh)).then(check(s.visible and s.revision==1 and s.cancels==1))
}
