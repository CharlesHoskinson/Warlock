module readonly_current_close {
 type Event=BeginAppend|Write(bool)|Publish(bool)|Adopt|Borrow|Release|CorruptOld|NormalClose(bool)|Crash
 type State={pending:bool,file:bool,published:bool,borrowers:int,fullCurrent:bool,fault:bool,closed:bool,ackNow:bool,retained:bool,nativeEffects:int}
 var s:State
 action init=s'={pending:false,file:false,published:false,borrowers:0,fullCurrent:true,fault:false,closed:false,ackNow:false,retained:true,nativeEffects:0}
 action fire(e:Event):bool={val b={...s,ackNow:false};s'=if(s.fault)b else match e {
 | BeginAppend=>if(not(s.pending) and not(s.closed)){...b,pending:true,file:false,published:false} else {...b,fault:true}
 | Write(ok)=>if(s.pending and ok){...b,file:true} else {...b,fault:true}
 | Publish(ok)=>if(s.pending and s.file and ok){...b,published:true} else {...b,fault:true}
 | Adopt=>if(s.pending and s.file and s.published){...b,pending:false,file:false,published:false} else {...b,fault:true}
 | Borrow=>if(not(s.closed) and s.borrowers<2){...b,borrowers:s.borrowers+1} else {...b,fault:true}
 | Release=>if(s.borrowers>0){...b,borrowers:s.borrowers-1} else {...b,fault:true}
 | CorruptOld=>{...b,fullCurrent:false}
 | NormalClose(audit)=>if(not(s.pending) and s.borrowers==0 and audit and s.fullCurrent){...b,closed:true,ackNow:true} else b
 | Crash=>{...b,closed:true,ackNow:false}
 }}
 val allProps=s.retained and s.nativeEffects==0 and (s.ackNow implies(s.closed and not(s.pending) and s.borrowers==0 and s.fullCurrent and not(s.fault)))
 action step={nondet yes=Set(true,false).oneOf();nondet e=Set(BeginAppend,Write(yes),Publish(yes),Adopt,Borrow,Release,CorruptOld,NormalClose(yes),Crash).oneOf();fire(e)}
}
