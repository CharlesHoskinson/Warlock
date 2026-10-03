module batch_service_binding {
 type Selection={outer:int,baseline:int,recovery:int,loaded:int,token:int,coverage:Set[int],complete:bool,paths:bool,hashes:bool,modes:bool}
 type Batch={moduleToken:int,ownerToken:int,exactClass:bool,sameCommands:bool,sameRoot:bool,samePreview:bool,callbacks:bool}
 type Event=Observe(Selection)|Owner(int)|Link(Batch)|Original(bool)|Finish({moduleToken:int,ownerToken:int,callbacks:bool,normalCleanup:bool})|Accept|Refuse
 type State={moduleToken:int,ownerToken:int,modules:bool,batch:bool,original:bool,final:bool,accepted:bool,refused:bool}
 var s:State
 action init=s'={moduleToken:0,ownerToken:0,modules:false,batch:false,original:false,final:false,accepted:false,refused:false}
 pure val required=1.to(19)
 pure def exact(p:Selection):bool=p.outer==23 and p.baseline==23 and p.recovery==23 and p.loaded==23 and p.token>0 and p.coverage==required and p.complete and p.paths and p.hashes and p.modes
 action fire(e:Event):bool=s'=if(s.refused)s else match e {
 | Observe(p)=>if(exact(p) and (s.moduleToken==0 or s.moduleToken==p.token)){...s,modules:true,moduleToken:p.token}else {...s,refused:true,accepted:false}
 | Owner(token)=>if(token>0 and (s.ownerToken==0 or s.ownerToken==token)){...s,ownerToken:token}else {...s,refused:true,accepted:false}
 | Link(p)=>if(s.modules and s.ownerToken>0 and p.moduleToken==s.moduleToken and p.ownerToken==s.ownerToken and p.exactClass and p.sameCommands and p.sameRoot and p.samePreview and p.callbacks){...s,batch:true}else {...s,refused:true,accepted:false}
 | Original(yes)=>{...s,original:yes,accepted:false}
 | Finish(p)=>if(s.modules and s.batch and p.moduleToken==s.moduleToken and p.ownerToken==s.ownerToken and p.callbacks and p.normalCleanup){...s,final:true}else {...s,refused:true,accepted:false}
 | Accept=>{...s,accepted:s.modules and s.batch and s.ownerToken>0 and s.original and s.final}
 | Refuse=>{...s,refused:true,accepted:false}
 }
 val allProps=s.accepted implies s.modules and s.batch and s.ownerToken>0 and s.original and s.final and not(s.refused)
 action step={nondet n=Set(20,22,23).oneOf();nondet yes=Set(true,false).oneOf();nondet token=Set(1,2).oneOf();nondet e=Set(Observe({outer:23,baseline:n,recovery:23,loaded:n,token:token,coverage:if(yes)required else 1.to(18),complete:yes,paths:true,hashes:true,modes:true}),Owner(token),Link({moduleToken:token,ownerToken:token,exactClass:yes,sameCommands:true,sameRoot:true,samePreview:true,callbacks:true}),Original(yes),Finish({moduleToken:token,ownerToken:token,callbacks:yes,normalCleanup:yes}),Accept,Refuse).oneOf();fire(e)}
}
