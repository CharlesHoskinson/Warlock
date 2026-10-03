module effects {
  type State = { connected: bool, status: str, authority: int, pendingAuthority: int, request: int, observedMinimized: bool }
  var s: State
  type Event = { kind: str, request: int, authority: int, status: str, minimized: bool }
  var e: Event
  pure def event(kind: str): Event = {kind:kind,request:0,authority:0,status:"",minimized:false}
  action init = all {s' = {connected:true,status:"Idle",authority:1,pendingAuthority:0,request:0,observedMinimized:false},e'=event("init")}
  action begin = all {s' = if(s.connected and s.status != "Pending") {...s,status:"Pending",pendingAuthority:s.authority,request:s.request+1} else s,e'=event("begin")}
  action receipt(request: int, authority: int, status: str) =
    all {s' = if(s.connected and s.status == "Pending" and request == s.request and authority == s.pendingAuthority and authority == s.authority) {...s,status:status} else s,e'={...event("receipt"),request:request,authority:authority,status:status}}
  action disconnect = all {s' = {...s,connected:false,status:if(s.status == "Pending") "Unknown" else s.status},e'=event("disconnect")}
  action rebind = all {s' = {...s,connected:true,authority:s.authority+1,status:if(s.status == "Pending") "Unknown" else s.status},e'=event("rebind")}
  action scene(minimized: bool) = all {s' = if(s.connected) {...s,observedMinimized:minimized} else s,e'={...event("scene"),minimized:minimized}}
  action step = any {
    begin,
    receipt(s.request,s.authority,"Committed"),
    receipt(s.request,s.authority,"Refused"),
    receipt(s.request,s.authority,"Cancelled"),
    receipt(s.request+1,s.authority,"Committed"),
    receipt(s.request,s.authority+1,"Committed"),
    disconnect,rebind,scene(true),scene(false)
  }
  val safety = (s.status == "Pending" implies s.connected and s.pendingAuthority == s.authority) and s.request >= 0
  run pendingNoOptimismTest = init.then(begin).then(all{assert(not(s.observedMinimized)),s'=s,e'=event("assert")})
  run commitNoOptimismTest = init.then(begin).then(receipt(1,1,"Committed")).then(all{assert(s.status == "Committed" and not(s.observedMinimized)),s'=s,e'=event("assert")})
  run staleRequestTest = init.then(begin).then(receipt(2,1,"Committed")).then(all{assert(s.status == "Pending"),s'=s,e'=event("assert")})
  run staleAuthorityTest = init.then(begin).then(receipt(1,2,"Committed")).then(all{assert(s.status == "Pending"),s'=s,e'=event("assert")})
  run disconnectedTest = init.then(begin).then(disconnect).then(receipt(1,1,"Committed")).then(all{assert(s.status == "Unknown"),s'=s,e'=event("assert")})
  run reboundTest = init.then(begin).then(rebind).then(receipt(1,1,"Committed")).then(all{assert(s.status == "Unknown"),s'=s,e'=event("assert")})
  run terminalTest = init.then(begin).then(receipt(1,1,"Refused")).then(receipt(1,1,"Committed")).then(all{assert(s.status == "Refused"),s'=s,e'=event("assert")})
  run cancellationTest = init.then(begin).then(receipt(1,1,"Cancelled")).then(all{assert(s.status == "Cancelled"),s'=s,e'=event("assert")})
  run pendingBoundTest = init.then(begin).then(begin).then(all{assert(s.request == 1),s'=s,e'=event("assert")})
}
