# Final UI/UX review: desktop consistency and usability

**Verdict: changes required.** Native safety and migration boundaries are well specified. Five product-contract gaps remain: deterministic interaction policy, uniform uncertain-operation recovery, reachable hotplug recovery, first-use discovery and empirical usability acceptance.

Reviewed requirements SHA-256: `04fee8c928a929915f676baae39730754786fca921c7673a3d8cbd5e395d20fe` (216 requirements).

This is a read-only planning review. Implementation acceptance and actual usability/native qualification remain pending.

Confirmed strengths: Native authority versus Elm presentation ownership is clear. Minimized enumeration is separated from live scene/input eligibility. Normal workspace identity, modal drafts, stale incarnation rejection and rollback are explicit. Optional compositor replacement is appropriately separated from mandatory shell delivery. GPU discovery and actual accelerated webview/WebGPU qualification are correctly distinct.

## UX-CONS-001 — high: Cross-workspace activation and taskbar click semantics remain unspecified

Requirements: ELM-UX-005, ELM-UX-008, ELM-UX-011, ELM-UX-017, ELM-REV-016.

On workspace 1 the user selects the retained taskbar preview of minimized A on workspace 2. A can be restored on workspace 2 with no workspace switch, so its native receipt passes UX-008 while the user sees no response. Different display views can also choose incompatible behavior for the same target. The contract does not define active-window taskbar clicks, group selection, MRU ordering or which workspaces the switcher enumerates.

Proposed EARS addition:

The desktop experience inventory SHALL define default and supported preference policies for taskbar click states, group selection, switcher ordering and workspace/output scope, and cross-workspace activation before those interactions are implemented.

Phase: P0 policy / P3 implementation.

Scenario 1: GIVEN workspace 1 is current and minimized target A belongs to workspace 2; WHEN the user selects A through the taskbar using the frozen activation policy; THEN one correlated operation makes A visible and focused according to that policy, normal workspace membership is preserved, and all display projections agree.

Scenario 2: GIVEN one active window, one inactive window and a grouped application on the current workspace; WHEN the interaction-table fixtures exercise each taskbar click state and switcher traversal; THEN each resulting minimize, activate, restore or group-opening action matches the frozen table and produces no duplicate effect.

## UX-CONS-002 — high: Native operation states lack a uniform user-visible recovery contract

Requirements: ELM-ARC-007, ELM-ARC-014, ELM-UX-016, ELM-UX-018, ELM-UX-029, ELM-UX-032.

A pin request remains Pending or Unknown after the authority disconnects. The existing pin indicator correctly waits for correlated observations, but the user sees no feedback and repeatedly clicks. Launch and transfer refusals have feedback; minimize, restore, pin and snap do not uniformly require it or a recovery path.

Proposed EARS addition:

WHEN a user-requested shell operation is pending, refused or unknown, the shell SHALL expose accessible operation status and a permitted recovery action without asserting success before native confirmation or resending an uncertain mutation.

Phase: P3 shared status / P5 complete surfaces.

Scenario 1: GIVEN a pin request becomes Unknown during authority disconnection; WHEN the user inspects status or invokes recovery; THEN the UI announces uncertainty, retains last confirmed pin state, reconciles before any new effect and does not replay the old mutation.

Scenario 2: GIVEN a snap or minimize operation receives a terminal refusal; WHEN the matching outcome is rendered; THEN the shell provides a concise accessible reason and safe next action while preserving native-confirmed state and keyboard focus.

## UX-CONS-003 — medium: Output removal reconciles generations without guaranteeing reachable controls

Requirements: ELM-QA-020, ELM-REN-020, ELM-UX-020, ELM-UX-024, ELM-REV-028.

A keyboard-focused settings popup is on an external output when it is disconnected. Old generations are invalidated correctly and ownership reconciles, but the popup can remain logically focused with no visible surface on the surviving output. A window can also reconcile to off-screen placement.

Proposed EARS addition:

WHEN an output disappears, the native host SHALL apply a documented surviving-output recovery policy that keeps shell controls and application recovery actions reachable, resolves displaced popup focus and preserves window workspace identity.

Phase: P5.

Scenario 1: GIVEN a focused settings popup and an application recovery control occupy the removed external display; WHEN that output is unplugged; THEN the popup is dismissed with eligible focus restoration or rehosted on the declared surviving output, and application recovery remains keyboard reachable with no invisible focus trap.

Scenario 2: GIVEN all configured outputs disappear and later one returns; WHEN current output state is reconciled; THEN shell controls recover on the available output under the same policy without effects against removed generations.

## UX-CONS-004 — medium: First-use discovery and preference migration are not specified

Requirements: ELM-UX-001, ELM-UX-023, ELM-UX-030, ELM-DEL-009, ELM-DEL-016, ELM-DEL-020.

The feature selector successfully switches one qualified component and preserves the prior settings file, but a user cannot discover the new Task View/snap shortcuts or find rollback without a working Elm host. Existing shortcut collisions can silently change muscle memory even though settings persistence passes.

Proposed EARS addition:

WHEN a user first enables a migrated component, the shell SHALL offer dismissible keyboard-accessible guidance for changed interactions, preserve approved existing preferences and expose the documented offline recovery route without requiring onboarding completion.

Phase: P5 guidance / P6 activation.

Scenario 1: GIVEN an existing Omarchy profile with customized shortcuts and a qualified replacement component; WHEN the user enables it and dismisses first-use guidance; THEN the existing preference mapping or explicit conflict decision is preserved, new actions remain discoverable in help/settings and the component works without mandatory onboarding.

Scenario 2: GIVEN first-use guidance is dismissed and the Elm host later fails; WHEN the user follows the documented recovery route; THEN the predecessor can be restored offline and the preserved compatible preferences remain usable.

## UX-CONS-005 — medium: User acceptance does not define evidence-based usability criteria

Requirements: ELM-DEL-025, ELM-UX-035, ELM-QA-016, ELM-QA-019.

An engineer demonstrates every named flow and all native assertions pass, but first-time users cannot discover pin, recover from a refusal or understand a historical preview. The current user gate can pass without recording assistance, confusion, completion time, failures or the user cohorts whose accessibility needs are in scope.

Proposed EARS addition:

The product verifier SHALL freeze representative usability tasks, participant profiles, assistance rules and measurable success thresholds before candidate evaluation, and SHALL block usability acceptance when required outcomes lack observed evidence.

Phase: P0 protocol / P5 formative / P6 gate.

Scenario 1: GIVEN a frozen protocol covering novice and experienced desktop users and declared keyboard or assistive-technology routes; WHEN participants attempt taskbar restore, switcher selection, pin, snap, failed-operation recovery and rollback discovery; THEN task success, assistance, errors, recovery and completion measures are recorded against the predeclared thresholds; failed or unobserved required outcomes block usability acceptance.

Scenario 2: GIVEN a candidate fails a usability threshold; WHEN the report is reviewed; THEN the failure remains recorded and any changed threshold requires a new documented protocol before a separately identified rerun.

These additions should freeze product choices before implementation rather than expand the mandatory feature set. Existing application APIs remain outside the Windows-style parity claim. The mandatory 30–60 engineer-week estimate is plausible only as a provisional range; host feasibility, preview interoperability and AT integration remain explicit stop gates.
