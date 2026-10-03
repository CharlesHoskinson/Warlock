module scene_tests {
  import scene.* from "./gpu-lease-survives"
  run minimizedFullscreenExcludedTest = init.then(fire(Fullscreen(2))).then(fire(Minimize(2))).then(all {assert(paintTop(s)==1 and inputTop(s)==1 and allProps),fire(Activate)})
  run inactivePinnedExcludedTest = init.then(fire(Pin(2))).then(fire(Inactive(2))).then(all {assert(paintTop(s)==1 and allProps),fire(Activate)})
  run maximizedStaysOrdinaryTest = init.then(fire(Maximize(1))).then(all {assert(band(s,1)==1 and paintTop(s)==2 and allProps),fire(Activate)})
  run pinnedAboveFullscreenPolicyTest = init.then(fire(Fullscreen(2))).then(fire(Pin(1))).then(all {assert(paintTop(s)==1 and allProps),fire(Activate)})
  run transparentPaintInputDivergenceTest = init.then(fire(Transparent(2))).then(all {assert(paintTop(s)==2 and inputTop(s)==1 and allProps),fire(Activate)}).then(all {assert(s.focus==1 and allProps),fire(Capture)})
  run inertRestoreProxyTest = init.then(fire(Capture)).then(fire(Minimize(1))).then(fire(RestoreBegin)).then(all {assert(s.proxy and not(proxyHit(s)) and s.minimized.contains(1) and allProps),fire(Activate)})
  run atomicLiveHandoffTest = init.then(fire(Capture)).then(fire(Minimize(1))).then(fire(RestoreBegin)).then(fire(LiveReady)).then(fire(Handoff)).then(all {assert(not(s.proxy) and not(s.minimized.contains(1)) and allProps),fire(Activate)})
  run prematureHandoffRefusedTest = init.then(fire(Capture)).then(fire(Minimize(1))).then(fire(RestoreBegin)).then(fire(Handoff)).then(all {assert(s.proxy and s.minimized.contains(1) and allProps),fire(Lock)})
  run lockRevokesPublicationTest = init.then(fire(Capture)).then(fire(Activate)).then(fire(Lock)).then(all {assert(not(s.lease) and s.focus==0 and paintTop(s)==0 and allProps),fire(Capture)}).then(all {assert(not(s.lease) and allProps),fire(Unlock)}).then(all {assert(not(s.lease) and allProps),fire(Capture)})
  run gpuLossRevokesLeaseTest = init.then(fire(Capture)).then(fire(DeviceLoss)).then(all {assert(not(s.lease) and allProps),fire(DeviceRecover)}).then(all {assert(not(s.lease) and allProps),fire(Capture)})
  run lockCancelsRestoreProxyTest = init.then(fire(Capture)).then(fire(Minimize(1))).then(fire(RestoreBegin)).then(fire(LiveReady)).then(fire(Lock)).then(fire(Handoff)).then(all {assert(not(s.proxy) and s.minimized.contains(1) and not(s.lease) and allProps),fire(Unlock)})
}
