module service_queries {
  var registered: bool
  var executed: bool
  var targets: List[int]
  var refresh: int
  var refused: bool
  var stopped: bool
  var accepted: bool
  action init = all { registered'=false,executed'=false,targets'=List(0,0,0),refresh'=0,refused'=false,stopped'=false,accepted'=false }
  action register = all { not(executed),registered'=true,executed'=executed,targets'=targets,refresh'=refresh,refused'=refused,stopped'=stopped,accepted'=accepted }
  action exec = all { registered,not(executed),executed'=true,registered'=registered,targets'=targets,refresh'=refresh,refused'=refused,stopped'=stopped,accepted'=accepted }
  action target = {
    nondet member = Set(0,1,2).oneOf()
    all { registered,executed,not(stopped),targets.nth(member)<2,
      targets'=targets.replaceAt(member,targets.nth(member)+1),registered'=registered,executed'=executed,refresh'=refresh,refused'=refused,stopped'=stopped,accepted'=accepted }
  }
  action refreshQuery = all { registered,executed,not(stopped),refresh<3,refresh'=refresh+1,
    registered'=registered,executed'=executed,targets'=targets,refused'=refused,stopped'=stopped,accepted'=accepted }
  action refuse = all { refused'=true,registered'=registered,executed'=executed,targets'=targets,refresh'=refresh,stopped'=stopped,accepted'=false }
  action stop = all { stopped'=true,registered'=registered,executed'=executed,targets'=targets,refresh'=refresh,refused'=refused,accepted'=accepted }
  action accept = all { stopped,not(refused),targets==List(2,2,2),refresh==3,accepted'=true,
    registered'=registered,executed'=executed,targets'=targets,refresh'=refresh,refused'=refused,stopped'=stopped }
  action idle = all { registered'=registered,executed'=executed,targets'=targets,refresh'=refresh,refused'=refused,stopped'=stopped,accepted'=accepted }
  action step = any { register,exec,target,refreshQuery,refuse,stop,accept,idle }
  val invariant = all { executed implies registered,targets.indices().forall(i=>targets.nth(i)>=0 and targets.nth(i)<=2),refresh>=0 and refresh<=3,
    accepted implies all { stopped,not(refused),targets==List(2,2,2),refresh==3 } }
  run registerBeforeExecTest = init.then(register).then(exec).then(all { assert(executed and registered and invariant),idle })
  run boundedMemberQueryTest = init.then(register).then(exec).then(target).then(target).then(all { assert(targets.foldl(0,(a,b)=>a+b)==2 and invariant),idle })
  run unknownQueryRefusesAcceptanceTest = init.then(register).then(exec).then(refuse).then(stop).then(all { assert(refused and not(accepted) and invariant),idle })
  run incompleteQueriesCannotAcceptTest = init.then(register).then(exec).then(target).then(stop).then(all { assert(not(accepted) and invariant),idle })
}
