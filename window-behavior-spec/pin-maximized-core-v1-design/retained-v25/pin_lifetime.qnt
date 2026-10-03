module pin_lifetime {
  type Event = Capture(int) | Commit({owner:int, session:int, ready:bool})
    | Close(int) | Reuse | Focus(int) | Tick({owner:int, generation:int})
    | Minimize(int) | Restore(int) | Reload | Reduce | Idle
  type S = { live:Set[int], minimized:Set[int], pinned:Set[int], saved:Set[int],
    focus:int, captured:int, session:int, generation:int,
    fade:int -> int, lastWrite:int, refused:bool }
  var s:S
  action init = s' = {live:Set(1,2), minimized:Set(), pinned:Set(2), saved:Set(),
    focus:1, captured:0, session:1, generation:0, fade:Map(), lastWrite:0, refused:false}
  def eligible(w:int):bool = s.live.contains(w) and not(s.minimized.contains(w))
  action fire(e:Event):bool = {
    val b = {...s,lastWrite:0,refused:false}
    s' = match e {
      | Capture(w) => {...b,captured:if(eligible(w))w else 0}
      | Commit(p) => if(p.owner==s.captured and p.session==s.session and eligible(p.owner) and p.ready) {
          ...b, pinned:if(s.pinned.contains(p.owner))s.pinned.exclude(Set(p.owner)) else s.pinned.union(Set(p.owner)),
          generation:s.generation+1, fade:s.fade.put(p.owner,s.generation+1), lastWrite:p.owner
        } else {...b,refused:true}
      | Close(w) => {...b,live:s.live.exclude(Set(w)),minimized:s.minimized.exclude(Set(w)),
          pinned:s.pinned.exclude(Set(w)),saved:s.saved.exclude(Set(w)),fade:s.fade.keys().exclude(Set(w)).mapBy(k=>s.fade.get(k))}
      | Reuse => {...b,live:s.live.union(Set(3))}
      | Focus(w) => {...b,focus:if(eligible(w))w else s.focus}
      | Tick(p) => if(eligible(p.owner) and s.fade.keys().contains(p.owner) and s.fade.get(p.owner)==p.generation) {...b,lastWrite:p.owner} else b
      | Minimize(w) => if(eligible(w)) {...b,minimized:s.minimized.union(Set(w)),
          saved:if(s.pinned.contains(w))s.saved.union(Set(w)) else s.saved.exclude(Set(w)),
          pinned:s.pinned.exclude(Set(w)),fade:s.fade.keys().exclude(Set(w)).mapBy(k=>s.fade.get(k))} else b
      | Restore(w) => if(s.live.contains(w) and s.minimized.contains(w)) {...b,
          minimized:s.minimized.exclude(Set(w)),pinned:if(s.saved.contains(w))s.pinned.union(Set(w)) else s.pinned,
          saved:s.saved.exclude(Set(w))} else b
      | Reload => {...b,session:s.session+1,generation:s.generation+1,fade:Map(),captured:0}
      | Reduce => {...b,generation:s.generation+1,fade:Map()}
      | Idle => b
    }
  }
  val invariant = all {
    s.pinned.subseteq(s.live), s.minimized.subseteq(s.live), s.saved.subseteq(s.minimized),
    s.pinned.intersect(s.minimized)==Set(),
    s.fade.keys().subseteq(s.live.exclude(s.minimized)),
    s.lastWrite==0 or eligible(s.lastWrite)
  }
  action step = {
    nondet w=Set(1,2,3).oneOf()
    nondet e=Set(Capture(w),Commit({owner:w,session:1,ready:true}),Commit({owner:w,session:2,ready:true}),
      Commit({owner:w,session:1,ready:false}),Close(w),Reuse,Focus(w),
      Tick({owner:w,generation:1}),Tick({owner:w,generation:2}),Minimize(w),Restore(w),Reload,Reduce,Idle).oneOf()
    fire(e)
  }
  action check(p:bool):bool = all {assert(p),s'=s}
  action pinOne = fire(Capture(1)).then(fire(Commit({owner:1,session:1,ready:true})))
  run focusCannotRedirectCapturedPinTest = init.then(fire(Capture(1))).then(fire(Focus(2))).then(fire(Commit({owner:1,session:1,ready:true}))).then(check(s.pinned==Set(1,2) and s.lastWrite==1 and s.focus==2))
  run otherMemberNeverToggledTest = init.then(pinOne).then(check(s.pinned.contains(2)))
  run twoRealClicksToggleTwiceTest = init.then(pinOne).then(pinOne).then(check(s.pinned==Set(2)))
  run closedOwnerGetsNoPinWriteTest = init.then(fire(Capture(1))).then(fire(Close(1))).then(fire(Commit({owner:1,session:1,ready:true}))).then(check(s.lastWrite==0 and s.refused))
  run reusedAddressCannotReceiveOldOwnerPinTest = init.then(fire(Capture(1))).then(fire(Close(1))).then(fire(Reuse)).then(fire(Commit({owner:1,session:1,ready:true}))).then(check(not(s.pinned.contains(3)) and s.lastWrite==0))
  run noActiveWindowFallbackTest = init.then(fire(Capture(3))).then(fire(Commit({owner:3,session:1,ready:true}))).then(check(s.pinned==Set(2) and s.refused))
  run backendRefusalPreservesAllPinsTest = init.then(fire(Capture(1))).then(fire(Commit({owner:1,session:1,ready:false}))).then(check(s.pinned==Set(2) and s.lastWrite==0 and s.refused))
  run oldSessionCannotPinTest = init.then(fire(Capture(1))).then(fire(Reload)).then(fire(Capture(1))).then(fire(Commit({owner:1,session:1,ready:true}))).then(check(s.lastWrite==0 and s.refused))
  run newerFadeRejectsOldGenerationTest = init.then(pinOne).then(pinOne).then(fire(Tick({owner:1,generation:1}))).then(check(s.lastWrite==0 and s.fade.get(1)==2))
  run closedAndReusedWindowRejectsOldFadeTest = init.then(pinOne).then(fire(Close(1))).then(fire(Reuse)).then(fire(Tick({owner:1,generation:1}))).then(check(s.lastWrite==0 and not(s.fade.keys().contains(3))))
  run reducedMotionRejectsOldFadeTest = init.then(pinOne).then(fire(Reduce)).then(fire(Tick({owner:1,generation:1}))).then(check(s.lastWrite==0 and s.fade==Map()))
  run reloadRejectsOldFadeTest = init.then(pinOne).then(fire(Reload)).then(fire(Tick({owner:1,generation:1}))).then(check(s.lastWrite==0 and s.fade==Map()))
  run minimizeRetiresFadeWithoutLosingPinIntentTest = init.then(pinOne).then(fire(Minimize(1))).then(fire(Tick({owner:1,generation:1}))).then(check(s.lastWrite==0 and s.saved.contains(1))).then(fire(Restore(1))).then(check(s.pinned==Set(1,2) and invariant))
  run unpinBeforeMinimizeStaysUnpinnedOnRestoreTest = init.then(pinOne).then(pinOne).then(fire(Minimize(1))).then(fire(Restore(1))).then(check(s.pinned==Set(2) and invariant))
}
