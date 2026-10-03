I'll audit the frozen Elm roadmap packet read-only, starting with the review packet, manifest, and requirements so the report stays tied to that snapshot.The registry has 181 requirements across nine phases. Next I’ll read every requirement and the OpenSpec/traceability material that is supposed to make them executable.## Verdict

**Not admitted for implementation.** The frozen plan is a real requirements baseline, and the open host, WebGPU, preview-import, and compositor-substrate choices are not defects. It is not an execution-ready contract: the OpenSpec task list does not encode phases, several must-pass scenarios cannot fail a wrong product or can pass a failed one, and mandatory lock, capture-authorization, lossless identity, and budget-sheet behavior is still prose.

Input SHA256 (supplied, not recomputed): `9b7f47af2664ab40322cf40241d04f69348a0a6064b20b1cec34a37713436b6b`

No implementation, native, or GPU acceptance is claimed. None of these findings were checked by running tests, builds, or the desktop.

## Scope and limitations

Reviewed against the frozen manifest and draft packet, not later live edits.

Read in full: `docs/elm-roadmap/audits/review-packet.md` (through the embedded proposal at line 4926), `draft-manifest.json`, `audits/README.md`, frozen `requirements.json` (all 181 requirements, scenarios, and verification strings), `TRACEABILITY.md`, `generation.json`, `validation.json`, `gpu-inventory.json`, `heroic-layering-observation.json`, and the packet copies of `ROADMAP.md`, `BASELINE.md`, `GPU.md`, `LAYERING.md`, the seven contribution markdown files, `design.md`, and `proposal.md`.

Read in part: `tasks.md` (full P0 block, lines 1–190, plus the P1, P2, and P8 headings, which repeat that block); OpenSpec specs `elm-gpu`, `elm-accessibility`, `elm-performance`, `elm-security` through ELM-DEL-017, and `elm-layering` from ELM-KDE-003 through ELM-LAY-003.

Primary sources actually opened, not the whole corpus: Mutter 49.0 `src/core/window.c` `meta_window_get_default_layer` at lines 6409–6427 in `docs/elm-roadmap/reference/mutter/complete/49.0-7697a7993e92dcef3b39b67051691a8b28f0b5ce/src/core/window.c`; KWin `InputRedirection::findToplevel` at lines 3439–3479 in `docs/elm-roadmap/reference/kwin/src__input.cpp`. Also read `docs/HANDOFF.md` lines 40–137 and `docs/crash-noise/HANDOFF-codex-window-qa.md` lines 1–30. `updateStackingOrder` was only confirmed to exist in `src__layers.cpp`. Compiler 0.19.2 was taken from the local research note, not re-fetched.

`review-packet.md` does not embed `tasks.md`, the capability specs, or `TRACEABILITY.md`. Those were taken from the manifest’s `draft-packet/`. SHA-256 values were not recomputed.

## Critical

### GRK-D-001 — Every phase checklist is a copy of all 181 tasks

- Severity: critical
- Requirement IDs: all 181; the gate that should have caught this is ELM-QA-016
- Artifact: `openspec/changes/elm-desktop-pivot/tasks.md`, headings `## P0` through `## P8 — optional compositor`; `validation.json` (`passed: true`, OpenSpec strict exit 0)
- Defect: The P0 section lists P0-ELM-ARC-001 through P8-ELM-ARC-029 and ends at P6-ELM-UX-035. The P1 section at line 191, the P2 section at line 375, and the P8 section at line 1479 start again at P0-ELM-ARC-001 with the same verify lines. Nine headings therefore each contain the full registry, including optional compositor implementation inside P0. Checking one copy leaves eight unchecked copies of the same task. Strict OpenSpec validation does not notice, because it never checks that a heading contains only that phase.
- Correction: Emit one checkbox per requirement, only under its `phase`. Keep P7 and P8 in the file and mark them conditional. Make the planner fail if a task id’s prefix disagrees with its heading, if any id appears twice, or if the checkbox count is not 181.
- Blocks implementation admission: **Yes.** The execution list cannot be followed or closed.

