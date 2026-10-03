I'll audit the frozen roadmap packet read-only, starting with the manifest and the full review packet, then check native-architecture claims against the requirements and reference sources.## Verdict

**Not ready for implementation admission** of the native architecture, layering, or GPU/host contracts. The frozen plan has a coherent Elm-versus-native split and several strong gates, and it has no critical finding that mandates a single unsafe behavior. It does have contradictory must-level rules for eligibility, commit races, animation proxies, modal hit/focus, and WebGPU success. Those contradictions admit implementations that recreate the Heroic/Brave class of bugs while still meeting some normative scenario. All implementation, native, and GPU acceptance remains pending. This session did not run code, tests, builds, or native commands, and did not recompute the supplied digest.

**Input SHA256:** `9b7f47af2664ab40322cf40241d04f69348a0a6064b20b1cec34a37713436b6b`

## Scope and limitations

Reviewed adversarially against the frozen packet and the frozen `draft-packet/` copies it embeds. The registry contains **181** requirements, **181** scenarios, and **15** capabilities (`validation.json` in the packet). Every requirement EARS statement was reviewed. OpenSpec text was read in full for `elm-layering`, `elm-gpu`, and `elm-native-bridge`. `design.md` and `proposal.md` were read from the packet. Contribution bodies read in full: `architecture.md`, `gnome-layering.md`, `kde-layering.md`, `rendering.md`. `GPU.md`, `LAYERING.md`, `ROADMAP.md`, and `BASELINE.md` were read from the packet. `heroic-layering-observation.json` and `gpu-inventory.json` were read from the frozen draft.

Primary sources actually opened:

- `docs/elm-roadmap/reference/mutter/src__core__window.c` — `meta_window_get_default_layer` (above-state suppressed when maximized, around line 6414) and `meta_window_showing_on_its_workspace` (lines 1749–1799, including `ancestor_is_minimized`).
- `docs/elm-roadmap/reference/kwin/src__layers.cpp` — `Workspace::constrainedStackingOrder` (lines 575–637): layer bands first, then above/below constraints that can move a window across bands.
- `docs/elm-roadmap/reference/kwin/src__window.cpp` — `Window::belongsToLayer` (lines 556–604).
- `docs/elm-roadmap/reference/kwin/src__input.cpp` — `InputRedirection::findToplevel` (lines 3439–3478): top-down constrained stack; skip deleted, other desktop/activity, minimized, hidden, show-desktop; lock screen keeps only lock, input-method, and lock overlay.
- `docs/elm-roadmap/reference/kwin/src__scene__windowitem.cpp` — `computeVisibility` (lines 153–181): force-visible counters can paint minimized or off-desktop items. Those counters are not consulted by `findToplevel`.

Not reviewed: the Mutter/KWin full archives, `tasks.md` beyond a search, `REQUIREMENTS.md`, and `TRACEABILITY.md`. Strict OpenSpec success in the packet is a structural result. It does not clear the semantic conflicts below.

Open, gated choices are **not** treated as defects: GTK/WebKit versus Qt WebEngine, numeric P0 budgets, the pin-versus-true-fullscreen winner once `ELM-GNO-001` freezes the inherited matrix, zero-copy versus measured copies, and the optional P7/P8 compositor substrate.

## Critical

None.

## High

### GRK-L01 — One stale intent has three commit outcomes

- **Severity:** high
- **Requirements:** `ELM-ARC-006`, `ELM-KDE-009`, `ELM-GNO-009`
- **Artifact:** `requirements.json` / `openspec/.../elm-native-bridge/spec.md` “ELM-ARC-006”; `elm-layering` “ELM-KDE-009”, “ELM-GNO-009”; `LAYERING.md` “Proposed native authority”
- **Defect:** `ELM-ARC-006` refuses the intent before mutation when the expected revision differs. `ELM-KDE-009` refuses **or reconciles**, and reconcile is undefined, so a stale focus can be rewritten onto the new scene and committed. `ELM-GNO-009` revalidates eligibility and its scenario always drops the effect when “its special workspace closes,” even if the window is eligible again. Counterexample: Elm validated focus for window A at revision 10. Before the critical section, A moves from `special:win-minimized` onto active workspace 1 and the revision becomes 11. ARC-006 refuses. KDE-009 can commit focus on A. GNO-009’s scenario forbids the effect even though A is now the correct target. A second case: A is minimized and ineligible at revision 11. GNO-009’s EARS allows commit if a racy recheck still sees the old eligible bit; ARC-006 forbids any commit.
- **Correction:** One rule. A revision or incarnation mismatch never mutates. Reconciliation is a read that produces a new snapshot only. A new effect needs a new request against the new revision.
- **Suggested EARS:** IF an effect intent’s window incarnation or expected scene revision differs from the native authority’s current committed revision, THEN the Elm desktop SHALL refuse that intent without mutation, record the refusal, and publish a fresh snapshot. WHEN reconciliation runs, the Elm desktop SHALL NOT convert the refused intent into a commit.
- **Blocks implementation admission:** Yes. Effect-boundary contract.

### GRK-L02 — A sequence gap can still apply later deltas

