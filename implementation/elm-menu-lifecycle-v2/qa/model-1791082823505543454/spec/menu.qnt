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
  pure def applyActivate(s: State, b: Binding, row: int): State = { ...s,
    operations: s.operations.append({ id: s.nextOperation, binding: b, outcome: Pending }),
    nextOperation: s.nextOperation + 1,
    view: match s.view { | Closed => Closed | Visible(view) => Visible({ ...view, selected: row }) } }
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
  pure def canInvalidate(s: State, b: Binding): bool = not(s.exhausted)
    and not(s.invalidated.contains(b)) and retiredCount(s) < retirementLimit
  pure def applyInvalidate(s: State, b: Binding): State = { ...s,
    invalidated: s.invalidated.union(Set(b)),
    view: match s.view {
      | Closed => Closed
      | Visible(view) => if (view.binding == b) Closed else s.view
    }
  }
  pure def canExhaust(s: State, b: Binding): bool = not(s.exhausted)
    and not(s.invalidated.contains(b)) and retiredCount(s) == retirementLimit
  pure def applyExhaust(s: State): State = { ...s, exhausted: true, view: Closed }
  pure def currentBinding(s: State): Binding = match s.view {
    | Closed => bindingA
    | Visible(view) => view.binding
  }
  pure def hasView(s: State): bool = match s.view { | Closed => false | Visible(_) => true }
  pure def lastRow(rows: Set[int]): int = rows.fold(-1, (acc, row) => if (row > acc) row else acc)
  pure def applyNavigation(s: State, direction: str): State = { ...s, view: match s.view {
    | Closed => Closed
    | Visible(view) => {
      val later = view.enabled.filter(row => row > view.selected)
      val earlier = view.enabled.filter(row => row < view.selected)
      val selected = if (direction == "home") firstRow(view.enabled)
        else if (direction == "end") lastRow(view.enabled)
        else if (direction == "down") { if (later.size() == 0) firstRow(view.enabled) else firstRow(later) }
        else { if (earlier.size() == 0) lastRow(view.enabled) else lastRow(earlier) }
      Visible({ ...view, selected: selected })
    }
  } }
  pure def canRetireOutput(s: State, output: RetiredOutput): bool = not(s.exhausted)
    and not(s.retiredOutputs.contains(output)) and retiredCount(s) < retirementLimit
  pure def applyRetireOutput(s: State, output: RetiredOutput): State = { ...s,
    retiredOutputs: s.retiredOutputs.union(Set(output)),
    view: match s.view { | Closed => Closed
      | Visible(view) => if (outputTuple(view.binding) == output) Closed else s.view }
  }

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
    canActivate(state, id, b, row), state' = applyActivate(state, b, row),
    monitor' = { ...evidence(state, monitor, "activate"),
      intents: monitor.intents.append({ id: state.nextOperation, menuId: id, binding: b, actionId: row }) }
  }
  action receipt(id: int, b: Binding, outcome: Outcome): bool = all {
    canReceipt(state, id, b, outcome), state' = applyReceipt(state, id, b, outcome),
    monitor' = { ...evidence(state, monitor, "receipt"),
      receiptId: id, receiptBinding: b, receiptOutcome: outcome }
  }
  action invalidate(b: Binding): bool = all {
    canInvalidate(state, b), state' = applyInvalidate(state, b),
    monitor' = evidence(state, monitor, "retire")
  }
  action duplicateRetirement(b: Binding): bool = all {
    state.invalidated.contains(b), state' = state,
    monitor' = evidence(state, monitor, "retire-duplicate")
  }
  action exhaust(b: Binding): bool = all {
    canExhaust(state, b), state' = applyExhaust(state),
    monitor' = evidence(state, monitor, "exhaust")
  }
  action rejectedOpen(b: Binding, rows: Set[int]): bool = all {
    not(canOpen(state, b, rows)), state' = state,
    monitor' = evidence(state, monitor, "open-rejected")
  }
  action rejectedActivate(id: int, b: Binding, row: int): bool = all {
    not(canActivateWithoutCapacity(state, id, b, row)), state' = state,
    monitor' = evidence(state, monitor, "activation-rejected")
  }
  action capacityRefusal(id: int, b: Binding, row: int): bool = all {
    canActivateWithoutCapacity(state, id, b, row), state.operations.length() == ledgerLimit,
    state' = state, monitor' = evidence(state, monitor, "capacity-refused")
  }
  action rejectReceipt(id: int, b: Binding, outcome: Outcome): bool = all {
    not(canReceipt(state, id, b, outcome)), state' = state,
    monitor' = evidence(state, monitor, "receipt-rejected")
  }
  action dismiss = all {
    hasView(state), state' = { ...state, view: Closed },
    monitor' = evidence(state, monitor, "dismiss")
  }
  action navigate(direction: str): bool = all {
    hasView(state), Set("up", "down", "home", "end").contains(direction),
    state' = applyNavigation(state, direction), monitor' = evidence(state, monitor, "navigate")
  }
  action retireOutput(output: RetiredOutput): bool = all {
    canRetireOutput(state, output), state' = applyRetireOutput(state, output),
    monitor' = evidence(state, monitor, "retire")
  }
  action duplicateOutput(output: RetiredOutput): bool = all {
    state.retiredOutputs.contains(output), state' = state,
    monitor' = evidence(state, monitor, "retire-duplicate")
  }
  action exhaustOutput(output: RetiredOutput): bool = all {
    not(state.exhausted), not(state.retiredOutputs.contains(output)), retiredCount(state) == retirementLimit,
    state' = applyExhaust(state), monitor' = evidence(state, monitor, "exhaust")
  }
  val opened = monitor.event == "open"
  val activated = monitor.event == "activate"
  val received = monitor.event == "receipt"
  val rejectedReceipt = monitor.event == "receipt-rejected"
  val rejectedActivation = monitor.event == "activation-rejected"
  val dismissed = monitor.event == "dismiss"
  val navigated = monitor.event == "navigate"
  val capacityReached = activated and state.operations.length() == ledgerLimit
  val capacityRefused = monitor.event == "capacity-refused"
  val capacityFreed = received and monitor.before.operations.length() == ledgerLimit
    and state.operations.length() == ledgerLimit - 1
  val exhaustedReceipt = received and monitor.before.exhausted
    and state.operations.length() < monitor.before.operations.length()
  val unknownRebound = opened and state.operations.foldl(false, (found, op) => found or (
    op.outcome == Unknown and op.binding.target == currentBinding(state).target
    and op.binding != currentBinding(state)))
  val retired = monitor.event == "retire"
  val duplicateRetired = monitor.event == "retire-duplicate"
  val exhaustedReached = monitor.event == "exhaust" and state.exhausted
  val nonmutating = monitor.event != "activate" implies monitor.intents.length() == monitor.beforeCount
  val exactDispatch = if (activated) {
    val emitted = monitor.intents.nth(monitor.intents.length() - 1)
    (match monitor.before.view {
      | Closed => false
      | Visible(view) => view.id == emitted.menuId and view.binding == emitted.binding
        and view.enabled.contains(emitted.actionId)
    })
      and not(monitor.before.exhausted)
      and monitor.before.operations.length() < ledgerLimit
      and monitor.before.operations.foldl(true, (free, op) => free and op.binding.target != emitted.binding.target)
      and not(monitor.before.invalidated.contains(emitted.binding))
      and not(monitor.before.retiredOutputs.contains({ output: emitted.binding.output, generation: emitted.binding.outputGeneration }))
      and emitted.id == monitor.before.nextOperation and state.nextOperation == emitted.id + 1
      and monitor.intents.length() == monitor.beforeCount + 1
      and state.operations == monitor.before.operations.append({ id: emitted.id, binding: emitted.binding, outcome: Pending })
  } else true
  val exactReceipt = if (received) {
    val original = monitor.before.operations.foldl(false, (matched, op) => matched or (
      op.id == monitor.receiptId and op.binding == monitor.receiptBinding
        and Set(Pending, Unknown).contains(op.outcome)))
    val unrelatedBefore = monitor.before.operations.select(op => op.id != monitor.receiptId)
    val unrelatedAfter = state.operations.select(op => op.id != monitor.receiptId)
    val resolved = if (monitor.receiptOutcome == Unknown)
      state.operations.foldl(false, (matched, op) => matched or (
        op.id == monitor.receiptId and op.binding == monitor.receiptBinding and op.outcome == Unknown))
      else state.operations.foldl(true, (removed, op) => removed and op.id != monitor.receiptId)
    original and monitor.receiptOutcome != Pending and unrelatedBefore == unrelatedAfter and resolved
      and state.nextOperation == monitor.before.nextOperation
      and monitor.intents.length() == monitor.beforeCount
  } else true
  val ledgerConservation = if (not(activated) and not(received)) state.operations == monitor.before.operations else true
  val uniqueIntents = monitor.intents.foldl(Set(), (ids, emission) => ids.union(Set(emission.id))).size() == monitor.intents.length()
  val stableSingleFlight = state.operations.foldl(Set(), (targets, op) => targets.union(Set(op.binding.target))).size() == state.operations.length()
  val retirementMonotonic = monitor.before.invalidated.forall(b => state.invalidated.contains(b))
    and monitor.before.retiredOutputs.forall(output => state.retiredOutputs.contains(output))
    and (monitor.before.exhausted implies state.exhausted)
  val selectedEnabled = match state.view { | Closed => true
    | Visible(view) => view.selected == -1 or view.enabled.contains(view.selected) }
  val safety = nonmutating and state.operations.length() <= ledgerLimit
    and retiredCount(state) <= retirementLimit and exactDispatch and exactReceipt
    and ledgerConservation and uniqueIntents and stableSingleFlight and retirementMonotonic and selectedEnabled
    and state.operations.foldl(true, (unresolved, op) => unresolved and Set(Pending, Unknown).contains(op.outcome))
  action step = any {
    openMenu(bindingA, Set(0, 2)), openMenu(bindingB, Set(0, 2)),
    openMenu(bindingC, Set(0, 2)), openMenu(reboundA, Set(0, 2)), openMenu(bindingA, Set()),
    rejectedOpen(bindingA, Set(9)),
    activate(visibleId(state), currentBinding(state), 0),
    rejectedActivate(visibleId(state), currentBinding(state), 0),
    rejectedActivate(visibleId(state), currentBinding(state), 1),
    capacityRefusal(visibleId(state), currentBinding(state), 0),
    receipt(oldest(state).id, oldest(state).binding, Committed),
    receipt(oldest(state).id, oldest(state).binding, Unknown),
    receipt(oldest(state).id, oldest(state).binding, Refused),
    receipt(oldest(state).id, oldest(state).binding, Cancelled),
    receipt(oldest(state).id, { ...oldest(state).binding, frontend: 99 }, Committed),
    rejectReceipt(oldest(state).id, { ...oldest(state).binding, frontend: 99 }, Committed),
    dismiss, navigate("down"), navigate("up"), navigate("home"), navigate("end"),
    invalidate(bindingA), invalidate(bindingB), invalidate(bindingC), invalidate(reboundA),
    duplicateRetirement(bindingA), duplicateRetirement(bindingB),
    exhaust(bindingA), exhaust(bindingB), exhaust(bindingC), exhaust(reboundA),
    retireOutput({ output: 1, generation: 1 }), duplicateOutput({ output: 1, generation: 1 }),
    exhaustOutput({ output: 1, generation: 1 })
  }
  // A separate input profile reaches capacity before rare retirement events
  // exhaust the controller. It uses exactly the same normative actions/guards.
  action capacityStep = any {
    openMenu(bindingA, Set(0, 2)), openMenu(bindingB, Set(0, 2)),
    openMenu(bindingC, Set(0, 2)), openMenu(reboundA, Set(0, 2)),
    activate(visibleId(state), currentBinding(state), 0),
    rejectedActivate(visibleId(state), currentBinding(state), 0),
    capacityRefusal(visibleId(state), currentBinding(state), 0),
    receipt(oldest(state).id, oldest(state).binding, Unknown),
    receipt(oldest(state).id, oldest(state).binding, Refused),
    receipt(oldest(state).id, oldest(state).binding, Committed),
    dismiss
  }
}
