# Final UI/UX review: motion and perceived performance

Verdict: **changes required** — three medium contract/scenario gaps. Reviewed requirements SHA-256: `04fee8c928a929915f676baae39730754786fca921c7673a3d8cbd5e395d20fe`.

This confirms planning coverage only. No native GUI or implementation testing occurred. The original requirements file and all plan inputs remain unchanged.

The core plan correctly puts frame scheduling and input in native ownership, reverses from last presented geometry, preserves original deadlines and cancellation, labels historical previews, and separates GPU inventory from executed acceleration. Privacy revocation and output/device/session changes have explicit authority rules.

## UX-MOTION-001 — Distinct protocol states do not yet guarantee user-visible progress and uncertainty feedback

Severity: medium. Affected: ELM-ARC-007, ELM-ARC-014, ELM-UX-007, ELM-UX-029, ELM-UX-032.

Pending, Unknown and refusal are correctly modeled, but no common contract requires timely feedback on a slow taskbar activation, restore, capture or system operation. An implementation could safely wait until the native deadline while looking unresponsive, or show an optimistic success before native confirmation. Preview fallback does not distinguish loading from unavailable.

Required EARS correction:

WHEN a shell operation awaits a native outcome beyond the frozen feedback threshold, the Elm desktop SHALL expose accessible pending or reconciling feedback, preserve usable cancellation and independent controls, and show success only after correlated native confirmation.

The preview view SHALL distinguish loading, retained historical, current-live and unavailable states through accessible labels without borrowing pixels from another incarnation.

Scenario `slow-native-feedback`:

- GIVEN a taskbar restore is Pending and the frozen feedback threshold is reached before the original restore deadline
- WHEN the UI presents feedback
- THEN pending state is visibly and accessibly communicated, independent controls remain usable, cancellation does not duplicate the request, and no success is claimed

Scenario `unknown-outcome-feedback`:

- GIVEN a submitted operation becomes Unknown after transport interruption
- WHEN native reconciliation runs
- THEN the UI communicates reconciliation rather than success or an actionable blind retry; terminal confirmation updates the same operation

Scenario `preview-state-feedback`:

- GIVEN the same preview fixture transitions through loading, authorized historical frame, identity-matched live frame and unavailable
- WHEN each state is rendered
- THEN visual and accessibility states identify the actual source condition, never exposing disallowed pixels

Verification: Freeze the feedback threshold in P0; run delayed receipt, unknown outcome and preview-state native recordings plus accessibility output. Preserve original operation deadlines.

## UX-MOTION-002 — Reduced-motion acceptance omits enabling the preference during motion and shell-overlay routes

Severity: medium. Affected: ELM-REN-011, ELM-UX-022, ELM-QA-019.

The steady enabled route is specified, but current acceptance scenarios exercise only minimize/restore with the preference already enabled. There is no stated handoff when the preference changes during an active transition, and no concrete overlay scenario despite ELM-UX-022 including overlays.

Required EARS correction:

WHEN reduced motion becomes enabled during an active window or shell-overlay transition, the renderer SHALL stop decorative motion at its next valid presentation opportunity and settle the existing transaction through the reduced-motion route without restarting its deadline, duplicating native effects or replaying motion when the setting is later disabled.

Scenario `enable-reduced-motion-midflight`:

- GIVEN a restore transition has presented intermediate geometry and has an original transaction deadline
- WHEN reduced motion is enabled before the next presentation
- THEN decorative interpolation stops at the next valid presentation opportunity; the same transaction reaches the matching final state and focus, retains its deadline and retires its proxy once

Scenario `reduced-motion-shell-overlays`:

- GIVEN reduced motion is enabled
- WHEN switcher, Task View and snap overlays open, change selection and dismiss in separate named fixtures
- THEN each follows the approved nondecorative profile with preserved focus/cancellation semantics

Scenario `disable-reduced-motion-no-replay`:

- GIVEN a transition completed through the reduced-motion route
- WHEN the preference is disabled
- THEN the completed motion is not replayed and subsequent transitions use the normal profile

Verification: Record native presentation sequences and effect/retirement receipts for each fixture; compare final semantics with the ordinary route.

## UX-MOTION-003 — Efficiency budgets need an explicit demand-driven preview and decorative-work contract

Severity: medium. Affected: ELM-REN-012, ELM-QA-023, ELM-REV-020, ELM-REV-021, ELM-GPU-010.

Limits, soak metrics and power budgets are strong, but there is no behavior requirement to stop recurring capture, texture upload and decorative GPU submissions once consumers close. This allows needless background work to survive while remaining below a broad budget, especially on the discrete GPU. Retention of the last accepted frame is necessary; repeated production for a closed consumer is different work.

Required EARS correction:

WHILE no visible preview consumer or required transition needs new content, the capture and rendering services SHALL suspend recurring preview acquisition, upload and decorative frame work while preserving authorized retained-frame ownership, control-event processing and bounded cleanup.

Scenario `dismiss-preview-quiesces-work`:

- GIVEN a visible preview is producing updates and owns an accepted retained frame
- WHEN its final consumer closes and the declared quiescence interval elapses
- THEN recurring preview acquisition/uploads and decorative submissions stop; the authorized retained lease remains usable and native control events still arrive

Scenario `preview-reopen-revalidates`:

- GIVEN preview production is quiescent and the output or source generation changed
- WHEN a consumer reopens
- THEN production resumes only after current authorization/identity/output validation and shows explicit pending or unavailable feedback until a valid frame exists

Scenario `hidden-consumer-resource-soak`:

- GIVEN repeated preview open/dismiss cycles on qualified integrated and selectable discrete profiles
- WHEN the idle/soak workload completes
- THEN whole-process wakeups, power and resource counts meet frozen budgets, and no recurring preview work or orphan helper accumulates

Verification: Native producer/submission counters and whole-process power/wakeup traces, with a P0-frozen quiescence interval. Do not stop required minimized retained-frame storage, lock revocation, retirement or native compositor work.

The resulting plan can be confirmed in this review scope once these contracts and named scenarios are incorporated. Implementation acceptance remains pending.
