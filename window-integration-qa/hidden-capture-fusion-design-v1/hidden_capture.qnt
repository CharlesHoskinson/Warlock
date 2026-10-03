module hidden_capture {
 type Event = ValidateCache | CaptureClient | Launch | Returned(bool) | ObserveCurrent | PublishSlot(int) | PublishIdentity | ReturnSource | Fail | Timeout | CloseUnknown | Discard | NativeChange | MaterialChange | Cancel | Tick(int) | FreshFamily | Seed
 var s:{phase:int,currentNative:bool,material:bool,receiptCurrent:bool,now:int,deadline:int,cache:bool,raw:bool,active:bool,normal:bool,outputs:bool,checked:bool,slots:Set[int],published:bool,sources:int,quarantined:bool,discarded:bool,familyFresh:bool,seeded:bool,justPublish:bool,justSeed:bool}
 pure val initial={phase:0,currentNative:true,material:true,receiptCurrent:true,now:0,deadline:20,cache:false,raw:false,active:false,normal:false,outputs:false,checked:false,slots:Set(),published:false,sources:0,quarantined:false,discarded:false,familyFresh:false,seeded:false,justPublish:false,justSeed:false}
 action init=s'=initial
 pure def advance(a,e)={
  val b={...a,justPublish:false,justSeed:false}
  match e {
   | ValidateCache=>if(a.phase==0 and a.currentNative and a.material and not(a.quarantined) and a.sources<3){...b,phase:1,cache:true,normal:false,outputs:false,checked:false,slots:Set(),published:false,raw:false}else b
   | CaptureClient=>if(a.phase==1 and a.cache and a.currentNative and a.material){...b,phase:2,raw:true}else b
   | Launch=>if(a.phase==2 and a.raw and a.cache and a.currentNative and a.material and not(a.active)){...b,phase:3,active:true}else b
   | Returned(ok)=>if(a.phase==3 and a.active){...b,phase:if(ok)4 else 8,active:false,normal:true,outputs:ok}else b
   | ObserveCurrent=>if(a.phase==4 and a.normal and a.outputs){...b,checked:a.currentNative and a.material,phase:if(a.currentNative and a.material)5 else 8}else b
   | PublishSlot(i)=>if(a.phase==5 and a.checked and a.currentNative and a.material and a.normal and a.outputs and i==a.slots.size() and i>=0 and i<2){...b,slots:a.slots.union(Set(i)),justPublish:true}else b
   | PublishIdentity=>if(a.phase==5 and a.slots==Set(0,1) and a.checked and a.currentNative and a.material and a.normal and a.outputs){...b,published:true,justPublish:true}else b
   | ReturnSource=>if(a.phase==5 and a.published and a.currentNative and a.material and a.normal and a.outputs){...b,phase:0,sources:a.sources+1,cache:false,raw:false}else b
   | Fail=>{...b,phase:8,quarantined:a.quarantined or a.active}
   | Timeout=>if(a.active){...b,phase:8,quarantined:true}else b
   | CloseUnknown=>if(a.quarantined){...b,active:false}else b
   | Discard=>if(not(a.active) and not(a.quarantined)){...b,discarded:true,phase:8}else b
   | NativeChange=>{...b,currentNative:false,familyFresh:false}
   | MaterialChange=>{...b,material:false,familyFresh:false}
   | Cancel=>{...b,receiptCurrent:false}
   | Tick(n)=>if(n>=0){...b,now:a.now+n}else b
   | FreshFamily=>if(a.sources==3 and a.phase==0 and not(a.active) and not(a.quarantined) and a.currentNative and a.material and a.receiptCurrent and a.now<a.deadline){...b,familyFresh:true}else b
   | Seed=>if(a.familyFresh and a.sources==3 and not(a.active) and not(a.quarantined) and a.currentNative and a.material and a.receiptCurrent and a.now<a.deadline){...b,seeded:true,justSeed:true}else b
  }
 }
 action fire(e)=s'=advance(s,e)
 val publication=s.justPublish implies(s.normal and not(s.active) and s.outputs and s.checked and s.currentNative and s.material)
 val noUnknownDiscard=s.quarantined implies not(s.discarded)
 val seedAuthority=s.justSeed implies(s.sources==3 and s.familyFresh and s.currentNative and s.material and s.receiptCurrent and s.now<s.deadline and not(s.active) and not(s.quarantined))
 val fixedBudget=s.deadline==20
 val bounded=s.sources>=0 and s.sources<=3 and s.slots.subseteq(Set(0,1))
 val allProps=publication and noUnknownDiscard and seedAuthority and fixedBudget and bounded
 action step={nondet e=Set(ValidateCache,CaptureClient,Launch,Returned(true),Returned(false),ObserveCurrent,PublishSlot(0),PublishSlot(1),PublishSlot(2),PublishIdentity,ReturnSource,Fail,Timeout,CloseUnknown,Discard,NativeChange,MaterialChange,Cancel,Tick(1),Tick(20),FreshFamily,Seed).oneOf();fire(e)}
}
