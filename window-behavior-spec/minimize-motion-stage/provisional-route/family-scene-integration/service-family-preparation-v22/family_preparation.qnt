module family_preparation {
 type Event=Capture({id:int,exact:bool})|BeginBatch|HelperClosed({normal:bool,outputs:bool})|CheckCurrent(bool)|Publish(int)|Seed|NativeReady|Supersede|Dispose
 type State={sources:Set[int],helper:bool,helperGone:bool,generated:bool,fresh:bool,published:Set[int],current:bool,seeded:bool,nativeCommitted:bool,commitWitness:bool,disposed:bool,failed:bool,launches:int,deadline:int}
 var s:State
 val family=Set(1,2,3)
 action init=s'={sources:Set(),helper:false,helperGone:true,generated:false,fresh:false,published:Set(),current:true,seeded:false,nativeCommitted:false,commitWitness:false,disposed:false,failed:false,launches:0,deadline:2}
 action fire(e:Event):bool={s'=match e {
 | Capture(p)=>if(s.current and not(s.disposed) and not(s.failed) and p.exact and family.contains(p.id) and not(s.sources.contains(p.id))){...s,sources:s.sources.union(Set(p.id))} else {...s,failed:true}
 | BeginBatch=>if(s.current and not(s.disposed) and not(s.failed) and s.sources==family and s.launches==0){...s,helper:true,helperGone:false,launches:1} else {...s,failed:true}
 | HelperClosed(p)=>if(s.helper){...s,helper:false,helperGone:true,generated:p.normal and p.outputs,failed:s.failed or not(p.normal and p.outputs)} else {...s,failed:true}
 | CheckCurrent(exact)=>{...s,fresh:exact,failed:s.failed or not(exact)}
 | Publish(id)=>if(s.current and s.fresh and s.generated and s.helperGone and not(s.failed) and not(s.disposed) and family.contains(id)){...s,published:s.published.union(Set(id))} else {...s,failed:true}
 | Seed=>if(s.current and s.fresh and s.generated and s.helperGone and s.published==family and s.sources==family and not(s.failed) and not(s.disposed)){...s,seeded:true} else {...s,failed:true}
 | NativeReady=>if(s.current and s.seeded and s.fresh and s.helperGone and s.published==family and not(s.failed) and not(s.disposed)){...s,nativeCommitted:true,commitWitness:true} else {...s,failed:true}
 | Supersede=>{...s,current:false,fresh:false}
 | Dispose=>if(not(s.current) and s.helperGone){...s,disposed:true} else {...s,failed:true}
 }}
 val allProps=s.deadline==2 and s.launches<=1 and s.sources.subseteq(family) and s.published.subseteq(family)
  and (s.generated implies s.helperGone and s.sources==family) and (s.disposed implies s.helperGone and not(s.current))
  and (s.seeded implies s.sources==family and s.published==family and s.generated and s.helperGone)
  and (s.nativeCommitted implies s.commitWitness and s.seeded and s.published==family)
 action step={nondet id=1.to(4).oneOf();nondet e=Set(Capture({id:id,exact:true}),Capture({id:id,exact:false}),BeginBatch,HelperClosed({normal:true,outputs:true}),HelperClosed({normal:true,outputs:false}),HelperClosed({normal:false,outputs:true}),CheckCurrent(true),CheckCurrent(false),Publish(id),Seed,NativeReady,Supersede,Dispose).oneOf();fire(e)}
}
