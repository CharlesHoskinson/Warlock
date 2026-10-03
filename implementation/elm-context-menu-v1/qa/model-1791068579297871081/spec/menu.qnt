module menu {
  import menu_types.* from "./menu-types"

  // Auxiliary ledger plus monitor evidence. Single target, at most one unresolved
  // operation globally; stricter than the production multi-target reducer.
  type Monitor = { unresolved: Set[int], nextOperation: int,
    event: str, beforeCount: int, dispatchEligible: bool,
    observations: int, beforeObservations: int, lastEnabled: Set[int], uncertain: bool }
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
      beforeObservations: 0, lastEnabled: Set(), uncertain: false }
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
    dispatchEligible: false, lastEnabled: s.menu.enabled }
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
  val opened = monitor.event == "open"
  val navigated = monitor.event == "navigate"
  val activated = monitor.event == "activate"
  val dismissed = monitor.event == "dismiss"
  val nonmutating = if (monitor.event != "activate") state.intents.length() == monitor.beforeCount else true
  val authorizedDispatch = if (monitor.event == "activate") monitor.dispatchEligible and state.intents.length() == monitor.beforeCount + 1 else true
  val selectedEnabled = state.menu.selected == -1 or state.menu.enabled.contains(state.menu.selected)
  val safety = nonmutating and authorizedDispatch and selectedEnabled and monitor.unresolved.size() <= 1
  action step = any {
    openMenu(Set(0, 2)), openMenu(Set()), navigate("down"), navigate("up"),
    navigate("home"), navigate("end"), dismiss,
    activate(state.menu.menuId, state.menu.target, 0), activate(state.menu.menuId, state.menu.target, 2),
    rejectedActivate(state.menu.menuId, state.menu.target, 1), rejectedActivate(state.menu.menuId, state.menu.target, 0)
  }
}
