module recovery {
 type State={owner:int,life:int,legacy:int,locked:bool,plan:int,complete:bool,a:int,b:int,c:int,forwards:int}
 var s:State
 action init=s'={owner:1,life:1,legacy:7,locked:false,plan:-1,complete:false,a:0,b:0,c:0,forwards:0}
 action changeLegacy(value:int):bool=s'={...s,legacy:value}
 action ownership(owner:int,life:int):bool=s'={...s,owner:owner,life:life}
 action lock=s'={...s,locked:true}
 action snapshot=s'=if(s.plan<0 and not(s.locked) and (s.life!=1 or s.owner!=0)){...s,plan:if(s.owner==1 and s.life==1)s.legacy else 0} else s
 action copyPlan=s'=if(not(s.complete) and s.plan>=0){...s,a:s.plan} else s
 action mark=s'=if(s.plan>=0 and s.a==s.plan){...s,complete:true} else s
 action settle=s'=if(s.complete){...s,a:99} else s
 action restart=s'=s
 action ownWrite(key:int,value:int):bool=s'=if(key==1){...s,a:value} else if(key==2){...s,b:value} else {...s,c:value}
 action step=any{snapshot,copyPlan,mark,settle,restart,changeLegacy(s.legacy+1),lock}
 val safety=s.b==0 and s.c==0 and s.forwards==0 and (s.complete implies s.plan>=0) and (s.plan>=0 implies s.plan==0 or s.plan>=7)
 run ownedImportTest=init.then(snapshot).then(copyPlan).then(mark).then(all{assert(s.complete and s.a==7 and safety),s'=s})
 run foreignInstanceTest=init.then(ownership(2,1)).then(snapshot).then(copyPlan).then(mark).then(all{assert(s.complete and s.a==0 and safety),s'=s})
 run foreignLifetimeTest=init.then(ownership(1,2)).then(snapshot).then(copyPlan).then(mark).then(all{assert(s.complete and s.a==0 and safety),s'=s})
 run ambiguousOwnerTest=init.then(ownership(0,1)).then(snapshot).then(copyPlan).then(mark).then(all{assert(not(s.complete) and s.plan== -1 and s.a==0),s'=s})
 run lockedLegacyTest=init.then(lock).then(snapshot).then(all{assert(s.plan== -1 and not(s.complete)),s'=s})
 run stableResumeTest=init.then(snapshot).then(changeLegacy(88)).then(restart).then(snapshot).then(copyPlan).then(mark).then(all{assert(s.a==7 and s.plan==7 and s.legacy==88 and safety),s'=s})
 run noResurrectionTest=init.then(snapshot).then(copyPlan).then(mark).then(settle).then(changeLegacy(88)).then(restart).then(snapshot).then(copyPlan).then(all{assert(s.a==99 and s.complete and s.forwards==0),s'=s})
 run independentNamespacesTest=init.then(ownWrite(1,7)).then(ownWrite(2,8)).then(ownWrite(3,9)).then(all{assert(s.a==7 and s.b==8 and s.c==9 and s.forwards==0),s'=s})
}
