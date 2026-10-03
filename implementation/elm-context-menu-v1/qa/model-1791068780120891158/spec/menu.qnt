module menu {
  import menu_types.* from "./menu-types"
  export menu_types.*

  // Auxiliary ledger plus monitor evidence. Single target, at most one unresolved
  // operation globally; stricter than the production multi-target reducer.
  type Monitor = { unresolved: Set[int], nextOperation: int,
    event: str, beforeCount: int, dispatchEligible: bool,
    observations: int, beforeObservations: int, lastEnabled: Set[int], uncertain: bool, beforeTarget: Identity, beforeOutput: int, beforeCapabilities: int }
  var monitor: Monitor
  pure val identity0 = { authority: 1, frontend: 1, incarnation: 1 }
  pure val emptyMenu = { phase: Closed, menuId: 0, target: identity0,
    outputGeneration: 1, capabilityGeneration: 1, enabled: Set(),
    selected: -1, operationId: 0 }
  action init = all {
    state' = { menu: emptyMenu, liveTarget: identity0, liveOutput: 1,
      liveCapabilities: 1, intents: [] },
    monitor' = { unresolved: Set(), nextOperation: 1, event: "init",
      beforeCount: 0, dispatchEligible: false, observations: 0,
      beforeObservations: 0, lastEnabled: Set(), uncertain: false, beforeTarget: identity0, beforeOutput: 1, beforeCapabilities: 1 }
  }
  pure def eligible(s: State): bool = s.menu.target == s.liveTarget
    and s.menu.outputGeneration == s.liveOutput
    and s.menu.capabilityGeneration == s.liveCapabilities
  pure def openedMenu(s: State, rows: Set[int]): Menu = {
    phase: Open, menuId: s.menu.menuId + 1, target: s.liveTarget,
    outputGeneration: s.liveOutput, capabilityGeneration: s.liveCapabilities,
    enabled: rows, selected: if (rows.size() == 0) -1 else rows.fold(999, (acc, row) => if (row < acc) row else acc),
    operationId: 0 }
  pure def evidence(s: State, m: Monitor, event: str): Monitor = { ...m, event: event,
    beforeCount: s.intents.length(), beforeObservations: m.observations,
    dispatchEligible: false, lastEnabled: s.menu.enabled, beforeTarget: s.liveTarget, beforeOutput: s.liveOutput, beforeCapabilities: s.liveCapabilities }
  action openMenu(rows: Set[int]): bool = all {
    state.menu.phase == Closed,
    state' = { ...state, menu: { ...openedMenu(state, rows), phase: if (monitor.unresolved.size() == 0) Open else if (monitor.uncertain) Unknown else Pending } },
    monitor' = evidence(state, monitor, "open")
  }

  pure def firstRow(rows: Set[int]): int = if (rows.size() == 0) -1 else rows.fold(999, (acc, row) => if (row < acc) row else acc)
  pure def lastRow(rows: Set[int]): int = if (rows.size() == 0) -1 else rows.fold(-1, (acc, row) => if (row > acc) row else acc)
  pure def navigatedRow(m: Menu, direction: str): int =
    if (direction == "home") firstRow(m.enabled)
    else if (direction == "end") lastRow(m.enabled)
    else if (direction == "down") {
      val later = m.enabled.filter(row => row > m.selected)
      if (later.size() == 0) firstRow(m.enabled) else firstRow(later)
    } else {
      val earlier = m.enabled.filter(row => row < m.selected)
      if (earlier.size() == 0) lastRow(m.enabled) else lastRow(earlier)
    }
  pure def dispatchGuard(s: State, m: Monitor, id: int, target: Identity, row: int): bool =
    s.menu.phase != Closed and id == s.menu.menuId and target == s.menu.target
    and eligible(s) and s.menu.enabled.contains(row) and m.unresolved.size() == 0
  action navigate(direction: str): bool = all {
    state.menu.phase != Closed,
    state' = { ...state, menu: { ...state.menu, selected: navigatedRow(state.menu, direction) } },
    monitor' = evidence(state, monitor, "navigate")
  }
  action dismiss = all {
    state.menu.phase != Closed,
    state' = { ...state, menu: { ...state.menu, phase: Closed } },
    monitor' = evidence(state, monitor, "dismiss")
  }
  action activate(id: int, target: Identity, row: int): bool = all {
    dispatchGuard(state, monitor, id, target, row),
    state' = { ...state, menu: { ...state.menu, phase: Pending, operationId: monitor.nextOperation, selected: row },
      intents: state.intents.append({ operationId: monitor.nextOperation, target: target, actionId: row }) },
    monitor' = { ...evidence(state, monitor, "activate"), unresolved: Set(monitor.nextOperation),
      nextOperation: monitor.nextOperation + 1, dispatchEligible: true, uncertain: false }
  }
  action rejectedActivate(id: int, target: Identity, row: int): bool = all {
    not(dispatchGuard(state, monitor, id, target, row)),
    state' = state,
    monitor' = evidence(state, monitor, "rejected")
  }

  // Receipt acknowledges an operation; it never manufactures new native facts.
  action receipt(id: int, outcome: str): bool = all {
    monitor.unresolved.contains(id),
    state' = { ...state, menu: { ...state.menu, phase:
      if (state.menu.phase == Closed) Closed
      else if (outcome == "uncertain") Unknown
      else if (outcome == "refused") Refused
      else Closed } },
    monitor' = { ...evidence(state, monitor, "receipt"),
      unresolved: if (outcome == "uncertain") monitor.unresolved else Set(),
      uncertain: outcome == "uncertain" }
  }
  action staleReceipt(id: int): bool = all {
    not(monitor.unresolved.contains(id)),
    state' = state,
    monitor' = evidence(state, monitor, "stale-receipt")
  }
  // Fresh observation is a distinct environment transition, including when a
  // receipt is lost. It cannot clear an unresolved operation or justify retry.
  action freshObserve(kind: str): bool = all {
    state' = if (kind == "capabilities") { ...state, liveCapabilities: state.liveCapabilities + 1 }
      else { ...state, liveTarget: { ...state.liveTarget, frontend: state.liveTarget.frontend + 1 } },
    monitor' = { ...evidence(state, monitor, "observe"), observations: monitor.observations + 1 }
  }
  action retireOutput = all {
    state' = { ...state, liveOutput: state.liveOutput + 1, menu: { ...state.menu, phase: Closed } },
    monitor' = evidence(state, monitor, "retire")
  }
  val opened = monitor.event == "open"
  val navigated = monitor.event == "navigate"
  val activated = monitor.event == "activate"
  val dismissed = monitor.event == "dismiss"
  val nonmutating = if (monitor.event != "activate") state.intents.length() == monitor.beforeCount else true
  val authorizedDispatch = if (monitor.event == "activate") monitor.dispatchEligible and state.intents.length() == monitor.beforeCount + 1 else true
  val selectedEnabled = state.menu.selected == -1 or state.menu.enabled.contains(state.menu.selected)
  val received = monitor.event == "receipt"
  val observed = monitor.event == "observe"
  val retired = monitor.event == "retire"
  val staleReceived = monitor.event == "stale-receipt"
  val exactDispatch = if (activated) {
    val intent = state.intents.nth(state.intents.length() - 1)
    intent.target == state.liveTarget and state.menu.target == state.liveTarget
      and state.menu.outputGeneration == state.liveOutput
      and state.menu.capabilityGeneration == state.liveCapabilities
      and monitor.lastEnabled.contains(intent.actionId)
      and intent.operationId == state.menu.operationId
  } else true
  val receiptsDoNotObserve = if (received) state.liveTarget == monitor.beforeTarget
    and state.liveOutput == monitor.beforeOutput and state.liveCapabilities == monitor.beforeCapabilities
    and monitor.observations == monitor.beforeObservations else true
  val uniqueIntents = state.intents.foldl(Set(), (seen, intent) => seen.union(Set(intent.operationId))).size() == state.intents.length()
  val unknownLedger = if (monitor.uncertain) monitor.unresolved.size() == 1 else true
  val safety = nonmutating and authorizedDispatch and selectedEnabled and exactDispatch
    and receiptsDoNotObserve and uniqueIntents and unknownLedger and monitor.unresolved.size() <= 1
  action step = any {
    openMenu(Set(0, 2)), openMenu(Set()), navigate("down"), navigate("up"),
    navigate("home"), navigate("end"), dismiss,
    activate(state.menu.menuId, state.menu.target, 0), activate(state.menu.menuId, state.menu.target, 2),
    rejectedActivate(state.menu.menuId, state.menu.target, 1), rejectedActivate(state.menu.menuId, state.menu.target, 0),
    receipt(monitor.nextOperation - 1, "committed"), receipt(monitor.nextOperation - 1, "refused"),
    receipt(monitor.nextOperation - 1, "uncertain"),
    staleReceipt(monitor.nextOperation + 99), freshObserve("capabilities"), freshObserve("frontend"), retireOutput
  }
}
