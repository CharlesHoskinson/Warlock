module release_inventory {
  type Pair = (int, int)
  type State = { payload: Set[int], owners: Set[Pair], edges: Set[Pair], shipped: Set[int], scanError: bool, decision: int, snapPayload: Set[int], snapOwners: Set[Pair], snapEdges: Set[Pair], snapShipped: Set[int], snapError: bool, changed: bool, events: Set[int] }
  pure val files = Set(1, 2)
  pure val components = Set(1, 2, 3)
  pure def exact(p: Set[int], o: Set[Pair]): bool = files.forall(f => if (p.contains(f)) o.filter(x => x._1 == f).size() == 1 else o.filter(x => x._1 == f).size() == 0)
  pure def roots(o: Set[Pair], s: Set[int]): Set[int] = s.filter(c => o.exists(x => x._2 == c))
  pure def expand(r: Set[int], e: Set[Pair]): Set[int] = r.union(components.filter(c => e.exists(x => r.contains(x._1) and x._2 == c)))
  pure def reachable(o: Set[Pair], e: Set[Pair], s: Set[int]): bool = {
    val r = roots(o, s)
    val r1 = expand(r, e)
    val r2 = expand(r1, e)
    s.subseteq(r2)
  }
  var st: State
  action init = st' = { payload: Set(1), owners: Set((1, 1)), edges: Set(), shipped: Set(1), scanError: false, decision: 0, snapPayload: Set(), snapOwners: Set(), snapEdges: Set(), snapShipped: Set(), snapError: false, changed: false, events: Set() }

  action addPayload(f: int): bool = st' = {...st, payload: st.payload.union(Set(f)), changed: true, events: st.events.union(Set(1))}
  action removePayload(f: int): bool = st' = {...st, payload: st.payload.exclude(Set(f)), changed: true, events: st.events.union(Set(2))}
  action addOwner(f: int, c: int): bool = st' = {...st, owners: st.owners.union(Set((f,c))), shipped: st.shipped.union(Set(c)), changed: true, events: st.events.union(Set(3))}
  action removeOwner(f: int, c: int): bool = st' = {...st, owners: st.owners.exclude(Set((f,c))), changed: true, events: st.events.union(Set(4))}
  action addEdge(a: int, b: int): bool = st' = {...st, edges: st.edges.union(Set((a,b))), shipped: st.shipped.union(Set(a,b)), changed: true, events: st.events.union(Set(5))}
  action removeEdge(a: int, b: int): bool = st' = {...st, edges: st.edges.exclude(Set((a,b))), changed: true, events: st.events.union(Set(6))}
  action setScanError(b: bool): bool = st' = {...st, scanError: b, changed: true, events: st.events.union(Set(if (b) 7 else 8))}
  action review = st' = {...st, decision: if (not(st.scanError) and exact(st.payload, st.owners) and reachable(st.owners, st.edges, st.shipped)) 1 else 2, snapPayload: st.payload, snapOwners: st.owners, snapEdges: st.edges, snapShipped: st.shipped, snapError: st.scanError, changed: false, events: st.events.union(Set(9))}
  action step = {
    nondet f = files.oneOf()
    nondet a = components.oneOf()
    nondet b = components.oneOf()
    any { addPayload(f), removePayload(f), addOwner(f,a), removeOwner(f,a), addEdge(a,b), removeEdge(a,b), setScanError(true), setScanError(false), review }
  }
  val acceptedSnapshotCovered = st.decision == 1 implies and {
    st.snapPayload.forall(f => st.snapOwners.filter(pair => pair._1 == f).size() == 1),
    st.snapOwners.forall(pair => st.snapPayload.contains(pair._1)),
  }
  val acceptedSnapshotReachable = st.decision == 1 implies st.snapShipped.forall(c => st.snapShipped.exists(root =>
    st.snapOwners.exists(pair => pair._2 == root) and
    (root == c or st.snapEdges.contains((root, c)) or
      components.exists(mid => st.snapEdges.contains((root, mid)) and st.snapEdges.contains((mid, c))))))
  val acceptedSnapshotComplete = st.decision == 1 implies not(st.snapError)
  val wAccepted = st.decision == 1
  val wRefused = st.decision == 2
  val wMutationAfterReview = st.decision == 1 and st.changed
  val wAdd = st.events.contains(1)
  val wRemove = st.events.contains(2)
  val wOwnerAdd = st.events.contains(3)
  val wOwnerRemove = st.events.contains(4)
  val wEdgeAdd = st.events.contains(5)
  val wEdgeRemove = st.events.contains(6)
  val wScanError = st.events.contains(7)
  val wScanRestore = st.events.contains(8) and st.events.contains(7)
}
