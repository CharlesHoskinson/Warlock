module SystemMenu {
 var revision: int
 var queued: int
 var available: bool
 var pending: bool
 var consumed: Set[int]
 var effects: int
 action init = all {revision'=1,queued'=0,available'=true,pending'=false,consumed'=Set(),effects'=0}
 val valid = queued==revision and available and not(consumed.contains(queued))
 action capture = all {not(pending),available,queued'=revision,pending'=true,revision'=revision,available'=available,consumed'=consumed,effects'=effects}
 action change = all {revision'=revision+1,queued'=queued,available'=available,pending'=pending,consumed'=consumed,effects'=effects}
 action withdraw = all {available'=false,revision'=revision+1,queued'=queued,pending'=pending,consumed'=consumed,effects'=effects}
 action submit = all {pending,valid,consumed'=consumed.union(Set(queued)),effects'=effects+1,pending'=true,queued'=queued,revision'=revision,available'=available}
 action refuse = all {pending,not(valid),pending'=false,revision'=revision,queued'=queued,available'=available,consumed'=consumed,effects'=effects}
 action receipt = all {pending,consumed.contains(queued),pending'=false,revision'=revision,queued'=queued,available'=available,consumed'=consumed,effects'=effects}
 action verify(condition: bool): bool = all {assert(condition),revision'=revision,queued'=queued,available'=available,pending'=pending,consumed'=consumed,effects'=effects}
 action step = any {capture,change,withdraw,submit,refuse,receipt}
 val safety = effects==consumed.size() and effects>=0 and revision>0
 run currentChangeOnceTest = init.then(capture).then(submit).then(receipt).then(capture).then(refuse).then(verify(effects==1))
 run staleStateRefusedTest = init.then(capture).then(change).then(refuse).then(verify(effects==0))
 run unavailableNeverSubmitsTest = init.then(capture).then(withdraw).then(refuse).then(verify(effects==0 and not(available)))
 run lostReceiptCannotReplayTest = init.then(capture).then(submit).then(refuse).then(capture).then(refuse).then(verify(effects==1))
}
