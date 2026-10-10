/** ELM-UX-021: current native ownership must precede shell interaction.
 * PointerOwnership.blocked/receive: epochs are opaque, serials ordered within
 * one binding; stale snapshots cannot open the gate. Native gesture lifecycle,
 * Wayland geometry/device ownership and delivery latency need real recordings.
 * Begin/release observations are atomic here; native effect admission continues
 * to check its actual controller independently of this frontend observation.
 */
module pointer_readiness {
  type Event = ObserveIdle | Begin | Release | Rebind | Stale | Shell
  var s: {binding:int,observed:int,serial:int,active:bool,opened:bool,last:str}
  pure def permits(v:{binding:int,observed:int,serial:int,active:bool,opened:bool,last:str}):bool = v.binding==v.observed and not(v.active)
  action init = s'={binding:1,observed:0,serial:0,active:false,opened:false,last:"init"}
  action fire(e:Event):bool = {
    s'=match e {
      | ObserveIdle => {...s,observed:s.binding,serial:s.serial+1,active:false,last:"idle"}
      | Begin => {...s,observed:s.binding,serial:s.serial+1,active:true,opened:false,last:"begin"}
      | Release => {...s,observed:s.binding,serial:s.serial+1,active:false,last:"release"}
      | Rebind => {...s,binding:s.binding+1,opened:false,last:"rebind"}
      | Stale => {...s,last:"stale"}
      | Shell => {...s,opened:permits(s),last:"shell"}
    }
  }
  pure val EVENTS=Set(ObserveIdle,Begin,Release,Rebind,Stale,Shell)
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val safety=(s.opened implies permits(s)) and (s.binding!=s.observed implies not(permits(s)))
  val initializedBlocked=s.last=="shell" and s.observed==0 and not(s.opened)
  val idleReached=s.last=="idle" and permits(s)
  val activeBlocked=s.last=="begin" and not(permits(s)) and not(s.opened)
  val releasedPermits=s.last=="release" and permits(s) and not(s.opened)
  val rebindBlocked=s.last=="rebind" and not(permits(s)) and not(s.opened)
  val staleReached=s.last=="stale" and s.binding!=s.observed and not(permits(s))
  val freshShellReached=s.last=="shell" and s.opened and permits(s)
}
