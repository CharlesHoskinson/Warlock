module Files {
 var revision: int
 var peer: int
 var proposal: (int,int)
 var spent: Set[(int,int)]
 var pending: bool
 var effects: int
 action init = all {revision'=1,peer'=1,proposal'=(0,0),spent'=Set(),pending'=false,effects'=0}
 action capture = all {not(pending),proposal'=(revision,peer),pending'=true,revision'=revision,peer'=peer,spent'=spent,effects'=effects}
 val admitted = proposal==(revision,peer) and not(spent.contains(proposal))
 action submit = all {pending,admitted,spent'=spent.union(Set(proposal)),effects'=effects+1,pending'=true,proposal'=proposal,revision'=revision,peer'=peer}
 action refuse = all {pending,not(admitted),pending'=false,proposal'=proposal,revision'=revision,peer'=peer,spent'=spent,effects'=effects}
 action read = all {revision'=revision+1,pending'=false,proposal'=proposal,peer'=peer,spent'=spent,effects'=effects}
 action replace = all {revision'=revision+1,peer'=peer+1,proposal'=proposal,pending'=pending,spent'=spent,effects'=effects}
 action verify(condition: bool): bool = all {assert(condition),revision'=revision,peer'=peer,proposal'=proposal,pending'=pending,spent'=spent,effects'=effects}
 action step = any {capture,submit,refuse,read,replace}
 val safety = effects==spent.size() and revision>0 and peer>0
 run currentInstanceOnceTest = init.then(capture).then(submit).then(refuse).then(capture).then(refuse).then(verify(effects==1))
 run replacementRefusesOldProposalTest = init.then(capture).then(replace).then(refuse).then(verify(effects==0))
 run unknownCannotReplayTest = init.then(capture).then(submit).then(refuse).then(verify(effects==1))
 run explicitFreshGestureTest = init.then(capture).then(submit).then(read).then(capture).then(submit).then(verify(effects==2))
}
