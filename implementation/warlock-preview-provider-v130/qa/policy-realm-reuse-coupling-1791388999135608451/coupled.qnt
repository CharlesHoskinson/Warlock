module coupled_realm_reuse {
 import policy_realm_reuse_v3.* from "./policy_realm_reuse_v3"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run actualTwoRealmCustody=init.then(fire(Acquire)).then(fire(Issue)).then(fire(Dispatch)).then(fire(Confirm)).then(check(s.epoch==1 and s.duty and not(s.closed))).then(fire(Permanent)).then(fire(Terminal)).then(fire(Retire)).then(check(s.epoch==1 and s.closed and s.permanent)).then(fire(OldEpoch)).then(fire(ForeignBinding)).then(check(s.epoch==1 and s.closed and s.permanent)).then(fire(Reopen)).then(check(s.epoch==2 and not(s.closed) and s.permanent and s.policy==1)).then(fire(Acquire)).then(fire(Issue)).then(fire(Dispatch)).then(fire(Confirm)).then(check(s.epoch==2 and s.duty and s.permanent)).then(fire(Terminal)).then(fire(Retire)).then(check(s.epoch==2 and s.closed and s.permanent and s.policy==1))
}