- **Severity:** high
- **Requirements:** `ELM-ARC-010`, `ELM-ARC-015`
- **Artifact:** `architecture.md` “Protocol design”; `elm-native-bridge` “ELM-ARC-010”
- **Defect:** The scenario discards event 9 after snapshot 10 and “triggers reconciliation” for the gap before 12. Nothing forbids applying 12 and 13, or admitting a focus intent, before resync installs the missing 11. Counterexample: event 11 destroys incarnation I and event 12 creates incarnation J at the same address. Applying 12 first makes Elm treat J’s pixels and focus as I. A minimize intent admitted during the gap hits J.
- **Correction:** Make the prose rule normative: a gap freezes delta application and effect admission until one snapshot covers the gap.
- **Suggested EARS:** WHEN the incoming event sequence skips one or more watermarks after a snapshot, the Elm desktop SHALL withhold every later delta and SHALL refuse new effect admission until one reconciliation snapshot establishes a new contiguous watermark.
- **Blocks implementation admission:** Yes. Bridge scene-truth contract.

### GRK-L03 — Cancel and commit are not one critical section

- **Severity:** high
- **Requirements:** `ELM-ARC-012`, `ELM-REN-009`, `ELM-UX-013`
- **Artifact:** `ROADMAP.md` “Architecture and data flow”; `rendering.md` “Ownership design”
- **Defect:** “Before an effect commits” is satisfiable by a check that is not the commit. Counterexample: the authority reads “not cancelled,” Escape is recorded, then restore commits and presents. `ELM-REN-009` rejects later receipts for that generation, so the late cancel receipt cannot undo the commit that already won the race. Helpers owned by the generation stay live because retirement runs only on the cancel path that lost.
- **Correction:** The cancellation flag, incarnation, and expected revision are read in the same critical section as the mutation. A cancel that arrives before that section finishes prevents the mutation and retires that generation’s resources.
- **Suggested EARS:** WHEN the native authority commits an effect, it SHALL observe cancellation, incarnation, and expected revision in the same critical section as the mutation. IF cancellation for that generation is recorded before the section completes, THEN the Elm desktop SHALL leave native state unchanged and retire only that generation’s resources.
- **Blocks implementation admission:** Yes. Effect-boundary contract.

### GRK-L04 — Unknown can unlock the next effect

- **Severity:** high
- **Requirements:** `ELM-ARC-007`, `ELM-ARC-008`, `ELM-ARC-014`
- **Artifact:** `elm-native-bridge` “ELM-ARC-008”
- **Defect:** Dependent dispatch waits until “the prerequisite receipt satisfies its declared precondition.” The only scenario is Pending. Unknown is a distinct receipt (`ELM-ARC-007`). Counterexample: restore’s connection drops, the outcome is Unknown, and focus is dispatched because a receipt object exists. `ELM-ARC-014` only blocks a **retry of the same effect**, so the dependent focus is still sent. The minimized window is focused without a proven restore, or focus hits the terminal that replaced it.
- **Correction:** Only a Committed receipt whose generation and incarnation match the declared precondition may release a dependent mutation.
- **Suggested EARS:** WHEN a dependent effect is requested, the Elm desktop SHALL dispatch it only after the prerequisite request is Committed for the same incarnation and generation. Pending, Refused, Cancelled, and Unknown SHALL NOT satisfy that precondition.
- **Blocks implementation admission:** Yes. Effect-boundary contract.

### GRK-L05 — 64-bit authority fields have no encoding requirement

- **Severity:** high
- **Requirements:** `ELM-ARC-005`, `ELM-ARC-006`, `ELM-UX-014`
- **Artifact:** `ROADMAP.md` “Architecture and data flow” (numeric encoding is named there and is absent from the registry)
- **Defect:** Intents carry incarnation, generations, and revisions across an Elm port, which is JSON through JavaScript. Values above 2^53 round to the same IEEE number. Counterexample: closed window incarnation `2^53+1` and the reused window `2^53+3` both become `9007199254740992`. `ELM-ARC-006` compares them equal and applies the old minimize to the new window. `ELM-UX-014` cannot see the address reuse. The roadmap tells the implementer to specify encoding before the transport; no requirement fails if they ship JSON numbers.
- **Correction:** Those fields are canonical decimal strings or byte arrays. A JSON number for any of them is a malformed envelope under `ELM-ARC-004`.
- **Suggested EARS:** The Elm desktop SHALL encode compositor lifetimes, epochs, request identities, operation generations, window incarnations, output generations, scene revisions, and monotonic deadlines as canonical decimal strings or byte arrays, and SHALL reject a JSON number for any of those fields before comparison or effect admission.
- **Blocks implementation admission:** Yes. Bridge contract.

### GRK-L06 — Causal events are coalescable

- **Severity:** high
- **Requirements:** `ELM-ARC-011`, `ELM-ARC-012`, `ELM-ARC-015`, `ELM-ARC-016`, `ELM-UX-012`
- **Artifact:** `design.md` “State and lifecycle”; `architecture.md` “Protocol design”; `ROADMAP.md` “Performance qualification”
- **Defect:** `ELM-ARC-015` coalesces “replaceable observations” and does not name a non-coalescible set. Design text says Alt release, cancellation, and retirement keep causal order. That text is not the registry. Counterexample: Alt release is coalesced into a later key sample while the switcher is opening. `ELM-UX-012` never sees the release, and the switcher stays open. A second case: a full observation queue drops a cancel as a replaceable duplicate, and restore commits.
- **Correction:** Put the decided exclusion list in EARS. Coalescing applies only to replaceable geometry or preview observations that carry a sequence proving replacement rather than loss.
- **Suggested EARS:** The Elm desktop SHALL NOT coalesce, drop, or reorder modifier press, repeat, release, Escape, cancellation, effect receipts, or retirement receipts. IF such a control item cannot be admitted, THEN the Elm desktop SHALL refuse new effect work and reconcile, and SHALL keep a reserved control queue for those items.
- **Blocks implementation admission:** Yes. Input and cancellation contract.

