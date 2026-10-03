module trace {
 type State={serial:int,active:bool,complete:bool,overflow:bool,committed:bool,count:int}
 var s:State
 action init=s'={serial:0,active:false,complete:false,overflow:false,committed:false,count:0}
 action begin=s'=if(s.serial<3) {serial:s.serial+1,active:true,complete:false,overflow:false,committed:false,count:0} else {...s,active:false,complete:false,committed:false}
 action draw=s'=if(not(s.active)) s else if(s.count==2) {...s,overflow:true} else {...s,count:s.count+1}
 action finish(commit:bool):bool=s'=if(s.active) {...s,active:false,complete:not(s.overflow),committed:commit} else s
 action invalidate=s'={...s,active:false,complete:false,committed:false,count:0}
 action step=any{begin,draw,finish(true),finish(false),invalidate}
 val usable=s.complete and s.committed and not(s.overflow)
 val safety=(not(s.complete) or (not(s.active) and not(s.overflow) and s.serial>0)) and s.count<=2 and s.serial<=3 and (not(s.committed) or (s.serial>0 and not(s.active)))
 run incompleteBeforeFinishTest=init.then(begin).then(draw).then(all{assert(not(usable)),s'=s})
 run committedCompleteTest=init.then(begin).then(draw).then(finish(true)).then(all{assert(usable),s'=s})
 run overflowRefusesUsableTest=init.then(begin).then(draw).then(draw).then(draw).then(finish(true)).then(all{assert(not(usable) and s.overflow),s'=s})
 run failedCommitTest=init.then(begin).then(draw).then(finish(false)).then(all{assert(not(usable) and s.complete),s'=s})
 run invalidationTest=init.then(begin).then(draw).then(finish(true)).then(invalidate).then(all{assert(not(usable) and s.count==0),s'=s})
 run lateFinishIgnoredTest=init.then(begin).then(draw).then(invalidate).then(finish(true)).then(all{assert(not(usable)),s'=s})
 run exhaustionTest=init.then(begin).then(finish(true)).then(begin).then(finish(true)).then(begin).then(finish(true)).then(begin).then(all{assert(not(usable) and s.serial==3),s'=s})
 run closedDrawIgnoredTest=init.then(begin).then(draw).then(finish(true)).then(draw).then(all{assert(usable and s.count==1),s'=s})
}
