module switcher {
  // Release/Ready ordering and tombstones. Actual selection is checked by the
  // compiled production reducer; this model supplies no native input verdict.
  var s: {ready: bool, released: bool, final: int, steps: Set[int], closed: bool, live: Set[int], frozen: Set[int], emitted: int, prepared: bool, cancelled: bool, consumed: bool, nativeEffects: int}
  action init = s'={ready:false,released:false,final:0,steps:Set(),closed:false,live:Set(1,2,3),frozen:Set(),emitted:0,prepared:false,cancelled:false,consumed:false,nativeEffects:0}
  action first = all {not(s.closed),s'={...s,steps:s.steps.union(Set(1)),frozen:if (s.steps.size()==0) s.live else s.frozen}}
  action second = all {not(s.closed),s'={...s,steps:s.steps.union(Set(2))}}
  action release = all {not(s.closed),s'={...s,released:true,final:2}}
  action ready = all {not(s.closed),not(s.ready),s'={...s,ready:true}}
  action settle = all {not(s.closed),s.ready,s.released,s.steps.contains(1),s.steps.contains(2),s'={...s,closed:true,emitted:s.emitted+1}}
  action cancel = s'={...s,closed:true,cancelled:true}
  action prepareNative = all {s.ready,s.released,s'={...s,prepared:true}}
  action commitNative = all {s.prepared,not(s.cancelled),not(s.consumed),s'={...s,consumed:true,nativeEffects:s.nativeEffects+1}}
  action retire = s'={...s,live:s.live.exclude(Set(2)),frozen:s.frozen.exclude(Set(2))}
  action arrive = s'={...s,live:s.live.union(Set(4))}
  action stale = s'=s
  action step = any {first,second,release,ready,settle,cancel,retire,arrive,stale,prepareNative,commitNative}
  val safety = s.nativeEffects<=1 and (s.nativeEffects==0 or s.consumed) and s.emitted<=1 and (s.emitted==0 or (s.ready and s.released and s.closed and s.steps.contains(1) and s.steps.contains(2)))
  run releaseBeforeReadyTest = init.then(first).then(second).then(release).then(ready).then(settle).then(stale).then(all {assert(s.emitted==1),s'=s})
  run releaseBeforeMissingStepTest = init.then(first).then(release).then(ready).then(second).then(settle).then(all {assert(s.emitted==1),s'=s})
  run cancelIsTerminalTest = init.then(first).then(ready).then(cancel).then(stale).then(all {assert(s.emitted==0 and s.closed),s'=s})
  run arrivalBeforeReadyExcludedTest = init.then(first).then(arrive).then(ready).then(all {assert(s.frozen==Set(1,2,3)),s'=s})
  run releasedCancellationBeforeReadyTest = init.then(first).then(second).then(release).then(cancel).then(stale).then(all {assert(s.emitted==0 and s.closed),s'=s})
  run cancelledPreparedNeverCommitsTest = init.then(first).then(second).then(release).then(ready).then(prepareNative).then(cancel).then(stale).then(all {assert(s.prepared and s.cancelled and not(s.consumed) and s.nativeEffects==0),s'=s})
  run nativeCommitConsumesOnceTest = init.then(first).then(second).then(release).then(ready).then(prepareNative).then(commitNative).then(stale).then(all {assert(s.consumed and s.nativeEffects==1),s'=s})
  run arrivalsWaitForNextRingTest = init.then(first).then(ready).then(arrive).then(retire).then(all {assert(s.frozen==Set(1,3)),s'=s})
  run retirementBeforeReadyCannotAdmitArrivalTest = init.then(first).then(second).then(release).then(retire).then(arrive).then(ready).then(settle).then(all {assert(s.frozen==Set(1,3) and s.emitted==1),s'=s})
}
