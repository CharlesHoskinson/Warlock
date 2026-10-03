module pin_action {
 type Identity={owner:int,pid:int,address:int,stable:int,session:int,epoch:int}
 type Result={ok:bool,mutated:bool}
 type Event=Begin(Identity)|Float(Result)|Pin(Result)|Raise(bool)|Finish
   |Close(int)|Minimize(int)|Restore(int)|Fullscreen(int)|Focus(int)|Reload|Reduce|Reuse
   |Tick({owner:int,generation:int})|Idle
 pure val identity={owner:1,pid:11,address:101,stable:1,session:1,epoch:1}
 type State={live:Set[int],floating:Set[int],pinned:Set[int],minimized:Set[int],saved:Set[int],full:Set[int],
   focus:int,session:int,epoch:int,active:bool,phase:int,captured:Identity,desired:bool,
   floatBefore:bool,pinBefore:bool,refused:bool,complete:bool,partial:bool,
   generation:int,feedback:int->int,lastWrite:int}
 var s:State
 def eligible(w:int):bool=s.live.contains(w) and not(s.minimized.contains(w)) and not(s.full.contains(w))
 val current=s.active and eligible(s.captured.owner) and s.captured.session==s.session and s.captured.epoch==s.epoch
 def exact(i:Identity):bool=i.owner==1 and i.pid==11 and i.address==101 and i.stable==1 and i.session==s.session and i.epoch==s.epoch
 val changed=s.pinned.contains(s.captured.owner)!=s.pinBefore or s.floating.contains(s.captured.owner)!=s.floatBefore
 action init=s'={live:Set(1,2),floating:Set(2),pinned:Set(2),minimized:Set(),saved:Set(),full:Set(),
   focus:2,session:1,epoch:1,active:false,phase:0,captured:identity,desired:false,
   floatBefore:false,pinBefore:false,refused:false,complete:false,partial:false,generation:0,feedback:Map(),lastWrite:0}
 action fire(e:Event):bool={
   val b={...s,lastWrite:0}
   s'=match e {
    |Begin(i)=>if(not(s.active) and exact(i) and eligible(i.owner)){
      ...b,active:true,phase:1,captured:i,desired:not(s.pinned.contains(i.owner)),
      pinBefore:s.pinned.contains(i.owner),floatBefore:s.floating.contains(i.owner),
      refused:false,complete:false,partial:false,generation:s.generation+1,
      feedback:s.feedback.keys().exclude(Set(i.owner)).mapBy(k=>s.feedback.get(k))
    }else{...b,refused:true}
    |Float(r)=>if(current and s.phase==1){...b,
      floating:if(r.mutated)s.floating.union(Set(s.captured.owner))else s.floating,
      phase:if(r.ok and (r.mutated or s.floating.contains(s.captured.owner)))2 else 0,
      active:r.ok and (r.mutated or s.floating.contains(s.captured.owner)),refused:not(r.ok),
      partial:if(not(r.ok))r.mutated or changed else s.partial,
      lastWrite:if(r.mutated)s.captured.owner else 0}
      else {...b,active:false,phase:0,refused:true,complete:false,partial:changed}
    |Pin(r)=>if(current and s.phase==2 and s.floating.contains(s.captured.owner)){
      ...b,pinned:if(r.mutated){if(s.desired)s.pinned.union(Set(s.captured.owner))else s.pinned.exclude(Set(s.captured.owner))}else s.pinned,
      phase:if(r.ok and (r.mutated or s.pinned.contains(s.captured.owner)==s.desired))3 else 0,
      active:r.ok and (r.mutated or s.pinned.contains(s.captured.owner)==s.desired),refused:not(r.ok),
      partial:if(not(r.ok))r.mutated or changed else s.partial,
      lastWrite:if(r.mutated)s.captured.owner else 0}
      else {...b,active:false,phase:0,refused:true,complete:false,partial:changed}
    |Raise(ok)=>if(current and s.phase==3 and s.pinned.contains(s.captured.owner)==s.desired and ok){...b,phase:4}
      else {...b,active:false,phase:0,refused:true,complete:false,partial:changed}
    |Finish=>if(current and (s.phase==4 or (s.phase==3 and not(s.desired))) and s.pinned.contains(s.captured.owner)==s.desired){
      ...b,active:false,phase:0,complete:true,partial:false,refused:false,
      feedback:s.feedback.put(s.captured.owner,s.generation)}
      else {...b,active:false,phase:0,complete:false,refused:true,partial:changed}
    |Close(w)=>{...b,live:s.live.exclude(Set(w)),floating:s.floating.exclude(Set(w)),pinned:s.pinned.exclude(Set(w)),
      minimized:s.minimized.exclude(Set(w)),saved:s.saved.exclude(Set(w)),full:s.full.exclude(Set(w)),
      feedback:s.feedback.keys().exclude(Set(w)).mapBy(k=>s.feedback.get(k)),complete:false}
    |Minimize(w)=>if(eligible(w)){...b,minimized:s.minimized.union(Set(w)),
      saved:if(s.pinned.contains(w))s.saved.union(Set(w))else s.saved.exclude(Set(w)),pinned:s.pinned.exclude(Set(w)),
      feedback:s.feedback.keys().exclude(Set(w)).mapBy(k=>s.feedback.get(k)),complete:false}else b
    |Restore(w)=>if(s.live.contains(w) and s.minimized.contains(w)){...b,minimized:s.minimized.exclude(Set(w)),
      pinned:if(s.saved.contains(w))s.pinned.union(Set(w))else s.pinned,
      saved:s.saved.exclude(Set(w)),complete:false}else b
    |Fullscreen(w)=>{...b,full:s.full.union(Set(w)),complete:false}
    |Focus(w)=>{...b,focus:w}
    |Reload=>{...b,epoch:s.epoch+1,active:false,phase:0,feedback:Map(),complete:false}
    |Reduce=>{...b,feedback:Map()}
    |Reuse=>{...b,live:s.live.union(Set(3))}
    |Tick(p)=>if(eligible(p.owner) and s.feedback.keys().contains(p.owner) and s.feedback.get(p.owner)==p.generation){...b,lastWrite:p.owner}else b
    |Idle=>b
   }
 }
 val allProps=all{s.pinned.subseteq(s.live),s.pinned.intersect(s.minimized)==Set(),s.saved.subseteq(s.minimized),
   s.feedback.keys().subseteq(s.live.exclude(s.minimized)),s.lastWrite==0 or eligible(s.lastWrite),
   s.complete implies not(s.active) and eligible(s.captured.owner) and s.pinned.contains(s.captured.owner)==s.desired,
   s.complete implies s.captured.session==s.session and s.captured.epoch==s.epoch}
 action step={nondet w=Set(1,2,3).oneOf();nondet e=Set(Begin(identity),Begin({...identity,pid:12}),
   Float({ok:true,mutated:true}),Float({ok:false,mutated:true}),Pin({ok:true,mutated:true}),Pin({ok:false,mutated:false}),
   Raise(true),Raise(false),Finish,Close(w),Minimize(w),Restore(w),Fullscreen(w),Focus(w),Reload,Reduce,Reuse,
   Tick({owner:w,generation:1}),Idle).oneOf();fire(e)}
 action check(p:bool):bool=all{assert(p),s'=s}
 action untilPin=fire(Begin(identity)).then(fire(Float({ok:true,mutated:true}))).then(fire(Pin({ok:true,mutated:true})))
 action fullPin=untilPin.then(fire(Raise(true))).then(fire(Finish))
}