## High

### GRK-D-002 — Minimized-window visibility requirements contradict each other, and the Heroic fixture drops the recorded peer

- Severity: high
- Requirement IDs: ELM-KDE-004, ELM-LAY-001, ELM-GNO-002, ELM-GNO-008, ELM-KDE-006
- Artifact: `elm-layering` spec, scenarios `kde-004` and `layer-001`; `LAYERING.md` “Current regression”; `heroic-layering-observation.json`
- Defect: `kde-004` THEN says the hidden window “cannot appear or receive focus.” `layer-001` THEN allows “an independently owned inert preview.” ELM-GNO-008 and ELM-KDE-006 also allow a noninteractive painted proxy. A taskbar preview of minimized Heroic fails KDE-004 and passes LAY-001. The recorded peer is also missing: `foot` is `fullscreen: 1`, `allowedOverFullscreen: true`, and the active window, on output `eDP-2` whose `specialWorkspace.id` is 0. A fixture that only puts Heroic on `special:win-minimized` beside an ordinary terminal can pass while Heroic still covers a fullscreen peer.
- Correction: One normative rule: the live minimized or inactive-workspace surface is absent from ordinary paint, hit, and focus; a distinct inert preview may be painted and must not hit-test as the live window. Replace the KDE-004 THEN with that sentence. Add one scenario whose GIVEN is the recorded pair, including foot `fullscreen: 1` and the non-atomic screenshot caveat.
- Blocks implementation admission: **Yes** for layering and preview work.

### GRK-D-003 — LAY-002 and LAY-003 are graded by the Heroic verifier

- Severity: high
- Requirement IDs: ELM-LAY-002, ELM-LAY-003 (same string also on ELM-LAY-001, where it matches)
- Artifact: `requirements.json` `verification` for those three ids; `tasks.md` lines 94–96; `TRACEABILITY.md` rows ELM-LAY-001 through ELM-LAY-003
- Defect: All three verifiers say “Protected native pixel/hit/focus fixture reproducing the recorded Heroic-versus-terminal symptom.” LAY-002’s scenario is overlapping windows and one stack revision. LAY-003’s scenario is restore, workspace identity, and stale-overlay retirement. A passing Heroic minimize fixture can be attached to all three tasks.
- Correction: Give LAY-002 a verifier that samples overlapping pixels, the hit window, and focus against one revision, including an input-transparent region and a modal redirect. Give LAY-003 a verifier that records pre-restore workspace id, one new eligible surface, and rejection of the previous transition generation.
- Blocks implementation admission: **Yes** for ELM-LAY-002 and ELM-LAY-003.

### GRK-D-004 — Optional WebGPU is also a ubiquitous P1 must

- Severity: high
- Requirement IDs: ELM-GPU-005, ELM-GPU-003, ELM-GPU-004, ELM-DEL-028, ELM-QA-024
- Artifact: `GPU.md` “Release and failure policy”; `elm-gpu` spec, requirements ELM-GPU-004 and ELM-GPU-005; `design.md` decision 5
- Defect: ELM-GPU-004 correctly says a null adapter leaves WebGPU unqualified and keeps another hardware path. ELM-GPU-005 is ubiquitous and priority `must` at P1: qualification SHALL verify a deterministic WebGPU render and compute result. Its only scenario GIVEN assumes “a nonsoftware adapter and accepted device.” If `requestAdapter` returns null, GPU-004 passes and GPU-005 remains an unsatisfied must, so host selection cannot finish. ELM-QA-024 is the evidence requirement and is only `conditional`. ELM-DEL-028 is the optional device-loss requirement, at P4.
- Correction: Change ELM-GPU-003 and ELM-GPU-005 to `WHERE WebGPU qualification is attempted`. State that a null adapter, rejected device, or software adapter completes those requirements by recording WebGPU as unqualified. Keep ELM-GPU-001 as the must for some non-WebGPU hardware path in the selected host. Make ELM-QA-024’s hardware-acceleration half `must`, and leave only the WebGPU half conditional.
- Blocks implementation admission: **Yes** for P1 host selection.

