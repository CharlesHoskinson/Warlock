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
  pure def visibleId(s: State): int = match s.view {
    | Closed => 0
    | Visible(view) => view.id
  }
  pure def sameTargetBusy(s: State, b: Binding): bool = s.operations.foldl(false, (busy, op) => busy or op.binding.target == b.target)
  pure def canSelect(s: State, id: int, b: Binding, row: int): bool = match s.view {
    | Closed => false
    | Visible(view) => view.id == id and view.binding == b and validBinding(s, b) and view.enabled.contains(row)
  }
  pure def canActivateWithoutCapacity(s: State, id: int, b: Binding, row: int): bool =
    canSelect(s, id, b, row) and not(sameTargetBusy(s, b))
  pure def canActivate(s: State, id: int, b: Binding, row: int): bool =
    canActivateWithoutCapacity(s, id, b, row) and s.operations.length() < ledgerLimit
  pure def applyActivate(s: State, b: Binding): State = { ...s,
    operations: s.operations.append({ id: s.nextOperation, binding: b, outcome: Pending }),
    nextOperation: s.nextOperation + 1 }
  pure def receiptMatches(s: State, id: int, b: Binding): bool =
    s.operations.foldl(false, (found, op) => found or (op.id == id and op.binding == b))
  pure def canReceipt(s: State, id: int, b: Binding, outcome: Outcome): bool =
    receiptMatches(s, id, b) and outcome != Pending
  pure def applyReceipt(s: State, id: int, b: Binding, outcome: Outcome): State = {
    ...s,
    operations: if (outcome == Unknown)
      s.operations.foldl([], (ledger, op) => ledger.append(if (op.id == id) { ...op, outcome: Unknown } else op))
      else s.operations.select(op => op.id != id),
    view: match s.view {
      | Closed => Closed
      | Visible(view) => if (outcome == Committed and view.binding.target == b.target) Closed else s.view
    }
  }
  pure def oldest(s: State): Operation = if (s.operations.length() == 0)
    { id: 0, binding: bindingA, outcome: Pending } else s.operations.head()

  action init = all {
    state' = initialState,
    monitor' = { event: "init", before: initialState, intents: [],
      beforeCount: 0, receiptId: 0, receiptBinding: bindingA, receiptOutcome: Pending }
  }
  action openMenu(b: Binding, rows: Set[int]): bool = all {
    canOpen(state, b, rows), state' = applyOpen(state, b, rows),
    monitor' = evidence(state, monitor, "open")
  }
  action activate(id: int, b: Binding, row: int): bool = all {
    canActivate(state, id, b, row), state' = applyActivate(state, b),
    monitor' = { ...evidence(state, monitor, "activate"),
      intents: monitor.intents.append({ id: state.nextOperation, menuId: id, binding: b, actionId: row }) }
  }
  action receipt(id: int, b: Binding, outcome: Outcome): bool = all {
    canReceipt(state, id, b, outcome), state' = applyReceipt(state, id, b, outcome),
    monitor' = { ...evidence(state, monitor, "receipt"),
      receiptId: id, receiptBinding: b, receiptOutcome: outcome }
  }
  val opened = monitor.event == "open"
  val activated = monitor.event == "activate"
  val received = monitor.event == "receipt"
  val nonmutating = monitor.event != "activate" implies monitor.intents.length() == monitor.beforeCount
  val exactDispatch = if (activated) {
    val emitted = monitor.intents.nth(monitor.intents.length() - 1)
    canActivate(monitor.before, emitted.menuId, emitted.binding, emitted.actionId)
      and emitted.id == monitor.before.nextOperation
      and monitor.intents.length() == monitor.beforeCount + 1
  } else true
  val safety = nonmutating and state.operations.length() <= ledgerLimit
    and retiredCount(state) <= retirementLimit and exactDispatch
  action step = any { openMenu(bindingA, Set(0, 2)), openMenu(bindingB, Set(0, 2)),
    activate(visibleId(state), bindingA, 0), activate(visibleId(state), bindingB, 0),
    receipt(oldest(state).id, oldest(state).binding, Committed),
    receipt(oldest(state).id, oldest(state).binding, Unknown) }
}
