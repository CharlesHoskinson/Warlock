// Proposed types only. Transition logic requires explicit sketch approval.
module menu_sketch {
  type Target = { lifetime: int, session: int, incarnation: int }
  type Binding = {
    target: Target, frontend: int, revision: int,
    output: int, outputGeneration: int, provider: int, capabilities: int
  }
  type Outcome = Pending | Unknown | Committed | Refused | Cancelled
  type Operation = { id: int, binding: Binding, outcome: Outcome }
  type View = Closed | Visible({ id: int, binding: Binding, enabled: Set[int], selected: int })
  type RetiredOutput = { output: int, generation: int }
  type State = {
    view: View,
    operations: List[Operation],
    invalidated: Set[Binding],
    retiredOutputs: Set[RetiredOutput],
    exhausted: bool,
    nextMenu: int,
    nextOperation: int
  }
  var state: State
}
