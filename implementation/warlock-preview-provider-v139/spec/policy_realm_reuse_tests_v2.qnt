module policy_realm_reuse_tests_v2 {
 import policy_realm_reuse_v2.* from "./policy_realm_reuse_v2"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 action settle=fire(Acquire).then(fire(Issue)).then(fire(Dispatch)).then(fire(Confirm)).then(fire(Terminal))
 run inputCustodyPreventsRetirement=init.then(fire(Retain)).then(fire(Retire)).then(check(not(s.closed) and s.inputs==1 and s.code==1))
 run physicalDutyPreventsReplacement=init.then(fire(Acquire)).then(fire(Retire)).then(fire(Reopen)).then(check(s.epoch==1 and s.duty and s.proposal and not(s.closed)))
 run independentConfirmationRemainsMandatory=init.then(fire(Acquire)).then(fire(Issue)).then(fire(Dispatch)).then(fire(Terminal)).then(fire(Retire)).then(check(s.confirmation and s.duty and not(s.closed)))
 run strictClosePreservesPolicy=init.then(settle).then(fire(Retire)).then(check(s.closed and s.policy==1 and s.epoch==1))
 run laterEpochReusesPolicy=init.then(settle).then(fire(Retire)).then(fire(Reopen)).then(check(s.epoch==2 and s.policy==1 and not(s.closed)))
 run permanentChronologySurvivesReplacement=init.then(fire(Permanent)).then(settle).then(fire(Retire)).then(fire(Reopen)).then(check(s.permanent and s.epoch==2 and s.policy==1))
 run staleAndForeignCannotTransfer=init.then(fire(Retire)).then(fire(OldEpoch)).then(fire(ForeignBinding)).then(check(s.closed and s.epoch==1 and s.policy==1 and s.code==1))
 run unknownCannotRetireOrReopen=init.then(fire(Acquire)).then(fire(Unknown)).then(fire(Retire)).then(fire(Reopen)).then(check(s.uncertain and s.duty and s.proposal and s.epoch==1 and not(s.closed)))
}

