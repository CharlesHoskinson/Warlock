module service_restart {
 type State={pid:int,start:int,oldLive:bool,source:int,members:int,queries:int,accepted:bool}
 var s:State
 action init=s'={pid:1,start:1,oldLive:true,source:1,members:1,queries:2,accepted:false}
 action close=s'={...s,oldLive:false}
 action replace(pid:int,start:int,source:int,members:int):bool=s'=if(not(s.oldLive) and pid>0 and start>0 and (pid!=s.pid or start!=s.start) and source==s.source and members==s.members){...s,pid:pid,start:start,oldLive:true,accepted:true} else {...s,accepted:false}
 val allProps=s.queries==2 and s.source==1 and s.members==1
 action step=any{close,replace(2,2,1,1),replace(1,2,1,1),replace(1,1,1,1),replace(2,2,2,1),replace(2,2,1,2),replace(0,2,1,1)}
}
