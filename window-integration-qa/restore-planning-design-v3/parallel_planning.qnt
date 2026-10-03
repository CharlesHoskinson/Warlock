module parallel_planning {
 type Phase = Planning | Draining | Armed | Focusing | Refreshing | Complete | Refused | Uncertain
 type Event = Start(int) | Done({i:int,ok:bool}) | Collect | AdmitMember(bool) | Dispatch | Return(bool) | Refresh | Seed | Cancel | ChangeMaterial | Tick(int) | GroupGone
 type State = {phase:Phase,now:int,deadline:int,current:bool,running:Set[int],done:Set[int],valid:Set[int],failed:bool,material:bool,admitted:bool,next:int,active:bool,effects:List[int],refreshes:int,seeded:bool,uncertain:bool,groupGone:bool,justEffect:bool,justSeed:bool}
 var s:State
 action init=s'={phase:Planning,now:0,deadline:20,current:true,running:Set(),done:Set(),valid:Set(),failed:false,material:true,admitted:false,next:0,active:false,effects:List(),refreshes:0,seeded:false,uncertain:false,groupGone:false,justEffect:false,justSeed:false}
 action fire(e:Event):bool={
  val b={...s,justEffect:false,justSeed:false}
  s'=match e {
   | Start(i)=>if(s.phase==Planning and s.current and s.now<s.deadline and not(s.failed) and i>=0 and i<3 and not(s.running.contains(i)) and not(s.done.contains(i)) and s.running.size()<3){...b,running:s.running.union(Set(i))}else b
   | Done(r)=>if(s.running.contains(r.i)){...b,running:s.running.exclude(Set(r.i)),done:s.done.union(Set(r.i)),valid:if(r.ok and s.current and s.now<s.deadline and not(s.failed))s.valid.union(Set(r.i))else s.valid,failed:s.failed or not(r.ok) or not(s.current) or s.now>=s.deadline} else b
   | Collect=>if(s.running.size()==0){...b,phase:if(s.valid==Set(0,1,2) and not(s.failed) and s.current and s.now<s.deadline)Armed else Refused}else {...b,phase:Draining,failed:true}
   | AdmitMember(ok)=>if((s.phase==Armed or s.phase==Focusing) and s.current and not(s.active) and s.next<6 and s.next%2==0){...b,phase:if(ok and s.material and (s.phase!=Armed or s.now<s.deadline))Focusing else Refused,admitted:ok and s.material and (s.phase!=Armed or s.now<s.deadline)}else b
   | Dispatch=>if(s.phase==Focusing and s.current and s.admitted and not(s.active) and s.next<6){...b,active:true}else b
   | Return(ok)=>if(s.active){...b,active:false,phase:if(not(ok))Uncertain else if(s.next==5)Refreshing else Focusing,next:if(ok)s.next+1 else s.next,effects:if(ok)s.effects.append(s.next)else s.effects,admitted:ok and s.next%2==0,uncertain:s.uncertain or not(ok),justEffect:ok}else b
   | Refresh=>if(s.phase==Refreshing and s.current and s.refreshes<3){...b,refreshes:s.refreshes+1,phase:if(s.refreshes==2)Complete else Refreshing}else b
   | Seed=>if(s.phase==Complete and s.current and s.now<s.deadline and s.material and not(s.uncertain)){...b,seeded:true,justSeed:true}else b
   | Cancel=>if(not(s.active) and s.phase!=Focusing){...b,current:false,failed:true}else b
   | ChangeMaterial=>{...b,material:false}
   | Tick(n)=>if(n>=0){...b,now:s.now+n}else b
   | GroupGone=>{...b,groupGone:true}
  }
 }
 val boundedWorkers=s.running.size()<=3 and s.done.size()<=3
 val effectsOrdered=s.effects==List(0,1,2,3,4,5).slice(0,s.effects.length())
 val noPlanEffect=(s.phase==Planning or s.phase==Draining) implies (s.effects.length()==0 and not(s.active) and not(s.seeded))
 val seedRequiresComplete=s.justSeed implies (s.current and s.now<s.deadline and s.effects.length()==6 and s.refreshes==3 and s.material and not(s.uncertain))
 val unknownNeverSeed=s.uncertain implies not(s.seeded)
 val noDeadlineReset=s.deadline==20
 val allProps=boundedWorkers and effectsOrdered and noPlanEffect and seedRequiresComplete and unknownNeverSeed and noDeadlineReset
 action step={nondet e=Set(Start(0),Start(1),Start(2),Start(3),Done({i:0,ok:true}),Done({i:1,ok:true}),Done({i:2,ok:true}),Done({i:0,ok:false}),Done({i:1,ok:false}),Done({i:2,ok:false}),Collect,AdmitMember(true),AdmitMember(false),Dispatch,Return(true),Return(false),Refresh,Seed,Cancel,ChangeMaterial,Tick(1),Tick(5),Tick(20),GroupGone).oneOf();fire(e)}
}
