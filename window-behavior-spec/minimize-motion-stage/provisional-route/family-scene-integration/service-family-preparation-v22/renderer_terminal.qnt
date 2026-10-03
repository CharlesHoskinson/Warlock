module renderer_terminal {
 type Life=Live|Zombie|Absent|Reused
 type State={life:Life,exact:bool,readable:bool,terminal:bool,helpers:bool,uncertain:bool,retired:bool,ack:bool,disposed:bool,write:bool}
 var s:State
 action init=s'={life:Live,exact:true,readable:true,terminal:false,helpers:false,uncertain:false,retired:false,ack:false,disposed:false,write:false}
 action observe(l:Life,exact:bool,readable:bool):bool=s'={...s,life:l,exact:exact,readable:readable,terminal:exact and readable and l!=Live}
 action helper(closed:bool,uncertain:bool):bool=s'={...s,helpers:closed,uncertain:s.uncertain or uncertain}
 action retire=s'=if(s.terminal and s.helpers and not(s.uncertain)){...s,retired:true} else s
 action ack=s'=if(s.terminal and s.helpers and s.retired and not(s.uncertain)){...s,ack:true} else s
 action dispose=s'=if(s.terminal and s.helpers and s.retired and s.ack and not(s.uncertain)){...s,disposed:true} else s
 val allProps=(s.ack implies s.retired) and (s.disposed implies(s.ack and s.retired)) and not(s.write)
 action step=any{nondet l=Set(Live,Zombie,Absent,Reused).oneOf();nondet e=Set(true,false).oneOf();nondet r=Set(true,false).oneOf();observe(l,e,r),helper(true,false),helper(false,false),helper(true,true),retire,ack,dispose}
}
