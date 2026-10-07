module native_policy_lifetime_tests {
 import native_policy_lifetime.* from "./native_policy_lifetime"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run wrongThreadCannotInvoke=init.then(fire(Grant)).then(fire(WrongThreadInvoke)).then(check(s.held and not(s.closed) and s.code==2))
 run wrongThreadCannotDestroy=init.then(fire(WrongThreadClose)).then(check(s.held and s.code==2))
 run malformedInputCannotChangeState=init.then(fire(Grant)).then(fire(Malformed)).then(check(s.controlled and not(s.closed) and s.code==1))
 run openRealmCannotDestroy=init.then(fire(Grant)).then(fire(Destroy)).then(check(s.held and s.code==5))
 run foreignCloseCannotAuthorizeDestroy=init.then(fire(Grant)).then(fire(ForeignClose)).then(fire(Destroy)).then(check(s.held and not(s.closed) and s.code==5))
 run originalThreadRemainsUsable=init.then(fire(Grant)).then(fire(WrongThreadInvoke)).then(fire(Status)).then(check(s.held and s.code==0))
 run trustedCloseThenNormalDestroy=init.then(fire(Grant)).then(fire(TrustedClose)).then(fire(Destroy)).then(check(not(s.held) and s.closed and s.code==0))
 run emptyUncontrolledOwnerCanDestroy=init.then(fire(Destroy)).then(check(not(s.held) and not(s.controlled) and s.code==0))
}
