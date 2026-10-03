module renderer_job_role {
 type Scalar=Integer(int)|Boolean(bool)|Decimal(int)|Text(str)|Null
 pure val typedOwner=Map("actor"->Integer(17),"ownership.pid"->Integer(101),"ownership.start"->Integer(7),"ownership.producer.device"->Integer(1),"ownership.producer.inode"->Integer(5),"ownership.producer.size"->Integer(1000),"ownership.producer.sha256"->Text("selected"),"ownership.environment.session"->Text("private"))
 type Role=Renderer|Helper|NativeExport|NativeEffect|Unknown
 type Phase=Gated|Released|Closed
 type Binding={actor:int,job:int,keeper:int,transport:int,launch:int,child:int,pid:int,start:int,producer:int,environment:int}
 type Job={role:Role,phase:Phase,binding:Binding}
 type Observation={keeper:bool,objects:bool,ownership:bool,kernel:bool,executed:bool,argv:bool,alive:bool,stable:bool,wrapperTyped:bool,wrapperPID:bool,registryTypes:str->Scalar,launchTypes:str->Scalar}
 type State={bound:bool,binding:Binding,jobs:Set[Job],observation:Observation,permitted:bool,bindRefused:bool}
 type Event=Bind(Binding)|Jobs(Set[Job])|Observe(Observation)|Check
 pure val good={actor:17,job:1,keeper:1,transport:1,launch:1,child:1,pid:101,start:7,producer:23,environment:1}
 pure val healthy={keeper:true,objects:true,ownership:true,kernel:true,executed:true,argv:true,alive:true,stable:true,wrapperTyped:true,wrapperPID:true,registryTypes:typedOwner,launchTypes:typedOwner}
 pure val renderer={role:Renderer,phase:Released,binding:good}
 pure def validBinding(b:Binding):bool=b==good
 pure def verified(o:Observation):bool=o.keeper and o.objects and o.ownership and o.kernel and o.executed and o.argv and o.alive and o.stable and o.wrapperTyped and o.wrapperPID and o.registryTypes==typedOwner and o.launchTypes==typedOwner
 pure def allowed(s:State):bool={val own=s.jobs.filter(j=>j.binding.actor==17);if(not(s.bound))own.size()==0 and s.observation.keeper else validBinding(s.binding) and verified(s.observation) and own==Set(renderer)}
 var s:State
 action init=s'={bound:false,binding:good,jobs:Set(),observation:healthy,permitted:false,bindRefused:false}
 action fire(e:Event):bool=s'=match e {
 |Bind(b)=>if(not(s.bound) and validBinding(b)){...s,bound:true,binding:b,permitted:false,bindRefused:false}else {...s,permitted:false,bindRefused:true}
 |Jobs(rows)=>{...s,jobs:rows,permitted:false}
 |Observe(o)=>{...s,observation:o,permitted:false}
 |Check=>{...s,permitted:allowed(s)}
 }
 val allProps=s.permitted implies allowed(s)
 action step={nondet role=Set(Renderer,Helper,NativeExport,NativeEffect,Unknown).oneOf();nondet phase=Set(Gated,Released,Closed).oneOf();nondet actor=Set(17,18).oneOf();nondet foreign=Set(1,2).oneOf();nondet goodFlag=Set(true,false).oneOf();val b={...good,actor:actor,job:foreign,transport:foreign};val row={role:role,phase:phase,binding:b};val o={...healthy,objects:goodFlag,kernel:goodFlag,stable:goodFlag};nondet e=Set(Bind(b),Jobs(Set(row)),Jobs(Set(renderer,row)),Jobs(Set()),Observe(o),Check).oneOf();fire(e)}
}
