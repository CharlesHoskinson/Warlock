module menu {
  import menu_types.* from "./menu-types"
  export menu_types.*

  // Single atomic controller; external events carry already validated bindings.
  // Abstract budgets are two operations and three combined tombstones. Three
  // target identities permit a genuinely independent capacity-refused command.
  pure val ledgerLimit = 2
  pure val retirementLimit = 3
  pure val targetA = { lifetime: 1, session: 1, incarnation: 1 }
  pure val targetB = { lifetime: 1, session: 1, incarnation: 2 }
  pure val targetC = { lifetime: 1, session: 1, incarnation: 3 }
  pure val bindingA = { target: targetA, frontend: 1, revision: 1,
    output: 1, outputGeneration: 1, provider: 1, capabilities: 1 }
  pure val reboundA = { ...bindingA, frontend: 2, revision: 2, capabilities: 2 }
  pure val bindingB = { ...bindingA, target: targetB }
  pure val bindingC = { ...bindingA, target: targetC }
  pure val initialState: State = { view: Closed, operations: [],
    invalidated: Set(), retiredOutputs: Set(), exhausted: false,
    nextMenu: 1, nextOperation: 1 }
  type Emission = { id: int, menuId: int, binding: Binding, actionId: int }
  type Monitor = { event: str, before: State, intents: List[Emission],
    beforeCount: int, receiptId: int, receiptBinding: Binding,
    receiptOutcome: Outcome }
  var monitor: Monitor

  pure def evidence(s: State, m: Monitor, event: str): Monitor = {
    ...m, event: event, before: s, beforeCount: m.intents.length() }
  pure def retiredCount(s: State): int = s.invalidated.size() + s.retiredOutputs.size()
  pure def outputTuple(b: Binding): RetiredOutput = { output: b.output, generation: b.outputGeneration }
  pure def validBinding(s: State, b: Binding): bool = not(s.exhausted)
    and not(s.invalidated.contains(b)) and not(s.retiredOutputs.contains(outputTuple(b)))
  pure def firstRow(rows: Set[int]): int = if (rows.size() == 0) -1
    else rows.fold(3, (acc, row) => if (row < acc) row else acc)
  pure def canOpen(s: State, b: Binding, rows: Set[int]): bool = validBinding(s, b)
    and rows.forall(row => row >= 0 and row <= 2)
  pure def applyOpen(s: State, b: Binding, rows: Set[int]): State = { ...s,
    view: Visible({ id: s.nextMenu, binding: b, enabled: rows, selected: firstRow(rows) }),
    nextMenu: s.nextMenu + 1 }

  action init = all {
    state' = initialState,
    monitor' = { event: "init", before: initialState, intents: [],
      beforeCount: 0, receiptId: 0, receiptBinding: bindingA, receiptOutcome: Pending }
  }
  action openMenu(b: Binding, rows: Set[int]): bool = all {
    canOpen(state, b, rows), state' = applyOpen(state, b, rows),
    monitor' = evidence(state, monitor, "open")
  }
  val opened = monitor.event == "open"
  val nonmutating = monitor.event != "activate" implies monitor.intents.length() == monitor.beforeCount
  val safety = nonmutating and state.operations.length() <= ledgerLimit
    and retiredCount(state) <= retirementLimit
  action step = any { openMenu(bindingA, Set(0, 2)), openMenu(bindingB, Set()) }
}
