module concrete_current_error_scope {
 import async_error_scope.* from "./async_error_scope"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run actualLegacyOldCancellation=init.then(finish(oldScope,false,false)).then(check(s.failed==true and s.stale==false and s.artifact==false and s.finished and s.nativeOwned and s.policy==1))
 run actualFixedOldCancellation=init.then(finish(oldScope,false,true)).then(check(s.failed==false and s.stale==true and s.artifact==false and s.finished and s.nativeOwned and s.policy==1))
 run actualCurrentCancellation=init.then(finish(currentScope,false,true)).then(check(s.failed==true and s.stale==false and s.artifact==false and s.finished and s.nativeOwned and s.policy==1))
 run actualCurrentSuccess=init.then(finish(currentScope,true,true)).then(check(s.failed==false and s.stale==false and s.artifact==true and s.finished and s.nativeOwned and s.policy==1))
}
