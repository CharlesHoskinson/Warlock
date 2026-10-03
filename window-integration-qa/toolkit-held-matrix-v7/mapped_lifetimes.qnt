module mapped_lifetimes {
 var public: Set[int]
 var native: Set[int]
 var registered: Set[int]
 var closed: Set[int]
 var failed: bool
 var finished: bool
 action init = all {public'=Set(),native'=Set(),registered'=Set(),closed'=Set(),failed'=false,finished'=false}
 action publicCreate = {nondet id=Set(1,2,3,4).filter(id=>not(public.contains(id)) and not(closed.contains(id))).oneOf();all {not(finished),not(public.contains(id)),not(closed.contains(id)),public'=public.union(Set(id)),native'=native,registered'=registered,closed'=closed,failed'=failed,finished'=finished}}
 action nativeMap = {nondet id=public.filter(id=>not(native.contains(id))).oneOf();all {not(finished),not(native.contains(id)),native'=native.union(Set(id)),public'=public,registered'=registered,closed'=closed,failed'=failed,finished'=finished}}
 action observeExact = {nondet id=native.filter(id=>not(registered.contains(id))).oneOf();all {not(finished),registered'=registered.union(Set(id)),public'=public,native'=native,closed'=closed,failed'=failed,finished'=finished}}
 action refuseUnknown = all {failed'=true,public'=public,native'=native,registered'=registered,closed'=closed,finished'=finished}
 action quit = all {native==public,native.subseteq(registered),closed'=closed.union(native),public'=Set(),native'=Set(),registered'=registered,failed'=failed,finished'=true}
 action idle = all {public'=public,native'=native,registered'=registered,closed'=closed,failed'=failed,finished'=finished}
 action step = any {publicCreate,nativeMap,observeExact,refuseUnknown,quit,idle}
 val invariant = all {native.subseteq(public),closed.subseteq(registered),closed.intersect(native)==Set(),finished implies all {native==Set(),public==Set()}}
 run publicBeforeNativeRemainsPendingTest = init.then(publicCreate).then(all {assert(native==Set() and not(finished)),idle})
 run exactNativeBeforeRegisteredCloseTest = init.then(publicCreate).then(nativeMap).then(observeExact).then(quit).then(all {assert(invariant and finished),idle})
 run earlierRegistrationsRetainedTest = init.then(publicCreate).then(nativeMap).then(observeExact).then(publicCreate).then(nativeMap).then(observeExact).then(quit).then(all {assert(registered.size()==2 and invariant),idle})
 run partialFailureStillRegistersExactBeforeQuitTest = init.then(publicCreate).then(nativeMap).then(refuseUnknown).then(observeExact).then(quit).then(all {assert(failed and finished and invariant),idle})
}
