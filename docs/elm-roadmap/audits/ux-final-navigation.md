# Final navigation and information architecture review

Verdict: **changes required**. The native-authority and identity contracts are strong, but several everyday navigation paths remain underspecified. These are planning corrections; implementation and native acceptance remain pending.

Requirements SHA-256: `04fee8c928a929915f676baae39730754786fca921c7673a3d8cbd5e395d20fe`.

Reviewed the final requirement registry, roadmap, repository instructions/handoff and taskbar, switcher and shell-experience OpenSpec capabilities. No GUI or implementation was changed.

## UX-NAV-001 — high: Taskbar primary-action decision table is missing

Affected: ELM-UX-004, ELM-UX-005, ELM-UX-008.

A pinned app with no windows, a group with one active window, and a group with three windows have no specified primary-click behavior. One implementation may launch a duplicate while another opens a picker or minimizes the active window.

Contract correction: Add a versioned taskbar interaction table covering zero/one/multiple eligible entries; active, inactive and minimized member; primary click, keyboard activation and explicit new-instance action. State whether active-window primary activation minimizes or stays active. Distinguish application pin from window always-on-top.

Acceptance correction: Named scenarios must cover launching a zero-window pinned app once, activating an inactive single member, restoring a minimized member, opening/selecting a multi-member group, and the selected active-click policy; verify native refusal keeps observed state.

## UX-NAV-002 — high: Launcher search state and stale-result behavior are undefined

Affected: ELM-UX-003, ELM-UX-029.

User types Brave then Files while a catalog refresh is outstanding. The old result selection may remain bound to Brave when Enter is pressed. Empty/loading/no-match/unavailable states also have no contract.

Contract correction: Require query-generation-bound results and selection; freeze deterministic matching/ranking and localized-label behavior in the product contract. Distinguish initial/loading/no-match/catalog-unavailable/refused-launch states. Preserve user query on refusal and provide a keyboard-reachable retry or refresh without automatic launch.

Acceptance correction: Exercise zero-match query, unavailable catalog, query change while refresh completes, selected catalog entry removed before Enter, and refused launch; no stale selection or blank/unreachable surface can trigger another app.

## UX-NAV-003 — medium: Switcher scope, initial order and zero/one-window behavior are unassigned

Affected: ELM-UX-011, ELM-UX-014, ELM-REV-016.

Frozen eligible-window order is required, but it could be alphabetical, MRU or native insertion order; scope could include all workspaces or only current workspace. Alt-Tab may select the already focused window on its first step.

Contract correction: Freeze eligibility scope, MRU or alternative ordering, initial selection, forward/reverse wrap, late arrivals and surviving-selection fallback before implementation. Include minimized members consistently with REV-016 and document cross-workspace activation policy.

Acceptance correction: Cover current window plus two others with known activation history, cross-workspace/minimized candidates, zero and one candidate, candidate closing mid-chord, a new arrival during chord and forward/reverse wrapping.

## UX-NAV-004 — medium: Task View can enumerate windows without a complete navigation journey

Affected: ELM-UX-017, ELM-UX-018, ELM-UX-023.

The requirements show workspace groups and transfers but do not require selecting a window from Task View to activate/restore it, switching workspace markers, or dismissing an empty overview. A populated workspace list can satisfy current scenarios without usable destination navigation.

Contract correction: Require keyboard/pointer selection of window and workspace, native-correlated activation/restore or switch outcome, predictable close/dismiss behavior, focus return and usable empty-workspace/no-window state. Explicitly inventory whether workspace create/delete/rename is in scope instead of implying full Task View parity.

Acceptance correction: Cover selecting a minimized member on another workspace, native refusal while overview stays usable, selecting an empty workspace, dismissal without mutation, and disappearance of selected member.

## UX-NAV-005 — medium: Operation states lack a user-visible recovery contract across surfaces

Affected: ELM-ARC-007, ELM-UX-008, ELM-UX-010, ELM-UX-019, ELM-UX-030.

ARC-007 distinguishes Pending/Committed/Refused/Cancelled/Unknown in the model, but only launch and transfer explicitly require refusal feedback. Pin, snap, taskbar restore, jump-list action and settings validation can leave a user guessing or clicking repeatedly.

Contract correction: Define a shared presentation contract for delayed pending, terminal refusal, cancellation and unknown/reconciling state. Keep native observed state authoritative; bound duplicate activation during pending and expose actionable, keyboard/AT-reachable recovery without replaying uncertain mutation. Define menu retention/dismissal after refused action.

Acceptance correction: For each action family, inject pending delay, refusal and transport loss; verify visible and accessible feedback, no false success or duplicate effect, recovery following native reconciliation and preserved focus/query/context.

## UX-NAV-006 — medium: Dense taskbar and action discoverability are not specified

Affected: ELM-UX-002, ELM-UX-005, ELM-UX-010, ELM-UX-023, ELM-UX-027.

Many pinned apps on a small or enlarged-text display may leave later icons unreachable. Jump-list invocation and access to window operations are referenced without a required discoverable affordance or input gesture.

Contract correction: Require all configured icons and group members remain keyboard and pointer reachable through a declared bounded overflow/scroll policy; retain selected-item visibility and order. Define menu/jump-list invocation by pointer and keyboard, label icon-only controls accessibly, and provide discoverable window minimize/restore/pin operations wherever supported.

Acceptance correction: Use a small-output/enlarged-text fixture with more icons and group members than fit; reach first/last items and menus without pointer-only gestures, verify offscreen selection is revealed and output resizing preserves identities/order.

## Confirmed strengths

Identity-bound native effects, preview-history labeling and fallback, switcher cancellation/release-before-readiness, native-correlated state changes, keyboard and assistive-technology gates, and draft preservation are represented. This review confirms those contract directions, not a deployed experience.