### GRK-L07 — Sticky windows are both shown and removed

- **Severity:** high
- **Requirements:** `ELM-GNO-002`, `ELM-LAY-001`
- **Artifact:** `elm-layering` “ELM-GNO-002”, “ELM-LAY-001”
- **Defect:** `ELM-LAY-001` excludes a window that is minimized **or** on an inactive **nonsticky** workspace. `ELM-GNO-002` excludes a window that is minimized **or** “belongs to an inactive workspace,” with no sticky exception. Counterexample: a sticky window on workspaces 1 and 2, with workspace 1 active. LAY-001 leaves it painted and hittable. GNO-002 removes it from ordinary paint and hit candidates because it also belongs to inactive workspace 2. The visible desktop loses the sticky window, or the two tests cannot both pass.
- **Correction:** Use one eligibility predicate. Sticky or on-all-workspaces membership on the active output stays eligible. Inactive nonsticky membership does not.
- **Suggested EARS:** WHILE a window is minimized, unmapped, destroyed, or present only on inactive nonsticky workspaces for an output, the Elm desktop SHALL exclude that live surface from paint and hit candidates on that output. WHILE a window is sticky on the active output and is not minimized, unmapped, or destroyed, the Elm desktop SHALL keep that live surface eligible on that output.
- **Blocks implementation admission:** Yes. Eligibility contract.

### GRK-L08 — Layer classification can resurrect an ineligible window

- **Severity:** high
- **Requirements:** `ELM-KDE-002`, `ELM-GNO-002`, `ELM-GNO-003`, `ELM-KDE-005`, `ELM-LAY-001`
- **Artifact:** `elm-layering` “ELM-KDE-002”; `kde-layering.md` “Direct historical source evidence”; pinned `Window::belongsToLayer`
- **Defect:** `ELM-KDE-002` derives “layer eligibility” from type, pin, fullscreen, family, and output context. Minimize, hidden, lock, workspace, and incarnation are absent. Those inputs match `belongsToLayer`, which does not decide hit eligibility. A literal reading paints a minimized pinned window because pin is an eligibility input. That fails `ELM-GNO-002` and `ELM-GNO-003`. Counterexample from the frozen observation shape: Heroic on `special:win-minimized`, `allowedOverFullscreen=true`, plus pin. KDE-002 places it in the pin/fullscreen band. The fullscreen terminal (`foot`, `fullscreen:1` in `heroic-layering-observation.json`) stays underneath. GNO-003 says the permission must not restore it.
- **Correction:** Split the predicates. First filter eligibility from the KDE-005 state tuple. Then classify layers only for survivors. Pin and fullscreen never re-add a filtered window.
- **Suggested EARS:** The native authority SHALL compute scene eligibility before layer classification. Layer classification SHALL apply only to windows that remain eligible, and pin, fullscreen, and family rank SHALL NOT reintroduce a window excluded as minimized, unmapped, destroyed, locked-out, or inactive-nonsticky.
- **Blocks implementation admission:** Yes. Layering contract.

### GRK-L09 — The Heroic scenario forbids the preview the restore scenario requires

- **Severity:** high
- **Requirements:** `ELM-KDE-004`, `ELM-LAY-001`, `ELM-GNO-008`, `ELM-UX-006`
- **Artifact:** `elm-layering` scenario `kde-004` versus scenario `layer-001`
- **Defect:** KDE-004’s EARS excludes ordinary live painting. Its THEN says the hidden window “cannot appear.” LAY-001’s THEN allows an independently owned inert preview. UX-006 requires that preview on the taskbar, labeled historical. Counterexample: Heroic is minimized, the terminal is active, and a taskbar preview shows Heroic’s last frame. The LAY-001 and UX-006 tests pass. The KDE-004 test fails because Heroic “appears.” Suppressing the preview to satisfy KDE-004 fails minimized-preview acceptance.
- **Correction:** Change the KDE-004 oracle so only the live source is absent from ordinary paint, hit, and direct focus. An inert preview actor with its own identity may remain.
- **Suggested EARS:** IF a window belongs to an inactive special workspace or is minimized, THEN the native authority SHALL exclude that live surface from ordinary paint, pointer targeting, and direct focus. An independently owned preview actor MAY remain visible only as a noninteractive historical image.
- **Blocks implementation admission:** Yes. Minimized-surface acceptance oracle.

### GRK-L10 — Animation proxies are both inert and optionally hittable

- **Severity:** high
- **Requirements:** `ELM-GNO-008`, `ELM-KDE-006`, `ELM-LAY-003`, `ELM-REN-007`
- **Artifact:** `gnome-layering.md` “Derived architecture”; `kde-layering.md` “Engineering inference”; pinned `computeVisibility` versus `findToplevel`
- **Defect:** GNO-008 says the animation or preview resource is only a noninteractive visual object. KDE-006 withholds it from hit testing only when it “lacks explicit input authority,” and the scenario says input follows “explicit proxy policy.” The KWin study’s own sources paint minimized windows when `m_forceVisibleByMinimizeCount > 0` while `findToplevel` still skips `isMinimized()`. KDE-006 allows the product to do the opposite of that split. Counterexample: during minimize, the effect sets force-visible and grants the proxy input authority. The user clicks the moving Heroic pixels. The proxy raises Heroic and cancels the minimize, or the click focuses Heroic while the terminal is the ordinary top hit. A second case: restore handoff (`ELM-REN-007`) leaves the retained overlay up until the live frame is ready, and LAY-003 has already made the live surface eligible. Both actors accept the click.
- **Correction:** Proxies stay out of ordinary hit and focus regardless of force-visible or elevation. Taskbar clicks hit the shell surface and become a new native intent. Live eligibility and overlay retirement commit in one revision.
- **Suggested EARS:** WHILE a preview or animation actor represents a minimized or ineligible window, the native authority SHALL omit that actor and the live source from hit testing and focus, including when a force-visible or elevation flag paints the actor. WHEN restore makes the live surface eligible, the Elm desktop SHALL retire that overlay in the same scene revision.
- **Blocks implementation admission:** Yes. Proxy and input-targeting contract.

