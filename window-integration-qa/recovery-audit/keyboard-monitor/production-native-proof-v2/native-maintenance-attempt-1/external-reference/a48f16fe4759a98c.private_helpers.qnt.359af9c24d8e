module private_helpers {
  var baseline: Set[int]
  var current: Set[int]
  var portalActivated: bool
  var gated: bool
  var accepted: bool
  action init = all {baseline'=Set(1,2,3),current'=Set(1,2,3),portalActivated'=false,gated'=false,accepted'=false}
  action observe(ids: Set[int],portal:bool): bool = all {baseline'=baseline,current'=ids,portalActivated'=portal,gated'=true,accepted'=(ids.subseteq(baseline) and not(portal))}
  action step = {nondet ids=Set(Set(),Set(1),Set(1,2,3),Set(1,2,3,4),Set(4),Set(1,4)).oneOf();nondet portal=Set(true,false).oneOf();observe(ids,portal)}
  val safe = accepted implies (gated and not(portalActivated) and current.subseteq(baseline))
  val rejectExtra = (gated and (portalActivated or not(current.subseteq(baseline)))) implies not(accepted)
  val invariants = safe and rejectExtra
}
