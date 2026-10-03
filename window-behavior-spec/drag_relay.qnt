/** Monotonic drag relay and watchdog: stale packets cannot revive hover. */
module drag_relay {
  type Event = New({active:bool,id:int}) | Stale({active:bool,id:int}) | Watchdog
  var s:{stamp:int,active:bool,target:int,oldActive:bool,oldTarget:int,ignored:bool}
  action init=s'={stamp:0,active:false,target:0,oldActive:false,oldTarget:0,ignored:false}
  action message(active:bool,target:int,stamp:int):bool=s'=
    if(stamp<=s.stamp) {...s,oldActive:s.active,oldTarget:s.target,ignored:true}
    else {stamp:stamp,active:active,target:if(active) target else 0,oldActive:s.active,oldTarget:s.target,ignored:false}
  action fire(e:Event):bool=match e {
    | New(data) => message(data.active,data.id,s.stamp+1)
    | Stale(data) => message(data.active,data.id,s.stamp)
    | Watchdog => message(false,0,s.stamp+1)
  }
  pure val EVENTS=Set(New({active:true,id:1}),New({active:true,id:2}),New({active:true,id:0}),New({active:false,id:0}),Stale({active:true,id:1}),Stale({active:true,id:2}),Stale({active:false,id:0}),Watchdog)
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val allProps=(s.active or s.target==0) and (not(s.ignored) or (s.active==s.oldActive and s.target==s.oldTarget))
}
