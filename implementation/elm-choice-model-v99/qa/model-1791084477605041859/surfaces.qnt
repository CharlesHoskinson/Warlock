module surfaces {
 type State={pending:bool,picker:bool,connected:bool,binding:int,chosenBinding:int,output:int,chosenOutput:int,available:bool,root:bool,application:bool,revision:int,expected:int,requests:int,dispatches:int,dispatchedRevision:int,authorized:bool,token:int,expired:bool}
 var s:State
 action init=s'={pending:false,picker:true,connected:true,binding:1,chosenBinding:1,output:1,chosenOutput:1,available:true,root:true,application:true,revision:1,expected:0,requests:0,dispatches:0,dispatchedRevision:0,authorized:false,token:0,expired:false}
 action choose=all{s.picker and s.connected and s.available and not(s.pending),s'={...s,pending:true,picker:false,chosenBinding:s.binding,chosenOutput:s.output,expected:s.requests+1,requests:s.requests+1,token:s.requests+1,expired:false}}
 action reply(id:int): bool =s'=if(s.pending and id==s.expected and s.connected and s.available) {
  val admit=s.binding==s.chosenBinding and s.output==s.chosenOutput and s.root and s.application
  {...s,pending:false,expected:0,dispatches:s.dispatches+(if(admit)1 else 0),dispatchedRevision:if(admit)s.revision else s.dispatchedRevision,authorized:s.authorized or admit}
 } else s
 action fresh=reply(s.expected)
 action stale=reply(s.expected+1)
 action focusRestore=s'={...s,revision:s.revision+1}
 action expire(token:int): bool = s'=if(s.pending and token==s.token) {...s,pending:false,expired:true} else s
 action timeout=expire(s.token)
 action staleTimeout=expire(s.token+1)
 action disconnect=s'={...s,connected:false,pending:false,expected:0}
 action rebind=s'={...s,binding:s.binding+1,pending:false,expected:0}
 action outputChange=s'={...s,output:s.output+1}
 action retireRoot=s'={...s,root:false}
 action changeApplication=s'={...s,application:false}
 action blocked=s'={...s,available:false}
 action step=any{timeout,staleTimeout,fresh,stale,focusRestore,disconnect,rebind,outputChange,retireRoot,changeApplication,blocked,if(s.picker and s.connected and s.available and not(s.pending)) choose else s'=s}
 val safety=s.dispatches<=1 and (s.dispatches==1 implies s.authorized and not(s.picker)) and (s.pending implies not(s.picker)) and s.dispatchedRevision<=s.revision and (s.expired implies s.dispatches==0)
 run closeBeforeDispatchTest=init.then(choose).then(all{assert(s.pending and not(s.picker) and s.dispatches==0),s'=s})
 run freshRevisionTest=init.then(choose).then(focusRestore).then(fresh).then(all{assert(s.dispatches==1 and s.dispatchedRevision==2),s'=s})
 run duplicateTest=init.then(choose).then(fresh).then(fresh).then(all{assert(s.dispatches==1),s'=s})
 run staleTest=init.then(choose).then(stale).then(all{assert(s.pending and s.dispatches==0),s'=s})
 run retiredRootTest=init.then(choose).then(retireRoot).then(fresh).then(all{assert(not(s.pending) and s.dispatches==0),s'=s})
 run changedApplicationTest=init.then(choose).then(changeApplication).then(fresh).then(all{assert(not(s.pending) and s.dispatches==0),s'=s})
 run changedOutputTest=init.then(choose).then(outputChange).then(fresh).then(all{assert(not(s.pending) and s.dispatches==0),s'=s})
 run blockedTest=init.then(choose).then(blocked).then(fresh).then(all{assert(s.dispatches==0),s'=s})
 run disconnectedTest=init.then(choose).then(disconnect).then(fresh).then(all{assert(not(s.pending) and s.dispatches==0),s'=s})
 run reboundTest=init.then(choose).then(rebind).then(fresh).then(all{assert(not(s.pending) and s.dispatches==0),s'=s})
 run timeoutTest=init.then(choose).then(timeout).then(fresh).then(all{assert(s.expired and s.dispatches==0 and not(s.pending)),s'=s})
 run staleTimeoutTest=init.then(choose).then(staleTimeout).then(fresh).then(all{assert(s.dispatches==1 and not(s.expired)),s'=s})
 run completedTimeoutTest=init.then(choose).then(fresh).then(timeout).then(all{assert(s.dispatches==1 and not(s.expired)),s'=s})
}
