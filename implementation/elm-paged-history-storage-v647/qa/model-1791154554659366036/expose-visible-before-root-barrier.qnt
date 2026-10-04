module storage {
 var durable: Set[int]
 var visible: Set[int]
 var staged: Set[int]
 var charge: int
 var phase: int
 var ready: bool
 var exposed: Set[int]
 action init = all { durable'=Set(), visible'=Set(), staged'=Set(), charge'=0, phase'=0, ready'=true, exposed'=Set() }
 action reserve(k:int):bool = all { ready and phase==0 and charge<4 and not(durable.contains(k)), charge'=charge+1, staged'=Set(k), phase'=1, durable'=durable, visible'=visible, ready'=ready, exposed'=exposed }
 action advance = all { phase>0 and phase<6, phase'=phase+1, visible'=if(phase==4) durable.union(staged) else visible, durable'=if(phase==5) visible else durable, ready'=if(phase==5) true else ready, staged'=if(phase==5) Set() else staged, charge'=charge, exposed'=exposed }
 action reset = all { phase'=0, durable'=durable, visible'=visible, staged'=staged, charge'=charge, ready'=ready, exposed'=exposed }
 action crash = all { ready'=false, phase'=0, staged'=Set(), durable'=durable, visible'=visible, charge'=charge, exposed'=Set() }
 action restart = all { not(ready), ready'=true, durable'=visible, visible'=visible, staged'=staged, charge'=charge, phase'=phase, exposed'=exposed }
 action powerLoss = all { ready'=false, visible'=durable, durable'=durable, staged'=Set(), charge'=charge, phase'=0, exposed'=Set() }
 action expose(k:int):bool = all { visible.contains(k), exposed'=exposed.union(Set(k)), durable'=durable, visible'=visible, staged'=staged, charge'=charge, phase'=phase, ready'=ready }
 action step = any { nondet k=Set(1,2,3,4,5).oneOf(); reserve(k), advance, reset, crash, restart, powerLoss, nondet k=Set(1,2,3,4,5).oneOf(); expose(k) }
 val safety = exposed.subseteq(durable) and durable.size()<=charge and charge<=4
 action commit = advance.then(advance).then(advance).then(advance).then(advance).then(reset)
 run visibleRestartTest = init.then(reserve(1)).then(advance).then(advance).then(advance).then(advance).then(crash).then(restart).then(expose(1)).then(all {assert(safety and durable==Set(1)),reset})
 run lossBeforeBarrierTest = init.then(reserve(1)).then(advance).then(advance).then(advance).then(advance).then(powerLoss).then(restart).then(all {assert(safety and durable==Set() and charge==1),reset})
 run conservationTest = init.then(reserve(1)).then(commit).then(reserve(2)).then(commit).then(crash).then(restart).then(all {assert(safety and durable==Set(1,2)),reset})
run unsafeExposureWitnessTest = init.then(reserve(1)).then(advance).then(advance).then(advance).then(advance).then(expose(1)).then(all {assert(safety),reset})
}