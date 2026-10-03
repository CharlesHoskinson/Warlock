// Type sketch only: no actions or transition logic before explicit review.
module menu_sketch {
  type Identity = { authority: int, frontend: int, incarnation: int }
  type Phase = Closed | Open | Pending | Refused | Unknown
  type Menu = {
    phase: Phase,
    menuId: int,
    target: Identity,
    outputGeneration: int,
    capabilityGeneration: int,
    enabled: Set[int],
    selected: int,
    operationId: int
  }
  type Intent = { operationId: int, target: Identity, action: int }
  type State = {
    menu: Menu,
    liveTarget: Identity,
    liveOutput: int,
    liveCapabilities: int,
    intents: List[Intent]
  }
  var state: State
}
