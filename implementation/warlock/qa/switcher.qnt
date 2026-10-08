module switcher {
  // Release/Ready ordering and tombstones. Actual selection is checked by the
  // compiled production reducer; this model supplies no native input verdict.
  var s: {ready: bool, released: bool, final: int, steps: Set[int], closed: bool, live: Set[int], frozen: Set[int], emitted: int}
  action init = s'={ready:false,released:false,final:0,steps:Set(),closed:false,live:Set(1,2,3),frozen:Set(),emitted:0}
  action first = all {not(s.closed),s'={...s,steps:s.steps.union(Set(1))}}
  action second = all {not(s.closed),s'={...s,steps:s.steps.union(Set(2))}}
  action release = all {not(s.closed),s'={...s,released:true,final:2}}
  action ready = all {not(s.closed),not(s.ready),s'={...s,ready:true,frozen:s.live}}
  action settle = all {not(s.closed),s.ready,s.released,s.steps.contains(1),s.steps.contains(2),s'={...s,closed:true,emitted:s.emitted+1}}
  action cancel = s'={...s,closed:true}
  action retire = s'={...s,live:s.live.exclude(Set(2)),frozen:s.frozen.exclude(Set(2))}
  action arrive = s'={...s,live:s.live.union(Set(4))}
  action stale = s'=s
  action step = any {first,second,release,ready,settle,cancel,retire,arrive,stale}
  val safety = s.emitted<=1 and (s.emitted==0 or (s.ready and s.released and s.closed and s.steps.contains(1) and s.steps.contains(2)))
  run releaseBeforeReadyTest = init.then(first).then(second).then(release).then(ready).then(settle).then(stale).then(all {assert(s.emitted==1),s'=s})
  run releaseBeforeMissingStepTest = init.then(first).then(release).then(ready).then(second).then(settle).then(all {assert(s.emitted==1),s'=s})
  run cancelIsTerminalTest = init.then(first).then(ready).then(cancel).then(stale).then(all {assert(s.emitted==0 and s.closed),s'=s})
  run arrivalsWaitForNextRingTest = init.then(first).then(ready).then(arrive).then(retire).then(all {assert(s.frozen==Set(1,3)),s'=s})
}
