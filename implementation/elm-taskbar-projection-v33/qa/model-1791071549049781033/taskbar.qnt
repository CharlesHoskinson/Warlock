module taskbar {
 type Scope={binding:int,revision:int,output:int}
 type State={scope:Scope,shown:Scope,count:int,pinned:bool,active:bool,minimized:bool,available:bool,pending:bool,decision:str,emitted:bool,selection:bool}
 var s:State
 pure def primary(count:int,pinned:bool,active:bool,minimized:bool,available:bool):str=
  if(count==0) {if(pinned) "Launch" else "Unavailable"}
  else if(count>1) "Picker"
  else if(not(available)) "Unavailable"
  else if(minimized) "Restore"
  else if(active) "Minimize" else "Activate"
 pure def choose(minimized:bool,available:bool):str=if(not(available)) "Unavailable" else if(minimized) "Restore" else "Activate"
 action init=s'={scope:{binding:1,revision:1,output:1},shown:{binding:1,revision:1,output:1},count:1,pinned:false,active:false,minimized:false,available:true,pending:false,decision:"Idle",emitted:false,selection:false}
 action configure(count:int,pinned:bool,active:bool,minimized:bool,available:bool):bool=s'={...s,count:count,pinned:pinned,active:active,minimized:minimized,available:available,decision:"Idle",emitted:false,selection:false}
 action click=all{not(s.pending),s.shown==s.scope,s'={...s,decision:primary(s.count,s.pinned,s.active,s.minimized,s.available),emitted:Set("Activate","Restore","Minimize").contains(primary(s.count,s.pinned,s.active,s.minimized,s.available)),selection:false}}
 action select=all{not(s.pending),s.shown==s.scope,s.count>0,s'={...s,decision:choose(s.minimized,s.available),emitted:Set("Activate","Restore").contains(choose(s.minimized,s.available)),selection:true}}
 action reject=all{s.pending or s.shown!=s.scope,s'={...s,decision:"Rejected",emitted:false,selection:false}}
 action invalidate=s'={...s,scope:{...s.scope,revision:s.scope.revision+1},decision:"Idle",emitted:false}
 action reconnect=s'={...s,scope:{...s.scope,binding:s.scope.binding+1},decision:"Idle",emitted:false}
 action refresh=s'={...s,shown:s.scope,decision:"Idle",emitted:false}
 action hold=s'={...s,pending:true,decision:"Idle",emitted:false}
 action release=s'={...s,pending:false,decision:"Idle",emitted:false}
 action step=any{configure(0,true,false,false,true),configure(0,false,false,false,true),configure(1,false,false,false,true),configure(1,false,true,false,true),configure(1,false,true,true,true),configure(2,false,true,false,true),configure(1,false,true,false,false),click,select,reject,invalidate,reconnect,refresh,hold,release}
 val safety=all{s.emitted implies not(s.pending) and s.shown==s.scope and s.available,s.selection implies s.decision!="Minimize",s.decision=="Launch" implies s.pinned and s.count==0,s.decision=="Picker" implies s.count>1,not(s.emitted) or s.count>0}
 run zeroPinnedTest=init.then(configure(0,true,false,false,true)).then(click).then(all{assert(s.decision=="Launch"),s'=s})
 run zeroUnpinnedTest=init.then(configure(0,false,false,false,true)).then(click).then(all{assert(s.decision=="Unavailable"),s'=s})
 run inactiveTest=init.then(click).then(all{assert(s.decision=="Activate"),s'=s})
 run activeTest=init.then(configure(1,false,true,false,true)).then(click).then(all{assert(s.decision=="Minimize"),s'=s})
 run minimizedTest=init.then(configure(1,false,false,true,true)).then(click).then(all{assert(s.decision=="Restore"),s'=s})
 run unavailableTest=init.then(configure(1,false,true,false,false)).then(click).then(all{assert(not(s.emitted)),s'=s})
 run multipleTest=init.then(configure(2,false,true,false,true)).then(click).then(all{assert(s.decision=="Picker" and not(s.emitted)),s'=s})
 run pickerActiveTest=init.then(configure(2,false,true,false,true)).then(select).then(all{assert(s.decision=="Activate"),s'=s})
 run pickerMinimizedTest=init.then(configure(2,false,false,true,true)).then(select).then(all{assert(s.decision=="Restore"),s'=s})
 run staleRevisionTest=init.then(invalidate).then(reject).then(all{assert(not(s.emitted)),s'=s})
 run staleSessionTest=init.then(reconnect).then(reject).then(all{assert(not(s.emitted)),s'=s})
 run pendingTest=init.then(hold).then(reject).then(all{assert(not(s.emitted)),s'=s})
}
