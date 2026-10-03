module readback_attribution_test {
 import readback_attribution.* from "./readback_attribution"
 action check(p:bool):bool=all{assert(p),s'=s}
 run readMatchesCurrentDrawBeforeSwapTest=init.then(fire(Draw(1))).then(fire(Read(1))).then(check(s.readObserved and not(s.nativeAuthority)))
 run readAfterSwapIsNotCurrentBufferTest=init.then(fire(Draw(1))).then(fire(Swap(1))).then(fire(Read(1))).then(check(not(s.readObserved)))
 run staleSequenceReadCannotNameCurrentSceneTest=init.then(fire(Draw(1))).then(fire(Draw(2))).then(fire(Read(1))).then(check(not(s.readObserved)))
 run diagnosticPresentationNeverAuthorizesNativeTest=init.then(fire(Draw(1))).then(fire(Read(1))).then(fire(Swap(1))).then(fire(Presented(1))).then(check(not(s.nativeAuthority)))
}