### GRK-L11 — Modal redirect is both required and forbidden

- **Severity:** high
- **Requirements:** `ELM-QA-017`, `ELM-REN-015`, `ELM-GNO-006`, `ELM-LAY-002`, `ELM-REN-018`, `ELM-KDE-007`, `ELM-ARC-018`
- **Artifact:** `rendering.md` “Ownership design”; `elm-layering` “ELM-GNO-006”; `requirements.json` `ELM-QA-017`
- **Defect:** QA-017 and REN-015 require painted order, hit target, and committed focus to agree, with no modal exception. GNO-006 and LAY-002 allow a modal-redirection exception. KDE-007 and REN-018 select an “intended” or “family policy” recipient and do not say who that is. Counterexample: a modal draft is above maximized Brave. The user clicks Brave. Windows-style modality keeps focus on the draft and does not focus Brave. That fails QA-017, because hit (Brave) and focus (draft) differ. Focusing Brave satisfies QA-017 and fails modality. Recording “clicks hit the topmost pin” as the GNO-006 “recorded native exception” also satisfies GNO-006 while leaving the modal buried.
- **Correction:** Define the redirect. For an eligible modal family, the hit and the focus recipient are the current modal child when the click is on the owner or another window of that family. Unrelated applications use ordinary topmost agreement. Name every other exception in the P0 table. “Family policy” is not an oracle.
- **Suggested EARS:** WHEN the user clicks the owner of an eligible modal family or another window in that family, the native authority SHALL deliver the hit and the committed focus to the current eligible modal recipient and SHALL leave unrelated drafts open. WHEN the user clicks an unrelated eligible window with no modal exception, painted top, hit target, and focus SHALL be that window.
- **Blocks implementation admission:** Yes. Modal and hit-test contract.

### GRK-L12 — Maximized windows are not required to stay in the ordinary band

- **Severity:** high
- **Requirements:** `ELM-REN-015`, `ELM-REN-017`, `ELM-GNO-001`, `ELM-KDE-001`
- **Artifact:** `LAYERING.md` “Layer policy to freeze in P0”; pinned Mutter `meta_window_get_default_layer` (`wm_state_above && !meta_window_is_maximized`)
- **Defect:** LAYERING.md decides that MAX stays in ordinary application order and that raising a covered eligible peer paints that peer. The registry never says this. REN-015 only says that **whatever is already the visible top** receives focus. A compositor that always stacks MAX above floats makes MAX the visible top, the click focuses it, and REN-015 passes. REN-017 only says true fullscreen is not floating MAX, so MAX can still be a third band above ordinary windows. That is the reported Brave maximized-window defect, and Mutter’s maximized suppression of above-state is the reference behavior the plan said not to copy. `ELM-GNO-001` can record a table that stacks MAX above ordinary windows and still pass.
- **Correction:** Add the decided MAX rule as a must requirement. Leave pin-versus-true-fullscreen to the P0 inherited matrix.
- **Suggested EARS:** WHILE a window is maximized and not pinned and not true-fullscreen, the native authority SHALL keep it in the ordinary application band. WHEN an eligible ordinary peer is raised over that maximized window, the native authority SHALL paint and hit-test that peer above the maximized window in the same scene revision.
- **Blocks implementation admission:** Yes. Layering contract. This is the plan’s own rule, not a new product request.

### GRK-L13 — Overlap and restore are “proved” by the Heroic fixture text

- **Severity:** high
- **Requirements:** `ELM-LAY-002`, `ELM-LAY-003`, `ELM-LAY-001`
- **Artifact:** `requirements.json` verification fields for `ELM-LAY-002` and `ELM-LAY-003`
- **Defect:** Both verification strings say “Protected native pixel/hit/focus fixture reproducing the recorded Heroic-versus-terminal symptom,” copied from LAY-001. LAY-002’s scenario is overlapping windows and one stack revision. LAY-003’s scenario is atomic restore, preserved workspace identity, and no stale overlay. Counterexample: a campaign runs only the Heroic minimized case and attaches that receipt to LAY-002 and LAY-003. The verification text passes. A float still cannot cover maximized Brave, and restore still leaves the minimized overlay clickable.
- **Correction:** Give each requirement a verifier that matches its scenario: overlap pixels plus hit/focus for LAY-002; one restore revision, workspace id, and overlay retirement for LAY-003.
- **Suggested EARS:** No new behavioral sentence. Replace the verification text. LAY-002’s verifier SHALL show two overlapping eligible windows, one revision id, and agreement of pixel top, hit, and focus. LAY-003’s verifier SHALL show the pre-minimize workspace id, one new revision, a single eligible live surface, and an absent prior overlay generation.
- **Blocks implementation admission:** Yes. Layering acceptance oracles.

### GRK-L14 — “Eligible” both excludes and includes minimized windows