### GRK-D-005 — The budget gate can pass on one filled-in row

- Severity: high
- Requirement IDs: ELM-QA-021, ELM-QA-022, ELM-GPU-008, ELM-GPU-010, ELM-REN-021
- Artifact: `ROADMAP.md` “Performance qualification”; `elm-performance` scenario `qa-021`; `GPU.md` “Preview import and copy budget”
- Defect: ELM-QA-021 says freeze numeric absolute and regression budgets before host selection. The only scenario blocks selection when “a budget lacks a measured baseline.” A `budgets.json` that freezes startup p50 and leaves idle, desktop-entry refresh, reversible motion, output transfer, soak, power, and copy bytes unset still passes. ELM-GPU-010 then compares profiles “against frozen latency, memory, power and transfer budgets” that QA-021 never requires to exist. ELM-GPU-008 records copies and does not require a threshold. The roadmap’s workload list is not a requirement.
- Correction: Add a requirement whose absence fails P0. Suggested EARS: **The performance owner SHALL publish `budgets.json` containing, for cold startup, idle taskbar, desktop-entry refresh, switcher open, switcher navigation, minimized preview, capture-to-first-frame, reversible motion, output transfer, and whole-tree soak, the measured baseline, unit, sample count, hardware identity, refresh rate, one numeric absolute threshold, and one numeric regression threshold for CPU, wakeups, resident memory, private memory, and missed frames, plus a numeric cross-GPU copy-byte threshold, and the host selector SHALL reject a candidate while any of those fields is absent.**
- Blocks implementation admission: **Yes** for host selection and preview performance claims. Measuring the numbers at P0 is still the right open experiment.

### GRK-D-006 — 64-bit identities have no requirement

- Severity: high
- Requirement IDs: ELM-ARC-005, ELM-ARC-006, ELM-ARC-010, ELM-ARC-013; prose only in `ROADMAP.md` “Architecture and data flow”
- Artifact: `ROADMAP.md` paragraph beginning “Publish coherent native snapshots”; `contributions/architecture.md` “Protocol design”
- Defect: The roadmap says to specify numeric encoding for 64-bit identities and clocks, queue limits, resynchronization, timeouts, and rejection codes before the transport. No requirement says that. JSON numbers cannot represent every integer above 2^53. Two incarnations that differ only in the high bits become equal, ELM-ARC-006’s revision check passes, and the stale effect is applied. The same hole swallows an absolute monotonic deadline (ELM-ARC-013, ELM-REN-008).
- Correction: Suggested EARS: **The bridge SHALL encode every identity, generation, revision, and monotonic deadline as a lossless canonical field, SHALL reject a numeric JSON value for those fields, and SHALL publish the queue byte cap, item cap, resync rule, timeout, and rejection-code table in the same versioned schema before the first host spike sends an effect.**
- Blocks implementation admission: **Yes** for the bridge and any effect that carries identity or a deadline.

### GRK-D-007 — Lock and capture authorization are missing on the mandatory path

