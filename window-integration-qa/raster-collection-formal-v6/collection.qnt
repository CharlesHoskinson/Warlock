module collection {
  var observed: Set[int]
  var bad: Set[int]
  var fatal: bool
  var finished: bool
  var accepted: bool

  action init = all {
    observed' = Set(), bad' = Set(), fatal' = false,
    finished' = false, accepted' = false
  }
  action observe(slot: int, bindingValid: bool, pixelsValid: bool): bool = all {
    not(finished), not(fatal),
    if (slot < 0 or slot >= 8 or observed.contains(slot) or not(bindingValid)) all {
      observed' = observed, bad' = bad, fatal' = true,
      finished' = false, accepted' = false
    } else all {
      observed' = observed.union(Set(slot)),
      bad' = if (pixelsValid) bad else bad.union(Set(slot)),
      fatal' = false, finished' = false, accepted' = false
    }
  }
  action finish = all {
    observed' = observed, bad' = bad, fatal' = fatal, finished' = true,
    accepted' = (not(fatal) and bad == Set() and observed == 0.to(7))
  }
  action idle = all {
    observed' = observed, bad' = bad, fatal' = fatal,
    finished' = finished, accepted' = accepted
  }
  val invariant = all {
    bad.subseteq(observed), observed.subseteq(0.to(7)),
    accepted implies all { finished, not(fatal), bad == Set(), observed == 0.to(7) },
    (fatal or bad != Set()) implies not(accepted)
  }
  action step = {
    nondet slot = (-1).to(8).oneOf()
    nondet binding = Set(true, false).oneOf()
    nondet pixels = Set(true, false).oneOf()
    any { observe(slot, binding, pixels), finish, idle }
  }
}