- **Severity:** high
- **Requirements:** `ELM-GNO-002`, `ELM-UX-005`, `ELM-UX-008`, `ELM-UX-011`, `ELM-UX-017`
- **Artifact:** `requirements.json` UX scenarios `ux-008`, `ux-011`, `ux-017`; `LAYERING.md` “Proposed native authority”
- **Defect:** Scene rules exclude minimized windows from ordinary paint and hit candidates. UX-008’s scenario selects a minimized window on workspace 2 and restores it. UX-011 advances Alt-Tab in “the frozen eligible-window order.” UX-017 shows “eligible windows” in Task View. One shared boolean cannot do both jobs. Counterexample: the implementer reuses GNO-002 eligibility for the switcher. Minimized Heroic is absent from Alt-Tab and Task View, so the user cannot restore it, and UX-008 fails. The other implementer marks Heroic shell-eligible and also leaves it in the paint and hit lists. The terminal cannot cover it.
- **Correction:** Name two predicates. Scene-input eligibility excludes minimized and inactive-nonsticky live surfaces. Shell enumeration includes those incarnations as selectable rows and does not feed them back into paint or hit.
- **Suggested EARS:** The Elm desktop SHALL keep scene-input eligibility and shell-enumeration eligibility as distinct predicates. Scene-input eligibility SHALL exclude minimized and inactive-nonsticky live surfaces from paint and hit testing. Taskbar, switcher, and Task View SHALL enumerate those same incarnations as selectable entries without granting their live surfaces paint or hit eligibility.
- **Blocks implementation admission:** Yes. Scene-truth contract.

### GRK-L15 — Device loss can show a stale frame or drop the only retained copy

- **Severity:** high
- **Requirements:** `ELM-GPU-007`, `ELM-QA-025`, `ELM-DEL-028`, `ELM-REN-003`, `ELM-REN-004`
- **Artifact:** `GPU.md` “Release and failure policy”; `elm-gpu` “ELM-GPU-007”
- **Defect:** GPU-007 invalidates GPU resources and forbids replaying a stale **window effect**. It does not forbid presenting a rebuilt image as current. QA-025 forbids stale frames only “WHERE a GPU renderer is selected,” so a mandatory webview GPU crash need not run that test. DEL-028 is conditional on WebGPU being enabled. REN-003 requires the last accepted frame to survive until lease retirement. Counterexample: the webview device on the NVIDIA adapter is lost after the user restores Heroic and types. The host builds a new texture from the minimized lease and presents those pixels as the live window. GPU-007 passes because the old minimize intent was not replayed. The opposite counterexample: invalidation destroys the only copy of the lease, source-stop retention fails, and the preview goes blank or the buffer is reused after retirement.
- **Correction:** Device loss invalidates every dependent GPU object on every adapter the shell used, bumps the rendering generation, and presents again only from a lease whose incarnation, output generation, and scene revision were re-read. A device-independent retained copy exists before the GPU object is dropped. QA-025’s stale-frame rule applies to the mandatory webview GPU path.
- **Suggested EARS:** WHEN any GPU device used for shell composition or preview import is lost, the host SHALL make that device’s resources unusable, increment the rendering generation, and SHALL NOT present a frame as current until the native authority revalidates its lease incarnation, output generation, and scene revision. The host SHALL retain a device-independent copy of an accepted source-stop frame until lease retirement, and SHALL NOT replay pending application-window effects.
- **Blocks implementation admission:** Yes. GPU recovery contract.

### GRK-L16 — WebGPU success is mandatory and optional

- **Severity:** high
- **Requirements:** `ELM-GPU-004`, `ELM-GPU-005`, `ELM-GPU-003`, `ELM-DEL-028`
- **Artifact:** `GPU.md` “P1 WebGPU experiment” and “Release and failure policy”; `elm-gpu` “ELM-GPU-005”
- **Defect:** GPU-005 is a ubiquitous must: the qualification verifies a deterministic render and compute result. GPU-004 says a null adapter rejects WebGPU qualification and keeps another hardware route. GPU.md says a WebGPU failure disables optional effects. DEL-028 applies only where WebGPU is enabled. Counterexample: `requestAdapter` returns null on both pinned hosts because the secure local origin is not a secure context, or the engine has no `navigator.gpu`, while the sandbox stays on (`ELM-GPU-003`). GPU-004 records WebGPU as unqualified. GPU-005 is still unmet, so every must requirement cannot pass, and the host gate cannot fall back to the native GPU path the same document allows.
- **Correction:** Make GPU-005 conditional on an available non-software device. A null adapter or rejected device satisfies GPU-004 and does not fail host selection.
- **Suggested EARS:** WHEN WebGPU evaluation obtains a non-software adapter and a device, the host SHALL verify a deterministic render and compute result and an independently observed native frame. IF the adapter or device is unavailable, the host SHALL record WebGPU as unqualified and SHALL continue with an accepted non-WebGPU hardware path or the degraded-mode rule.
- **Blocks implementation admission:** Yes. GPU host-selection contract.

### GRK-L17 — Lock state is an input with no exclusion outcome

- **Severity:** high
- **Requirements:** `ELM-KDE-005`, `ELM-GNO-001`
- **Artifact:** `LAYERING.md` table row “Lock/security surfaces”; pinned `findToplevel` lines 3469–3472 and `computeVisibility` lines 158–159
- **Defect:** The layering table gives lock surfaces exclusive priority. GNO-001’s required table omits lock. KDE-005 says eligibility is “derived from” lock state and does not say ordinary, pinned, or allowed-over-fullscreen windows lose paint and hit. The KWin functions that were cited do that exclusion, for both paint and hit. Counterexample: the session is locked, a pinned window still has `allowedOverFullscreen=true`, and it remains the hit target above the lock surface. KDE-005 passes because the revision included a lock bit that the ranker ignored. The shell webview receives the password click.
- **Correction:** Add a must exclusion. Locked mode paints and hits only lock, lock-overlay, and input-method surfaces. Pin, fullscreen permission, and shell layer priority do not override it.
- **Suggested EARS:** WHILE the session lock is active, the native authority SHALL paint and hit-test only lock, lock-overlay, and input-method surfaces. Pinned, maximized, fullscreen, ordinary, preview, and shell surfaces SHALL NOT receive pointer or keyboard events until lock ends.
- **Blocks implementation admission:** Yes. Layering contract. The table row is already a decided plan rule.

