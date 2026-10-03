module drag_relay_test {
  import drag_relay.* from "./drag_relay"
  run lateMoveCannotReviveCancelledDragTest=init.then(fire(New({active:true,id:1}))).then(fire(New({active:false,id:0}))).then(fire(Stale({active:true,id:1}))).then(all{assert(not(s.active) and s.target==0),fire(Watchdog)})
  run oldLeaveCannotCancelNewHoverTest=init.then(fire(New({active:true,id:2}))).then(fire(Stale({active:false,id:0}))).then(all{assert(s.active and s.target==2),fire(Watchdog)})
  run watchdogClearsLostReleaseTest=init.then(fire(New({active:true,id:1}))).then(fire(Watchdog)).then(all{assert(not(s.active) and s.target==0),fire(New({active:true,id:2}))}).then(all{assert(s.active and s.target==2),fire(Watchdog)})
}
