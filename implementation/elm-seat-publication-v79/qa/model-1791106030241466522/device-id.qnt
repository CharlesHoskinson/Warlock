// Serialized seat capability / delayed publication abstraction. One kind of
// device; actual C++ replay separately checks keyboard and pointer paths.
// Native protocol delivery, coordinates and rendering are excluded.
module seat {
  type Token = {owner:int,id:int}
  type State = {live:bool,core:bool,ready:bool,transport:bool,cap:bool,owner:int,id:int,
                q:List[Token],published:List[Token],violations:int}
  var s:State
  action init = s'={live:true,core:true,ready:true,transport:true,cap:false,owner:1,id:0,q:[],published:[],violations:0}
  action enable = s'=if (s.live and not(s.cap)) {...s,cap:true,id:s.id+1,q:s.q.append({owner:s.owner,id:s.id+1})} else s
  action disable = s'={...s,cap:false}
  val eligible = s.live and s.core and s.ready and s.transport and s.cap and s.q.head().owner==s.owner and s.q.head().id==s.id
  val admitted = s.live and s.core and s.ready and s.transport and s.cap and s.q.head().owner==s.owner
  action idle = s'=if (s.q.length()>0) {...s,q:s.q.tail(),published:if(admitted) s.published.append(s.q.head()) else s.published,
    violations:s.violations+(if(admitted and not(eligible)) 1 else 0)} else s
  action loseCore = s'={...s,core:false}
  action pauseReady = s'={...s,ready:false}
  action resumeReady = s'={...s,ready:true}
  action failTransport = s'={...s,transport:false}
  action shutdown = s'={...s,live:false}
  // A replacement can reuse numeric device ids but cannot own the old task.
  action replaceBackend = s'={...s,owner:s.owner+1,cap:false,id:0}
  action step = any {enable,disable,idle,loseCore,pauseReady,resumeReady,failTransport,shutdown,replaceBackend}
  val safety = s.violations==0 and s.id>=0 and s.owner>=1
  run currentDevicePublishedTest = init.then(enable).then(idle).then(all{assert(s.published.length()==1 and s.q.length()==0),s'=s})
  run retiredDeviceRefusedTest = init.then(enable).then(disable).then(idle).then(all{assert(s.published.length()==0),s'=s})
  run replacementOnlyTest = init.then(enable).then(disable).then(enable).then(idle).then(idle).then(all{assert(s.published==[{owner:1,id:2}]),s'=s})
  run duplicateCapabilityTest = init.then(enable).then(enable).then(idle).then(all{assert(s.published.length()==1 and s.q.length()==0),s'=s})
  run backendOwnerReuseRefusedTest = init.then(enable).then(replaceBackend).then(enable).then(idle).then(idle).then(all{assert(s.published==[{owner:2,id:1}]),s'=s})
  run deadBackendRefusedTest = init.then(enable).then(shutdown).then(idle).then(all{assert(s.published.length()==0),s'=s})
  run deadCoreRefusedTest = init.then(enable).then(loseCore).then(idle).then(all{assert(s.published.length()==0),s'=s})
  run notReadyRefusedTest = init.then(enable).then(pauseReady).then(idle).then(all{assert(s.published.length()==0),s'=s})
  run failedTransportRefusedTest = init.then(enable).then(failTransport).then(idle).then(all{assert(s.published.length()==0),s'=s})
  run burstOnlyCurrentTest = init.then(enable).then(disable).then(enable).then(disable).then(enable).then(idle).then(idle).then(idle).then(all{assert(s.published==[{owner:1,id:3}]),s'=s})
}
