/**
 * ELM-UX-023 keyboard-launcher; approved free defaults and explicit choices.
 * Quint LLM Kit: from-requirements, one compositor owner and shared state.
 * Native functions: registerShortcutBindings, restoreShortcutBindings,
 * beginShortcutReload, applyShortcutBindings, shortcutInventory.
 * Configuration callbacks are serialized on the native owner thread. Foreign
 * configuration can introduce a conflict; only its owner changes those rows.
 * Model includes lost preference receipts and reload between check/application.
 * It omits filesystem durability, physical key delivery, AT and ABI identity.
 */
module ShortcutRegistration {
 type Choice = Keep | Default | Alternate
 type Life = Ready | Reloading | Stopped
 type Phase = Idle | Pending | Applied | Unknown
 type State = {
   desired: Choice, installed: Choice, life: Life, generation: int,
   foreign: Set[str], phase: Phase, expected: int, proposed: Choice,
   writes: int, submissions: int, reloads: int, restores: int,
   lastApplied: int, lastExpected: int
 }
 var state: State
 pure def free(s: State, choice: Choice): bool =
   choice == Keep or not(s.foreign.contains(if (choice == Default) "default" else "alternate"))
 pure def canApply(s: State): bool =
   s.phase == Pending and s.life == Ready and s.expected == s.generation and free(s, s.proposed)
 pure def restored(s: State): State = {
   ...s, life: Ready,
   installed: if (free(s, s.desired)) s.desired else Keep,
   restores: s.restores + 1
 }
 pure def applied(s: State): State = {
   ...s, desired: s.proposed, installed: s.proposed, phase: Applied,
   writes: s.writes + 1, generation: s.generation + 1,
   lastApplied: s.generation, lastExpected: s.expected
 }
 action init = state' = {
   desired: Default, installed: Keep, life: Reloading, generation: 1,
   foreign: Set("existing"), phase: Idle, expected: 0, proposed: Keep,
   writes: 0, submissions: 0, reloads: 0, restores: 0,
   lastApplied: 0, lastExpected: 0
 }
 action finishReload = all { state.life == Reloading, state' = restored(state) }
 action beginReload = all {
   state.life == Ready,
   state' = { ...state, life: Reloading, installed: Keep,
     generation: state.generation + 1, reloads: state.reloads + 1 }
 }
 action submit(choice: Choice): bool = all {
   state.life == Ready, state.phase == Idle, free(state, choice),
   state' = { ...state, phase: Pending, proposed: choice,
     expected: state.generation, submissions: state.submissions + 1 }
 }
 action apply = all { canApply(state), state' = applied(state) }
 action refuse = all {
   state.phase == Pending, not(canApply(state)),
   state' = { ...state, phase: Idle }
 }
 action receipt = all { state.phase == Applied, state' = { ...state, phase: Idle } }
 action loseReceipt = all { state.phase == Applied, state' = { ...state, phase: Unknown } }
 action read = all { state.phase == Unknown, state' = { ...state, phase: Idle } }
 action foreignConflict(chord: str): bool = all {
   not(state.foreign.contains(chord)), state' = { ...state, foreign: state.foreign.union(Set(chord)) }
 }
 action stop = all {
   state.life != Stopped, state' = { ...state, life: Stopped, installed: Keep }
 }
 action verify(condition: bool): bool = all { assert(condition), state' = state }
 action step = {
   nondet choice = Set(Keep, Default, Alternate).oneOf()
   nondet chord = Set("default", "alternate").oneOf()
   any {finishReload, beginReload, submit(choice), apply, refuse, receipt,
     loseReceipt, read, foreignConflict(chord), stop}
 }
 val safety = all {
   state.foreign.contains("existing"),
   state.desired == Keep implies state.installed == Keep,
   state.life != Ready implies state.installed == Keep,
   state.writes <= state.submissions,
   state.lastApplied == state.lastExpected
 }
 val defaultReady = state.life == Ready and state.installed == Default and state.restores > 0
 val keptAfterReload = state.life == Ready and state.desired == Keep and state.reloads > 0 and state.writes > 0
 val alternateAfterReload = state.life == Ready and state.installed == Alternate and state.reloads > 0 and state.writes > 0
 val unknownAfterReload = state.life == Ready and state.phase == Unknown and state.reloads > 0 and state.writes == 1
}
