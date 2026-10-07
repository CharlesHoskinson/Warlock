module concrete_known_reload {
 import known_renderer_reload.* from "./known_renderer_reload"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run actualLegacyUncertainReload=init.then(check(legacyReload(s).failed and legacyReload(s).unknown and legacyReload(s).owned))
 run actualKnownReloadQuarantine=init.then(fire(Reload)).then(check(s.closing and s.owned and not(s.initialized or s.failed)))
 run actualOriginalStrictClosedRealm=init.then(fire(Reload)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(check(s.closed and not(s.owned or s.initialized)))
 run actualSamePopupReplacement=init.then(fire(Reload)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(check(s.replaced and s.closed and s.navigation==3 and s.lease==1))
 run actualFreshDOMLaterEpoch=init.then(fire(Reload)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(fire(DOMReady)).then(fire(Admit)).then(check(s.epoch==2 and s.initialized and s.policy==1 and s.lease==1))
 run actualMonotonicSnapshot=init.then(fire(Reload)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(fire(DOMReady)).then(fire(Admit)).then(fire(Capture)).then(check(s.snapshot==2 and s.navigation==3 and s.epoch==2))
 run actualFinalStrictClose=init.then(fire(Reload)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(fire(DOMReady)).then(fire(Admit)).then(fire(Capture)).then(fire(Reload)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(check(s.closed and not(s.owned or s.initialized) and s.epoch==2))
}
