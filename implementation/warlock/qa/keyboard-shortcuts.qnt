module keyboardShortcuts {
  // Bounded journal abstraction. Navigation coalesces; it carries no window effect.
  var s: {epoch:int, owner:int, high:int, seen:int, first:int, blocked:bool, route:int, exposures:List[int]}
  action init = s'={epoch:1,owner:1,high:0,seen:0,first:1,blocked:false,route:0,exposures:List()}
  action emit = all {s.high<8, s'={...s,high:s.high+1,route:(s.high%3)+1}}
  action consume = s'=if(s.owner==s.epoch and s.high>s.seen) {
    ...s,seen:s.high,exposures:if(not(s.blocked) and s.first<=s.seen+1) s.exposures.append(s.high) else s.exposures
  } else s
  action duplicate = s'=s
  action block = s'={...s,blocked:true}
  action unblock = s'={...s,blocked:false}
  action trim = all {s.high>1,s'={...s,first:s.high}}
  action rebind = s'={...s,epoch:s.epoch+1,seen:s.high}
  action adopt = s'={...s,owner:s.epoch,seen:s.high}
  action step = any {emit,consume,duplicate,block,unblock,trim,rebind,adopt}
  val safety = s.seen<=s.high and s.exposures.indices().forall(i=>s.exposures.nth(i)<=s.high and s.exposures.indices().forall(j=>i==j or s.exposures.nth(i)!=s.exposures.nth(j)))
  run consumeOnceTest = init.then(emit).then(consume).then(consume).then(all {assert(s.exposures==List(1)),s'=s})
  run blockedNeverRoutesTest = init.then(emit).then(block).then(consume).then(unblock).then(consume).then(all {assert(s.exposures==List() and s.seen==1),s'=s})
  run gapNeverReplaysTest = init.then(emit).then(emit).then(trim).then(consume).then(all {assert(s.exposures==List() and s.seen==2),s'=s})
  run rebindAdoptsWithoutReplayTest = init.then(emit).then(rebind).then(consume).then(adopt).then(consume).then(all {assert(s.exposures==List()),s'=s})
  run burstCoalescesToLatestTest = init.then(emit).then(emit).then(consume).then(all {assert(s.exposures==List(2)),s'=s})
}
