/** Stop may report idle without connecting only when no live daemon/lock and
 * no accepted pending journal exists. It never launches a daemon or discards
 * journal state. A submitted shutdown uses its acknowledgement exactly once. */
module stop_contract {
 var running:bool
 var busy:bool
 var pending:bool
 var listener:bool
 var ok:bool
 var submitted:int
 var spawned:int
 action init=all{running'=false,busy'=false,pending'=false,listener'=false,ok'=false,submitted'=0,spawned'=0}
 action configure(r:bool,b:bool,p:bool,l:bool):bool=all{running'=r,busy'=b,pending'=p,listener'=l,ok'=false,submitted'=submitted,spawned'=spawned}
 action stop=if(listener)all{running'=false,busy'=false,pending'=false,listener'=false,ok'=true,submitted'=submitted+1,spawned'=spawned}
  else all{running'=running,busy'=busy,pending'=pending,listener'=listener,ok'=(not(running) and not(busy) and not(pending)),submitted'=submitted,spawned'=spawned}
 action step=any{stop,configure(true,true,false,false),configure(false,false,true,false),configure(true,true,true,true),configure(false,false,false,false)}
 val noSpawn=spawned==0
 val idleSuccess=ok implies not(running) and not(busy) and not(pending)
 val allProps=noSpawn and idleSuccess
}