- Severity: high
- Requirement IDs: layer policy is only in `LAYERING.md` “Layer policy to freeze in P0”; capture consent is ELM-REN-027 (`conditional`, P8). Related but insufficient: ELM-ARC-011, ELM-DEL-010, ELM-DEL-011, ELM-DEL-017, ELM-KDE-005
- Artifact: `LAYERING.md` row “Lock/security surfaces”; `elm-native-compositor` ELM-REN-027; KWin `findToplevel` lines 3444–3472, which does filter lock-screen hits in the reference and is not copied into a product requirement
- Defect: A keyboard-interactive layer surface can remain above the lock screen, and the shell can lease another client’s pixels, including a password dialog, because nothing in the 181 requirements forbids it. ELM-DEL-011 rejects shell commands and, in the EARS only, filesystem paths. The scenario never sends a path or a window id. ELM-DEL-017 keeps pixels out of logs after they have been captured. Portal consent exists only if the optional compositor is selected. ELM-ARC-011 journals modifier, repeat, release, and Escape before the view is ready and never says other keystrokes are discarded. A password typed during startup can enter the Elm replay log. ELM-DEL-010’s only scenario is a different Unix user. A same-user process that presents a UID and no session credential is untested.
- Correction: Add these requirements, and do not treat them as recommendations:
  - **WHEN the session lock is engaged, the shell SHALL drop keyboard interactivity and hit eligibility on ordinary shell surfaces, and SHALL NOT paint or lease lock-screen pixels.**
  - **The broker SHALL mint a preview lease only for a window in the authenticated session that shell policy may preview, and SHALL refuse lock-screen, credential-entry, and cross-session surfaces.**
  - **WHEN the host journals input before frontend readiness, it SHALL retain only the declared chord events and SHALL NOT retain any other keystroke.**
  - Split ELM-DEL-011 so arbitrary filesystem paths are their own scenario, and add a same-UID, wrong-session refusal to ELM-DEL-010.
- Blocks implementation admission: **Yes** for layer-shell keyboard focus and for preview leases.

### GRK-D-008 — Two release scenarios accept failure, and one launcher scenario rejects success

- Severity: high
- Requirement IDs: ELM-ARC-023, ELM-UX-035, ELM-UX-029, ELM-GNO-006
- Artifact: `elm-host` scenario `architecture-023`; `elm-shell-experience` scenarios `ux-035` and `ux-029`; `elm-layering` scenario `gnome-layering-006`
- Defect:
  - ELM-ARC-023 SHALL pass IME, keyboard navigation, Orca, braille, clipboard, drag-and-drop, fractional scale, and negative coordinates. The THEN is “each named route has native evidence or blocks release.” Clipboard can be untested while release is blocked for any other reason, and the only scenario still passes.
  - ELM-UX-035 SHALL release only after original campaigns pass. The THEN is that 38/34, pin, 52 drag/resize, and surface scenarios “have explicit results.” A ledger of failures satisfies the scenario.
  - ELM-UX-029’s THEN is “one request occurs and refused launch displays an error.” One run cannot both succeed and be refused. A correct single launch fails the only scenario.
  - ELM-GNO-006 THEN allows the wrong window to take the click “unless a recorded native exception applies,” and the exception can be written after the click.
- Correction: Split each conjunct into its own requirement and scenario. ARC-023’s THEN becomes “each named route has a passing native result on the frozen tuple.” UX-035’s THEN becomes “each mapped original campaign result is pass on that tuple.” UX-029 becomes two scenarios, one accepted launch and one refused launch. GNO-006 names the exception in the GIVEN, or the exception is a failure.
- Blocks implementation admission: **Yes** for the host-compatibility gate, the shell release gate, and the launcher gate.

### GRK-D-009 — Native layering waits on the webview, and the P1 IME test requires the P5 launcher

- Severity: high
- Requirement IDs: ELM-LAY-001, ELM-GNO-002, ELM-KDE-004, ELM-UX-028, ELM-UX-012, ELM-UX-025
- Artifact: `ROADMAP.md` phase table P1 and P2 (“P1 transport before native effects”) and decision “Correct active native layering independently”; `design.md` decision 1; `elm-accessibility` scenario `ux-028`
- Defect: The Heroic failure is current Hyprland eligibility, not an Elm port. Its requirements are P2, and P2 native effects wait on the P1 host. A failed or slow WebKit-versus-Qt spike blocks the compositor fix the design says to do independently. Separately, ELM-UX-028 is P1 must, and its only GIVEN is “launcher search has focus.” The launcher requirement ELM-UX-029 is P5. P1 cannot pass the written scenario until the P5 surface exists, or a dummy field passes the behavior and fails the scenario text. ELM-UX-025 has the same shape for taskbar and switcher, which the roadmap does not deliver until P3.
- Correction: Put the Hyprland eligibility fix in a phase whose only dependency is the P0 policy table. Keep Elm’s projection of that scene in P2. Change the UX-028 GIVEN to “a minimal shell text field on the candidate host,” and point UX-025 at that same spike’s taskbar and switcher roles, or move those requirements to the phase that first builds the surfaces.
- Blocks implementation admission: **Yes** for sequencing. It does not require the host choice itself to be decided in this audit.

