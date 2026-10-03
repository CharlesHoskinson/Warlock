module housekeeping_admission {
 type Owner=Free|Native|Housekeeping
 type Phase=Idle|Waiting|Admitted|Running|Registered|Replied|Closed|Published|Returned|Refused|Between|Done
 type State={now:int,owner:Owner,phase:Phase,start:int,deadline:int,round:int,registered:bool,closed:bool,eof:bool,shape:bool,authority:bool,failed:bool,everFailed:bool,published:bool,accepted:bool,admittedAt:int,returnedAt:int,networkStarts:int,releaseCount:int,nativeWaits:bool,coverage:bool}
 type Event=Begin|StartQuery|NativeTake|NativeRelease|Admit|Register|Reply({eof:bool,shape:bool})|Close|Confirm|Return|Release|Tick(int)|AuthorityChange|Error|Prune|CoverageChange
 var s:State
 pure val initial={now:0,owner:Free,phase:Idle,start:-1,deadline:-1,round:0,registered:false,closed:false,eof:false,shape:false,authority:true,failed:false,everFailed:false,published:false,accepted:false,admittedAt:-1,returnedAt:-1,networkStarts:0,releaseCount:0,nativeWaits:false,coverage:true}
 pure def live(x:State):bool=x.start>=0 and x.now<x.deadline and x.authority and not(x.failed)
 pure def fail(x:State):State={...x,failed:true,everFailed:true,accepted:false}
 pure def refuse(x:State):State={...fail(x),phase:Refused}
 pure def transition(x:State,e:Event):State=match e {
 | Tick(n)=>if(n>=0){...x,now:x.now+n}else fail(x)
 | NativeTake=>if(x.owner==Free){...x,owner:Native}else{...x,nativeWaits:true}
 | NativeRelease=>if(x.owner==Native){...x,owner:Free}else x
 | Begin=>if((x.phase==Idle or x.phase==Between)and x.round<3){...x,phase:Waiting,start:-1,deadline:-1,registered:false,closed:false,eof:false,shape:false,failed:false,published:false,accepted:false,admittedAt:-1,returnedAt:-1}else x
 | Admit=>if(x.phase==Waiting and x.owner==Free){...x,owner:Housekeeping,phase:Admitted,admittedAt:x.now}else x
 | StartQuery=>if(x.phase==Admitted and x.owner==Housekeeping){...x,phase:Running,start:x.now,deadline:x.now+6}else x
 | Register=>if(x.phase==Running and x.owner==Housekeeping and live(x)){...x,phase:Registered,registered:true,networkStarts:x.networkStarts+1}else if(x.phase==Running)refuse({...x,closed:true})else x
 | Reply(r)=>if(x.phase==Registered and x.owner==Housekeeping){...x,phase:Replied,eof:r.eof,shape:r.shape}else x
 | Close=>if(x.owner==Housekeeping and (x.phase==Registered or x.phase==Replied)){...x,phase:Closed,closed:true}else x
 | Confirm=>if(x.phase==Closed and x.owner==Housekeeping){...x,phase:Published,published:true,failed:x.failed or not(live(x)and x.eof and x.shape),everFailed:x.everFailed or not(live(x)and x.eof and x.shape)}else x
 | Return=>if(x.phase==Published and x.owner==Housekeeping and live(x)and x.closed and x.eof and x.shape){...x,phase:Returned,accepted:true,returnedAt:x.now}else if(x.phase==Published and x.owner==Housekeeping)refuse(x)else x
 | Release=>if(x.owner==Housekeeping and (x.phase==Returned or x.phase==Refused)){...x,owner:Free,phase:Between,round:x.round+1,releaseCount:x.releaseCount+1}else x
 | AuthorityChange=>{...x,authority:false}
 | Error=>if(x.owner==Housekeeping)fail(x)else x
 | CoverageChange=>{...x,coverage:false}
 | Prune=>if(x.phase==Between and x.round==3 and not(x.everFailed)and x.authority and x.coverage){...x,phase:Done}else x
 }
 action init=s'=initial
 action fire(e:Event):bool=s'=transition(s,e)
 val allProps=(s.phase==Waiting implies s.start== -1 and s.deadline== -1 and not(s.registered))and(s.registered and s.phase!=Between and s.phase!=Done implies s.owner==Housekeeping)and(s.deadline>=0 implies s.deadline-s.start==6)and(s.accepted implies s.closed and s.eof and s.shape and s.returnedAt>=s.start and s.returnedAt<s.deadline and not(s.failed))and(s.phase==Done implies s.round==3 and s.releaseCount==3 and not(s.everFailed)and s.coverage)and(s.round==s.releaseCount)and(s.owner==Native implies not(s.phase==Running or s.phase==Registered or s.phase==Replied or s.phase==Closed or s.phase==Published))
 action step={nondet n=0.to(8).oneOf();nondet e=Set(Begin,StartQuery,NativeTake,NativeRelease,Admit,Register,Reply({eof:true,shape:true}),Reply({eof:false,shape:true}),Reply({eof:true,shape:false}),Close,Confirm,Return,Release,Tick(n),AuthorityChange,Error,Prune,CoverageChange).oneOf();fire(e)}
}
