/** UX-021 terminal semantics, following unchanged caption_drag/native_drag.
 * Floating move/resize geometry is abstracted as integers. Native device,
 * fullscreen/tiled layout, snapped-caption restoration and output timing remain
 * separate. Existing native controller identity and synchronous end reason
 * map to owner/reason; no additional public state/ABI fields are required.
 */
module gesture_end {
  var s:{current:int,alive:bool,owner:int,held:bool,mode:str,geom:int,original:int,ends:int,drops:int,last:str,ended:bool,beforeOwner:int,beforeGeom:int,beforeEnds:int,beforeDrops:int,space:int,originalSpace:int,beforeSpace:int}
  action init=s'={current:1,alive:true,owner:0,held:false,mode:"idle",geom:10,original:10,ends:0,drops:0,last:"init",ended:false,beforeOwner:0,beforeGeom:10,beforeEnds:0,beforeDrops:0,space:1,originalSpace:1,beforeSpace:1}
  type Event=BeginMove | BeginResize | Motion | Release | EscapePress | EscapeRelease | CloseOwner | ClosePeer | Reopen
  action fire(e:Event):bool={
    val active=s.owner==s.current and s.alive
    val ready=s.alive and s.owner==0 and not(s.held)
    val base={...s,ended:false,beforeOwner:s.owner,beforeGeom:s.geom,beforeEnds:s.ends,beforeDrops:s.drops,beforeSpace:s.space}
    s'=match e {
      | BeginMove=>if(ready) {...base,owner:s.current,held:true,mode:"move",original:s.geom,originalSpace:s.space,last:"beginMove"} else {...base,last:"refusedBegin"}
      | BeginResize=>if(ready) {...base,owner:s.current,held:true,mode:"resize",original:s.geom,originalSpace:s.space,last:"beginResize"} else {...base,last:"refusedBegin"}
      | Motion=>{...base,geom:if(active) s.geom+3 else s.geom,space:if(active) 2 else s.space,last:"motion"}
      | Release=>{...base,owner:0,held:false,mode:"idle",ends:s.ends+if(active) 1 else 0,drops:s.drops+if(active) 1 else 0,ended:active,last:"release"}
      | EscapePress=>{...base,owner:0,mode:"idle",geom:if(active) s.original else s.geom,space:if(active) s.originalSpace else s.space,ends:s.ends+if(active) 1 else 0,ended:active,last:"cancel"}
      | EscapeRelease=>{...base,last:"escapeRelease"}
      | CloseOwner=>{...base,alive:false,owner:0,mode:"idle",ends:s.ends+if(active) 1 else 0,ended:active,last:"retire"}
      | ClosePeer=>{...base,last:"peerClose"}
      | Reopen=>if(not(s.alive)) {...base,current:s.current+1,alive:true,geom:99,space:1,last:"reopen"} else {...base,last:"duplicateOpen"}
    }
  }
  pure val EVENTS=Set(BeginMove,BeginResize,Motion,Release,EscapePress,EscapeRelease,CloseOwner,ClosePeer,Reopen)
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val moving=s.last=="motion" and s.mode=="move" and s.geom!=s.original
  val resizing=s.last=="motion" and s.mode=="resize" and s.geom!=s.original
  val cancelRestores=s.last=="cancel" and s.ended and s.geom==s.original and s.space==s.originalSpace and s.drops==s.beforeDrops
  val crossedCancel=cancelRestores and s.beforeSpace!=s.originalSpace
  val releaseCommits=s.last=="release" and s.ended and s.geom==s.beforeGeom and s.drops==s.beforeDrops+1
  val retireWithoutDrop=s.last=="retire" and s.ended and s.drops==s.beforeDrops and s.geom==s.beforeGeom
  val replacementIdle=s.last=="reopen" and s.current>1 and s.owner==0 and s.geom==99
  val duplicateEndIgnored=(s.last=="release" or s.last=="cancel") and s.beforeOwner==0 and not(s.ended) and s.ends==s.beforeEnds
  val peerKeepsOwner=s.last=="peerClose" and s.owner!=0 and s.owner==s.beforeOwner and s.ends==s.beforeEnds
  val safety=(s.owner==0 or (s.owner==s.current and s.alive and s.held)) and s.drops<=s.ends
    and s.ends==s.beforeEnds+(if(s.ended) 1 else 0)
    and ((s.last=="cancel" and s.ended) implies cancelRestores)
    and ((s.last=="retire" and s.ended) implies retireWithoutDrop)
    and (s.last=="escapeRelease" implies s.owner==s.beforeOwner and s.ends==s.beforeEnds)
}
