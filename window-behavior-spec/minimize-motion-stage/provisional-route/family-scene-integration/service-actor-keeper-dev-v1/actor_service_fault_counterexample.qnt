module actor_service_fault_counterexample {
 import actor_service_binding.* from "./retained-initial-model/actor_service_binding"
 action check(p:bool):bool=all{assert(p),s'=s}
 run lateFailureMustRevokeCurrentClosureClaimTest=init.then(fire(Register(true)))
   .then(fire(Release)).then(fire(ActualReturn(true)))
   .then(fire(Semantic({exact:true,durable:true}))).then(fire(KeeperAck(true)))
   .then(fire(ServicePublication(true))).then(fire(PhysicalGone)).then(fire(Close))
   .then(check(s.closed)).then(fire(ServicePublication(false)))
   .then(check(allProps))
}
