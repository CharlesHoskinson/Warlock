module host_realm_lifecycle_tests {
 import host_realm_lifecycle.* from "./host_realm_lifecycle"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 action admitted=fire(OpenIntent).then(fire(DOMReady)).then(fire(Admit)).then(fire(Initialize)).then(fire(Apply))
 action retired=fire(ClosePopup).then(fire(Drain)).then(fire(Retire))
 run closeCannotSettleDuty=init.then(admitted).then(fire(ClosePopup)).then(fire(Retire)).then(check(s.duty and s.native and not(s.current) and not(s.retired)))
 run sameContextCannotInitializeTwice=init.then(admitted).then(fire(Initialize)).then(check(s.context==1 and s.epoch==1 and s.code==1))
 run oldViewCannotReplaceBeforeClose=init.then(admitted).then(fire(Replace)).then(check(s.context==1 and s.native and s.duty and s.code==1))
 run normalReopenKeepsPolicy=init.then(admitted).then(retired).then(fire(Replace)).then(admitted).then(check(s.epoch==2 and s.context==2 and s.policy==1 and s.current and not(s.reveal)))
 run pendingIntentKeepsLease=init.then(admitted).then(fire(ClosePopup)).then(fire(OpenIntent)).then(fire(Drain)).then(fire(Retire)).then(fire(Replace)).then(check(s.popup and s.lease==2 and not(s.dom) and s.policy==1 and s.context==2))
 run pendingIntentRequiresFreshDOM=init.then(admitted).then(fire(ClosePopup)).then(fire(OpenIntent)).then(fire(Drain)).then(fire(Retire)).then(fire(Replace)).then(fire(Admit)).then(check(s.epoch==1 and s.code==1 and not(s.native)))
 run pendingIntentThenFreshAdmission=init.then(admitted).then(fire(ClosePopup)).then(fire(OpenIntent)).then(fire(Drain)).then(fire(Retire)).then(fire(Replace)).then(fire(DOMReady)).then(fire(Admit)).then(fire(Initialize)).then(fire(Apply)).then(check(s.lease==2 and s.epoch==2 and s.context==2 and s.current))
 run oldCallbackHasNoAuthority=init.then(admitted).then(retired).then(fire(Replace)).then(admitted).then(fire(StaleCallback)).then(check(s.epoch==2 and s.context==2 and s.current and s.code==1 and not(s.reveal)))
 run unknownCannotRetireOrReplace=init.then(admitted).then(fire(ClosePopup)).then(fire(Unknown)).then(fire(Drain)).then(fire(Retire)).then(fire(Replace)).then(check(s.duty and s.native and s.uncertain and s.context==1 and s.epoch==1))
}
