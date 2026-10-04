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
    val targetValid = targetId != 0 and ((targetId == s.b and targetFrontend == s.bf) or (targetId == s.a and targetFrontend == s.af))
    val permitted = callerValid and targetValid and sameLifetime and callerId != targetId
    s' = if(not(permitted)) s else if(targetId == s.a) {...s,a:0,af:0,retired:s.retired.union(Set(targetId))} else {...s,b:0,bf:0,retired:s.retired.union(Set(targetId))}
  }
  action step = any { hello(1),hello(2),detach(1),detach(2),retire(s.a,s.af,s.b,s.bf,true),retire(0,0,s.b,s.bf,true),retire(s.a,s.af,s.b,s.bf,false),retire(s.a,s.af,s.b,s.bf+1,true),retire(s.a,s.af,s.a,s.af,true) }
  val safety = s.last <= 4 and s.a <= s.last and s.b <= s.last and (s.a == 0 or s.a != s.b) and not(s.retired.contains(s.a)) and not(s.retired.contains(s.b))
  // 0 refused, 1 registered, 2 future, 3 retired. Query is pure/read-only.
  pure def stateOf(st: { last: int, a: int, af: int, b: int, bf: int, retired: Set[int] }, callerId: int, callerFrontend: int, id: int, frontend: int, sameLifetime: bool): int = {
    val auth = callerId != 0 and callerId == st.a and callerFrontend == st.af
    val current = if(id == st.a) st.af else if(id == st.b) st.bf else 0
    if(not(auth) or not(sameLifetime) or id <= 0 or frontend <= 0) 0
    else if(id > st.last or (false)) 2
    else if(current > 0 and frontend == current) 1 else 3
  }
  run queryRegisteredTest = init.then(hello(1)).then(hello(2)).then(all{assert(stateOf(s,s.a,s.af,s.b,s.bf,true)==1),s'=s})
  run queryAbsentRetiredTest = init.then(hello(1)).then(hello(2)).then(detach(2)).then(all{assert(stateOf(s,s.a,s.af,2,1,true)==3),s'=s})
  run queryOldFrontendRetiredTest = init.then(hello(1)).then(hello(2)).then(hello(2)).then(all{assert(stateOf(s,s.a,s.af,s.b,1,true)==3),s'=s})
  run queryFutureSessionTest = init.then(hello(1)).then(all{assert(stateOf(s,s.a,s.af,2,1,true)==2),s'=s})
  run queryFutureFrontendTest = init.then(hello(1)).then(hello(2)).then(all{assert(stateOf(s,s.a,s.af,s.b,2,true)==2 and stateOf(s,s.a,s.af,s.a,2,true)==2),s'=s})
  run querySelfRegisteredTest = init.then(hello(1)).then(all{assert(stateOf(s,s.a,s.af,s.a,s.af,true)==1),s'=s})
  run queryForeignCallerTest = init.then(hello(1)).then(hello(2)).then(all{assert(stateOf(s,0,0,s.b,s.bf,true)==0),s'=s})
  run queryForeignLifetimeTest = init.then(hello(1)).then(hello(2)).then(all{assert(stateOf(s,s.a,s.af,s.b,s.bf,false)==0),s'=s})
  run queryZeroIdentityTest = init.then(hello(1)).then(all{assert(stateOf(s,s.a,s.af,0,1,true)==0 and stateOf(s,s.a,s.af,1,0,true)==0),s'=s})
  run queryOldGrantAfterReattachTest = init.then(hello(1)).then(hello(2)).then(detach(2)).then(hello(2)).then(all{assert(stateOf(s,s.a,s.af,2,1,true)==3 and stateOf(s,s.a,s.af,3,1,true)==1),s'=s})
  run exactRetirementTest = init.then(hello(1)).then(hello(2)).then(retire(s.a,s.af,s.b,s.bf,true)).then(all{assert(s.a == 1 and s.af == 1 and s.b == 0 and s.retired.contains(2)),s'=s})
  run reattachTest = init.then(hello(1)).then(hello(2)).then(retire(s.a,s.af,s.b,s.bf,true)).then(hello(2)).then(all{assert(s.b == 3 and s.last == 3 and s.retired.contains(2)),s'=s})
  run oldGrantDeniedTest = init.then(hello(1)).then(hello(2)).then(retire(s.a,s.af,s.b,s.bf,true)).then(hello(2)).then(retire(s.a,s.af,2,1,true)).then(all{assert(s.b == 3 and s.retired.contains(2)),s'=s})
  run detachNoReuseTest = init.then(hello(2)).then(detach(2)).then(hello(2)).then(all{assert(s.b == 2 and s.last == 2),s'=s})
  run foreignCallerTest = init.then(hello(1)).then(hello(2)).then(retire(0,0,s.b,s.bf,true)).then(all{assert(s.b == 2),s'=s})
  run foreignLifetimeTest = init.then(hello(1)).then(hello(2)).then(retire(s.a,s.af,s.b,s.bf,false)).then(all{assert(s.b == 2),s'=s})
  run staleTargetTest = init.then(hello(1)).then(hello(2)).then(hello(2)).then(retire(s.a,s.af,s.b,1,true)).then(all{assert(s.b == 2 and s.bf == 2),s'=s})
  run currentCallerTest = init.then(hello(1)).then(retire(s.a,s.af,s.a,s.af,true)).then(all{assert(s.a == 1 and s.af == 1),s'=s})
  run allocatorExhaustionTest = init.then(hello(1)).then(detach(1)).then(hello(1)).then(detach(1)).then(hello(1)).then(detach(1)).then(hello(1)).then(detach(1)).then(hello(1)).then(all{assert(s.last == 4 and s.a == 0),s'=s})
  run frontendExhaustionTest = init.then(hello(1)).then(hello(1)).then(hello(1)).then(hello(1)).then(hello(1)).then(all{assert(s.a == 1 and s.af == 4),s'=s})
  run futureSessionRefusalNotProofTest = init.then(hello(1)).then(hello(2)).then(retire(s.a,s.af,3,1,true)).then(all{assert(s.b == 2 and not(s.retired.contains(3))),s'=s}).then(detach(2)).then(hello(2)).then(all{assert(s.b == 3 and s.bf == 1),s'=s})
  run futureFrontendRefusalNotProofTest = init.then(hello(1)).then(hello(2)).then(retire(s.a,s.af,s.b,2,true)).then(all{assert(s.b == 2 and s.bf == 1),s'=s}).then(hello(2)).then(all{assert(s.b == 2 and s.bf == 2),s'=s})
}
