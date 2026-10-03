module recovery {
 type State = {binding:int,request:int,expected:int,phase:str,reconnecting:bool,status:str,intentBinding:int,counter:int,observed:int}
 type Event = {kind:str,binding:int,request:int,minimized:int,status:str}
 var s:State
 var e:Event
 pure def event(kind:str,binding:int,request:int,minimized:int,status:str):Event = {kind:kind,binding:binding,request:request,minimized:minimized,status:status}
 action init = all {s'={binding:0,request:0,expected:0,phase:"Detached",reconnecting:true,status:"Idle",intentBinding:0,counter:0,observed:-1},e'=event("init",0,0,0,"")}
 action attach(binding:int):bool = all {
  s'=if(s.phase=="Detached" and s.reconnecting and binding!=s.binding) {...s,binding:binding,request:s.request+1,expected:s.request+1,phase:"Reconciling",reconnecting:false,status:if(s.status=="Pending") "Unknown" else s.status} else s,
  e'=event("attach",binding,0,0,"")
 }
 action refresh = all {
  s'=if(s.phase!="Detached" and s.status!="Pending") {...s,request:s.request+1,expected:s.request+1,phase:"Reconciling"} else s,
  e'=event("refresh",0,0,0,"")
 }
 action snapshot(binding:int,request:int,minimized:int):bool = all {
  s'=if(s.phase!="Detached" and s.binding==binding and s.expected==request and request>0) {...s,phase:"Ready",expected:0,observed:minimized} else s,
  e'=event("snapshot",binding,request,minimized,"")
 }
 action begin = all {
  s'=if(s.phase=="Ready" and s.status!="Pending") {...s,counter:s.counter+1,intentBinding:s.binding,status:"Pending"} else s,
  e'=event("begin",0,0,0,"")
 }
 action disconnect = all {s'={...s,phase:"Detached",expected:0,reconnecting:false,status:if(s.status=="Pending") "Unknown" else s.status},e'=event("disconnect",0,0,0,"")}
 action reconnect = all {s'=if(s.phase=="Detached" and not(s.reconnecting)) {...s,reconnecting:true} else s,e'=event("reconnect",0,0,0,"")}
 action receipt(binding:int,request:int,status:str):bool = all {
  s'=if(s.phase!="Detached" and s.binding==binding and s.status=="Pending" and s.intentBinding==binding and s.counter==request) {...s,status:status,phase:"Reconciling",request:s.request+1,expected:s.request+1} else s,
  e'=event("receipt",binding,request,0,status)
 }
 action step = any {attach(1),attach(2),refresh,snapshot(s.binding,s.expected,0),snapshot(s.binding,s.expected,1),snapshot(s.binding,s.expected-1,1),snapshot(if(s.binding==1) 2 else 1,s.expected,1),begin,disconnect,reconnect,receipt(s.binding,s.counter,"Committed"),receipt(s.binding,s.counter,"Unknown"),receipt(s.binding,s.counter-1,"Committed"),receipt(if(s.binding==1) 2 else 1,s.counter,"Committed")}
 val safety = (s.phase!="Ready" or (s.binding>0 and s.expected==0 and s.observed>=0)) and (s.status!="Pending" or s.counter>0) and (s.phase!="Detached" or s.expected==0)
 run awaitSnapshotTest = init.then(attach(1)).then(begin).then(all{assert(s.phase=="Reconciling" and s.counter==0),s'=s,e'=event("assert",0,0,0,"")})
 run coherentAdmissionTest = init.then(attach(1)).then(snapshot(1,1,0)).then(begin).then(all{assert(s.status=="Pending" and s.counter==1 and s.observed==0),s'=s,e'=event("assert",0,0,0,"")})
 run pendingUnknownTest = init.then(attach(1)).then(snapshot(1,1,0)).then(begin).then(disconnect).then(all{assert(s.status=="Unknown" and s.observed==0),s'=s,e'=event("assert",0,0,0,"")})
 run reconnectNoReplayTest = init.then(attach(1)).then(snapshot(1,1,0)).then(begin).then(disconnect).then(reconnect).then(attach(2)).then(snapshot(2,2,0)).then(all{assert(s.phase=="Ready" and s.status=="Unknown" and s.counter==1),s'=s,e'=event("assert",0,0,0,"")})
 run staleProjectionTest = init.then(attach(1)).then(refresh).then(snapshot(1,1,1)).then(all{assert(s.phase=="Reconciling" and s.observed== -1),s'=s,e'=event("assert",0,0,0,"")})
 run oldBindingReceiptTest = init.then(attach(1)).then(snapshot(1,1,0)).then(begin).then(disconnect).then(reconnect).then(attach(2)).then(receipt(1,1,"Committed")).then(all{assert(s.status=="Unknown" and s.phase=="Reconciling"),s'=s,e'=event("assert",0,0,0,"")})
 run receiptNotSceneTest = init.then(attach(1)).then(snapshot(1,1,0)).then(begin).then(receipt(1,1,"Committed")).then(all{assert(s.observed==0 and s.phase=="Reconciling"),s'=s,e'=event("assert",0,0,0,"")})
 run terminalCannotOverwriteTest = init.then(attach(1)).then(snapshot(1,1,0)).then(begin).then(receipt(1,1,"Unknown")).then(receipt(1,1,"Committed")).then(all{assert(s.status=="Unknown"),s'=s,e'=event("assert",0,0,0,"")})
}
