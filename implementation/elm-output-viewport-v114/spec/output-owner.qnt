module outputs {
 type State={owner:int,alive:Set[int],retired:bool,mapped:bool,popup:bool,queued:int,forwarded:int}
 var s:State
 action init=s'={owner:2,alive:Set(1,2),retired:false,mapped:true,popup:false,queued:0,forwarded:0}
 action queue=s'=if(not(s.retired)) {...s,queued:s.queued+1} else s
 action forward=s'=if(not(s.retired) and s.queued>0) {...s,queued:s.queued-1,forwarded:s.forwarded+1} else s
 action open=s'=if(not(s.retired)) {...s,popup:true} else s
 action remove(id:int):bool=s'=if(id==s.owner) {...s,alive:s.alive.exclude(id),retired:true,mapped:false,popup:false,queued:0} else {...s,alive:s.alive.exclude(id)}
 action replace=s'={...s,alive:s.alive.union(Set(3))}
 action step=any{queue,forward,open,remove(1),remove(2),replace}
 val safety=s.owner==2 and (s.retired implies not(s.mapped) and not(s.popup) and s.queued==0) and (s.mapped implies s.alive.contains(s.owner))
 run unrelatedRemovalTest=init.then(open).then(remove(1)).then(all{assert(not(s.retired) and s.mapped and s.popup),s'=s})
 run ownerRemovalTest=init.then(open).then(queue).then(remove(2)).then(all{assert(s.retired and not(s.popup) and s.queued==0),s'=s})
 run replacementTest=init.then(remove(2)).then(replace).then(open).then(all{assert(s.retired and not(s.mapped)),s'=s})
 run lateQueueTest=init.then(remove(2)).then(queue).then(forward).then(all{assert(s.forwarded==0),s'=s})
}
