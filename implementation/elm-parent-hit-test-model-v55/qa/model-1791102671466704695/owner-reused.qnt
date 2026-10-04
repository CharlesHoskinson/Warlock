// Event-loop listener ordering and deferred parent hit-testing only.
// Coordinates, native transport, window surfaces and rendering are excluded.
module hit {
  type State = {monitorGen:int, windowGen:int, pointerGen:int, focusGen:int,
                inBus:bool, queued:bool, anchor:bool, parentFocus:bool,
                deviceAlive:bool, live:bool, owner:int, queuedOwner:int, repicks:int}
  var s: State
  action init = s' = {monitorGen:1, windowGen:1, pointerGen:1, focusGen:1,
                     inBus:false, queued:false, anchor:true, parentFocus:true,
                     deviceAlive:true, live:true, owner:1, queuedOwner:1, repicks:0}
  action pointerLayout = s' = if (s.live and not(s.inBus)) {
    ...s, monitorGen:s.monitorGen+1, pointerGen:s.monitorGen+1, focusGen:0,
    inBus:true, queued:s.queued or s.anchor,
    queuedOwner:if (s.queued) s.queuedOwner else s.owner
  } else s
  action windowLayout = s' = if (s.inBus) {...s, windowGen:s.monitorGen, inBus:false} else s
  val eligible = s.live and s.anchor and s.parentFocus and s.deviceAlive
  action idle = s' = if (s.queued and not(s.inBus)) {
    ...s, queued:false, focusGen:if (eligible) s.windowGen else s.focusGen,
    repicks:if (eligible) s.repicks+1 else s.repicks
  } else s
  action supersede = s' = {...s, anchor:false}
  action loseParentFocus = s' = {...s, parentFocus:false}
  action retireDevice = s' = {...s, deviceAlive:false}
  action replaceOwner = s' = {...s, owner:s.owner+1}
  action shutdown = s' = {...s, live:false}
  action step = any {pointerLayout, windowLayout, idle, supersede, loseParentFocus, retireDevice, replaceOwner, shutdown}
  val safety = s.windowGen<=s.monitorGen and s.pointerGen==s.monitorGen and
               s.focusGen<=s.monitorGen and s.repicks>=0 and
               (not(s.inBus) implies s.windowGen==s.monitorGen)
  run listenerOrderRepairedTest = init.then(pointerLayout).then(windowLayout).then(idle).then(all{assert(s.focusGen==s.monitorGen and s.repicks==1 and not(s.queued)),s'=s})
  run noIdleDuringDispatchTest = init.then(pointerLayout).then(idle).then(all{assert(s.queued and s.repicks==0 and s.focusGen==0),s'=s}).then(windowLayout).then(idle).then(all{assert(s.focusGen==2),s'=s})
  run latestLayoutCoalescesTest = init.then(pointerLayout).then(windowLayout).then(pointerLayout).then(windowLayout).then(idle).then(all{assert(s.monitorGen==3 and s.focusGen==3 and s.repicks==1),s'=s})
  run supersedingMotionFencesTaskTest = init.then(pointerLayout).then(windowLayout).then(supersede).then(idle).then(all{assert(s.repicks==0 and not(s.queued)),s'=s})
  run parentFocusLossFencesTaskTest = init.then(pointerLayout).then(windowLayout).then(loseParentFocus).then(idle).then(all{assert(s.repicks==0),s'=s})
  run deviceRetirementFencesTaskTest = init.then(pointerLayout).then(windowLayout).then(retireDevice).then(idle).then(all{assert(s.repicks==0),s'=s})
  run ownerReplacementFencesTaskTest = init.then(pointerLayout).then(windowLayout).then(replaceOwner).then(idle).then(all{assert(s.repicks==0),s'=s})
  run shutdownFencesTaskTest = init.then(pointerLayout).then(windowLayout).then(shutdown).then(idle).then(all{assert(s.repicks==0),s'=s})
}