### GRK-D-010 — Inherited native failures are not executable or hash-pinned

- Severity: high
- Requirement IDs: ELM-QA-001, ELM-QA-002, ELM-REN-001, ELM-REN-016, ELM-REN-018, ELM-DEL-001, ELM-UX-035
- Artifact: `BASELINE.md` “The immutable handoff”; `docs/HANDOFF.md` lines 46–61 and 99–103; `generation.json` inputs, which do not include `docs/HANDOFF.md`
- Defect: QA-002 requires a one-to-one map of 38 restore, 34 fault, and 52 drag/resize/reload cases. The frozen packet and the handoff section name the counts and do not list the case oracles or their hashes. HANDOFF is outside the manifest, so a later edit changes the obligation with no packet diff. The known B11 defect is specific: Bv4 failed because QA treated `allows_input=false` as an input blocker, and B12 was not run. ELM-REN-016’s only scenario is pin then unpin. Its task mentions B11–B24, and ELM-REN-018’s verification says to distinguish blockers from `allows_input`, but neither scenario forbids the false premise. An implementation can repeat B11 and pass `ren-016`.
- Correction: At P0, freeze the ancestor path and SHA-256 inside the ledger before any derivative is accepted. Add a scenario per inherited predicate, including: **WHEN a window reports `allows_input=false` and no separate native blocker is set, the authority SHALL NOT treat that flag as a no-focus blocker.** Keep B12 and B13–B24 as named scenarios, not a range in a task sentence. This P0 freeze is required work, not an unresolved product choice.
- Blocks implementation admission: **Yes** for any claim that inherited campaigns are preserved. New Elm view work can be drafted beside it, but it cannot be accepted against those campaigns.

## Medium

### GRK-D-011 — One scenario is being used as a whole requirement

- Severity: medium
- Requirement IDs: ELM-ARC-002, ELM-ARC-004, ELM-ARC-007, ELM-ARC-015, ELM-QA-008, ELM-QA-010, ELM-QA-019, ELM-DEL-015, ELM-UX-010, ELM-UX-015, ELM-UX-018, ELM-UX-028, ELM-REN-014
- Artifact: each requirement’s single `scenarios` array; contributions that call these “atomic EARS”
- Defect: The sentences bind several outcomes, and the scenario exercises one. Counterexamples: ELM-ARC-007 names Pending, Committed, Refused, Cancelled, and Unknown, and only proves Unknown is not Committed. ELM-ARC-004’s task says both trust boundaries, and the scenario only injects into the host. ELM-QA-010 names four protections and only proves two campaigns cannot overlap. ELM-DEL-015 requires atomic writes, and the scenario is a finished upgrade, so a crash during the write is untested. ELM-UX-010 requires recent-item actions, and the scenario only counts two catalog actions. ELM-UX-015 THEN is “native modal target or terminal activates,” so selecting the terminal and focusing Brave still passes. ELM-UX-018 THEN requires both an accepted transfer and a refusal in one result. ELM-UX-028 requires cancellation, and the scenario only commits. ELM-REN-014 EARS allows a labeled partial capture; the scenario requires recorded bounds to match covered pixels, so an honestly labeled client-only preview fails.
- Correction: Split each AND, OR, and WHILE/IF pair into one EARS requirement and one scenario. Where a behavior is intentionally out of scope, say so in the requirement rather than leaving it only in the task sentence.
- Blocks implementation admission: **Yes** for using these scenarios as the sole acceptance oracle. It does not block writing the code those scenarios already describe.

