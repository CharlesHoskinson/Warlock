module known_renderer_reload_tests {
 import known_renderer_reload.* from "./known_renderer_reload"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run legacyReloadBecomesUncertain=init.then(check(legacyReload(s).failed and legacyReload(s).unknown and legacyReload(s).owned))
 run reloadDoesNotSettleOriginalCustody=init.then(fire(Reload)).then(fire(StrictRetire)).then(fire(Replace)).then(check(s.owned and s.closing and not(s.replaced or s.initialized or s.failed)))
 run nativeSettlementPrecedesStrictReplacement=init.then(fire(Reload)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(check(s.closed and s.replaced and not(s.owned or s.initialized)))
 run freshDOMPrecedesAdmission=init.then(fire(Reload)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(fire(Admit)).then(check(s.epoch==1 and not(s.initialized)))
 run laterEpochKeepsPolicyAndLease=init.then(fire(Reload)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(fire(DOMReady)).then(fire(Admit)).then(fire(Capture)).then(check(s.epoch==2 and s.policy==1 and s.lease==1 and s.navigation==3 and s.snapshot==2 and s.initialized))
 run staleCallbackHasNoAuthority=init.then(fire(Reload)).then(fire(OldCallback)).then(check(s.owned and s.closing and not(s.initialized)))
 run laterIntentCannotCancelDrain=init.then(fire(Reload)).then(fire(LaterIntent)).then(fire(Reload)).then(check(s.owned and s.closing and s.navigation==3 and not(s.initialized)))
 run unknownPreventsReplacement=init.then(fire(Reload)).then(fire(Unknown)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(fire(DOMReady)).then(fire(Admit)).then(check(s.owned and s.unknown and s.epoch==1 and not(s.initialized or s.closed or s.replaced)))
 run currentFailureCannotRecoverAsSuccess=init.then(fire(Failure)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(check(s.failed and s.closed and not(s.replaced or s.initialized)))
}
