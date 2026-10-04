// One logical pointer, three bounded button identities. Callback atomicity and
// multi-object lifetime are checked by actual C++ replay, not proved here.
module held {
  type State = {failed:bool,retired:bool,pointerLive:bool,held:Set[int],pressed:int,
    released:int,cancelFrames:int,cancelled:Set[int]}
  var s:State
  action init = s'={failed:false,retired:false,pointerLive:true,held:Set(),pressed:0,
    released:0,cancelFrames:0,cancelled:Set()}
  action press(button:int):bool = s'=if(s.pointerLive and not(s.failed) and button>0 and button<=3 and not(s.held.contains(button)))
    {...s,held:s.held.union(Set(button)),pressed:s.pressed+1} else s
  action physicalRelease(button:int):bool = s'=if(s.pointerLive and not(s.failed) and s.held.contains(button))
    {...s,held:s.held.exclude(Set(button)),released:s.released+1} else s
  action lose = s'={...s,failed:true}
  action cancel = s'=if(s.failed and not(s.retired))
    {...s,held:Set(),released:s.released+s.held.size(),cancelFrames:s.cancelFrames+(if(s.held.size()>0) 1 else 0),cancelled:s.cancelled.union(s.held)} else s
  action retire = s'=if(s.failed and s.held.size()==0) {...s,retired:true,pointerLive:false} else s
  action step = any{press(0),press(1),press(2),press(3),physicalRelease(1),physicalRelease(2),physicalRelease(3),lose,cancel,retire}
  val safety = s.released<=s.pressed and s.cancelFrames<=1 and
    (not(s.retired) or (not(s.pointerLive) and s.held.size()==0)) and s.held.subseteq(Set(1,2,3))
  run oneHeldCancelledTest = init.then(press(1)).then(lose).then(cancel).then(all{assert(s.held.size()==0 and s.released==1 and s.cancelled==Set(1)),s'=s})
  run allHeldCancelledTest = init.then(press(1)).then(press(2)).then(press(3)).then(lose).then(cancel).then(all{assert(s.released==3 and s.cancelled==Set(1,2,3) and s.cancelFrames==1),s'=s})
  run unheldLossSilentTest = init.then(lose).then(cancel).then(all{assert(s.released==0 and s.cancelFrames==0),s'=s})
  run duplicatePressRefusedTest = init.then(press(1)).then(press(1)).then(lose).then(cancel).then(all{assert(s.pressed==1 and s.released==1),s'=s})
  run alreadyReleasedExcludedTest = init.then(press(1)).then(press(2)).then(physicalRelease(1)).then(lose).then(cancel).then(all{assert(s.released==2 and s.cancelled==Set(2)),s'=s})
  run repeatCancellationSilentTest = init.then(press(1)).then(lose).then(cancel).then(cancel).then(all{assert(s.released==1 and s.cancelFrames==1),s'=s})
  run cancellationBeforeRetirementTest = init.then(press(1)).then(lose).then(cancel).then(all{assert(s.pointerLive and s.held.size()==0 and s.released==1),s'=s}).then(retire).then(all{assert(s.retired and not(s.pointerLive)),s'=s})
  run latePressRefusedTest = init.then(lose).then(press(1)).then(cancel).then(all{assert(s.pressed==0 and s.released==0),s'=s})
  run lostPhysicalReleaseCannotBalanceTest = init.then(press(1)).then(lose).then(physicalRelease(1)).then(all{assert(s.held==Set(1) and s.released==0),s'=s}).then(cancel).then(all{assert(s.released==1),s'=s})
  run staleCancellationAfterRetirementTest = init.then(press(1)).then(lose).then(cancel).then(retire).then(cancel).then(all{assert(s.released==1 and s.cancelFrames==1 and s.retired),s'=s})
}
