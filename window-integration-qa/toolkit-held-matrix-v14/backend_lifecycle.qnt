module backend_lifecycle {
 var observed: bool
 var candidates: bool
 var exact: bool
 var backendAccepted: bool
 var serviceRegistered: bool
 var snapshotUsed: bool
 var normalQuit: bool
 var fullAccepted: bool
 action init = all {observed'=false,candidates'=false,exact'=false,backendAccepted'=false,serviceRegistered'=false,snapshotUsed'=false,normalQuit'=false,fullAccepted'=false}
 action observeExact = all {not(observed),observed'=true,candidates'=true,exact'=true,backendAccepted'=false,serviceRegistered'=serviceRegistered,snapshotUsed'=snapshotUsed,normalQuit'=normalQuit,fullAccepted'=fullAccepted}
 action observeMissing = all {not(observed),observed'=true,candidates'=true,exact'=false,backendAccepted'=false,serviceRegistered'=serviceRegistered,snapshotUsed'=snapshotUsed,normalQuit'=normalQuit,fullAccepted'=fullAccepted}
 action observeEmpty = all {not(observed),observed'=true,candidates'=false,exact'=false,backendAccepted'=false,serviceRegistered'=serviceRegistered,snapshotUsed'=snapshotUsed,normalQuit'=normalQuit,fullAccepted'=fullAccepted}
 action acceptBackend = all {observed,candidates,exact,backendAccepted'=true,observed'=observed,candidates'=candidates,exact'=exact,serviceRegistered'=serviceRegistered,snapshotUsed'=snapshotUsed,normalQuit'=normalQuit,fullAccepted'=fullAccepted}
 action registerService = all {backendAccepted,serviceRegistered'=true,observed'=observed,candidates'=candidates,exact'=exact,backendAccepted'=backendAccepted,snapshotUsed'=snapshotUsed,normalQuit'=normalQuit,fullAccepted'=fullAccepted}
 action genuineSnapshot = all {serviceRegistered,snapshotUsed'=true,observed'=observed,candidates'=candidates,exact'=exact,backendAccepted'=backendAccepted,serviceRegistered'=serviceRegistered,normalQuit'=normalQuit,fullAccepted'=fullAccepted}
 action quit = all {normalQuit'=true,observed'=observed,candidates'=candidates,exact'=exact,backendAccepted'=backendAccepted,serviceRegistered'=serviceRegistered,snapshotUsed'=snapshotUsed,fullAccepted'=fullAccepted}
 action acceptFull = all {backendAccepted,serviceRegistered,snapshotUsed,normalQuit,fullAccepted'=true,observed'=observed,candidates'=candidates,exact'=exact,backendAccepted'=backendAccepted,serviceRegistered'=serviceRegistered,snapshotUsed'=snapshotUsed,normalQuit'=normalQuit}
 action idle = all {observed'=observed,candidates'=candidates,exact'=exact,backendAccepted'=backendAccepted,serviceRegistered'=serviceRegistered,snapshotUsed'=snapshotUsed,normalQuit'=normalQuit,fullAccepted'=fullAccepted}
 action step = any {observeExact,observeMissing,observeEmpty,acceptBackend,registerService,genuineSnapshot,quit,acceptFull,idle}
 val invariant = all {backendAccepted implies all {observed,candidates,exact},fullAccepted implies all {backendAccepted,serviceRegistered,snapshotUsed,normalQuit}}
 run missingClosureCannotAcceptTest = init.then(observeMissing).then(quit).then(all {assert(normalQuit and not(backendAccepted) and not(fullAccepted)),idle})
 run emptyCandidateCannotAcceptTest = init.then(observeEmpty).then(quit).then(all {assert(not(backendAccepted) and invariant),idle})
 run partialNormalCleanupIsNotFullWorkloadTest = init.then(observeExact).then(acceptBackend).then(quit).then(all {assert(normalQuit and not(fullAccepted) and invariant),idle})
 run serviceWithoutSnapshotIsNotFullTest = init.then(observeExact).then(acceptBackend).then(registerService).then(quit).then(all {assert(not(fullAccepted) and invariant),idle})
 run exactBackendGenuineFullWorkloadTest = init.then(observeExact).then(acceptBackend).then(registerService).then(genuineSnapshot).then(quit).then(acceptFull).then(all {assert(fullAccepted and invariant),idle})
}