### GRK-D-012 — Three published effort tables disagree, and P1 is 30 musts inside 2–4 weeks

- Severity: medium
- Requirement IDs: ELM-DEL-002
- Artifact: `ROADMAP.md` phase table (P0–P6 sums to 19–36 engineer-weeks; P1 is 2–4; P8 is 20–50+); `contributions/architecture.md` “Stages, dependencies and deliverables” (P0–P6 called 24–48; P1 is 4–8; P8 is 26–78+); `contributions/rendering.md` phase table (P1 is 3–6; P4 is 6–12; P6 is 4–8; P8 is 40–100+); `contributions/delivery.md` “Effort and user acceptance,” which repeats 19–36
- Defect: Nothing says which table wins. `generation.json` counts 30 P1 requirements and 39 P2 requirements. The roadmap’s 2–4 week P1 includes two host spikes, CSP, offline assets, GPU qualification, the QA preflight, an accessibility bridge, and IME. DEL-002’s scenario passes if both tracks merely “have separate costs,” even when the costs conflict. Unnamed staffing roles are not the defect. The roadmap already says the roles are not six assigned people.
- Correction: Declare `ROADMAP.md` the only effort ledger, mark contribution tables as superseded, and make DEL-002 fail when two normative tables differ. Re-estimate P1 and P2 from the requirement counts at P0 before host work starts.
- Blocks implementation admission: **Yes** for ELM-DEL-002 / P0 plan acceptance. It does not require a headcount decision in this audit.

### GRK-D-013 — The diagram and one feasibility scenario disagree with the phase table

- Severity: medium
- Requirement IDs: ELM-ARC-028, ELM-QA-027; P5 dependencies in the roadmap table
- Artifact: `ROADMAP.md` mermaid diagram (`P4 --> P5`, `P1 --> P7`, `P2 --> P7`) versus the P5 row “P3; previews/motion depend on P4” and the P7 row “independent of shell release”; scenario `architecture-028` GIVEN “shell parity accepted”
- Defect: The drawing holds launcher, settings, and menus until capture/motion finishes, adding the whole P4 range to work the table says can start after P3. The P7 scenario cannot start until shell parity is accepted, while the diagram starts P7 after P2. “Independent” correctly means the shell does not wait for the compositor. It does not say feasibility waits for P6.
- Correction: Make the diagram match the table. Change the ARC-028 GIVEN to “P1 and P2 evidence and a separate scope decision exist.” Keep main-session replacement behind ELM-QA-028.
- Blocks implementation admission: **No** for coding, **yes** for treating the diagram as the schedule.

### GRK-D-014 — Traceability does not carry owners, and several evidence paths do not resolve

- Severity: medium
- Requirement IDs: ELM-QA-016, ELM-KDE-001 through ELM-KDE-009
- Artifact: `TRACEABILITY.md` columns (no owner); KDE legacy paths such as `docs/elm-roadmap/reference/kwin/layers.cpp` and `input.cpp`; `validation.json` `errors: []`
- Defect: QA-016 requires every requirement to map to an owner. The matrix has no owner column, and the passing validator does not look for one. The cited `layers.cpp`, `input.cpp`, and `windowitem.cpp` are not the files on disk. The readable copies are `src__layers.cpp`, `src__input.cpp`, and `src__scene__windowitem.cpp`, plus the historical and upstream trees. Mutter citations that use the `src__core__window.c` form do resolve.
- Correction: Add the workstream owner required by QA-016, point KDE evidence at the real relative paths, and fail validation on a missing owner or a legacy path that does not exist. Leaving the person unnamed until P0 staffing is acceptable. Leaving the column absent is not.
- Blocks implementation admission: **Yes** for claiming the planning verifier already passed QA-016.

### GRK-D-015 — Release and accessibility obligations never became requirements

