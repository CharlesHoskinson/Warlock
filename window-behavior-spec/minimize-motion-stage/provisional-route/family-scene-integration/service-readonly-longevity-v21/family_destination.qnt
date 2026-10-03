module family_destination {
 type Observation={epoch:int,ids:List[int],complete:bool,edges:bool}
 type Event=Reserve|Observe(Observation)|Destination(Observation)|Replace(int)
 type State={epoch:int,ids:List[int],effectEpoch:int,effectIds:List[int],effect:bool,observedEpoch:int}
 var s:State
 action init=s'={epoch:1,ids:List(1,2,3),effectEpoch:0,effectIds:List(),effect:false,observedEpoch:0}
 action fire(e:Event):bool={
  val b={...s,effect:false}
  s'=match e {
   | Reserve=>{...b,epoch:s.epoch+1}
   | Observe(p)=>{...b,observedEpoch:p.epoch}
   | Destination(p)=>if(p.epoch==s.epoch and p.ids==s.ids and p.complete and p.edges){...b,effect:true,effectEpoch:p.epoch,effectIds:p.ids} else b
   | Replace(i)=>if(i>=0 and i<3){...b,epoch:s.epoch+1,ids:s.ids.replaceAt(i,s.ids.nth(i)+10)} else b
  }
 }
 val effectHasCurrentOwnership=s.effect implies (s.effectEpoch==s.epoch and s.effectIds==s.ids)
 val allProps=effectHasCurrentOwnership
 action step={
  val p={epoch:s.epoch,ids:s.ids,complete:true,edges:true}
  nondet e=Set(Reserve,Observe(p),Destination(p),Destination({...p,epoch:s.epoch-1}),Destination({...p,ids:List(1,2,3)}),Destination({...p,complete:false}),Destination({...p,edges:false}),Replace(0),Replace(1),Replace(2)).oneOf();fire(e)
 }
}
