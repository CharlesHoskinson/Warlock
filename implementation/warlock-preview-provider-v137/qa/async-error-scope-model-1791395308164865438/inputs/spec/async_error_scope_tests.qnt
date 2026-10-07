module async_error_scope_tests {
 import async_error_scope.* from "./async_error_scope"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run legacyOldErrorPoisonsCurrent=init.then(finish(oldScope,false,false)).then(check(s.failed and not(s.stale) and s.nativeOwned))
 run oldErrorCannotFailCurrent=init.then(finish(oldScope,false,true)).then(check(s.stale and not(s.failed) and not(s.artifact)))
 run oldSuccessStillRejected=init.then(finish(oldScope,true,true)).then(check(s.stale and not(s.failed) and not(s.artifact)))
 run currentFailureStillFailsClosed=init.then(finish(currentScope,false,true)).then(check(s.failed and not(s.stale) and not(s.artifact) and s.nativeOwned))
 run currentSuccessCanWrite=init.then(finish(currentScope,true,true)).then(check(s.artifact and not(s.failed) and not(s.stale)))
 run replacedViewRejectsError=init.then(finish({...currentScope,view:1},false,true)).then(check(s.stale and not(s.failed)))
 run laterEpochRejectsError=init.then(finish({...currentScope,epoch:1},false,true)).then(check(s.stale and not(s.failed)))
 run laterNavigationRejectsError=init.then(finish({...currentScope,navigation:1},false,true)).then(check(s.stale and not(s.failed)))
 run newProjectionRejectsError=init.then(finish({...currentScope,projection:1},false,true)).then(check(s.stale and not(s.failed)))
 run noDuplicateCompletionAuthority=init.then(finish(oldScope,false,true)).then(finish(currentScope,true,true)).then(check(s.stale and not(s.artifact) and s.nativeOwned and s.policy==1))
}
