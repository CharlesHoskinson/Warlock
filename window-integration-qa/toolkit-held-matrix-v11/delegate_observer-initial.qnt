module delegate_observer {
 type State={auth:bool,own:bool,route:bool,source:bool,gate:bool,boot:bool,traced:bool,exec:bool,pending:bool,bytes:bool,paired:bool,error:bool,exit:bool,wait:bool,normal:bool,accepted:bool,mutation:bool,forwards:int}
 var s:State
 action init=s'={auth:true,own:true,route:true,source:true,gate:false,boot:false,traced:false,exec:false,pending:false,bytes:false,paired:true,error:false,exit:false,wait:false,normal:false,accepted:false,mutation:false,forwards:0}
 action authorize(auth:bool,own:bool,source:bool):bool=s'={...s,auth:auth,own:own,source:source}
 action gate=s'=if(s.auth and s.own and s.source and s.route){...s,gate:true} else {...s,error:true}
 action bootstrap(exact:bool):bool=s'=if(s.gate and exact and s.own){...s,boot:true,traced:true} else {...s,error:true}
 action exec(exact:bool):bool=s'=if(s.traced and exact and s.own and s.source){...s,exec:true} else {...s,error:true}
 action enter(complete:bool,bounded:bool,fd:bool):bool=s'=if(s.traced and s.exec and s.own and s.route and complete and bounded and fd and not(s.pending)){...s,pending:true,bytes:true} else {...s,error:true}
 action result(exact:bool):bool=s'=if(s.pending and exact){...s,pending:false} else {...s,error:true,paired:false}
 action signal(genuine:bool):bool=s'=if(s.traced and genuine){...s,forwards:s.forwards+1} else {...s,error:true}
 action unknown=s'={...s,error:true}
 action detach=s'={...s,traced:false,pending:false}
 action exited(normal:bool):bool=s'={...s,exit:true,normal:normal}
 action waited(exact:bool):bool=s'=if(s.exit and exact and s.own){...s,wait:true,accepted:not(s.error) and s.normal and not(s.pending) and s.boot and s.exec} else {...s,error:true}
 val allProps=not(s.mutation) and s.route and (s.accepted implies(s.auth and s.own and s.source and s.wait and s.exit and s.normal and s.boot and s.exec and not(s.error) and s.paired and not(s.pending)))
 action step=any{gate,bootstrap(true),bootstrap(false),exec(true),exec(false),enter(true,true,true),enter(false,true,true),enter(true,false,true),enter(true,true,false),result(true),result(false),signal(true),signal(false),unknown,detach,exited(true),exited(false),waited(true),waited(false)}
}
