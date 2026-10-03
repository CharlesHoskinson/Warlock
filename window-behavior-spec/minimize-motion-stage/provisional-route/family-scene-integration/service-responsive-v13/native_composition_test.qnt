module native_composition_test {
 import native_composition.* from "./native_composition"
 action check(p:bool):bool=all{assert(p),s'=s}
 run wrongSessionCannotLaunchActorTest=init.then(fire(Proof(true))).then(fire(Seal)).then(fire(Launch)).then(check(not(s.launched)))
 run wrongMaterialCannotLaunchActorTest=init.then(fire(Select(true))).then(fire(Proof(false))).then(fire(Seal)).then(fire(Launch)).then(check(not(s.launched)))
 run sealedBytesSurviveSourceReplacementTest=init.then(fire(Select(true))).then(fire(Proof(true))).then(fire(Seal)).then(fire(ReplacePath)).then(fire(EditSource)).then(fire(Launch)).then(check(s.launched and s.sealed))
 run lostResponseDoesNotRetryFallbackTest=init.then(fire(Select(true))).then(fire(Proof(true))).then(fire(Seal)).then(fire(Launch)).then(fire(Send)).then(fire(Disconnect)).then(fire(RetryFallback)).then(check(s.unknown and not(s.effect)))
}
