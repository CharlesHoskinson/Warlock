// Event-loop listener ordering and deferred parent hit-testing only.
// Coordinates, native transport, window surfaces and rendering are excluded.
module hit {
  type State = {monitorGen:int, windowGen:int, surfaceGen:int, pointerGen:int, focusGen:int,
                inBus:bool, queued:bool, anchor:bool, parentFocus:bool,
                deviceAlive:bool, live:bool, owner:int, queuedOwner:int, repicks:int, pending:bool, committedTarget:bool, focusOwner:int}
  var s: State
  action init = s' = {monitorGen:1, windowGen:1, surfaceGen:1, pointerGen:1, focusGen:1,
                     inBus:false, queued:false, anchor:true, parentFocus:true,
                     deviceAlive:true, live:true, owner:1, queuedOwner:1, repicks:0, pending:false, committedTarget:false, focusOwner:1}
  action pointerLayout = s' = if (s.live and not(s.inBus)) {
    ...s, monitorGen:s.monitorGen+1, pointerGen:s.monitorGen+1, focusGen:0,
    inBus:true, pending:true, queued:s.queued or s.anchor,
    queuedOwner:if (s.queued) s.queuedOwner else s.owner
  } else s
  action windowLayout = s' = if (s.inBus) {...s, windowGen:s.monitorGen, inBus:false} else s
  val eligible = s.live and s.anchor and s.parentFocus and s.deviceAlive and s.owner==s.queuedOwner
  action idle = s' = if (s.queued and not(s.inBus)) {
    ...s, queued:false, pending:if (eligible and s.committedTarget and s.surfaceGen==s.monitorGen) false else s.pending, focusOwner:if (eligible) 1 else s.focusOwner, focusGen:if (eligible) (if (s.surfaceGen==s.monitorGen) s.surfaceGen else 0) else s.focusGen,
    repicks:if (eligible) s.repicks+1 else s.repicks
  } else s
  action surfaceCommit = s' = if (not(s.inBus)) {...s, surfaceGen:s.windowGen, committedTarget:true,
    queued:s.queued or (s.live and s.anchor), queuedOwner:if (s.queued) s.queuedOwner else s.owner} else s
  action backgroundCommit = s' = {...s, committedTarget:false, queued:s.queued or (s.live and s.anchor and s.pending), queuedOwner:if (s.queued) s.queuedOwner else s.owner}
  action programmaticFocus = s' = {...s, focusOwner:2}
  action supersede = s' = {...s, anchor:false}
  action loseParentFocus = s' = {...s, parentFocus:false}
  action retireDevice = s' = {...s, deviceAlive:false}
  action replaceOwner = s' = {...s, owner:s.owner+1}
  action shutdown = s' = {...s, live:false}
  action step = any {pointerLayout, windowLayout, idle, surfaceCommit, backgroundCommit, programmaticFocus, supersede, loseParentFocus, retireDevice, replaceOwner, shutdown}
  val safety = s.surfaceGen<=s.monitorGen and s.windowGen<=s.monitorGen and s.pointerGen==s.monitorGen and
               s.focusGen<=s.monitorGen and s.repicks>=0 and
               (not(s.inBus) implies s.windowGen==s.monitorGen)
  run listenerOrderRepairedTest = init.then(pointerLayout).then(windowLayout).then(surfaceCommit).then(idle).then(all{assert(s.focusGen==s.monitorGen and s.repicks==1 and not(s.queued)),s'=s})
  run noIdleDuringDispatchTest = init.then(pointerLayout).then(idle).then(all{assert(s.queued and s.repicks==0 and s.focusGen==0),s'=s}).then(windowLayout).then(surfaceCommit).then(idle).then(all{assert(s.focusGen==2),s'=s})
  run latestLayoutCoalescesTest = init.then(pointerLayout).then(windowLayout).then(pointerLayout).then(windowLayout).then(surfaceCommit).then(idle).then(all{assert(s.monitorGen==3 and s.focusGen==3 and s.repicks==1),s'=s})
  run supersedingMotionFencesTaskTest = init.then(pointerLayout).then(windowLayout).then(supersede).then(idle).then(all{assert(s.repicks==0 and not(s.queued)),s'=s})
  run parentFocusLossFencesTaskTest = init.then(pointerLayout).then(windowLayout).then(loseParentFocus).then(idle).then(all{assert(s.repicks==0),s'=s})
  run deviceRetirementFencesTaskTest = init.then(pointerLayout).then(windowLayout).then(retireDevice).then(idle).then(all{assert(s.repicks==0),s'=s})
  run ownerReplacementFencesTaskTest = init.then(pointerLayout).then(windowLayout).then(replaceOwner).then(idle).then(all{assert(s.repicks==0),s'=s})
  run delayedCommitRepairsEmptyFocusTest = init.then(pointerLayout).then(windowLayout).then(idle).then(all{assert(s.focusGen==0 and s.repicks==1),s'=s}).then(surfaceCommit).then(idle).then(all{assert(s.focusGen==2 and s.repicks==2),s'=s})
  run supersededCommitDoesNotQueueTest = init.then(supersede).then(surfaceCommit).then(all{assert(not(s.queued)),s'=s})
  run ordinaryCommitPreservesProgrammaticFocusTest = init.then(programmaticFocus).then(surfaceCommit).then(idle).then(all{assert(s.repicks==0 and s.focusOwner==2),s'=s})
  run settledLayoutPreservesLaterFocusTest = init.then(pointerLayout).then(windowLayout).then(surfaceCommit).then(idle).then(all{assert(not(s.pending)),s'=s}).then(programmaticFocus).then(surfaceCommit).then(idle).then(all{assert(s.repicks==1 and s.focusOwner==2),s'=s})
  run backgroundCommitCannotSettleTargetTest = init.then(pointerLayout).then(windowLayout).then(backgroundCommit).then(idle).then(all{assert(s.pending and s.focusGen==0),s'=s}).then(surfaceCommit).then(idle).then(all{assert(not(s.pending) and s.focusGen==2),s'=s})
  run shutdownFencesTaskTest = init.then(pointerLayout).then(windowLayout).then(shutdown).then(idle).then(all{assert(s.repicks==0),s'=s})
}
