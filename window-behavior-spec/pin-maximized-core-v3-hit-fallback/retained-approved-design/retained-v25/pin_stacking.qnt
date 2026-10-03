module pin_stacking {
 type Event=CoreRaise(int)|CoreLower(int)|Capture|Advance(bool)|Finish|Close(int)|Pin({owner:int,value:bool})|Reload|Reuse(int)|Minimize(int)|Restore(int)|Focus(int)
 type State={order:List[int],live:Set[int],pinned:Set[int],minimized:Set[int],epoch:int,generation:int->int,focus:int,capturedEpoch:int,capturedGeneration:int->int,capturedPins:Set[int],capturedLive:Set[int],capturedMinimized:Set[int],capturedFocus:int,plan:List[int],index:int,active:bool,complete:bool,failed:bool,lastWrite:int}
 var s:State
 pure def promote(order:List[int],members:List[int]):List[int]=order.select(w=>not(members.indices().exists(i=>members.nth(i)==w))).concat(members)
 pure def rank(order:List[int],owner:int):int=order.indices().fold(-1,(n,i)=>if(order.nth(i)==owner)i else n)
 pure def family(order:List[int],live:Set[int],owner:int):List[int]=if(owner==1)List(1,3).select(w=>live.contains(w))else List(owner).select(w=>live.contains(w))
 def eligible(owner:int):bool=s.live.contains(owner)and not(s.minimized.contains(owner))
 val protected=Set(1,2,3,4).filter(w=>eligible(w)and(s.pinned.contains(w)or(w==3 and eligible(1)and s.pinned.contains(1))))
 val plan=if(protected.contains(1)and protected.contains(2)){
  if(rank(s.order,3)>rank(s.order,2))List(2,1,3).select(w=>protected.contains(w))else List(1,3,2).select(w=>protected.contains(w))
 }else s.order.select(w=>protected.contains(w))
 val same=s.capturedEpoch==s.epoch and s.capturedGeneration==s.generation and s.capturedPins==s.pinned and s.capturedLive==s.live and s.capturedMinimized==s.minimized and s.capturedFocus==s.focus
 val stacked=protected.forall(p=>s.live.exclude(protected).exclude(s.minimized).forall(u=>rank(s.order,p)>rank(s.order,u)))and(eligible(1)and eligible(3)implies rank(s.order,3)>rank(s.order,1))
 action init=s'={order:List(1,3,2,4),live:Set(1,2,3,4),pinned:Set(1,2),minimized:Set(),epoch:1,generation:Map(1->1,2->1,3->1,4->1),focus:4,capturedEpoch:0,capturedGeneration:Map(),capturedPins:Set(),capturedLive:Set(),capturedMinimized:Set(),capturedFocus:0,plan:List(),index:0,active:false,complete:false,failed:false,lastWrite:0}
 action fire(e:Event):bool={val b={...s,lastWrite:0,complete:false};s'=match e{
 |Capture=>if(s.active)b else {...b,capturedEpoch:s.epoch,capturedGeneration:s.generation,capturedPins:s.pinned,capturedLive:s.live,capturedMinimized:s.minimized,capturedFocus:s.focus,plan:plan,index:0,active:true,failed:false}
 |Advance(ok)=>if(s.active and same and s.index<s.plan.length()and ok){val w=s.plan.nth(s.index);{...b,order:promote(s.order,family(s.order,s.live,w)),index:s.index+1,lastWrite:w}}else{...b,active:false,failed:true}
 |Finish=>{...b,complete:s.active and same and s.index==s.plan.length()and stacked,active:false,failed:not(s.active and same and s.index==s.plan.length()and stacked)}
 |CoreRaise(w)=>{...b,order:if(s.live.contains(w))promote(s.order,family(s.order,s.live,w))else s.order,active:false}
 |CoreLower(w)=>{...b,order:if(s.live.contains(w))List(w).concat(s.order.select(x=>x!=w))else s.order,active:false}
 |Close(w)=>{...b,live:s.live.exclude(Set(w)),pinned:s.pinned.exclude(Set(w)),order:s.order.select(x=>x!=w),generation:s.generation.set(w,s.generation.get(w)+1),active:false}
 |Pin(p)=>{...b,pinned:if(p.value and s.live.contains(p.owner))s.pinned.union(Set(p.owner))else s.pinned.exclude(Set(p.owner)),active:false}
 |Reload=>{...b,epoch:s.epoch+1,active:false}
 |Reuse(w)=>{...b,live:s.live.union(Set(w)),order:promote(s.order,List(w)),generation:s.generation.set(w,s.generation.get(w)+1),pinned:s.pinned.exclude(Set(w)),active:false}
 |Minimize(w)=>{...b,minimized:s.minimized.union(Set(w)),active:false}
 |Restore(w)=>{...b,minimized:s.minimized.exclude(Set(w)),active:false}
 |Focus(w)=>{...b,focus:w,active:false}
 }}
 val allProps=all{s.order.indices().map(i=>s.order.nth(i))==s.live,s.order.length()==s.live.size(),s.lastWrite==0 or(s.live.contains(s.lastWrite)and same),s.complete implies same and stacked}
 action step={nondet w=Set(1,2,3,4).oneOf();nondet b=Set(true,false).oneOf();nondet e=Set(CoreRaise(w),CoreLower(w),Capture,Advance(b),Finish,Close(w),Reuse(w),Pin({owner:w,value:b}),Reload,Minimize(w),Restore(w),Focus(w)).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),s'=s}
 action enforce=fire(Capture).then(fire(Advance(true))).then(fire(Advance(true))).then(fire(Advance(true))).then(fire(Finish))
}