### GRK-L18 — A minimized owner does not take its family with it

- **Severity:** high
- **Requirements:** `ELM-GNO-002`, `ELM-GNO-004`, `ELM-LAY-001`
- **Artifact:** `gnome-layering.md` “Derived architecture” (“family exclusions” before layer priority); pinned `meta_window_showing_on_its_workspace` lines 1793–1796
- **Defect:** Eligibility is per window. GNO-004 keeps an eligible child above its owner and does not say the child becomes ineligible when the owner is minimized. Mutter’s cited helper hides a window whose ancestor is minimized. Counterexample: Brave is minimized onto `special:win-minimized` and disappears. Its modal draft stays mapped, `visible=true`, and above the terminal. The draft receives clicks. The terminal cannot cover the family. Group promotion is forbidden, so the fix is not “raise every window with the same PID.”
- **Correction:** Ineligibility of an owner applies to its transient descendants in that scene revision. Shell previews of those descendants stay inert and separate.
- **Suggested EARS:** WHILE an owner is ineligible because it is minimized, unmapped, destroyed, or on an inactive nonsticky workspace, the native authority SHALL exclude that owner’s transient descendants from live paint and application input in the same scene revision.
- **Blocks implementation admission:** Yes. Family eligibility contract.

### GRK-L19 — Shell hit regions and the hit path can swallow application input

- **Severity:** high
- **Requirements:** `ELM-ARC-022`, `ELM-UX-021`, `ELM-REN-029`, `ELM-GNO-006`
- **Artifact:** `LAYERING.md` “Proposed native authority” and the panels row; `design.md` decision 6; `rendering.md` “Optional compositor program”
- **Defect:** ARC-022 requires layer and popup roles and some input region before the Elm view exists. It does not bound that region to interactive shell geometry. UX-021 only says a drag that already started is not stolen. REN-029, the rule that hit testing and frame scheduling do not wait for Elm, is conditional on replacing Hyprland. Counterexample: the taskbar host creates a full-output layer surface with keyboard interactivity, which is a common layer-shell setup. Every click hits the webview, including clicks on the terminal, and a drag that starts over the terminal never starts. A second counterexample on the mandatory Hyprland path: the plugin sends the hit to Elm and waits for a port reply. A stalled webview freezes pointer dispatch. No must requirement fails that design.
- **Correction:** Shell input regions equal the visible interactive shell geometry. Empty or input-transparent regions pass the hit to the next eligible surface. On the Hyprland path and on any replacement, pointer dispatch and frame composition use the committed native revision and do not wait for an Elm port.
- **Suggested EARS:** The native host SHALL set each shell surface input region to its interactive geometry before the surface accepts input. A fullscreen shell view SHALL NOT receive hits outside that region. The native authority SHALL resolve pointer hits from the committed scene revision without waiting for an Elm or webview reply.
- **Blocks implementation admission:** Yes. Input-targeting contract for the mandatory shell, not only P8.

## Medium

### GRK-L20 — Dedup eviction can repeat an effect

- **Severity:** medium
- **Requirements:** `ELM-ARC-009`
- **Artifact:** `architecture.md` “Protocol design” (expired-ID refusal is stated there; the EARS omits it)
- **Defect:** Dedup is “within a frontend epoch” and the scenario only covers a still-remembered committed request. The ledger is bounded. Counterexample: request 7 is committed and evicted. The same id is presented again with a new minimize body. It is not a tracked duplicate, so a second minimize runs.
- **Suggested EARS:** IF a request identity is outside the retained deduplication window or was already retired in that frontend epoch, THEN the Elm desktop SHALL refuse it without mutation and record expired-identity refusal.
- **Blocks implementation admission:** Yes for the dedup slice of the bridge. Other layering work can be specified beside it.

### GRK-L21 — Deadlines survive restart as values and still expire on the wrong clock

- **Severity:** medium
- **Requirements:** `ELM-ARC-013`, `ELM-REN-005`, `ELM-REN-008`
- **Artifact:** `architecture.md` “Protocol design”
- **Defect:** ARC-013 preserves the stored deadline across renderer restart. The scenario can pass if that value is wall-clock milliseconds. An NTP step forward expires a two-second restore immediately. A step backward makes it unexpirable. REN-005’s clock rule covers motion samples, not effect deadlines. Architecture text already says native monotonic time and clock normalization.
- **Suggested EARS:** The Elm desktop SHALL store effect and restore deadlines as native monotonic timestamps in one documented clock domain. A renderer or host restart SHALL NOT reinterpret those timestamps as wall-clock instants.
- **Blocks implementation admission:** Yes for the deadline slice.

### GRK-L22 — WebGPU rejection demands an already accepted alternative

