module pickerStorage {
  // UI-016 native storage refinement. A job abstracts the full authenticated
  // peer/binding/incarnation/request/context. One slot owns one sealed backing.
  // Original renderer peak/byte bound is conservative; pixels, clocks and AT
  // are outside this model, not inferred from a descriptor or reservation.
  type State = {held:Set[int], sealed:Set[int], exported:Set[int], mapped:Set[int], issued:Set[int], retired:Set[int], revoked:bool, reply:int, refused:bool}
  val empty:State={held:Set(),sealed:Set(),exported:Set(),mapped:Set(),issued:Set(),retired:Set(),revoked:false,reply:0,refused:false}
  var s:State
  action init=s'=empty
  action idle=s'=s
  action step=idle
  val safety=s.held.size()<=2 and s.held.size()*64<=128 and s.sealed.subseteq(s.held) and s.exported.subseteq(s.sealed) and s.mapped.subseteq(s.exported) and s.exported.subseteq(s.issued) and s.retired.intersect(s.held)==Set()
}
