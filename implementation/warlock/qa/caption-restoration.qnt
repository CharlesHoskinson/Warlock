/** UX-021 original caption fractional anchoring and terminal rollback.
 * One synchronous native controller, current opaque window incarnation and live
 * source space. Integer boxes abstract native doubles/configure constraints.
 * MAX/snap restoring saves the press-time box and mode before mutation. No
 * native device/lock/grab, tiled/group, source loss, AT or release proof.
 */
module caption_restoration {
  type Box={x:int,y:int,w:int,h:int}
  type State={current:int,alive:bool,owner:int,held:bool,geom:Box,ordinary:Box,placement:int,original:Box,originalPlacement:int,dx:int,anchor:int,last:str,ended:bool,ends:int,beforeEnds:int,beforeOwner:int}
  var s:State
  pure val NORMAL:Box={x:26,y:30,w:60,h:35}
  pure val MAX:Box={x:0,y:3,w:120,h:96}
  pure val SNAP:Box={x:0,y:3,w:80,h:96}
  action init=s'={current:1,alive:true,owner:0,held:false,geom:NORMAL,ordinary:NORMAL,placement:0,original:NORMAL,originalPlacement:0,dx:0,anchor:0,last:"init",ended:false,ends:0,beforeEnds:0,beforeOwner:0}
  type Event=Maximize | Snap | RestoreOrdinary | Press(int) | Motion(int) | Release | Cancel | Close | Reopen
  pure def canFire(state:State,e:Event):bool=match e {
    | Maximize=>state.alive and state.owner==0 and not(state.held) and state.placement==0
    | Snap=>state.alive and state.owner==0 and not(state.held) and state.placement==0
    | Press(dx)=>state.alive and state.owner==0 and not(state.held) and dx>=0 and dx<=state.geom.w
    | Motion(_)=>state.owner==state.current and state.alive and state.held
    | RestoreOrdinary=>state.alive and state.owner==0 and not(state.held) and state.placement==1
    | Close=>state.alive
    | Reopen=>not(state.alive)
    | _=>true
  }
  pure def apply(state:State,e:Event):State={
    val active=state.owner==state.current and state.alive
    val base={...state,ended:false,beforeEnds:state.ends,beforeOwner:state.owner}
    match e {
      | Maximize=>{...base,geom:MAX,ordinary:state.geom,placement:1,last:"maximize"}
      | Snap=>{...base,geom:SNAP,ordinary:state.geom,placement:2,last:"snap"}
      | RestoreOrdinary=>{...base,geom:state.ordinary,placement:0,last:"restoreOrdinary"}
      | Press(dx)=>{...base,owner:state.current,held:true,original:state.geom,originalPlacement:state.placement,dx:dx,anchor:dx*(if(state.placement!=0) state.ordinary.w else state.geom.w)/state.geom.w,last:"press"}
      | Motion(x)=>{...base,geom:{x:x-state.anchor,y:30,w:if(state.originalPlacement!=0) state.ordinary.w else state.original.w,h:if(state.originalPlacement!=0) state.ordinary.h else state.original.h},placement:0,last:"motion"}
      | Release=>{...base,owner:0,held:false,ends:state.ends+(if(active) 1 else 0),ended:active,last:"release"}
      | Cancel=>{...base,owner:0,geom:if(active) state.original else state.geom,placement:if(active) state.originalPlacement else state.placement,ends:state.ends+(if(active) 1 else 0),ended:active,last:"cancel"}
      | Close=>{...base,alive:false,owner:0,ends:state.ends+(if(active) 1 else 0),ended:active,last:"close"}
      | Reopen=>{...base,current:state.current+1,alive:true,geom:NORMAL,ordinary:NORMAL,placement:0,last:"reopen"}
    }
  }
  action fire(e:Event):bool=all{canFire(s,e),s'=apply(s,e)}
  pure val EVENTS=Set(Maximize,Snap,RestoreOrdinary,Press(10),Press(20),Press(30),Press(60),Motion(100),Motion(120),Release,Cancel,Close,Reopen)
  action step={nondet e=EVENTS.filter(e=>canFire(s,e)).oneOf();fire(e)}
  val maxAnchored=s.last=="motion" and s.originalPlacement==1 and s.geom.w==s.ordinary.w and s.anchor==s.dx*s.ordinary.w/s.original.w
  val snapAnchored=s.last=="motion" and s.originalPlacement==2 and s.geom.w==s.ordinary.w and s.anchor==s.dx*s.ordinary.w/s.original.w
  val maxCancel=s.last=="cancel" and s.ended and s.originalPlacement==1 and s.placement==1 and s.geom==s.original
  val snapCancel=s.last=="cancel" and s.ended and s.originalPlacement==2 and s.placement==2 and s.geom==s.original
  val releasedOrdinary=s.last=="release" and s.ended and s.placement==0
  val closeRetired=s.last=="close" and s.ended and s.owner==0
  val replacementIdle=s.last=="reopen" and s.current>1 and s.owner==0
  val ordinaryRestored=s.last=="restoreOrdinary" and s.geom==s.ordinary and s.placement==0
  val safety=(s.owner==0 or (s.owner==s.current and s.alive and s.held))
    and s.ends==s.beforeEnds+(if(s.ended) 1 else 0)
    and ((s.last=="cancel" and s.ended) implies s.geom==s.original and s.placement==s.originalPlacement)
    and (s.last=="restoreOrdinary" implies ordinaryRestored)
    and (s.last=="motion" implies s.placement==0 and s.geom.w==(if(s.originalPlacement!=0) s.ordinary.w else s.original.w) and s.anchor==s.dx*s.geom.w/s.original.w)
}
