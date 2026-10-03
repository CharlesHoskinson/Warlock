module menu {
  import menu_types.* from "./menu-types"

  // Auxiliary ledger plus monitor evidence. Single target, at most one unresolved
  // operation globally; stricter than the production multi-target reducer.
  type Monitor = { unresolved: Set[int], nextOperation: int,
    event: str, beforeCount: int, dispatchEligible: bool,
    observations: int, beforeObservations: int, lastEnabled: Set[int] }
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
      beforeObservations: 0, lastEnabled: Set() }
  }
  pure def eligible(s: State): bool = s.menu.target == s.liveTarget
    and s.menu.outputGeneration == s.liveOutput
    and s.menu.capabilityGeneration == s.liveCapabilities
  pure def openedMenu(s: State, enabled: Set[int]): Menu = {
    phase: Open, menuId: s.menu.menuId + 1, target: s.liveTarget,
    outputGeneration: s.liveOutput, capabilityGeneration: s.liveCapabilities,
    enabled: enabled, selected: if (enabled.isEmpty()) -1 else enabled.min(),
    operationId: 0 }
  pure def evidence(event: str): Monitor = { ...monitor, event: event,
    beforeCount: state.intents.length(), beforeObservations: monitor.observations,
    dispatchEligible: false, lastEnabled: state.menu.enabled }
  action openMenu(enabled: Set[int]) = all {
    state.menu.phase == Closed,
    state' = { ...state, menu: openedMenu(state, enabled) },
    monitor' = evidence("open")
  }
  val opened = monitor.event == "open"
  val safety = state.intents.length() == monitor.beforeCount
  action step = openMenu(Set(0, 2))
}
