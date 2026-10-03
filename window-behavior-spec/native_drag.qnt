/** Captured drag ownership, physical release and cancellation contract.
 * Geometry is abstracted to normal/snapped; native geometry is checked live.
 * Reload invalidates the Lua transaction, so a later native finish cannot snap.
 */
module native_drag {
  type Event = Begin(int) | Focus(int) | Release(bool) | Cancel | Close(int) | Open(int) | Reload | Resize(int)
  var s: {alive:Set[int],generation:int,owner:int,token:int,focus:int,snapped:Set[int],sourceSnapped:bool,lastTarget:int,lastOwner:int,lastRelease:bool}
  action init = s'={alive:Set(1,2),generation:1,owner:0,token:0,focus:1,snapped:Set(1),sourceSnapped:false,lastTarget:0,lastOwner:0,lastRelease:false}
  action fire(e:Event):bool = {
    val base={...s,lastTarget:0,lastOwner:s.owner,lastRelease:false}
    s'=match e {
      | Begin(id) => if(s.owner==0 and s.alive.contains(id)) {...base,owner:id,token:s.generation,sourceSnapped:s.snapped.contains(id),snapped:s.snapped.exclude(Set(id))} else base
      | Focus(id) => {...base,focus:id}
      | Release(edge) => if(s.owner!=0 and s.token==s.generation and s.alive.contains(s.owner)) {...base,owner:0,token:0,snapped:if(edge) s.snapped.union(Set(s.owner)) else s.snapped,lastTarget:if(edge) s.owner else 0,lastRelease:edge} else {...base,owner:0,token:0}
      | Cancel => {...base,owner:0,token:0,snapped:if(s.owner!=0 and s.token==s.generation and s.alive.contains(s.owner) and s.sourceSnapped) s.snapped.union(Set(s.owner)) else s.snapped}
      | Close(id) => {...base,alive:s.alive.exclude(Set(id)),snapped:s.snapped.exclude(Set(id)),owner:if(s.owner==id) 0 else s.owner,token:if(s.owner==id) 0 else s.token}
      | Open(id) => if(s.alive.contains(id)) base else {...base,alive:s.alive.union(Set(id))}
      | Reload => {...base,generation:s.generation+1,owner:0,token:0,snapped:if(s.owner!=0 and s.token==s.generation and s.alive.contains(s.owner) and s.sourceSnapped) s.snapped.union(Set(s.owner)) else s.snapped}
      | Resize(_) => base
    }
  }
  pure val EVENTS=Set(Begin(1),Begin(2),Focus(1),Focus(2),Release(true),Release(false),Cancel,Close(1),Close(2),Open(1),Open(2),Reload,Resize(1),Resize(2))
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val allProps=s.snapped.subseteq(s.alive) and (s.owner==0 or (s.alive.contains(s.owner) and s.token==s.generation))
    and (s.lastTarget==0 or (s.lastRelease and s.lastTarget==s.lastOwner))
}
