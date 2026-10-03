module process_observation {
 type State={registered:bool,registrationRefused:bool,observed:bool,live:bool,
   observationRefused:bool,unavailableProved:bool,normalExit:bool,terminalCount:int,
   accepted:bool,acceptProved:bool}
 var s:State
 pure val initial={registered:false,registrationRefused:false,observed:false,live:false,
   observationRefused:false,unavailableProved:true,normalExit:false,terminalCount:0,
   accepted:false,acceptProved:true}
 action init=s'=initial
 action registered=s'={...initial,registered:true}
 action register(kind:int,errno:int):bool=s'=if(kind==0 and errno==0)
   {...s,registered:true,accepted:false} else {...s,registrationRefused:true,accepted:false}
 action observe(kind:int,errno:int):bool=s'=if(not(s.registered))
   {...s,observationRefused:true,accepted:false} else if(kind==0 and errno==0)
   {...s,observed:true,live:true,accepted:false} else if(kind==1 and errno==0)
   {...s,observed:true,live:false,accepted:false} else if(kind==2 and (errno==2 or errno==3))
   {...s,observed:true,live:false,accepted:false,unavailableProved:s.unavailableProved and (errno==2 or errno==3)}
   else {...s,observationRefused:true,accepted:false}
 action terminal(normal:bool):bool=s'={...s,normalExit:normal,terminalCount:s.terminalCount+1,accepted:false}
 action accept={
   val allow=s.registered and s.observed and not(s.live) and not(s.observationRefused)
      and not(s.registrationRefused) and s.normalExit and s.terminalCount==1
   s'={...s,accepted:allow,acceptProved:s.acceptProved and (not(allow) or
      (s.normalExit and s.terminalCount==1 and s.observed and not(s.live)))}
 }
 val allProps=s.acceptProved and s.unavailableProved
   and (s.accepted implies s.registered and s.normalExit and s.terminalCount==1)
 action step={
   nondet operation=Set(0,1,2,3).oneOf()
   nondet kind=Set(0,1,2,3).oneOf()
   nondet errno=Set(0,1,2,3,5,13,99).oneOf()
   if(operation==0)register(kind,errno) else if(operation==1)observe(kind,errno)
   else if(operation==2)terminal(kind==0) else accept
 }
}
