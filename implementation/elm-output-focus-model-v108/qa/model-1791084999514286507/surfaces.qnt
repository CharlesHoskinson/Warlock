module surfaces {
 type State={picker:bool,pending:bool,connected:bool,binding:int,chosenBinding:int,request:int,group:bool,ready:bool,focuses:int,focusedRevision:int,revision:int,output:int,chosenOutput:int}
 var s:State
 action init=s'={picker:true,pending:false,connected:true,binding:1,chosenBinding:1,request:1,group:true,ready:true,focuses:0,focusedRevision:0,revision:1,output:1,chosenOutput:1}
 action close=all{s.picker and s.connected,s'={...s,picker:false,pending:true,ready:false,chosenBinding:s.binding,chosenOutput:s.output,request:s.request+1}}
 action reply(id:int):bool=s'=if(s.pending and id==s.request and s.connected) {...s,pending:false,ready:true,revision:s.revision+1,focuses:s.focuses+(if(s.binding==s.chosenBinding and s.output==s.chosenOutput and s.group and not(s.picker))1 else 0),focusedRevision:if(s.binding==s.chosenBinding and s.output==s.chosenOutput and s.group and not(s.picker))s.revision+1 else s.focusedRevision} else s
 action fresh=reply(s.request)
 action stale=reply(s.request+1)
 action disconnect=s'={...s,connected:false,pending:false}
 action rebind=s'={...s,binding:s.binding+1,pending:false}
 action outputChange=s'={...s,output:s.output+1}
 action gone=s'={...s,group:false}
 action openNew=s'={...s,picker:true,pending:false}
 action step=any{outputChange,fresh,stale,disconnect,rebind,gone,openNew,if(s.picker and s.connected and s.focuses==0 and not(s.pending))close else s'=s}
 val safety=s.focuses<=1 and s.focusedRevision<=s.revision
 run closeFirstTest=init.then(close).then(all{assert(s.pending and s.focuses==0 and not(s.picker)),s'=s})
 run freshScopeTest=init.then(close).then(fresh).then(all{assert(s.focuses==1 and s.focusedRevision==2 and not(s.pending)),s'=s})
 run staleTest=init.then(close).then(stale).then(all{assert(s.pending and s.focuses==0),s'=s})
 run duplicateTest=init.then(close).then(fresh).then(fresh).then(all{assert(s.focuses==1),s'=s})
 run disconnectTest=init.then(close).then(disconnect).then(fresh).then(all{assert(s.focuses==0),s'=s})
 run rebindTest=init.then(close).then(rebind).then(fresh).then(all{assert(s.focuses==0),s'=s})
 run goneTest=init.then(close).then(gone).then(fresh).then(all{assert(s.focuses==0),s'=s})
 run newPopupTest=init.then(close).then(openNew).then(fresh).then(all{assert(s.focuses==0),s'=s})
 run changedOutputTest=init.then(close).then(outputChange).then(fresh).then(all{assert(s.focuses==0 and not(s.pending)),s'=s})
}
