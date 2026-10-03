module naive_max_pin_counterexamples {
 import max_pin.* from "./max_pin"
 action legacyForcedFloat=s'={...s,lastNative:true,lastOwner:1,lastBefore:s.windows,lastFocus:s.focus,
   windows:s.windows.put(1,{...s.windows.get(1),floating:true,pinned:true,maxOrigin:true})}
 action emulatedMaxRectangle=s'={...s,lastNative:true,lastOwner:1,lastBefore:s.windows,lastFocus:s.focus,
   windows:s.windows.put(1,{...s.windows.get(1),mode:0,pinned:true,maxOrigin:true})}
 action copiedChildIntent=s'={...s,lastNative:true,lastOwner:1,lastBefore:s.windows,lastFocus:s.focus,
   windows:s.windows.put(1,{...s.windows.get(1),pinned:true,maxOrigin:true}).put(3,{...s.windows.get(3),pinned:true})}
 action coveringMembershipLoss=s'={...s,lastNative:true,lastOwner:1,lastBefore:s.windows,lastFocus:s.focus,
   windows:s.windows.put(1,{...s.windows.get(1),pinned:true,maxOrigin:true}).put(2,{...s.windows.get(2),mode:0})}
 run forcedFloatBreaksNativePinTest=init.then(legacyForcedFloat).then(check(not(pinProjection)))
 run resizeImitationLosesNativeModeTest=init.then(emulatedMaxRectangle).then(check(not(pinProjection)))
 run copiedChildBitBreaksIndependentIntentTest=init.then(copiedChildIntent).then(check(not(pinProjection)))
 run singleCoveringModeBreaksPeerTest=init.then(coveringMembershipLoss).then(check(not(pinProjection)))
}
