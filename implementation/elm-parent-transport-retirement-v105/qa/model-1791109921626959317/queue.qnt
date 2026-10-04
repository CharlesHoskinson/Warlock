// Bounded single nested backend. Transport and copied-idle interleavings are
// abstract; actual bodies and native connection/device evidence are separate.
module transport {
  type State = {transport:bool,retired:bool,ready:bool,fd:bool,pointers:int,keyboards:int,
    outputs:int,focus:bool,queued:int,frameCopy:bool,frames:int,publications:int,
    logs:int,notifyQueued:bool,notifications:int}
  var s:State
  action init = s'={transport:true,retired:false,ready:true,fd:true,pointers:1,keyboards:1,
    outputs:1,focus:true,queued:1,frameCopy:true,frames:0,publications:0,logs:0,
    notifyQueued:false,notifications:0}
  action loseConnection = s'={...s,transport:false}
  action dispatch = s'=if(not(s.transport) and not(s.retired))
    {...s,retired:true,ready:false,fd:false,pointers:0,keyboards:0,outputs:0,focus:false,
      queued:s.queued,logs:s.logs+1,notifyQueued:true}
    else if(s.transport) {...s,publications:s.publications+s.queued,queued:0} else s
  action consumerIdle = s'=if(s.notifyQueued) {...s,notifyQueued:false,notifications:s.notifications+1} else s
  action copiedFrame = s'=if(s.frameCopy) {...s,frameCopy:false,frames:s.frames+(if(not(s.retired) and s.transport) 1 else 0)} else s
  action enable = s'=if(s.transport and not(s.retired)) {...s,pointers:1,keyboards:1} else s
  action createOutput = s'=if(s.transport and not(s.retired)) {...s,outputs:1} else s
  action step = any{loseConnection,dispatch,consumerIdle,copiedFrame,enable,createOutput}
  val safety = s.logs<=1 and s.notifications<=1 and
    (not(s.retired) or (not(s.ready) and not(s.fd) and s.pointers==0 and s.keyboards==0 and
      s.outputs==0 and not(s.focus) and s.queued==0))
  run healthyPublicationTest = init.then(dispatch).then(all{assert(s.publications==1 and s.ready and s.fd),s'=s})
  run devicesRetiredTest = init.then(loseConnection).then(dispatch).then(all{assert(s.pointers==0 and s.keyboards==0),s'=s})
  run outputRetiredTest = init.then(loseConnection).then(dispatch).then(all{assert(s.outputs==0 and not(s.focus)),s'=s})
  run pendingPublicationDiscardedTest = init.then(loseConnection).then(dispatch).then(all{assert(s.queued==0 and s.publications==0),s'=s})
  run failedDescriptorWithdrawnTest = init.then(loseConnection).then(dispatch).then(all{assert(not(s.fd)),s'=s})
  run deferredDescriptorNotificationTest = init.then(loseConnection).then(dispatch).then(all{assert(s.notifyQueued and s.notifications==0),s'=s}).then(consumerIdle).then(all{assert(s.notifications==1 and not(s.notifyQueued)),s'=s})
  run repeatedLossOneShotTest = init.then(loseConnection).then(dispatch).then(dispatch).then(consumerIdle).then(dispatch).then(consumerIdle).then(all{assert(s.logs==1 and s.notifications==1),s'=s})
  run copiedFrameAfterRetirementTest = init.then(loseConnection).then(dispatch).then(copiedFrame).then(all{assert(s.frames==0),s'=s})
  run lateCapabilityRefusedTest = init.then(loseConnection).then(dispatch).then(enable).then(all{assert(s.pointers==0 and s.keyboards==0),s'=s})
  run lateOutputRefusedTest = init.then(loseConnection).then(dispatch).then(createOutput).then(all{assert(s.outputs==0 and not(s.ready)),s'=s})
}