- Severity: medium
- Requirement IDs: none for suspend/resume (prose in `ROADMAP.md` “Release and operation”); ELM-UX-023 omits surfaces that `contributions/experience.md` “UX acceptance and fixture matrix” names; ELM-QA-010 cites “five” protections; ELM-QA-019 versus ELM-UX-026
- Artifact: `ROADMAP.md` release paragraph; `experience.md` keyboard list; `HANDOFF-codex-window-qa.md` “Please change” and “Don’t”; phases on ELM-QA-019 (P5) and ELM-UX-026 (P6)
- Defect: Suspend/resume is a before-release check with no requirement. ELM-REN-025 covers it only for the optional compositor. ELM-UX-023’s keyboard set omits the notification center and jump lists, which the experience contribution includes. QA-010 says “all five crash-handoff protections” and does not list them. The handoff’s fifth change is unsandboxed compositor launch, and the “Don’t” clause forbids reverting the crash-watch override, grim, and gnome-keyring builds. Those two are not requirements. QA-009, QA-010, and QA-011 cover socket, core limit, Xwayland, DRM, serialization, and teardown only. QA-019 requires braille at P5. UX-026 requires it at P6, so the phase exits disagree. QA-019’s one scenario is a single popup plus IME, not each shell surface.
- Correction: Add: **WHEN the machine resumes from suspend, the shell SHALL invalidate output and renderer generations, reconcile one fresh snapshot, and SHALL NOT replay mutating intents that were in flight.** Extend ELM-UX-023 to notification center and jump lists. Replace “five protections” with five explicit requirements plus **The QA harness SHALL NOT revert the crash-watch override, the grim build, or the gnome-keyring build.** Put braille on one phase. Add one AT name/role scenario each for launcher, Task View, snap chooser, menus, settings, notifications, and jump lists.
- Blocks implementation admission: **Yes** for P6 release qualification and for calling accessibility complete. These are uncovered obligations already stated by the plan, not new product ideas.

### GRK-D-016 — ARC verifiers demand a failure injection the scenario does not define

- Severity: medium
- Requirement IDs: ELM-ARC-001 through ELM-ARC-029
- Artifact: every ARC `verification` string and the matching `tasks.md` “Verify:” clauses
- Defect: Each one ends with “failure injection and artifact hashes included.” ELM-ARC-001 is a manifest of versions and hashes. There is no fault to inject. A faithful manifest fails the written verifier, or an unrelated injected fault is attached and the task is marked done.
- Correction: Keep hashes on every ARC gate. Attach “failure injection” only to ARC-004, ARC-006, ARC-009, ARC-012, ARC-014, ARC-025, and the other requirements whose scenario is a fault.
- Blocks implementation admission: **Yes** for closing ARC tasks as written. It does not block the underlying behavior.

### GRK-D-017 — A software webview can pass the hardware-acceleration gate

- Severity: medium
- Requirement IDs: ELM-GPU-001, ELM-GPU-002, ELM-DEL-026, ELM-DEL-027
- Artifact: `elm-gpu` scenario `gpu-001`; `GPU.md` “Three different acceleration layers”
- Defect: GPU-001 fails only “software-only execution.” A host whose webview is deliberately software, while a native Vulkan preview path uses the NVIDIA device, is not software-only. GPU-002 correctly separates discovery, native GPU, webview composition, and WebGPU, but GPU-001’s pass line does not require the webview row to be hardware.
- Correction: Suggested EARS: **The host selector SHALL admit a candidate only when the shell webview’s own backend is a nonsoftware device on the frozen tuple, recorded separately from native preview composition and from WebGPU.**
- Blocks implementation admission: **Yes** for the accelerated-host claim. It does not pick WebKit or Qt.

## Low

### GRK-D-018 — 240 Hz is priority must on a conditional requirement

