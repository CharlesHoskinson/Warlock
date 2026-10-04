module registry {
  // Small bounded ID domain abstracts uint64 exhaustion; C++ tests its actual boundary.
  var s: { last: int, a: int, af: int, b: int, bf: int, retired: Set[int] }
  action init = s' = {last:0,a:0,af:0,b:0,bf:0,retired:Set()}
  action hello(peer: int): bool = {
    val id = if (peer == 1) s.a else s.b
    val frontend = if (peer == 1) s.af else s.bf
    val permitted = if (id == 0) s.last < 4 else frontend < 4
    val nextId = if (id == 0) s.last+1 else id
    s' = if (not(permitted)) s else if (peer == 1)
      {...s,last:if(id == 0) s.last+1 else s.last,a:nextId,af:frontend+1}
      else {...s,last:if(id == 0) s.last+1 else s.last,b:nextId,bf:frontend+1}
  }
  action detach(peer: int): bool = s' = if (peer == 1) {...s,a:0,af:0} else {...s,b:0,bf:0}
  action retire(callerId: int, callerFrontend: int, targetId: int, targetFrontend: int, sameLifetime: bool): bool = {
    val callerValid = callerId != 0 and callerId == s.a and callerFrontend == s.af
    val targetValid = targetId != 0 and targetId == s.b and targetFrontend == s.bf
    val permitted = callerValid and targetValid and sameLifetime and callerId != targetId
    s' = if(permitted) {...s,b:0,bf:0,retired:s.retired.union(Set(targetId))} else s
  }
  action step = any { hello(1),hello(2),detach(1),detach(2),retire(s.a,s.af,s.b,s.bf,true),retire(0,0,s.b,s.bf,true),retire(s.a,s.af,s.b,s.bf,false),retire(s.a,s.af,s.b,s.bf+1,true),retire(s.a,s.af,s.a,s.af,true) }
  val safety = s.last <= 4 and s.a <= s.last and s.b <= s.last and (s.a == 0 or s.a != s.b) and not(s.retired.contains(s.a)) and not(s.retired.contains(s.b))
  run exactRetirementTest = init.then(hello(1)).then(hello(2)).then(retire(s.a,s.af,s.b,s.bf,true)).then(all{assert(s.a == 1 and s.af == 1 and s.b == 0 and s.retired.contains(2)),s'=s})
  run reattachTest = init.then(hello(1)).then(hello(2)).then(retire(s.a,s.af,s.b,s.bf,true)).then(hello(2)).then(all{assert(s.b == 3 and s.last == 3 and s.retired.contains(2)),s'=s})
  run detachNoReuseTest = init.then(hello(2)).then(detach(2)).then(hello(2)).then(all{assert(s.b == 2 and s.last == 2),s'=s})
  run foreignCallerTest = init.then(hello(1)).then(hello(2)).then(retire(0,0,s.b,s.bf,true)).then(all{assert(s.b == 2),s'=s})
  run foreignLifetimeTest = init.then(hello(1)).then(hello(2)).then(retire(s.a,s.af,s.b,s.bf,false)).then(all{assert(s.b == 2),s'=s})
  run staleTargetTest = init.then(hello(1)).then(hello(2)).then(hello(2)).then(retire(s.a,s.af,s.b,1,true)).then(all{assert(s.b == 2 and s.bf == 2),s'=s})
  run currentCallerTest = init.then(hello(1)).then(retire(s.a,s.af,s.a,s.af,true)).then(all{assert(s.a == 1 and s.af == 1),s'=s})
  run allocatorExhaustionTest = init.then(hello(1)).then(detach(1)).then(hello(1)).then(detach(1)).then(hello(1)).then(detach(1)).then(hello(1)).then(detach(1)).then(hello(1)).then(all{assert(s.last == 4 and s.a == 0),s'=s})
  run frontendExhaustionTest = init.then(hello(1)).then(hello(1)).then(hello(1)).then(hello(1)).then(hello(1)).then(all{assert(s.a == 1 and s.af == 4),s'=s})
}
