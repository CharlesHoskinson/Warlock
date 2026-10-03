module focus_transaction {
 type Phase = Idle | Prepared | Registered | Executing | Returned | Closed | Quarantined | Refused
 type Event = Prepare | Register | Gate | Guard | Effect(bool) | Receipt({shape:bool,nonce:bool,count:int}) | Confirm | Exit | Gone | Cancel | Material | Native | Output | Tick(int) | StartRefresh(int) | FinishRefresh({index:int,ok:bool}) | Seed
 var s:{phase:Phase,current:bool,material:bool,native:bool,output:bool,now:int,deadline:int,guarded:bool,next:int,attempted:List[int],completed:List[int],active:bool,exited:bool,gone:bool,uncertain:bool,closed:bool,seeded:bool,justEffect:bool,justSeed:bool,admitted:bool,refreshRunning:Set[int],refreshDone:Set[int],refreshStop:bool}
 action init=s'={phase:Idle,current:true,material:true,native:true,output:true,now:0,deadline:20,guarded:false,next:0,attempted:[],completed:[],active:false,exited:false,gone:false,uncertain:false,closed:false,seeded:false,justEffect:false,justSeed:false,admitted:false,refreshRunning:Set(),refreshDone:Set(),refreshStop:false}
 pure def advance(a,e)={
  val b={...a,justEffect:false,justSeed:false}
  match e {
   | Prepare=>if(a.phase==Idle and a.current and a.material and a.native and a.output and a.now<a.deadline){...b,phase:Prepared}else b
   | Register=>if(a.phase==Prepared and a.current and a.material and a.native and a.output and a.now<a.deadline){...b,phase:Registered,active:true}else b
   | Gate=>if(a.phase==Registered){...b,phase:if(a.current and a.material and a.native and a.output and a.now<a.deadline)Executing else Refused,admitted:a.current and a.material and a.native and a.output and a.now<a.deadline}else b
   | Guard=>if(a.phase==Executing and a.next<6){...b,guarded:a.material and a.native and a.output,phase:if(a.material and a.native and a.output)Executing else Quarantined,uncertain:a.uncertain or not(a.material and a.native and a.output)}else b
   | Effect(ok)=>if(a.phase==Executing and a.guarded and a.next<6 and a.current and a.material and a.native and a.output){...b,guarded:false,next:a.next+1,attempted:a.attempted.append(a.next),completed:if(ok)a.completed.append(a.next)else a.completed,phase:if(ok)Executing else Quarantined,uncertain:a.uncertain or not(ok),justEffect:true}else b
   | Receipt(r)=>if(a.phase==Executing and a.next==6){...b,phase:if(r.shape and r.nonce and r.count==6 and a.completed.length()==6)Returned else Quarantined,uncertain:a.uncertain or not(r.shape and r.nonce and r.count==6 and a.completed.length()==6)}else if(a.active){...b,phase:Quarantined,uncertain:true}else b
   | Exit=>if(a.active){...b,exited:true}else b
   | Gone=>if(a.exited){...b,gone:true}else b
   | Confirm=>if(a.phase==Returned and a.exited and a.gone){...b,phase:if(a.current and a.material and a.native and a.output and not(a.uncertain))Closed else Quarantined,active:not(a.current and a.material and a.native and a.output and not(a.uncertain)),closed:a.current and a.material and a.native and a.output and not(a.uncertain),uncertain:a.uncertain or not(a.current and a.material and a.native and a.output)}else b
   | Cancel=>if(not(a.active)){...b,current:false}else b
   | Material=>{...b,material:false}
   | Native=>{...b,native:false}
   | Output=>{...b,output:false}
   | Tick(n)=>if(n>=0){...b,now:a.now+n}else b
   | StartRefresh(i)=>if(a.closed and a.current and a.material and a.native and a.output and a.now<a.deadline and not(a.refreshStop) and i>=0 and i<3 and not(a.refreshRunning.contains(i)) and not(a.refreshDone.contains(i))){...b,refreshRunning:a.refreshRunning.union(Set(i))}else b
   | FinishRefresh(r)=>if(a.refreshRunning.contains(r.index)){...b,refreshRunning:a.refreshRunning.exclude(Set(r.index)),refreshDone:if(r.ok)a.refreshDone.union(Set(r.index))else a.refreshDone,refreshStop:a.refreshStop or not(r.ok)}else b
   | Seed=>if(a.refreshRunning.size()==0 and a.refreshDone.size()==3 and not(a.refreshStop) and a.closed and a.current and a.material and a.native and a.output and a.now<a.deadline and not(a.uncertain)){...b,seeded:true,justSeed:true}else b
  }
 }
 action fire(e)=s'=advance(s,e)
 val order=s.attempted==List(0,1,2,3,4,5).slice(0,s.attempted.length()) and s.completed==List(0,1,2,3,4,5).slice(0,s.completed.length())
 val bound=s.next>=0 and s.next<=6 and s.attempted.length()<=6
 val guardedEffect=s.justEffect implies(s.admitted and s.current and s.material and s.native and s.output)
 val normalClosure=s.closed implies(s.completed.length()==6 and s.exited and s.gone and not(s.uncertain))
 val noUnknownSeed=s.uncertain implies not(s.seeded)
 val seedAuthority=s.justSeed implies(s.closed and s.current and s.material and s.native and s.output and s.now<s.deadline)
 val fixedDeadline=s.deadline==20
 val refreshBound=s.refreshRunning.size()<=3 and s.refreshDone.size()<=3 and s.refreshRunning.intersect(s.refreshDone)==Set()
 val seedDrained=s.justSeed implies(s.refreshRunning.size()==0 and s.refreshDone.size()==3 and not(s.refreshStop))
 val allProps=refreshBound and seedDrained and order and bound and guardedEffect and normalClosure and noUnknownSeed and seedAuthority and fixedDeadline
 action step={nondet e=Set(Prepare,Register,Gate,Guard,Effect(true),Effect(false),Receipt({shape:true,nonce:true,count:6}),Receipt({shape:false,nonce:true,count:6}),Receipt({shape:true,nonce:false,count:6}),Receipt({shape:true,nonce:true,count:5}),Confirm,Exit,Gone,Cancel,Material,Native,Output,Tick(1),Tick(10),Tick(20),StartRefresh(0),StartRefresh(1),StartRefresh(2),StartRefresh(3),FinishRefresh({index:0,ok:true}),FinishRefresh({index:1,ok:true}),FinishRefresh({index:2,ok:true}),FinishRefresh({index:0,ok:false}),Seed).oneOf();fire(e)}
}