- **Severity:** medium
- **Requirements:** `ELM-GPU-004`, `ELM-GPU-009`, `ELM-GPU-001`
- **Artifact:** `elm-gpu` scenario `gpu-004`
- **Defect:** GPU-004 is P1 and requires preserving “an accepted alternative hardware-rendering route” when the adapter is null. At first evaluation nothing is accepted yet. GPU-009’s degraded mode is P6. Counterexample: both hosts lack WebGPU and the webview GPU probe is still running. GPU-004 cannot be satisfied, GPU-009 is out of phase, and host selection stops even if a non-WebGPU hardware path would pass GPU-001.
- **Suggested EARS:** IF a WebGPU adapter or device is unavailable, the host SHALL record WebGPU as unqualified. IF another hardware path is still under evaluation, host selection SHALL continue. IF no hardware path qualifies, the host SHALL enter the disclosed degraded mode and block accelerated release.
- **Blocks implementation admission:** Yes for host selection.

### GRK-L23 — Preview copies are measured and not failed

- **Severity:** medium
- **Requirements:** `ELM-GPU-008`, `ELM-GPU-010`, `ELM-QA-021`
- **Artifact:** `GPU.md` “Preview import and copy budget”
- **Defect:** GPU.md says to define a copy budget and not to promise zero-copy. GPU-008 only requires the report to record copies and fences. GPU-010’s transfer-budget comparison is P1, before the P4 import path. Counterexample: P1 selects a host on DOM rendering. P4 imports every preview by a full-frame copy from the NVIDIA capture GPU to the Intel webview GPU. The report records the copies. No requirement fails the path or keeps the native preview renderer.
- **Suggested EARS:** IF measured preview import copy volume, fence wait, or cross-GPU transfer exceeds the frozen P0 budget, THEN preview qualification SHALL fail that import path and the host SHALL keep an accepted native preview path or an explicit unavailable preview.
- **Blocks implementation admission:** Yes for the import slice. Budget numbers themselves stay a P0 decision.

### GRK-L24 — Recording a fence does not require waiting for it

- **Severity:** medium
- **Requirements:** `ELM-GPU-008`, `ELM-REN-002`, `ELM-REN-019`
- **Artifact:** `GPU.md` “Preview import and copy budget”; `rendering.md` “Ownership design”
- **Defect:** The import requirement measures synchronization. It does not say the displayed frame waits for the fence, or that retirement makes the DMA-BUF unusable. Counterexample: the host imports a native buffer, records “fence present, one copy,” and samples the texture before the capture GPU signals. The preview tears or shows a retired buffer after `ELM-REN-004` revoked the lease. The qualification report still matches gpu-008.
- **Suggested EARS:** WHEN the host imports a native frame, it SHALL present that frame only after the recorded acquire fence is signaled, and SHALL NOT sample the buffer after lease revocation or rendering-generation invalidation.
- **Blocks implementation admission:** Yes for the import slice.

### GRK-L25 — A guessed lease id imports another window

- **Severity:** medium
- **Requirements:** `ELM-ARC-019`, `ELM-REN-002`, `ELM-REN-004`, `ELM-DEL-011`
- **Artifact:** `rendering.md` “Ownership design”
- **Defect:** Frame keys include incarnation and revision in prose. Nothing says a key is an unforgeable capability issued for this epoch. DEL-011 rejects shell commands and filesystem paths. Counterexample: the renderer sends a preview import for incarnation `18000005` (the terminal in the frozen observation) while the shell intended Heroic. Sequential ids make that guessable. The terminal’s pixels enter the webview. REN-004 only revokes leases after incarnation **replacement**, so a live foreign window still imports.
- **Suggested EARS:** The native broker SHALL issue preview lease keys as unguessable capabilities bound to frontend epoch, window incarnation, and output generation. IF a key was not issued for that tuple, or was revoked, THEN the host SHALL refuse the import without reading the foreign buffer.
- **Blocks implementation admission:** Yes for the lease slice.

### GRK-L26 — A silent GPU switch keeps the old accelerated verdict

- **Severity:** medium
- **Requirements:** `ELM-GPU-010`, `ELM-DEL-026`, `ELM-GPU-007`
- **Artifact:** `gpu-inventory.json` (Intel ARL plus NVIDIA RTX 5090 Laptop, `VK_LAYER_NV_optimus` present); `GPU.md` “What is available on this machine”
- **Defect:** Qualification identifies the adapter that was current during the probe. The inventory shows a dual-GPU laptop with the Optimus layer. A later process can come up on the other device without a device-lost event. Counterexample: P1 qualifies the webview on NVIDIA. On battery the same host binary initializes on Intel. DEL-026’s old report still supports an accelerated NVIDIA claim, and GPU-010 is not rerun.
- **Suggested EARS:** WHEN the active GPU adapter name, UUID, or driver version differs from the qualified tuple, the host SHALL drop the accelerated verdict and SHALL NOT present that configuration as a qualified GPU release until the qualification is repeated.
- **Blocks implementation admission:** Yes for the GPU qualification slice.

### GRK-L27 — Epoch revocation is a release-phase requirement

- **Severity:** medium
- **Requirements:** `ELM-ARC-026`, `ELM-DEL-018`, `ELM-ARC-006`
- **Artifact:** `ROADMAP.md` phase table P1 and P2; `architecture.md` “Host security and recovery”
- **Defect:** Renderer and authority epoch invalidation is P6. P2 already admits mutating effects, and P3 admits taskbar restore. Counterexample: during P3 the renderer crashes and the new page resends the same epoch and a minimize whose revision is still current. ARC-006 allows it. The minimize runs twice. ARC-026 would have refused the old epoch, and it is not yet required.
- **Suggested EARS:** Keep the ARC-026 sentence and move its phase to the first phase that admits native effects (P2), including authority restart as well as renderer restart.
- **Blocks implementation admission:** Yes for live effect phases. It does not block P0 inventory.

