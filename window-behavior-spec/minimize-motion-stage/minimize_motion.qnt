/** Snapshot motion has no authority to resize a native window. Only the latest
 * identity-bound request may hide/reveal it. Restore commits at the endpoint;
 * watchdog/reload and reduced motion commit the latest intent immediately. */
module minimize_motion {
  type Event = Minimize | Restore | Activate | Defocus | OtherDesktop | Ready(int) | Finish(int) | Watchdog | Reduce | Close | Reuse | Reload
  type State = {live:bool,focused:bool,desktop:int,homeDesktop:int,identity:int,epoch:int,intent:bool,minimized:bool,
    overlay:bool,ready:bool,reduced:bool,nativeRect:int,savedRect:int,
    stale:bool,beforeMinimized:bool,beforeRect:int}
  var s:State
  action init=s'={live:true,focused:true,desktop:2,homeDesktop:2,identity:1,epoch:0,intent:false,minimized:false,
    overlay:false,ready:false,reduced:false,nativeRect:42,savedRect:42,
    stale:false,beforeMinimized:false,beforeRect:42}
  action fire(e:Event):bool={
    val b={...s,stale:false,beforeMinimized:s.minimized,beforeRect:s.nativeRect}
    s'=match e {
      | Minimize => if(not(s.live))b else {...b,epoch:s.epoch+1,intent:true,
          minimized:if(s.reduced)true else s.minimized,overlay:not(s.reduced),ready:false}
      | Restore => if(not(s.live))b else {...b,desktop:s.homeDesktop,epoch:s.epoch+1,intent:false,
          minimized:if(s.reduced)false else s.minimized,overlay:not(s.reduced),ready:false}
      | Activate => if(not(s.live))b else {
          val intent=if(s.overlay)not(s.intent) else s.focused and not(s.minimized)
          {...b,desktop:if(intent)s.desktop else s.homeDesktop,epoch:s.epoch+1,intent:intent,minimized:if(s.reduced)intent else s.minimized,
            focused:if(s.reduced)not(intent) else s.focused,overlay:not(s.reduced),ready:false}
        }
      | Defocus => {...b,focused:false}
      | OtherDesktop => {...b,desktop:1,overlay:false,ready:false}
      | Ready(epoch) => if(not(s.live) or epoch!=s.epoch or not(s.overlay)) {...b,stale:true}
          else {...b,ready:true,minimized:if(s.intent)true else s.minimized,focused:if(s.intent)false else s.focused}
      | Finish(epoch) => if(not(s.live) or epoch!=s.epoch) {...b,stale:true}
          else {...b,minimized:s.intent,focused:not(s.intent),overlay:false,ready:false}
      | Watchdog => if(not(s.live))b else {...b,minimized:s.intent,focused:not(s.intent),overlay:false,ready:false,epoch:s.epoch+1}
      | Reduce => {...b,reduced:true,minimized:if(s.live)s.intent else s.minimized,overlay:false,ready:false,epoch:s.epoch+1}
      | Reload => if(not(s.live))b else {...b,minimized:s.intent,focused:not(s.intent),overlay:false,ready:false,epoch:s.epoch+1}
      | Close => {...b,live:false,overlay:false,ready:false,epoch:s.epoch+1}
      | Reuse => if(s.live)b else {...b,live:true,focused:true,identity:s.identity+1,epoch:s.epoch+1,
          intent:false,minimized:false,overlay:false,ready:false,nativeRect:73,savedRect:73}
    }
  }
  action step={nondet e=Set(Minimize,Restore,Activate,Defocus,OtherDesktop,Ready(s.epoch),Ready(s.epoch-1),Finish(s.epoch),Finish(s.epoch-1),Watchdog,Reduce,Close,Reuse,Reload).oneOf();fire(e)}
  val geometryPreserved=s.nativeRect==s.savedRect
  val staleCannotCommit=s.stale implies (s.minimized==s.beforeMinimized and s.nativeRect==s.beforeRect)
  val noDeadOverlay=not(s.live) implies not(s.overlay)
  val reducedSettled=(s.live and s.reduced) implies (not(s.overlay) and s.minimized==s.intent)
  val destinationBeforeExpansion=(s.overlay and not(s.intent)) implies s.desktop==s.homeDesktop
  val allProps=destinationBeforeExpansion and geometryPreserved and staleCannotCommit and noDeadOverlay and reducedSettled
}
