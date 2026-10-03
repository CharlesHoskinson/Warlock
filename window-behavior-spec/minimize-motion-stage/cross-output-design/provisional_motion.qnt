/** Visual reversal may continue from retained pixels before fresh validation.
 * It has no native authority. Promotion preserves the current visual position;
 * reaching a speculative endpoint never sends done. Reject/timeout/reduce use
 * explicit fresh validation before settling a previously accepted native intent.
 */
module provisional_motion {
 type Observation={identity:int,epoch:int}
 type Event=Request | Tick | Validate(Observation) | Reject(Observation) | End(Observation) | Timeout(Observation) | Reduce(Observation) | Reuse
 type State={id:int,epoch:int,phase:str,requested:bool,accepted:bool,validated:bool,presented:bool,nativeMin:bool,
   x:int,from:int,to:int,pixelsIdentity:int,originalPixels:int,pixels:int,nativeGeometry:int,savedGeometry:int,
   stale:bool,beforeNative:bool,requestedEvent:bool,beforeX:int,promotedEvent:bool,unauthorizedEnd:bool}
 var s:State
 action init=s'={id:1,epoch:1,phase:"running",requested:true,accepted:true,validated:true,presented:true,nativeMin:true,
  x:5,from:0,to:10,pixelsIdentity:1,originalPixels:107,pixels:107,nativeGeometry:100,savedGeometry:100,
  stale:false,beforeNative:true,requestedEvent:false,beforeX:5,promotedEvent:false,unauthorizedEnd:false}
 def current(o:Observation):bool=o.identity==s.id and o.epoch==s.epoch and s.pixelsIdentity==s.id
 action fire(e:Event):bool={
  val b={...s,stale:false,beforeNative:s.nativeMin,requestedEvent:false,beforeX:s.x,promotedEvent:false,unauthorizedEnd:false}
  s'=match e {
   | Request=>if(s.pixelsIdentity!=s.id)b else {...b,epoch:s.epoch+1,phase:"provisional",requested:not(s.requested),validated:false,from:s.x,to:if(s.requested)0 else 10,requestedEvent:true}
   | Tick=>if(s.phase!="provisional" and s.phase!="running" and s.phase!="rollback")b else {...b,x:if(s.x<s.to)s.x+1 else if(s.x>s.to)s.x-1 else s.x}
   | Validate(o)=>if(not(current(o)) or s.phase!="provisional"){...b,stale:true} else {...b,phase:"running",accepted:s.requested,validated:true,promotedEvent:true,nativeMin:if(s.requested and s.presented)true else s.nativeMin}
   | Reject(o)=>if(not(current(o)) or s.phase!="provisional"){...b,stale:true} else {...b,phase:"rollback",requested:s.accepted,validated:true,from:s.x,to:if(s.accepted)10 else 0}
   | End(o)=>if(not(current(o))){...b,stale:true} else if(not(s.validated) or s.phase=="provisional"){...b,unauthorizedEnd:true} else if((s.phase=="running" or s.phase=="rollback") and s.x==s.to){...b,phase:"idle",nativeMin:s.accepted} else b
   | Timeout(o)=>if(not(current(o))){...b,stale:true} else {...b,phase:"idle",requested:s.accepted,validated:true,nativeMin:s.accepted}
   | Reduce(o)=>if(not(current(o))){...b,stale:true} else {...b,phase:"idle",requested:s.accepted,validated:true,nativeMin:s.accepted}
   | Reuse=>{...b,id:s.id+1,epoch:s.epoch+1,phase:"idle",nativeMin:false,validated:false,presented:false,pixelsIdentity:0,pixels:0,originalPixels:(s.id+1)*100+7,accepted:false,requested:false,nativeGeometry:42,savedGeometry:42}
  }
 }
 val provisionalHasNoNativeAuthority=(s.phase=="provisional" or s.unauthorizedEnd) implies s.nativeMin==s.beforeNative
 val exactVisualContinuity=(s.requestedEvent or s.promotedEvent) implies s.x==s.beforeX
 val sameIdentityPixels=s.pixelsIdentity!=0 implies (s.pixelsIdentity==s.id and s.pixels==s.originalPixels)
 val nativeGeometryPreserved=s.nativeGeometry==s.savedGeometry
 val staleCannotCommit=s.stale implies s.nativeMin==s.beforeNative
 val allProps=provisionalHasNoNativeAuthority and exactVisualContinuity and sameIdentityPixels and nativeGeometryPreserved and staleCannotCommit
 action step={nondet e=Set(Request,Tick,Validate({identity:s.id,epoch:s.epoch}),Validate({identity:s.id-1,epoch:s.epoch-1}),Reject({identity:s.id,epoch:s.epoch}),End({identity:s.id,epoch:s.epoch}),End({identity:s.id,epoch:s.epoch-1}),Timeout({identity:s.id,epoch:s.epoch}),Timeout({identity:s.id-1,epoch:s.epoch}),Reduce({identity:s.id,epoch:s.epoch}),Reuse).oneOf();fire(e)}
}
