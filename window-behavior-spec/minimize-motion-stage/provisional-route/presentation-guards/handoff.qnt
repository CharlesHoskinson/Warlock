/** Computed route geometry is not an observation of a displayed fragment.
 * Reserve consumes a per-output presentation handoff only when every output
 * has a current observation and all submitted old frames have been drained.
 * New fragments retain individual actual origins and one shared progress.
 */
module handoff {
 type State={epoch:int,progress:int,computed:List[int],shown:List[int],origins:List[int],known:Set[int],pending:Set[int],pendingX:List[int],reserved:bool,handoffShown:List[int],beforeEpoch:int,rejected:bool}
 type Event=Tick | Submit(int) | Present(int) | Reserve(bool) | Forget(int)
 var s:State
 action init=s'={epoch:1,progress:0,computed:List(4,5),shown:List(4,5),origins:List(4,5),known:Set(0,1),pending:Set(),pendingX:List(0,0),reserved:false,handoffShown:List(4,5),beforeEpoch:1,rejected:false}
 def position(from:int,p:int):int=from+(10-from)*p/10
 action fire(e:Event):bool={val b={...s,beforeEpoch:s.epoch,rejected:false}
  s'=match e {
   | Tick=>{...b,progress:if(s.progress<10)s.progress+1 else 10,computed:s.origins.foldl(List(),(rows,x)=>rows.append(position(x,if(s.progress<10)s.progress+1 else 10)))}
   | Submit(o)=>if(o<0 or o>1)b else {...b,pending:s.pending.union(Set(o)),pendingX:s.pendingX.replaceAt(o,s.computed.nth(o))}
   | Present(o)=>if(not(s.pending.contains(o)))b else {...b,shown:s.shown.replaceAt(o,s.pendingX.nth(o)),known:s.known.union(Set(o)),pending:s.pending.exclude(Set(o))}
   | Reserve(validToken)=>if(not(validToken) or s.known!=Set(0,1) or s.pending!=Set()){...b,rejected:true} else {...b,epoch:s.epoch+1,origins:s.shown,computed:s.shown,handoffShown:s.shown,reserved:true,progress:0}
   | Forget(o)=>{...b,known:s.known.exclude(Set(o))}
  }
 }
 val actualOrigin=s.reserved implies s.origins==s.handoffShown
 val rejectedCannotReserve=s.rejected implies s.epoch==s.beforeEpoch
 val sharedClock=s.progress>=0 and s.progress<=10
 val allProps=actualOrigin and rejectedCannotReserve and sharedClock
 action step={nondet e=Set(Tick,Submit(0),Submit(1),Present(0),Present(1),Reserve(true),Reserve(false),Forget(0),Forget(1)).oneOf();fire(e)}
}
