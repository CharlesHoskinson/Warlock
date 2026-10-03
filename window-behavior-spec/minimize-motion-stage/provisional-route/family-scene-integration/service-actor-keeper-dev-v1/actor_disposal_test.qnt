module actor_disposal_test {
  import actor_disposal.* from "./actor_disposal"
  action check(p: bool): bool = all {assert(p),nativePending'=nativePending,
    otherNativePending'=otherNativePending,physicalGone'=physicalGone,faulted'=faulted,completeInventory'=completeInventory,
    rendererLive'=rendererLive,disposed'=disposed,disposalAuthorized'=disposalAuthorized}
  run unresolvedNativeCannotDrainOrDisposeTest = init.then(fire(NativeStart))
    .then(fire(RendererDrain)).then(fire(Dispose))
    .then(check(rendererLive and not(disposed)))
  run physicalExitCannotReplaceSemanticDrainTest = init.then(fire(NativeStart))
    .then(fire(NativePhysicalGone)).then(fire(RendererDrain)).then(fire(Dispose))
    .then(check(rendererLive and not(disposed)))
  run actualReturnedNativeAllowsNormalRendererDrainTest = init.then(fire(NativeStart))
    .then(fire(NativePhysicalGone)).then(fire(ExactSemanticReturn))
    .then(fire(RendererDrain)).then(fire(Dispose))
    .then(check(not(rendererLive) and disposed and disposalAuthorized))
  run prematureSemanticReturnCannotAllowDisposalTest = init.then(fire(NativeStart))
    .then(fire(ExactSemanticReturn)).then(fire(RendererDrain)).then(fire(Dispose))
    .then(check(nativePending and rendererLive and not(disposed)))
  run faultKeepsRendererAndCapturesQuarantinedTest = init.then(fire(Fault))
    .then(fire(RendererDrain)).then(fire(Dispose))
    .then(check(rendererLive and not(disposed)))
  run missingInventoryKeepsCapturesQuarantinedTest = init.then(fire(MissingInventory))
    .then(fire(RendererDrain)).then(fire(Dispose))
    .then(check(rendererLive and not(disposed)))
  run liveRendererCannotBeDisposedTest = init.then(fire(Dispose))
    .then(check(rendererLive and not(disposed)))
  run idleHealthyRendererMayDrainAndDisposeTest = init.then(fire(RendererDrain))
    .then(fire(Dispose)).then(check(disposed and disposalAuthorized))
  run lateNativeStartRequiresFreshGuardAtActualDisposalTest = init
    .then(fire(RendererDrain)).then(fire(NativeStart)).then(fire(Dispose))
    .then(check(nativePending and not(disposed)))
  run disjointActorsPendingNativeWorkDoesNotPreventSelectedDisposalTest = init
    .then(fire(OtherNativeStart)).then(fire(RendererDrain)).then(fire(Dispose))
    .then(check(otherNativePending and disposed and allProps))
}
