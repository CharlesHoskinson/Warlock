module readonly_policy_lifetime_tests {
 import readonly_policy_lifetime.* from "./readonly_policy_lifetime"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run wrongThreadCannotInvoke=init.then(fire(Grant)).then(fire(WrongThreadInvoke)).then(check(s.held and not(s.closed) and s.code==2))
 run wrongThreadCannotDestroy=init.then(fire(WrongThreadClose)).then(check(s.held and s.code==2))
 run malformedInputCannotChangeState=init.then(fire(Grant)).then(fire(Malformed)).then(check(s.controlled and not(s.closed) and s.code==1))
 run openRealmCannotDestroy=init.then(fire(Grant)).then(fire(Destroy)).then(check(s.held and s.code==5))
 run foreignCloseCannotAuthorizeDestroy=init.then(fire(Grant)).then(fire(ForeignClose)).then(fire(Destroy)).then(check(s.held and not(s.closed) and s.code==5))
 run originalThreadRemainsUsable=init.then(fire(Grant)).then(fire(WrongThreadInvoke)).then(fire(Status)).then(check(s.held and s.code==0))
 run trustedCloseThenNormalDestroy=init.then(fire(Grant)).then(fire(TrustedClose)).then(fire(Destroy)).then(check(not(s.held) and s.closed and s.code==0))
 run emptyUncontrolledOwnerCanDestroy=init.then(fire(Destroy)).then(check(not(s.held) and not(s.controlled) and s.code==0))
 run absentAuthorityRefusesReadonly=init.then(fire(ReadVisual)).then(check(s.held and not(s.controlled) and s.code==6))
 run openAuthorityReadonlyKeepsModel=init.then(fire(Grant)).then(fire(ReadVisual)).then(check(s.held and s.controlled and not(s.closed) and s.code==0))
 run closedAuthorityRefusesReadonly=init.then(fire(Grant)).then(fire(TrustedClose)).then(fire(ReadVisual)).then(check(s.held and s.closed and s.code==6))
 run foreignThreadRefusesReadonly=init.then(fire(Grant)).then(fire(ForeignRead)).then(check(s.held and s.controlled and not(s.closed) and s.code==2))
 run refusedInputRetainsReadableProjection=init.then(fire(Grant)).then(fire(Malformed)).then(fire(ReadVisual)).then(check(s.held and s.controlled and not(s.closed) and s.code==0))
 run destroyedOwnerCannotRead=init.then(fire(Destroy)).then(fire(ReadVisual)).then(check(not(s.held) and s.code==1))
}
