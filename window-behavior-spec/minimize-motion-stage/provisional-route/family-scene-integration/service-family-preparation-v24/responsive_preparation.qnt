module responsive_preparation {
 type Event=Reserve(int)|BeginObserve(int)|FinishObserve(int)|BeginEffect(int)|FinishEffect|Promote(int)|Endpoint(int)|Fail(int)
 type State={latest:int,observing:Set[int],observed:Set[int],effect:int,retarget:int,validated:int,endpoint:int,writeReceipt:int,write:bool}
 var s:State
 action init=s'={latest:0,observing:Set(),observed:Set(),effect:0,retarget:0,validated:0,endpoint:0,writeReceipt:0,write:false}
 action fire(e:Event):bool={val b={...s,write:false};s'=match e {
 | Reserve(r)=>if(r>s.latest and s.effect==0){...b,latest:r,retarget:r,validated:0} else b
 | BeginObserve(r)=>if(r==s.latest and r>0){...b,observing:s.observing.union(Set(r))} else b
 | FinishObserve(r)=>if(s.observing.contains(r)){...b,observing:s.observing.exclude(Set(r)),observed:if(r==s.latest)s.observed.union(Set(r)) else s.observed} else b
 | BeginEffect(r)=>if(r==s.latest and s.observed.contains(r) and s.effect==0){...b,effect:r,write:true,writeReceipt:r} else b
 | FinishEffect=>{...b,effect:0}
 | Promote(r)=>if(r==s.latest and s.observed.contains(r) and s.effect==0){...b,validated:r} else b
 | Endpoint(r)=>if(r==s.latest and s.validated==r and s.effect==0){...b,effect:r,write:true,writeReceipt:r,endpoint:r} else b
 | Fail(r)=>if(r==s.latest){...b,validated:0} else b
 }}
 val allProps=(s.write implies(s.writeReceipt==s.latest and s.effect==s.latest)) and (s.validated>0 implies s.validated==s.latest) and (s.retarget==s.latest)
 action step={nondet e=Set(Reserve(1),Reserve(2),Reserve(3),BeginObserve(1),BeginObserve(2),BeginObserve(3),FinishObserve(1),FinishObserve(2),FinishObserve(3),BeginEffect(1),BeginEffect(2),BeginEffect(3),FinishEffect,Promote(1),Promote(2),Promote(3),Endpoint(1),Endpoint(2),Endpoint(3),Fail(1),Fail(2),Fail(3)).oneOf();fire(e)}
}
