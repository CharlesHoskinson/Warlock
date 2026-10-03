module capability_probe {
  type Event = EvConstruct(int) | EvHold | EvRelease | EvDirty | EvClean | EvNegotiate | EvProbe
    | EvReclaim | EvReplay | EvOwnerEpoch | EvExistingProbe | EvFail | EvUnexpectedPolicies | EvArm | EvArmUnknown | EvArmDenied | EvUnsupported
  var fresh:bool
  var owned:bool
  var held:bool
  var debt:bool
  var phase:int
  var available:bool
  var selected:bool
  var refused:bool
  action init=all {fresh'=false,owned'=false,held'=false,debt'=false,phase'=0,
    available'=false,selected'=false,refused'=false}
  action fire(e:Event):bool={
    val construction=e==EvConstruct(1) and phase==0 and not(held) and not(debt)
    val permitted=e==EvNegotiate and fresh and owned and not(held) and not(debt) and not(selected) and phase==1
    all {
      fresh'=if(construction) true else if(e==EvOwnerEpoch or (e==EvReclaim and phase==3)) false else fresh,
      owned'=if(construction or (e==EvReclaim and phase==3)) true
        else if(permitted) false else owned,
      held'=if(e==EvHold and selected) true else if(e==EvRelease) false else held,
      debt'=if(e==EvDirty and selected) true else if(e==EvClean) false else debt,
      phase'=if(construction) 1 else if(permitted) 2
        else if((e==EvProbe or e==EvFail or e==EvUnsupported) and phase==2 and not(owned)) 3
        else if(e==EvReclaim and phase==3) 4 else if((e==EvArm or e==EvArmUnknown) and phase==4 and owned and available) 5 else if(e==EvOwnerEpoch) (if(phase==2 or phase==3) 3 else 0) else phase,
      available'=if(e==EvProbe and phase==2 and not(owned)) true else if(e==EvOwnerEpoch or ((e==EvFail or e==EvUnsupported) and phase==2) or (e==EvArmDenied and phase==4)) false else available,
      selected'=if((e==EvReplay and phase==5 and owned and available) or (e==EvUnexpectedPolicies and phase==1)) true else if(e==EvOwnerEpoch) false else selected,
      refused'=(e==EvNegotiate and not(permitted))
    }
  }
  pure val EVENTS=Set(EvConstruct(1),EvHold,EvRelease,EvDirty,EvClean,EvNegotiate,EvProbe,EvReclaim,EvReplay,EvOwnerEpoch,EvExistingProbe,EvFail,EvUnexpectedPolicies,EvArm,EvArmUnknown,EvArmDenied,EvUnsupported)
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val allProps=(phase==2 implies not(owned) and not(held) and not(debt) and not(selected))
    and (phase==3 implies not(owned))
    and (selected implies owned and (phase==5 or phase==1))
}