- Severity: low
- Requirement IDs: ELM-REN-021
- Artifact: `elm-capture-motion` ELM-REN-021 (`pattern: complex`, `priority: must`, phase P6)
- Defect: The EARS correctly starts with “WHERE 240 Hz hardware is available.” The priority says `must`. A release review can demand a 240 Hz packet from a panel that is not 240 Hz. The inventory records GPUs and no refresh rate.
- Correction: Set priority to `conditional`. Record the output modes in the P0 hardware sheet. Absence of a 240 Hz panel is an explicit skip, not a pass and not a P6 failure.
- Blocks implementation admission: **No**, after the priority field is corrected.

## Recommendations, not admission blockers

These are not failed user requirements. The plan correctly bounds Windows parity to an explicit inventory.

- Magnification, sticky keys, switch access, and color-vision themes are not in the accessibility set. Add them only if the P0 inventory ELM-UX-001 signs them in.
- HDR, variable refresh, and color management are already deferred to an explicit P7 scope decision in `contributions/rendering.md`. Leaving them out of the mandatory shell is consistent.
- Theme coverage is thin but present: ELM-UX-027 is contrast and text scale, and ELM-UX-030 persists a theme value. Enumerating tokens can wait for the settings schema.
- Unnamed engineers are an open staffing fact. ELM-DEL-002 should record roles and ranges, which the roadmap already distinguishes from headcount.

## Coverage strengths

- All 181 registry rows have a phase, a task id, one OpenSpec scenario, and a verification string. Capability counts in `generation.json` sum to 181. The sampled specs match the registry text for GPU, accessibility, performance, and the layering section that was read.
- The plan separates Elm policy, native surface lifetime, and native effect authority, and it refuses to treat a reducer, `Cmd.batch`, or a DOM callback as presentation proof (ELM-ARC-008, ELM-ARC-020, ELM-REN-022).
- Hyprland stays the mandatory compositor. P8 cannot inherit a Hyprland pass (ELM-QA-028). That split is sound. The open substrate choice is not a hole.
- GPU.md matches `gpu-inventory.json`: Intel Arrow Lake-S on Mesa 26.2.2 and NVIDIA RTX 5090 Laptop GPU at driver 615.71.09, Vulkan instance 1.4.357, WebKitGTK 2.52.6. The inventory is labeled as discovery only. WebGPU is not inferred from Vulkan.
- The Heroic note is honest: `atomicSnapshot` is false, the screenshot is earlier than the client sample, and `visible` / `acceptsInput` are not the hit path.
- The Mutter claim that was checked is true. In the pinned 49.0 `window.c`, above-state maps to `META_LAYER_TOP` only when the window is not maximized (line 6414), and a dock on a fullscreen monitor maps to `META_LAYER_BOTTOM` (lines 6420–6421). The KWin claim that was checked is true: `findToplevel` walks the published stack from the top and skips deleted, other activity or desktop, minimized, hidden, show-desktop, and not-ready windows, and it restricts hits while the screen is locked (lines 3455–3473).
- Inherited evidence is not laundered in the narrative. BASELINE and the verification contribution keep B14, B11, the seven-case MAX result, V29 CPU tests, and the 503 named Quint scenarios in their original scopes.
- Release mechanics that are actually specified are concrete: user-owned paths and no `/usr/share/omarchy` (ELM-DEL-008), exact plugin ABI refusal (ELM-ARC-025, ELM-DEL-022), offline recovery without a compositor restart (ELM-DEL-020), interrupted-upgrade boundaries (ELM-DEL-019), settings downgrade without guessing a newer schema (ELM-DEL-016), and separate CPU, replay, fuzz, native, hardware, and accessibility columns (ELM-QA-005).
- Protected QA constraints that did become requirements match the handoff: parent socket, 0700 runtime, core limit 1, no incidental DRM fallback, serial campaigns, ordered teardown, and no main-session restart (ELM-QA-009 through ELM-QA-013).

The revision that admits implementation is: partition `tasks.md`, close the high findings’ scenarios and missing EARS, and leave the host, copy-path, and compositor go/no-go decisions as the gated experiments they already are.
