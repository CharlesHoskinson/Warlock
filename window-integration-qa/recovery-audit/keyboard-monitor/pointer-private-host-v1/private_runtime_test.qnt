module private_runtime_test {
  import private_runtime.* from "./private_runtime"
  action check(expected:bool):bool=all {assert(loaded==expected),loaded'=loaded,candidate'=candidate}
  run validOwnedPrivateTest=init.then(attempt(good)).then(check(true))
  run mainRefusedTest=init.then(attempt(good.with("pathKind","main"))).then(check(false))
  run legacyTmpRefusedTest=init.then(attempt(good.with("pathKind","legacy-tmp"))).then(check(false))
  run uppercaseRefusedTest=init.then(attempt(good.with("pathKind","uppercase"))).then(check(false))
  run nestedSuffixRefusedTest=init.then(attempt(good.with("pathKind","extra-component"))).then(check(false))
  run implicitRefusedTest=init.then(attempt(good.with("explicit",false))).then(check(false))
  run foreignRuntimeRefusedTest=init.then(attempt(good.with("ownRuntime",false))).then(check(false))
  run foreignParentRefusedTest=init.then(attempt(good.with("ownParent",false))).then(check(false))
  run foreignUserRefusedTest=init.then(attempt(good.with("ownUser",false))).then(check(false))
  run publicModeRefusedTest=init.then(attempt(good.with("privateModes",false))).then(check(false))
  run symlinkRefusedTest=init.then(attempt(good.with("dirsNotLinks",false))).then(check(false))
  run foreignBusRefusedTest=init.then(attempt(good.with("ownBus",false))).then(check(false))
}
