module helper_closure {
 type Event=Reserve|Gate({exact:bool,isolated:bool,noEscape:bool})|Register({peer:bool,descriptor:bool})|Publish|Release|LeaderExit|DescendantExit|Escape|ServiceDeath|KeeperDeath|Signal|Terminal|Delete
 type State={reserved:bool,gate:bool,isolated:bool,noEscape:bool,registered:bool,published:bool,released:bool,leaderAlive:bool,descendantAlive:bool,escaped:bool,serviceDead:bool,keeperAlive:bool,signaled:bool,terminal:bool,deleted:bool}
 var s:State
 action init=s'={reserved:false,gate:false,isolated:false,noEscape:false,registered:false,published:false,released:false,leaderAlive:false,descendantAlive:false,escaped:false,serviceDead:false,keeperAlive:true,signaled:false,terminal:false,deleted:false}
 action fire(e:Event):bool={val b={...s,signaled:false};s'=if(s.deleted)b else if(s.terminal){...b,deleted:s.deleted or e==Delete} else match e {
 | Reserve=>{...b,reserved:true}
 | Gate(p)=>if(s.reserved and not(s.gate) and p.exact){...b,gate:true,isolated:p.isolated,noEscape:p.noEscape,leaderAlive:true} else b
 | Register(p)=>if(s.gate and s.leaderAlive and s.isolated and s.noEscape and s.keeperAlive and p.peer and p.descriptor){...b,registered:true} else b
 | Publish=>if(s.registered){...b,published:true} else b
 | Release=>if(s.registered and s.published and s.keeperAlive and s.leaderAlive and not(s.released) and not(s.serviceDead)){...b,released:true,descendantAlive:true} else b
 | LeaderExit=>{...b,leaderAlive:false}
 | DescendantExit=>{...b,descendantAlive:false}
 | Escape=>if(s.released and not(s.noEscape)){...b,escaped:true} else b
 | ServiceDeath=>{...b,serviceDead:true}
 | KeeperDeath=>{...b,keeperAlive:false}
 | Signal=>if(s.serviceDead and s.keeperAlive and s.registered){...b,signaled:true,leaderAlive:false,descendantAlive:false} else b
 | Terminal=>if(s.keeperAlive and s.registered and s.published and not(s.leaderAlive) and not(s.descendantAlive) and not(s.escaped)){...b,terminal:true} else b
 | Delete=>if(s.terminal){...b,deleted:true} else b
 }}
 val allProps=(s.released implies(s.registered and s.published and s.isolated and s.noEscape)) and (s.signaled implies(s.serviceDead and s.keeperAlive and s.registered)) and (s.terminal implies(s.published and s.registered and not(s.leaderAlive) and not(s.descendantAlive) and not(s.escaped))) and (s.deleted implies(s.terminal))
 action step={nondet e=Set(Reserve,Gate({exact:true,isolated:true,noEscape:true}),Gate({exact:true,isolated:false,noEscape:true}),Gate({exact:true,isolated:true,noEscape:false}),Gate({exact:false,isolated:true,noEscape:true}),Register({peer:true,descriptor:true}),Register({peer:false,descriptor:true}),Register({peer:true,descriptor:false}),Publish,Release,LeaderExit,DescendantExit,Escape,ServiceDeath,KeeperDeath,Signal,Terminal,Delete).oneOf();fire(e)}
}
