module recovery {
 type State={views:Set[int],owner:int,menu:int,prepared:int,legacy:bool,geometry:bool,submissions:int,canceled:bool,dirty:bool}
 var s:State
 action init=s'={views:Set(1,2),owner:1,menu:0,prepared:0,legacy:false,geometry:false,submissions:0,canceled:false,dirty:false}
 action context(scope:int):bool=s'=if(s.views.contains(scope) and s.prepared==0){...s,owner:scope,menu:scope,canceled:false} else s
 action prepare(scope:int):bool=s'=if(s.menu==scope and s.owner==scope and s.views.contains(scope)){...s,menu:0,prepared:scope,legacy:false,geometry:false,canceled:false} else s
 action relocate(scope:int):bool=s'=if(s.views.contains(scope) and scope!=s.owner){...s,owner:scope,menu:0,prepared:0,legacy:false,geometry:false,canceled:true} else s
 action retire(scope:int):bool=s'=if(s.owner==scope){...s,views:s.views.exclude(Set(scope)),owner:0,menu:0,prepared:0,legacy:false,geometry:false,canceled:true} else {...s,views:s.views.exclude(Set(scope))}
 action legacy(scope:int):bool=s'=if(s.prepared==scope and s.owner==scope and s.views.contains(scope)){...s,legacy:true} else s
 action geometry(scope:int):bool=s'=if(s.prepared==scope and s.owner==scope and s.views.contains(scope)){...s,geometry:true} else s
 action dispatch=s'=if(s.prepared!=0 and s.owner==s.prepared and s.views.contains(s.owner) and s.legacy and s.geometry){...s,prepared:0,legacy:false,geometry:false,submissions:s.submissions+1,canceled:false} else s
 action notification=s'={...s,dirty:true}
 action step=any{context(1),context(2),prepare(1),prepare(2),relocate(1),relocate(2),retire(1),retire(2),legacy(1),legacy(2),geometry(1),geometry(2),dispatch,notification}
 val safety=(s.prepared==0 or (s.views.contains(s.prepared) and s.owner==s.prepared and s.menu==0 and not(s.canceled))) and (s.menu==0 or (s.views.contains(s.menu) and s.owner==s.menu)) and s.submissions>=0
 run distinctOwnerTest=init.then(context(2)).then(all{assert(s.owner==2 and s.menu==2 and s.submissions==0),s'=s})
 run wrongViewCannotSelectTest=init.then(context(1)).then(prepare(2)).then(all{assert(s.prepared==0 and s.menu==1),s'=s})
 run closeBeforeObservationTest=init.then(context(1)).then(prepare(1)).then(all{assert(s.menu==0 and s.prepared==1 and s.submissions==0),s'=s})
 run pairedObservationOnceTest=init.then(context(1)).then(prepare(1)).then(legacy(1)).then(geometry(1)).then(dispatch).then(dispatch).then(all{assert(s.submissions==1 and s.prepared==0),s'=s})
 run singleStreamNeverDispatchesTest=init.then(context(1)).then(prepare(1)).then(legacy(1)).then(dispatch).then(all{assert(s.submissions==0 and s.prepared==1),s'=s})
 run relocationCancelsPreparedTest=init.then(context(1)).then(prepare(1)).then(relocate(2)).then(legacy(1)).then(geometry(1)).then(dispatch).then(all{assert(s.owner==2 and s.canceled and s.submissions==0),s'=s})
 run retiringPreparedOwnerTest=init.then(context(1)).then(prepare(1)).then(retire(1)).then(legacy(1)).then(geometry(1)).then(dispatch).then(all{assert(s.owner==0 and s.prepared==0 and s.submissions==0),s'=s})
 run zeroOutputsCancelTest=init.then(context(1)).then(prepare(1)).then(retire(2)).then(retire(1)).then(all{assert(s.views==Set() and s.prepared==0 and s.menu==0),s'=s})
 run nonownerRemovalPreservesTest=init.then(context(1)).then(prepare(1)).then(retire(2)).then(all{assert(s.owner==1 and s.prepared==1 and not(s.canceled)),s'=s})
 run stalePairCannotChooseNewOwnerTest=init.then(context(1)).then(prepare(1)).then(relocate(2)).then(context(2)).then(prepare(2)).then(legacy(1)).then(geometry(1)).then(dispatch).then(all{assert(s.prepared==2 and not(s.legacy) and not(s.geometry) and s.submissions==0),s'=s})
 run notificationsDoNotRetargetTest=init.then(context(1)).then(prepare(1)).then(notification).then(notification).then(all{assert(s.owner==1 and s.prepared==1 and s.dirty and s.submissions==0),s'=s})
 run retiredViewCannotReopenTest=init.then(context(1)).then(retire(1)).then(context(1)).then(prepare(1)).then(all{assert(s.owner==0 and s.menu==0 and s.prepared==0),s'=s})
}
