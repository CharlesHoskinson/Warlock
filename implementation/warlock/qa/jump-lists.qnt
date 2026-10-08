module JumpLists {
 var revision: int
 var owner: int
 var queued: (int,int)
 var actionOwner: int
 var spent: Set[(int,int)]
 var effects: int
 action init = all {revision'=1,owner'=1,queued'=(0,0),actionOwner'=0,spent'=Set(),effects'=0}
 action choose(actor: int): bool = all {queued'=(revision,owner),actionOwner'=actor,revision'=revision,owner'=owner,spent'=spent,effects'=effects}
 action submit = all {queued==(revision,owner),actionOwner==owner,not(spent.contains(queued)),spent'=spent.union(Set(queued)),effects'=effects+1,revision'=revision,owner'=owner,queued'=queued,actionOwner'=actionOwner}
 action refuse = all {queued!=(revision,owner) or actionOwner!=owner or spent.contains(queued),revision'=revision,owner'=owner,queued'=queued,actionOwner'=actionOwner,spent'=spent,effects'=effects}
 action changed = all {revision'=revision+1,owner'=owner,queued'=queued,actionOwner'=actionOwner,spent'=spent,effects'=effects}
 action verify(condition: bool): bool = all {assert(condition),revision'=revision,owner'=owner,queued'=queued,actionOwner'=actionOwner,spent'=spent,effects'=effects}
 action step = any {choose(1),choose(2),submit,refuse,changed}
 val safety = effects==spent.size() and revision>0
 run ownedActionOnceTest = init.then(choose(1)).then(submit).then(refuse).then(verify(effects==1))
 run foreignRecentNeverDispatchesTest = init.then(choose(2)).then(refuse).then(verify(effects==0))
 run staleActionRefusedTest = init.then(choose(1)).then(changed).then(refuse).then(verify(effects==0))
 run unknownCannotReplayTest = init.then(choose(1)).then(submit).then(choose(1)).then(refuse).then(verify(effects==1))
}
