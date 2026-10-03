module refusal_observation {
  var calls: int
  var ok: bool
  var error: int
  var accepted: bool
  var policy: int
  var nonce: int
  action init = all { calls'=0, ok'=true, error'=0, accepted'=false, policy'=7, nonce'=2 }
  action native = {
    nondet observedError = Set(0,1,2).oneOf()
    all { calls==0, calls'=1, ok'=(observedError==0), error'=observedError,
      accepted'=false, policy'=policy, nonce'=nonce }
  }
  action accept = all { calls==1, not(ok), error==1, accepted'=true,
    calls'=calls, ok'=ok, error'=error, policy'=policy, nonce'=nonce }
  action stutter = all { calls'=calls, ok'=ok, error'=error, accepted'=accepted, policy'=policy, nonce'=nonce }
  action step = any { native, accept, stutter }
  val invariant = all { policy==7, nonce==2, calls<=1,
    accepted implies all { calls==1, not(ok), error==1 } }
  run genuineExactNativeRefusalTest = init.then(all { calls'=1,ok'=false,error'=1,accepted'=false,policy'=policy,nonce'=nonce })
    .then(accept).then(all { assert(accepted and invariant),stutter })
  run genericErrorCannotAcceptTest = init.then(all { calls'=1,ok'=false,error'=2,accepted'=false,policy'=policy,nonce'=nonce })
    .then(all { assert(not(accepted) and error!=1 and invariant),stutter })
  run nativeSuccessCannotAcceptRefusalTest = init.then(all { calls'=1,ok'=true,error'=0,accepted'=false,policy'=policy,nonce'=nonce })
    .then(all { assert(not(accepted) and ok and invariant),stutter })
  run refusalPreservesNoncePolicyTest = init.then(native).then(all { assert(policy==7 and nonce==2 and calls==1),stutter })
}