### GRK-L28 — A full control queue drops cancellation

- **Severity:** medium
- **Requirements:** `ELM-ARC-016`, `ELM-ARC-015`
- **Artifact:** `architecture.md` “Protocol design”
- **Defect:** ARC-016 reserves control capacity against preview saturation. It does not say what happens when the control reservation itself is full. Architecture text says stop effect admission and reconcile. Counterexample: preview and control queues are both full. Escape is discarded. The prepared restore commits.
- **Suggested EARS:** IF control-queue admission for cancellation, receipts, or retirement fails, THEN the Elm desktop SHALL refuse new effect admission and force supervised reconciliation, and SHALL NOT drop a cancellation silently.
- **Blocks implementation admission:** Yes for the queue slice.

### GRK-L29 — The malformed-envelope scenario covers one direction

- **Severity:** medium
- **Requirements:** `ELM-ARC-004`
- **Artifact:** `elm-native-bridge` scenario `architecture-004`
- **Defect:** The EARS rejects a bad envelope anywhere. The only scenario is the host receiving it. Counterexample: a snapshot omits the minimized bit. Elm’s decoder fills `minimized=false` for Heroic on `special:win-minimized` and requests focus. The host scenario never runs. The terminal loses the stack.
- **Suggested EARS:** Keep the existing sentence and add a second scenario: GIVEN a snapshot missing incarnation or eligibility fields, WHEN Elm decodes it, THEN Elm applies no observation and records the rejection without sending a new effect.
- **Blocks implementation admission:** Yes for the decoder slice.

### GRK-L30 — The normative Heroic scenario drops the fullscreen peer

- **Severity:** medium
- **Requirements:** `ELM-GNO-002`, `ELM-LAY-001`, `ELM-GNO-003`
- **Artifact:** `heroic-layering-observation.json`; `elm-layering` scenario `gnome-layering-002`
- **Defect:** The frozen sample is not only Heroic with permissive flags. The active client is `foot` at `0x57a77b98bc10`, workspace 1, `fullscreen:1`, `allowedOverFullscreen=true`, and the output’s special workspace id is 0. The screenshot hash is earlier than the metadata sample; the plan already says so. The normative scenario does not include that fullscreen peer. Counterexample: a test builds Heroic’s flags beside an ordinary terminal, excludes Heroic from the ordinary candidate list, and passes GNO-002. A later fullscreen pass still draws every `allowedOverFullscreen` surface over `foot`. GNO-003’s abstract sentence would forbid that, and the concrete observation is not the fixture.
- **Suggested EARS:** GIVEN Heroic on inactive `special:win-minimized` with `hidden=false`, `visible=true`, `acceptsInput=true`, and `allowedOverFullscreen=true`, AND an active fullscreen terminal on workspace 1 while the output special workspace is empty, WHEN paint and hit candidates are solved, THEN Heroic’s live surface is absent from both, including any fullscreen or effect pass.
- **Blocks implementation admission:** Yes for the Heroic acceptance fixture. GNO-003 can stay as the abstract rule.

## Low

None. The remaining gaps are the gated decisions listed in scope. Tightening them further would be a recommendation, not a defect in this packet.

## Coverage strengths

The plan already separates several things that usually get collapsed:

- Elm presentation versus native surface lifetime versus effect authority (`ELM-ARC-002`), with ports limited to opaque leases (`ELM-ARC-019`, `ELM-REN-002`, `ELM-GPU-006`).
- Pending, Committed, Refused, Cancelled, and Unknown are distinct (`ELM-ARC-007`). A DOM animation callback is not presentation (`ELM-ARC-020`, `ELM-REN-022`).
- Hardware discovery, native GPU rendering, webview composition, and WebGPU are separate claims (`ELM-GPU-002`). The frozen inventory matches that caution: Intel ARL (Mesa 26.2.2) and NVIDIA RTX 5090 Laptop (615.71.09), Vulkan 1.4, WebKitGTK 2.52.6 present, and no webview or WebGPU execution claimed.
- Software fallback cannot wear an accelerated verdict (`ELM-GPU-001`, `ELM-QA-026`, `ELM-DEL-027`). Sandbox disablement is not an allowed way to expose `navigator.gpu` (`ELM-GPU-003`).
- The Heroic sample is labeled non-atomic, and convenience flags are not treated as the hit path. Mutter’s maximized suppression of above-state and KWin’s split between `computeVisibility` and `findToplevel` are described accurately in the passages checked.
- Cyclic families are refused with no partial order (`ELM-GNO-005`). Child-above-owner does not promote an unrelated group peer (`ELM-GNO-004`). Minimize must not move a window to a scratchpad (`ELM-REN-006`, `ELM-UX-008`). Restore keeps the original two-second deadline (`ELM-REN-008`).
- Hyprland remains the mandatory compositor. P7/P8 replacement is conditional, including seat, DRM/KMS, and “do not wait for Elm” on that optional path (`ELM-REN-025`, `ELM-REN-029`).
- Evidence classes cannot stand in for each other (`ELM-QA-005`), and a mixed ABI tuple cannot qualify (`ELM-QA-015`).

## What would clear admission

Correct the high findings in the registry and the matching OpenSpec scenarios, especially one commit rule, one eligibility predicate, inert proxies, modal hit/focus, ordinary MAX, lock exclusion, family descendants, shell input regions, the 64-bit encoding, non-coalescible control events, and WebGPU as a fallible probe. Medium findings block only their named slices. After that text changes, native and GPU acceptance is still unproven until the protected campaigns run.
