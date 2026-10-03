module process_observation_test {
 import process_observation.* from "./process_observation"
 action check(p:bool):bool=all{assert(p),s'=s}
 run sameExactLiveTest=registered.then(observe(0,0)).then(terminal(true)).then(accept).then(check(s.live and not(s.accepted)))
 run reusedExactLifetimeGoneTest=registered.then(observe(1,0)).then(terminal(true)).then(accept).then(check(s.accepted))
 run selectedEnoentGoneTest=registered.then(observe(2,2)).then(terminal(true)).then(accept).then(check(s.accepted))
 run selectedEsrchGoneTest=registered.then(observe(2,3)).then(terminal(true)).then(accept).then(check(s.accepted))
 run unknownErrnoRefusesTest=registered.then(observe(2,99)).then(terminal(true)).then(accept).then(check(s.observationRefused and not(s.accepted)))
 run permissionErrorRefusesTest=registered.then(observe(2,13)).then(terminal(true)).then(accept).then(check(s.observationRefused and not(s.accepted)))
 run ioErrorRefusesTest=registered.then(observe(2,5)).then(terminal(true)).then(accept).then(check(s.observationRefused and not(s.accepted)))
 run unknownMalformedIdentityRefusesTest=registered.then(observe(3,0)).then(terminal(true)).then(accept).then(check(s.observationRefused and not(s.accepted)))
 run freshRegistrationEsrchStrictTest=init.then(register(2,3)).then(check(s.registrationRefused and not(s.registered)))
 run freshRegistrationEnoentStrictTest=init.then(register(2,2)).then(check(s.registrationRefused and not(s.registered)))
 run unregisteredObservationCannotAuthorizeTest=init.then(observe(2,3)).then(terminal(true)).then(accept).then(check(not(s.accepted)))
 run disappearanceIsNotNormalExitTest=registered.then(observe(2,3)).then(terminal(false)).then(accept).then(check(not(s.accepted)))
 run missingTerminalCannotAuthorizeTest=registered.then(observe(2,3)).then(accept).then(check(not(s.accepted)))
 run duplicateTerminalCannotAuthorizeTest=registered.then(observe(2,3)).then(terminal(true)).then(terminal(true)).then(accept).then(check(not(s.accepted)))
 run priorUnknownCannotBeErasedTest=registered.then(observe(2,5)).then(observe(2,3)).then(terminal(true)).then(accept).then(check(not(s.accepted)))
}
