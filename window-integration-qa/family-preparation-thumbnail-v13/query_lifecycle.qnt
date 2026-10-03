module query_lifecycle {
  var registered: bool
  var qsExec: bool
  var running: Set[int]
  var finished: Set[int]
  var failed: Set[int]
  var stopped: bool
  var unloaded: bool
  action init = all { registered'=false, qsExec'=false, running'=Set(),
    finished'=Set(), failed'=Set(), stopped'=false, unloaded'=false }
  action register = all { not(registered), not(qsExec), registered'=true,
    qsExec'=qsExec, running'=running, finished'=finished, failed'=failed,
    stopped'=stopped, unloaded'=unloaded }
  action exec = all { registered, not(qsExec), qsExec'=true,
    registered'=registered, running'=running, finished'=finished, failed'=failed,
    stopped'=stopped, unloaded'=unloaded }
  action query = {
    nondet lifetime = Set(0,1,2,3).oneOf()
    all { registered, qsExec, not(stopped),
      not(running.union(finished).union(failed).contains(lifetime)),
      running'=running.union(Set(lifetime)), finished'=finished, failed'=failed,
      registered'=registered, qsExec'=qsExec, stopped'=stopped, unloaded'=unloaded }
  }
  action terminal = {
    nondet lifetime = running.oneOf()
    all { running'=running.exclude(Set(lifetime)), finished'=finished.union(Set(lifetime)),
      failed'=failed, registered'=registered, qsExec'=qsExec, stopped'=stopped, unloaded'=unloaded }
  }
  action failure = {
    nondet lifetime = running.oneOf()
    all { running'=running.exclude(Set(lifetime)), failed'=failed.union(Set(lifetime)),
      finished'=finished, registered'=registered, qsExec'=qsExec, stopped'=stopped, unloaded'=unloaded }
  }
  action stop = all { registered, qsExec, stopped'=true, registered'=registered,
    qsExec'=qsExec, running'=running, finished'=finished, failed'=failed, unloaded'=unloaded }
  action unload = all { stopped, running==Set(), failed==Set(), finished.contains(0),
    // 0 is the one harness query; 1..3 are distinct registered QS lifetimes.
    finished.intersect(Set(1,2,3))!=Set(), unloaded'=true, registered'=registered,
    qsExec'=qsExec, running'=running, finished'=finished, failed'=failed, stopped'=stopped }
  action stutter = all { registered'=registered, qsExec'=qsExec, running'=running,
    finished'=finished, failed'=failed, stopped'=stopped, unloaded'=unloaded }
  action step = any { register, exec, query, terminal, failure, stop, unload, stutter }
  val invariant = all { qsExec implies registered,
    running.intersect(finished)==Set(), running.intersect(failed)==Set(), finished.intersect(failed)==Set(),
    unloaded implies all { stopped, registered, qsExec, running==Set(), failed==Set(),
      finished.contains(0), finished.intersect(Set(1,2,3))!=Set() } }
  run gateBeforeExecTest = init.then(register).then(exec).then(all { assert(registered and qsExec and invariant), stutter })
  run failedQueryCannotUnloadTest = init.then(register).then(exec).then(query).then(failure).then(stop)
    .then(all { assert(failed!=Set() and not(unloaded)), stutter })
  run runningQueryCannotUnloadTest = init.then(register).then(exec).then(query).then(stop)
    .then(all { assert(running!=Set() and not(unloaded)), stutter })
  run completedQueriesCanUnloadTest = init.then(register).then(exec)
    .then(query).then(terminal).then(query).then(terminal).then(query).then(terminal).then(query).then(terminal)
    .then(stop).then(unload).then(all { assert(unloaded and invariant), stutter })
}
