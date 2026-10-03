module family_registry {
 type Event=Reserve((int,int))|Claim((int,Set[int],bool))|Commit(int)|Replace(int)
 type State={serial:int,receipts:int->int,requested:int->int,tickets:int->int,scopes:int->Set[int],owner:int->int,effect:bool,effectTicket:int,effectScope:Set[int]}
 var s:State
 val actors=Set(0,1)
 val windows=Set(0,1,2)
 action init=s'={serial:0,receipts:Map(0->0,1->0,2->0),requested:Map(0->0,1->1),tickets:Map(0->0,1->0),scopes:Map(0->Set(),1->Set()),owner:Map(0-> -1,1-> -1,2-> -1),effect:false,effectTicket:0,effectScope:Set()}
 action fire(e:Event):bool={
  val b={...s,effect:false}
  s'=match e {
   | Reserve(pair)=>{val a=pair._1;val w=pair._2;if(actors.contains(a) and windows.contains(w)){
     val scope=s.scopes.get(a).union(Set(w))
     {...b,serial:s.serial+1,tickets:s.tickets.set(a,s.serial+1),requested:s.requested.set(a,w),receipts:scope.fold(s.receipts,(m,i)=>m.set(i,s.serial+1))}
    } else b}
   | Claim(triple)=>{val a=triple._1;val scope=triple._2;val complete=triple._3;if(actors.contains(a) and complete and scope.contains(s.requested.get(a)) and scope.subseteq(windows) and s.tickets.get(a)>0 and scope.forall(w=>s.receipts.get(w)<=s.tickets.get(a))){
      {...b,scopes:s.scopes.set(a,scope),owner:scope.fold(s.owner,(m,w)=>m.set(w,a)),receipts:scope.fold(s.receipts,(m,w)=>m.set(w,s.tickets.get(a)))}
    } else b}
   | Commit(a)=>if(actors.contains(a) and s.scopes.get(a).size()>0 and s.scopes.get(a).forall(w=>s.owner.get(w)==a and s.receipts.get(w)==s.tickets.get(a))){...b,effect:true,effectTicket:s.tickets.get(a),effectScope:s.scopes.get(a)} else b
   | Replace(w)=>if(windows.contains(w)){...b,serial:s.serial+1,receipts:s.receipts.set(w,s.serial+1),owner:s.owner.set(w,-1)} else b
  }
 }
 val currentWholeScope=s.effect implies s.effectScope.forall(w=>s.receipts.get(w)==s.effectTicket)
 val allProps=currentWholeScope
 action step={nondet e=Set(Reserve((0,0)),Reserve((1,1)),Claim((0,Set(0,1),true)),Claim((1,Set(0,1),true)),Claim((0,Set(0),false)),Claim((1,Set(1),false)),Claim((1,Set(2),true)),Commit(0),Commit(1),Replace(0),Replace(1)).oneOf();fire(e)}
}
