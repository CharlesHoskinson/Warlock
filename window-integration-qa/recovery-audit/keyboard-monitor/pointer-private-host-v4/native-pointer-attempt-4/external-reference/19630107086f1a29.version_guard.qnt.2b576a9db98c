module version_guard {
  var advertised: int
  var cap: int
  var minimum: int
  var bound: int
  var rejected: bool
  pure def common(a: int,c: int): int = if (a<c) a else c
  pure def negotiated(a: int,c: int,m: int): int = if (common(a,c) >= m) common(a,c) else 0
  action init = all { advertised'=0,cap'=6,minimum'=4,bound'=0,rejected'=true }
  action bind(a: int,c: int,m: int): bool = all {
    advertised'=a,cap'=c,minimum'=m,
    bound'=negotiated(a,c,m),rejected'=negotiated(a,c,m)==0
  }
  action step = {
    nondet a = 0.to(12).oneOf()
    nondet policy = Set((9,5),(6,1),(6,4),(1,1),(4,4)).oneOf()
    bind(a,policy._1,policy._2)
  }
  val validBinding = bound==0 or (bound<=advertised and bound<=cap and bound>=minimum)
  val truthfulRefusal = rejected==(common(advertised,cap)<minimum)
  action check(p: bool): bool = all {assert(p),advertised'=advertised,cap'=cap,minimum'=minimum,bound'=bound,rejected'=rejected}
  run compositor5Binds5Test=init.then(bind(5,6,4)).then(check(bound==5 and not(rejected)))
  run lowCompositorRefusesDamageBufferTest=init.then(bind(3,6,4)).then(check(bound==0 and rejected))
  run lowDmabufRefusesDefaultFeedbackTest=init.then(bind(3,4,4)).then(check(bound==0 and rejected))
  run futureVersionClampsToClientTest=init.then(bind(12,6,4)).then(check(bound==6 and validBinding))
  run absentGlobalDoesNotBindTest=init.then(bind(0,9,5)).then(check(bound==0 and rejected))
}
