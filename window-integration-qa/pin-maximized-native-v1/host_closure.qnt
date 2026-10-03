module host_closure {
 type Row={role:int,registered:bool,identity:bool,reaped:bool,rc:int,term:bool,kill:bool,error:bool}
 pure val core:Row={role:1,registered:true,identity:true,reaped:true,rc:0,term:true,kill:false,error:false}
 pure def normal(r:Row):bool=all {r.registered,r.identity,r.reaped,not(r.kill),not(r.error),r.role.in(Set(1,2,3)),r.rc==0 or (r.role==3 and r.rc == -15 and r.term)}
 pure def accepted(a:Row,b:Row,c:Row,clientsGone:bool,reverseOrder:bool,originalGates:bool):bool=all {a.role==1,b.role==2,c.role==3,normal(a),normal(b),normal(c),clientsGone,reverseOrder,originalGates}
 var row:Row
 action init={row'=core}
 action check(ok:bool):bool=all{assert(ok),row'=row}
 action step={
  nondet role=0.to(4).oneOf()
  nondet registered=Set(true,false).oneOf()
  nondet identity=Set(true,false).oneOf()
  nondet reaped=Set(true,false).oneOf()
  nondet rc=Set(-15,-9,-6,0,1).oneOf()
  nondet term=Set(true,false).oneOf()
  nondet kill=Set(true,false).oneOf()
  nondet error=Set(true,false).oneOf()
  row'={role:role,registered:registered,identity:identity,reaped:reaped,rc:rc,term:term,kill:kill,error:error}
 }
 val allProps=all {normal(row) implies not(row.kill),normal(row) implies row.reaped,normal(row) and row.role!=3 implies row.rc==0,normal(row) and row.rc == -15 implies (row.role==3 and row.term),normal(row) implies (row.registered and row.identity and not(row.error))}
 run healthyCore=init.then(check(normal(core)))
 run healthyWeston=init.then(check(normal(core.with("role",2))))
 run namedBusTerm=init.then(check(normal(core.with("role",3).with("rc",-15))))
 run coreTermRefused=init.then(check(not(normal(core.with("rc",-15)))))
 run killEvenZeroRefused=init.then(check(not(normal(core.with("kill",true)))))
 run incompleteRefused=init.then(check(not(normal(core.with("reaped",false)))))
 run wrongLifetimeRefused=init.then(check(not(normal(core.with("identity",false)))))
 run stopErrorRefused=init.then(check(not(normal(core.with("error",true)))))
 run unknownRoleRefused=init.then(check(not(normal(core.with("role",4)))))
 run busUnwitnessedTermRefused=init.then(check(not(normal(core.with("role",3).with("rc",-15).with("term",false)))))
 run clientsFirstRequired=init.then(check(not(accepted(core,core.with("role",2),core.with("role",3),false,true,true))))
 run reverseOrderRequired=init.then(check(not(accepted(core,core.with("role",2),core.with("role",3),true,false,true))))
 run originalGatesRequired=init.then(check(not(accepted(core,core.with("role",2),core.with("role",3),true,true,false))))
}
