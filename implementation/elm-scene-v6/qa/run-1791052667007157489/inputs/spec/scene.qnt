module scene {
  type Scene = { minimized: Set[int], inactive: Set[int], locked: bool, order: List[int], focus: int }
  var s: Scene
  pure val IDS = Set(1,2,3)
  pure def eligible(st: Scene, id: int): bool =
    not(st.locked) and not(st.minimized.contains(id)) and not(st.inactive.contains(id))
      and (id != 2 or (not(st.minimized.contains(1)) and not(st.inactive.contains(1))))
  pure def members(order: List[int]): Set[int] = order.foldl(Set(), (acc,id) => acc.union(Set(id)))
  pure def valid(st: Scene): bool = {
    val expected = IDS.filter(id => eligible(st,id))
    val familyOrdered = not(expected.contains(2)) or st.order.indices().exists(i =>
      st.order[i] == 1 and st.order.indices().exists(j => st.order[j] == 2 and i < j))
    members(st.order) == expected and st.order.length() == expected.size() and familyOrdered
      and (st.focus == 0 or (expected.contains(st.focus) and not(st.focus == 1 and expected.contains(2))))
  }
  action init = s' = {minimized:Set(),inactive:Set(),locked:false,order:List(1,2,3),focus:2}
  action admit(candidate: Scene): bool = s' = if (valid(candidate)) candidate else s
  action step = {
    nondet minimized = IDS.powerset().oneOf()
    nondet inactive = IDS.powerset().oneOf()
    nondet locked = Set(false,true).oneOf()
    nondet order = Set(List(),List(1),List(2),List(3),List(1,2),List(1,3),List(2,3),List(1,2,3),List(2,1,3),List(1,2,2,3)).oneOf()
    nondet focus = Set(0,1,2,3).oneOf()
    admit({minimized:minimized,inactive:inactive,locked:locked,order:order,focus:focus})
  }
  val safety = valid(s)
  run minimizedOwnerRefusedTest = init.then(admit({...s,minimized:Set(1),order:List(2,3),focus:2})).then(all {assert(s.order == List(1,2,3)),s'=s})
  run minimizedFamilyAcceptedTest = init.then(admit({...s,minimized:Set(1),order:List(3),focus:3})).then(all {assert(s.order == List(3)),s'=s})
  run modalParentRefusedTest = init.then(admit({...s,focus:1})).then(all {assert(s.focus == 2),s'=s})
  run childBeforeOwnerRefusedTest = init.then(admit({...s,order:List(2,1,3)})).then(all {assert(s.order == List(1,2,3)),s'=s})
  run lockAcceptedTest = init.then(admit({...s,locked:true,order:List(),focus:0})).then(all {assert(s.locked and s.order == List()),s'=s})
  run duplicateRefusedTest = init.then(admit({...s,order:List(1,2,2,3)})).then(all {assert(s.order == List(1,2,3)),s'=s})
}
