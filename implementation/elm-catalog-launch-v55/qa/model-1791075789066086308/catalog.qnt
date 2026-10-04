module catalog {
 type State={generation:int,shown:int,lifetime:int,shownLifetime:int,available:bool,present:bool,last:int,lastGeneration:int,lastLifetime:int,lastEntry:bool,journal:str,status:str,attempts:int,previousAttempts:int,replay:bool,admitted:bool}
 var s:State
 action init=s'={generation:1,shown:1,lifetime:1,shownLifetime:1,available:true,present:true,last:0,lastGeneration:0,lastLifetime:0,lastEntry:false,journal:"Idle",status:"Idle",attempts:0,previousAttempts:0,replay:false,admitted:false}
 pure def eligible(state:State):bool=state.available and state.present and state.shown==state.generation and state.shownLifetime==state.lifetime
 action submit(result:str):bool=s'={...s,last:s.last+1,lastGeneration:s.shown,lastLifetime:s.shownLifetime,lastEntry:s.present,journal:if(eligible(s)) result else "Refused",status:if(eligible(s)) result else "Refused",attempts:s.attempts+(if(eligible(s)) 1 else 0),previousAttempts:s.attempts,replay:false,admitted:eligible(s)}
 action retry=all{s.last>0,s'={...s,status:if(s.lastLifetime==s.lifetime) s.journal else "Refused",previousAttempts:s.attempts,replay:true,admitted:false}}
 action reuse=all{s.last>0,s'={...s,status:"Refused",previousAttempts:s.attempts,replay:true,admitted:false}}
 action change=s'={...s,generation:s.generation+1,status:"Idle",previousAttempts:s.attempts,replay:false,admitted:false}
 action retire=s'={...s,lifetime:s.lifetime+1,status:"Idle",previousAttempts:s.attempts,replay:false,admitted:false}
 action refresh=s'={...s,shown:s.generation,shownLifetime:s.lifetime,available:true,status:"Idle",previousAttempts:s.attempts,replay:false,admitted:false}
 action overflow=s'={...s,available:false,status:"Idle",previousAttempts:s.attempts,replay:false,admitted:false}
 action remove=s'={...s,present:false,generation:s.generation+1,status:"Idle",previousAttempts:s.attempts,replay:false,admitted:false}
 action step=any{submit("Submitted"),submit("Unknown"),retry,reuse,change,retire,refresh,overflow,remove}
 val safety=all{s.attempts>=s.previousAttempts,s.attempts<=s.previousAttempts+1,s.replay implies s.attempts==s.previousAttempts,s.admitted implies eligible(s),s.status=="Submitted" implies s.journal=="Submitted",s.status=="Unknown" implies s.journal=="Unknown",s.status=="Refused" implies s.attempts==s.previousAttempts}
 run submittedTest=init.then(submit("Submitted")).then(all{assert(s.status=="Submitted" and s.attempts==1),s'=s})
 run unknownTest=init.then(submit("Unknown")).then(retry).then(all{assert(s.status=="Unknown" and s.attempts==1),s'=s})
 run retryTest=init.then(submit("Submitted")).then(retry).then(all{assert(s.status=="Submitted" and s.attempts==1),s'=s})
 run reuseTest=init.then(submit("Submitted")).then(reuse).then(all{assert(s.status=="Refused" and s.attempts==1),s'=s})
 run staleTest=init.then(change).then(submit("Submitted")).then(all{assert(s.status=="Refused" and s.attempts==0),s'=s})
 run retiredTest=init.then(submit("Submitted")).then(retire).then(retry).then(all{assert(s.status=="Refused" and s.attempts==1),s'=s})
 run overflowTest=init.then(overflow).then(submit("Submitted")).then(all{assert(s.status=="Refused" and s.attempts==0),s'=s})
 run removedTest=init.then(remove).then(refresh).then(submit("Submitted")).then(all{assert(s.status=="Refused" and s.attempts==0),s'=s})
}
