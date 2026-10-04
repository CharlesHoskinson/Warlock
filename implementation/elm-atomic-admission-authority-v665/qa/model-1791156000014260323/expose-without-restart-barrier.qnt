module admission {
 type Authority = { origins:Set[(int,int,int)], request:int, generation:int, reserved:int }
 var durable:Authority
 var visible:Authority
 var staged:Authority
 var charge:int
 var phase:int
 var ready:bool
 var exposed:bool
 val empty={origins:Set(),request:0,generation:0,reserved:0}
 action init=all{durable'=empty,visible'=empty,staged'=empty,charge'=0,phase'=0,ready'=true,exposed'=false}
 action admit(target:int,request:int,generation:int):bool=all{
  ready and phase==0 and charge+4<=12 and durable.origins.size()<2 and request>durable.request and generation>durable.generation and request<=4 and generation<=4 and not(durable.origins.exists(x=>x._1==target)),
  staged'={origins:durable.origins.union(Set((target,request,generation))),request:request,generation:generation,reserved:durable.reserved+3},
  charge'=charge+4,phase'=1,durable'=durable,visible'=visible,ready'=ready,exposed'=false
 }
 action advance=all{phase>0 and phase<6,phase'=phase+1,visible'=if(phase==4) staged else visible,durable'=if(phase==5) visible else durable,staged'=staged,charge'=charge,ready'=ready,exposed'=exposed}
 action reset=all{phase'=0,durable'=durable,visible'=visible,staged'=staged,charge'=charge,ready'=ready,exposed'=exposed}
 action crash=all{phase'=0,ready'=false,exposed'=false,durable'=durable,visible'=visible,staged'=empty,charge'=charge}
 action restart=all{not(ready),durable'=visible,ready'=true,visible'=visible,staged'=staged,charge'=charge,phase'=phase,exposed'=exposed}
 action powerLoss=all{phase'=0,ready'=false,exposed'=false,visible'=durable,durable'=durable,staged'=empty,charge'=charge}
 action expose=all{phase==0,exposed'=true,durable'=durable,visible'=visible,staged'=staged,charge'=charge,phase'=phase,ready'=ready}
 val coherent=(durable.reserved==3*durable.origins.size()) and durable.origins.forall(x=>x._2<=durable.request and x._3<=durable.generation) and durable.origins.map(x=>x._2).size()==durable.origins.size() and durable.origins.map(x=>x._3).size()==durable.origins.size()
 val safety=coherent and durable.reserved+durable.origins.size()<=charge and charge<=12 and (not(exposed) or ready)
 action step=any{nondet t=Set(1,2).oneOf();nondet r=Set(1,2,3,4).oneOf();nondet g=Set(1,2,3,4).oneOf();admit(t,r,g),advance,reset,crash,restart,powerLoss,expose}
 action commit=advance.then(advance).then(advance).then(advance).then(advance).then(reset)
 run atomicAdmissionTest=init.then(admit(1,1,1)).then(commit).then(expose).then(all{assert(safety and durable.origins==Set((1,1,1)) and durable.reserved==3),reset})
 run independentDomainsTest=init.then(admit(1,1,2)).then(commit).then(admit(2,3,4)).then(commit).then(all{assert(safety and durable.request==3 and durable.generation==4),reset})
 run visibleRestartTest=init.then(admit(1,1,1)).then(advance).then(advance).then(advance).then(advance).then(crash).then(restart).then(expose).then(all{assert(safety and durable.reserved==3),reset})
 run powerLossBeforeBarrierTest=init.then(admit(1,1,1)).then(advance).then(advance).then(advance).then(advance).then(powerLoss).then(restart).then(all{assert(safety and durable==empty and charge==4),reset})
}
