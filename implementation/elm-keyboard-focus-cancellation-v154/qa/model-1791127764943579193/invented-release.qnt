// One logical keyboard, two bounded key identities. Callback atomicity and
// multi-object lifetime are checked by actual C++ replay, not proved here.
module held {
  type State = {failed:bool,retired:bool,keyboardLive:bool,capable:bool,focused:bool,held:Set[int],pressed:int,
    released:int,modifierResets:int,cancelled:Set[int]}
  var s:State
  action init = s'={failed:false,retired:false,keyboardLive:true,capable:true,focused:true,held:Set(),pressed:0,
    released:0,modifierResets:0,cancelled:Set()}
  action press(key:int):bool = s'=if(s.keyboardLive and s.capable and s.focused and not(s.failed) and key>0 and key<=2 and not(s.held.contains(key)))
    {...s,held:s.held.union(Set(key)),pressed:s.pressed+1} else s
  action physicalRelease(key:int):bool = s'=if(s.keyboardLive and s.capable and s.focused and not(s.failed) and s.held.contains(key))
    {...s,held:s.held.exclude(Set(key)),released:s.released+1} else s
  action lose = s'={...s,failed:true}
  action cancel = s'=if((s.failed or not(s.focused) or not(s.capable)) and not(s.retired))
    {...s,held:Set(),focused:false,released:s.released+s.held.size()+1,modifierResets:s.modifierResets+(if(s.held.size()>0) 1 else 0),cancelled:s.cancelled.union(s.held)} else s
  action retire = s'=if((s.failed or not(s.capable)) and s.held.size()==0) {...s,retired:true,keyboardLive:false} else s
  action focusLost = s'={...s,focused:false}
  action enter = s'=if(s.keyboardLive and s.capable and not(s.failed) and s.held.size()==0) {...s,focused:true} else s
  action capabilityLost = s'={...s,capable:false,focused:false}
  action capabilityRestored = s'=if(not(s.failed) and s.retired and s.held.size()==0)
    {...s,capable:true,focused:false,keyboardLive:true,retired:false} else s
  action step = any{press(0),press(1),press(2),physicalRelease(1),physicalRelease(2),lose,cancel,retire,focusLost,enter,capabilityLost,capabilityRestored}
  val safety = s.released<=s.pressed and s.modifierResets<=s.pressed and
    (not(s.retired) or (not(s.keyboardLive) and s.held.size()==0)) and s.held.subseteq(Set(1,2))
  run oneHeldCancelledTest = init.then(press(1)).then(lose).then(cancel).then(all{assert(s.held.size()==0 and s.released==1 and s.cancelled==Set(1)),s'=s})
  run allHeldCancelledTest = init.then(press(1)).then(press(2)).then(lose).then(cancel).then(all{assert(s.released==2 and s.cancelled==Set(1,2) and s.modifierResets==1),s'=s})
  run unheldLossSilentTest = init.then(lose).then(cancel).then(all{assert(s.released==0 and s.modifierResets==0),s'=s})
  run duplicatePressRefusedTest = init.then(press(1)).then(press(1)).then(lose).then(cancel).then(all{assert(s.pressed==1 and s.released==1),s'=s})
  run alreadyReleasedExcludedTest = init.then(press(1)).then(press(2)).then(physicalRelease(1)).then(lose).then(cancel).then(all{assert(s.released==2 and s.cancelled==Set(2)),s'=s})
  run repeatCancellationSilentTest = init.then(press(1)).then(lose).then(cancel).then(cancel).then(all{assert(s.released==1 and s.modifierResets==1),s'=s})
  run cancellationBeforeRetirementTest = init.then(press(1)).then(lose).then(cancel).then(all{assert(s.keyboardLive and s.held.size()==0 and s.released==1),s'=s}).then(retire).then(all{assert(s.retired and not(s.keyboardLive)),s'=s})
  run latePressRefusedTest = init.then(lose).then(press(1)).then(cancel).then(all{assert(s.pressed==0 and s.released==0),s'=s})
  run lostPhysicalReleaseCannotBalanceTest = init.then(press(1)).then(lose).then(physicalRelease(1)).then(all{assert(s.held==Set(1) and s.released==0),s'=s}).then(cancel).then(all{assert(s.released==1),s'=s})
  run staleCancellationAfterRetirementTest = init.then(press(1)).then(lose).then(cancel).then(retire).then(cancel).then(all{assert(s.released==1 and s.modifierResets==1 and s.retired),s'=s})
  run focusLeaveCancelsWithoutRetirementTest = init.then(press(1)).then(focusLost).then(cancel).then(all{assert(s.keyboardLive and not(s.retired) and not(s.focused) and s.released==1 and s.held.size()==0),s'=s})
  run physicalReleaseWhileUnfocusedIgnoredTest = init.then(press(1)).then(focusLost).then(physicalRelease(1)).then(all{assert(s.held==Set(1) and s.released==0),s'=s})
  run newPressWhileUnfocusedRefusedTest = init.then(press(1)).then(focusLost).then(press(2)).then(all{assert(s.held==Set(1) and s.pressed==1),s'=s})
  run reenterCannotInventHeldKeyTest = init.then(press(1)).then(focusLost).then(cancel).then(enter).then(all{assert(s.focused and s.keyboardLive and s.held.size()==0 and s.pressed==1 and s.released==1),s'=s}).then(press(2)).then(physicalRelease(2)).then(all{assert(s.pressed==2 and s.released==2),s'=s})
  run capabilityRestoreAllowsFreshKeysTest = init.then(press(1)).then(capabilityLost).then(cancel).then(retire).then(capabilityRestored).then(enter).then(press(2)).then(physicalRelease(2)).then(all{assert(s.capable and s.keyboardLive and s.pressed==2 and s.released==2 and s.held.size()==0),s'=s})
  run retirementBeforeCancellationRefusedTest = init.then(press(1)).then(capabilityLost).then(retire).then(all{assert(s.keyboardLive and not(s.retired) and s.held==Set(1)),s'=s})
}
