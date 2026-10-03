module actor_disposal {
  type Event = NativeStart | NativePhysicalGone | ExactSemanticReturn
    | OtherNativeStart | Fault | MissingInventory | RendererDrain | Dispose
  var nativePending: bool
  var otherNativePending: bool
  var physicalGone: bool
  var faulted: bool
  var completeInventory: bool
  var rendererLive: bool
  var disposed: bool
  var disposalAuthorized: bool
  action init = all {nativePending'=false,otherNativePending'=false,physicalGone'=false,faulted'=false,
    completeInventory'=true,rendererLive'=true,disposed'=false,disposalAuthorized'=false}
  val authority = not(nativePending) and not(faulted) and completeInventory
  action fire(e: Event): bool = all {
    otherNativePending' = (otherNativePending or e == OtherNativeStart),
    nativePending' = match e {
      | NativeStart => if(not(disposed) and not(faulted)) true else nativePending
      | ExactSemanticReturn => if(physicalGone and not(faulted) and completeInventory) false else nativePending
      | _ => nativePending },
    physicalGone' = match e {| NativeStart => false | NativePhysicalGone => true | _ => physicalGone},
    faulted' = (faulted or e == Fault),
    completeInventory' = (completeInventory and e != MissingInventory),
    rendererLive' = if(e == RendererDrain and authority) false else rendererLive,
    disposed' = (disposed or (e == Dispose and authority and not(rendererLive))),
    disposalAuthorized' = (disposalAuthorized or (e == Dispose and authority and not(rendererLive)))
  }
  action step = nondet e = Set(NativeStart,NativePhysicalGone,ExactSemanticReturn,
    OtherNativeStart,Fault,MissingInventory,RendererDrain,Dispose).oneOf(); fire(e)
  val allProps = disposed implies (disposalAuthorized and not(rendererLive) and not(nativePending))
}
