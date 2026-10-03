/** Native endpoint authority contract, replayed against the installed controller.
 * Rendering is supplied by a deterministic adapter; geometry, pin, stale tokens,
 * readiness, crash recovery and address reuse are checked at every transition.
 */
module minimize_commit {
  type Event = Minimize | Restore | Activate | Ready(int) | Finish(int) |
    Watchdog | Reduce | EnableMotion | Reload | Close | Reuse |
    ReuseBeforeReady | PIDChangeBeforeReady
  type State = {live:bool,identity:int,pid:int,epoch:int,pending:bool,ready:bool,
    intent:bool,minimized:bool,reduced:bool,rect:int,savedRect:int,pinned:bool,
    stale:bool,beforeMinimized:bool}
  var s:State
  var lastEvent:Event
  action init=all {
    s'={live:true,identity:1,pid:101,epoch:0,pending:false,ready:false,intent:false,
      minimized:false,reduced:false,rect:42,savedRect:42,pinned:true,
      stale:false,beforeMinimized:false},
    lastEvent'=Reload
  }
  def allowed(e:Event):bool=match e {
    | Minimize => s.live and (s.pending or not(s.minimized))
    | Restore => s.live and (s.pending or s.minimized)
    | Activate => s.live
    | Reuse => not(s.live)
    | ReuseBeforeReady => s.live and s.pending and not(s.ready)
    | PIDChangeBeforeReady => s.live and s.pending and not(s.ready)
    | _ => true
  }
  action fire(e:Event):bool=all {
    allowed(e),
    lastEvent'=e,
    s'={
      val b={...s,stale:false,beforeMinimized:s.minimized}
      match e {
        | Minimize => {...b,epoch:s.epoch+1,intent:true,pending:not(s.reduced),
            ready:false,minimized:if(s.reduced)true else s.minimized}
        | Restore => {...b,epoch:s.epoch+1,intent:false,pending:not(s.reduced),
            ready:false,minimized:if(s.reduced)false else s.minimized}
        | Activate => {
            val target=if(s.pending)not(s.intent) else not(s.minimized)
            {...b,epoch:s.epoch+1,intent:target,pending:not(s.reduced),ready:false,
              minimized:if(s.reduced)target else s.minimized}
          }
        | Ready(epoch) => if(s.live and s.pending and not(s.ready) and epoch==s.epoch)
            {...b,ready:true,minimized:if(s.intent)true else s.minimized}
          else {...b,stale:true}
        | Finish(epoch) => if(s.live and s.pending and epoch==s.epoch)
            {...b,minimized:s.intent,pending:false,ready:false}
          else {...b,stale:true}
        | Watchdog => if(s.live and s.pending)
            {...b,minimized:s.intent,pending:false,ready:false}
          else b
        | Reload => if(s.live and s.pending)
            {...b,minimized:s.intent,pending:false,ready:false}
          else b
        | Reduce => {...b,reduced:true,pending:false,ready:false,
            minimized:if(s.live and s.pending)s.intent else s.minimized}
        | EnableMotion => {...b,reduced:false}
        | Close => {...b,live:false,pending:false,ready:false}
        | Reuse => {...b,live:true,identity:s.identity+1,pid:s.pid+1,pending:false,ready:false,
            intent:false,minimized:false,rect:73,savedRect:73}
        | ReuseBeforeReady => {...b,identity:s.identity+1,pending:false,ready:false,
            intent:false,minimized:false,rect:73,savedRect:73}
        | PIDChangeBeforeReady => {...b,pid:s.pid+1,pending:false,ready:false,
            intent:false,minimized:false,rect:73,savedRect:73}
      }
    }
  }
  action step={
    nondet e=Set(Minimize,Restore,Activate,Ready(s.epoch),Ready(s.epoch-1),
      Finish(s.epoch),Finish(s.epoch-1),Watchdog,Reduce,EnableMotion,Reload,Close,Reuse,
      ReuseBeforeReady,PIDChangeBeforeReady)
      .filter(allowed).oneOf()
    fire(e)
  }
  val allProps=s.rect==s.savedRect and s.pinned and
    (s.stale implies s.minimized==s.beforeMinimized) and
    (not(s.live) implies not(s.pending)) and
    (s.reduced implies not(s.pending)) and
    (s.ready implies s.pending)
}
