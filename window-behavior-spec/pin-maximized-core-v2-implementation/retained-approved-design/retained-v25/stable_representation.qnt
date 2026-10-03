module stable_representation {
 type Event=Select({textType:bool,canonical:bool,bounded:bool,exact:bool,pidInteger:bool})|Query|Read({typed:bool,equal:bool})|Complete|Mutation
 type State={valid:bool,queried:bool,received:bool,complete:bool,writes:int}
 var s:State
 action init=s'={valid:false,queried:false,received:false,complete:false,writes:0}
 action fire(e:Event):bool={s'=match e{
 |Select(v)=>{...s,valid:v.textType and v.canonical and v.bounded and v.exact and v.pidInteger,queried:false,received:false,complete:false}
 |Query=>{...s,queried:s.valid,complete:false}
 |Read(v)=>{...s,received:s.queried and s.valid and v.typed and v.equal,complete:false}
 |Complete=>{...s,complete:s.valid and s.queried and s.received}
 |Mutation=>s
 }}
 val allProps=all{s.writes==0,s.complete implies s.valid and s.queried and s.received,s.queried implies s.valid}
 action step={nondet a=Set(true,false).oneOf();nondet b=Set(true,false).oneOf();nondet c=Set(true,false).oneOf();nondet d=Set(true,false).oneOf();nondet f=Set(true,false).oneOf();nondet e=Set(Select({textType:a,canonical:b,bounded:c,exact:d,pidInteger:f}),Query,Read({typed:a,equal:b}),Complete,Mutation).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),s'=s}
 pure val exact={textType:true,canonical:true,bounded:true,exact:true,pidInteger:true}
 run exactHexStringPassTest=init.then(fire(Select(exact))).then(fire(Query)).then(fire(Read({typed:true,equal:true}))).then(fire(Complete)).then(check(s.complete and s.writes==0))
 run numericStableRefusedTest=init.then(fire(Select({...exact,textType:false}))).then(fire(Query)).then(check(not(s.queried)))
 run noncanonicalRefusedTest=init.then(fire(Select({...exact,canonical:false}))).then(fire(Query)).then(check(not(s.queried)))
 run overflowRefusedTest=init.then(fire(Select({...exact,bounded:false}))).then(fire(Query)).then(check(not(s.queried)))
 run foreignValueRefusedTest=init.then(fire(Select({...exact,exact:false}))).then(fire(Query)).then(check(not(s.queried)))
 run boolPIDRefusedTest=init.then(fire(Select({...exact,pidInteger:false}))).then(fire(Query)).then(check(not(s.queried)))
 run differentReplyRefusedTest=init.then(fire(Select(exact))).then(fire(Query)).then(fire(Read({typed:true,equal:false}))).then(fire(Complete)).then(check(not(s.complete)))
}
