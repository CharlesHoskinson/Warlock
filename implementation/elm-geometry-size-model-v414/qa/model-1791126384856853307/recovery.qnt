module recovery {
 type State={clientMin:int,clientMax:int,layoutMin:int,layoutMax:int,target:int,valid:bool,blocked:bool,scope:bool,unknown:bool,mutations:int}
 var s:State
 action init=s'={clientMin:2,clientMax:0,layoutMin:0,layoutMax:100,target:12,valid:true,blocked:false,scope:true,unknown:false,mutations:0}
 val lower=if(s.clientMin>s.layoutMin)s.clientMin else s.layoutMin
 val rawUpper=if(s.clientMax==0)100 else s.clientMax
 val upper=if(rawUpper<s.layoutMax)rawUpper else s.layoutMax
 val feasible=s.valid and s.target>0 and lower<=s.target and s.target<=upper and not(lower>0 and lower==upper)
 action apply=s'=if(feasible and not(s.blocked) and s.scope and not(s.unknown)){...s,mutations:s.mutations+1}else s
 action highMinimum=s'={...s,clientMin:13}
 action finiteLowMaximum=s'={...s,clientMax:11}
 action equalMaximum=s'={...s,clientMax:12}
 action fixed=s'={...s,clientMin:12,clientMax:12}
 action invalid=s'={...s,valid:false}
 action conflict=s'={...s,clientMin:7,layoutMax:6}
 action changedOriginal=s'={...s,target:3,clientMin:4}
 action block=s'={...s,blocked:true}
 action stale=s'={...s,scope:false}
 action uncertain=s'={...s,unknown:true}
 action combinedFixed=s'={...s,clientMin:12,layoutMax:12}
 action step=any{apply,combinedFixed,highMinimum,finiteLowMaximum,equalMaximum,fixed,invalid,conflict,changedOriginal,block,stale,uncertain}
 val safety=s.mutations>=0
 run combinedFixedIntersectionTest=init.then(combinedFixed).then(apply).then(all{assert(s.mutations==0),s'=s})
 run minimumOnlyTest=init.then(apply).then(all{assert(s.mutations==1),s'=s})
 run minimumAboveWorkareaTest=init.then(highMinimum).then(apply).then(all{assert(s.mutations==0),s'=s})
 run finiteMaximumBelowTest=init.then(finiteLowMaximum).then(apply).then(all{assert(s.mutations==0),s'=s})
 run finiteMaximumEqualTest=init.then(equalMaximum).then(apply).then(all{assert(s.mutations==1),s'=s})
 run fixedAxisTest=init.then(fixed).then(apply).then(all{assert(s.mutations==0),s'=s})
 run malformedBoundTest=init.then(invalid).then(apply).then(all{assert(s.mutations==0),s'=s})
 run rawLayoutConflictTest=init.then(conflict).then(apply).then(all{assert(s.mutations==0),s'=s})
 run changedOriginalTest=init.then(changedOriginal).then(apply).then(all{assert(s.mutations==0),s'=s})
 run inputBlockedTest=init.then(block).then(apply).then(all{assert(s.mutations==0),s'=s})
 run staleScopeTest=init.then(stale).then(apply).then(all{assert(s.mutations==0),s'=s})
 run unknownBarrierTest=init.then(uncertain).then(apply).then(all{assert(s.mutations==0),s'=s})
}
