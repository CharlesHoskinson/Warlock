module helper_lifecycle {
  var permitted: Set[int]
  var running: Set[int]
  var finished: Set[int]
  var failed: Set[int]
  var unloaded: bool
  action init = all {
    permitted' = Set(0, 1, 2, 3, 4), running' = Set(),
    finished' = Set(), failed' = Set(), unloaded' = false
  }
  action start = {
    nondet id = permitted.oneOf()
    all { not(unloaded), not(running.contains(id)),
      not(finished.contains(id)), not(failed.contains(id)),
      running' = running.union(Set(id)), permitted' = permitted,
      finished' = finished, failed' = failed, unloaded' = unloaded }
  }
  action finish = {
    nondet id = running.oneOf()
    all { running' = running.exclude(Set(id)), finished' = finished.union(Set(id)),
      permitted' = permitted, failed' = failed, unloaded' = unloaded }
  }
  action failure = {
    nondet id = running.oneOf()
    all { running' = running.exclude(Set(id)), failed' = failed.union(Set(id)),
      permitted' = permitted, finished' = finished, unloaded' = unloaded }
  }
  action unload = all {
    finished == permitted, running == Set(), failed == Set(),
    unloaded' = true, permitted' = permitted, running' = running,
    finished' = finished, failed' = failed
  }
  action stutter = all { permitted' = permitted, running' = running,
    finished' = finished, failed' = failed, unloaded' = unloaded }
  action step = any { start, finish, failure, unload, stutter }
  val invariant = all {
    running.intersect(finished) == Set(), running.intersect(failed) == Set(),
    finished.intersect(failed) == Set(),
    running.union(finished).union(failed).subseteq(permitted),
    unloaded implies all { finished == permitted, running == Set(), failed == Set() }
  }
  run startedCannotUnloadTest = init.then(start).then(all { assert(not(unloaded)), stutter })
  run failedCannotUnloadTest = init.then(start).then(failure).then(all { assert(not(unloaded)), stutter })
  run completedPrefixCannotUnloadTest = init.then(start).then(finish).then(all { assert(not(unloaded)), stutter })
  run allNormalCanUnloadTest = init.then(start).then(finish).then(start).then(finish)
    .then(start).then(finish).then(start).then(finish).then(start).then(finish)
    .then(unload).then(all { assert(unloaded and invariant), stutter })
}
