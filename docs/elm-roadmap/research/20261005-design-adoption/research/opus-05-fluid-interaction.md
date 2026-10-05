# Fluid interaction review: latency, presentation, motion and backpressure (opus-05-fluid-interaction)

This is a research draft. It does not accept anything, change any requirement or check any task. I read the frozen inputs, browsed the external sources myself, ran no agents, and did not read the other reviewers' reports.

## 1. Current-design findings

I label each finding as **implemented** (what the frozen source does, read but not run), **obligation** (already required by the baseline) or **gap** (acceptance not yet shown).

**F1. Effect receipts and presentation receipts are kept apart.** *Obligation.*
- The architecture says commit never proves displayed pixels (`inputs/docs/elm-roadmap/ARCHITECTURE.md:186`). Native per-frame work never waits on Elm (`ARCHITECTURE.md:188`).
- Requirements ELM-ARC-020 (`REQUIREMENTS.md:1317`) and ELM-REN-022 require independent evidence of presentation.
- *Gap:* nothing in the source asks for compositor presentation feedback. The native hosts only use `g_get_monotonic_time()` and GLib timeouts (`inputs/implementation/elm-preview-shared-bridge-v509/native/host.c:826-859`, `shared-host.c:465-488`). ELM-QA-022 asks for "input-to-present" samples (`REQUIREMENTS.md:1535`), but nothing says how a sample is split into stages or which clock each stage uses.

**F2. Native input proofs start their clock when the GTK handler runs, not at the input event.** *Implemented.*
- The context-menu proof records `.captured=g_get_monotonic_time()` at handler time (`native/shared-context.h:85,98,108`) and accepts proofs up to 500000 µs old (`:131`).
- The event's own timestamp (`key->time`) is printed only in QA mode (`:75`).
- The Wayland core protocol defines input `time` as "timestamp with millisecond granularity" from an undefined base (`/usr/share/wayland/wayland.xml:1029,2251`). So any delay before the handler runs is invisible to the "original start event" rule (`ARCHITECTURE.md:229`).

**F3. Frontend deadlines still use JavaScript timers.** *Implemented; already tracked under W05.*
- `Process.sleep 2000/2000/10000` (`src/Main.elm:36-38`).
- This duplicates findings 01-03/05-05 (`FRP-ELM-WORKPLAN.json`, W05). I make no new proposal here.

**F4. Only one window transaction can be in flight; extra input is dropped without feedback.** *Implemented.*
- `Effects.apply` refuses "Operation already pending" (`src/Effects.elm:90`). `Shell.available` is false while anything is pending or the phase is not `Ready` (`src/Shell.elm:67`).
- A primary click or picker choice while unavailable returns `(model,[])` (`src/TaskbarShell.elm:77,92`). Nothing is recorded or shown.
- The safety side is right: nothing is queued or replayed. The user-facing cost is a silent no-op.

**F5. A native refresh notification closes an open picker.** *Implemented; how often it happens is not measured.*
- `host-refresh` → `notificationRefresh` → `refresh` sets `phase = Reconciling` (`Shell.elm:60,160-162,295-299`).
- `TaskbarShell` then clears the picker whenever `available` is false (`TaskbarShell.elm:42`).
- Picking from the picker adds another projection round trip and arms a 2 s JS timer before the action is sent (`src/Desktop.elm:155-168,222-224`). The architecture separates global scene revisions from dependency revisions (`ARCHITECTURE.md:219`), but the frontend gates on one global phase.

**F6. Notification refresh is coalesced correctly, but preview demand is not.** *Implemented.*
- A single dirty bit bounds notifications and only drains on admitted responses (`Shell.elm:301-309`). This is good.
- Preview `Request` is admitted only when capture is idle and nothing is cancelling or retiring (`src/PreviewLifecycle.elm:258`). Anything else returns `base` and is not remembered, so a content change that arrives during a capture can be lost (the full mechanism is in FI-04).

**F7. The preview label treats any newer content as "historical".** *Implemented.*
- `Live` requires the frame's scene and content revisions to equal the current scope (`PreviewLifecycle.elm:142`). Any later root-surface commit relabels a still-live window "Historical preview" (`:366`).
- ELM-UX-006 uses "historical" for minimized windows (`REQUIREMENTS.md:2059`). The S09 gate requires labels to "match actual source state" (`REMAINING-WORK-EARS.md:17`).

**F8. A new preview replaces the old one before it has loaded.** *Implemented; visual effect unmeasured.*
- Accepting a new frame retires the old accepted lease straight away (`PreviewLifecycle.elm:207,270`).
- The view keys the `img` by handle (`:371`), so the old element is removed before the new image is decoded. W06 already says "image load distinct from physical presentation" (`FRP-ELM-WORKPLAN.md:64`).

**F9. Prototype capture runs synchronously on the compositor thread.** *Implemented, prototype route.*
- `captureOwnedPlane` does a synchronous `glReadPixels` of the full monitor plane, then a PNG encode (`elm-preview-source-authority-v492/native/preview_capture.hpp:39-65`). The authority refuses work off its owner thread (`native/authority.cpp:447`).
- Recorded capture times were 24.55 ms and 22.72 ms (`FRP-ELM-WORKPLAN.md:243,268`).
- Whether this caused missed compositor frames was never measured. The 128 MiB / two-item cap is explicitly a prototype bound (`:256`).

**F10. Motion, reversal and reduced motion are well specified but unimplemented.**
- ELM-REN-010/011, ELM-UI-014/018 and ELM-UX-022 cover them, and W12 is queued (`FRP-ELM-WORKPLAN.md:69`). No motion or CSS animation exists in the frozen source (grep found no transitions or `prefers-reduced-motion`).
- Two things are undefined: where the system reduced-motion preference comes from, and whether reversal starts from the "last presented" or the "last sampled" geometry.

**F11. Budgets are not frozen.**
- ELM-QA-021/ELM-REV-020/ELM-REV-021 require a versioned `budgets.json` (`REQUIREMENTS.md:1525`). INTERACTION also leaves the feedback and quiescence thresholds unfrozen (`INTERACTION.md:41`).
- `Shell.status` shows "Applying window change…" as soon as an action is pending (`Shell.elm:73`), with no threshold yet.
- Because nothing is frozen, I give no numbers below. Every threshold refers to the budget contract plus a task to freeze it.

## 2. Sources (retrieved 2026-10-05)

| ID | Source | Claim relied on | Limitations |
|---|---|---|---|
| A1 | Shneiderman, "Direct Manipulation: A Step Beyond Programming Languages," *IEEE Computer* 16(8), 1983. [Author PDF](https://www.cs.umd.edu/users/ben/papers/Shneiderman1983Direct.pdf), pp. 64–65 | Principle: "Rapid, incremental, reversible operations whose impact on the object of interest is immediately visible." Benefit: users "can immediately see if their actions are furthering their goals, and if not, they can simply change the direction of their activity." | Conceptual essay. No latency numbers and no asynchronous authority. Supports immediate feedback and reversal, not optimistic commit. |
| A2 | Casiez, Conversy, Falce, Huot, Roussel, "Looking through the Eye of the Mouse," UIST 2015, DOI 10.1145/2807442.2807454. [Author PDF](http://direction.bordeaux.inria.fr/~roussel/publications/2015-UIST-mouse-based-lagmeter.pdf), pp. 629–631 | Defines end-to-end latency as action → on-screen feedback. Probes can be inserted "at different levels of the system" on a common clock. Latency "is affected by the operating system and system load," with toolkit and browser differences. Its related-work summary: about 50 ms hurts mouse pointing; jitter of 20–40 ms is likely noticed. | 2015 systems. The thresholds are second-hand summaries, **not budgets** here. I read only the first three pages. |
| A3 | Heer & Robertson, "Animated Transitions in Statistical Data Graphics," IEEE TVCG (InfoVis) 2007. [Author PDF](https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf), pp. 1–3 | Animation is "a double-edged sword." Too slow "may prove boring or degrade task times," too fast "may result in increased errors," and "optimal times may be hard to predict." Marks for specific data points "should not be reused to depict different data points across a transition." | About charts, not window management. Supports measuring durations rather than choosing them, and object constancy. |
| O1 | wayland-protocols `stable/presentation-time/presentation-time.xml` (wp_presentation v2). Read from the installed copy `/usr/share/wayland-protocols/stable/presentation-time/presentation-time.xml:126-265`; upstream [GitLab](https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/main/stable/presentation-time/presentation-time.xml) blocked me with Anubis. | Feedback is "presented" (light first emitted, plus refresh, retrace counter `seq` and flags `vsync`/`hw_clock`/`hw_completion`/`zero_copy`) or "discarded" ("never displayed"). Software clock sampling is "not acceptable" for `hw_clock`. | Package version not recorded; pin the upstream commit. Hyprland's support for this on the selected layer-shell/WebKit surfaces has not been checked. |
| O2 | Wayland core `wayland.xml`, `wl_surface.frame` and input event `time`. Installed copy `/usr/share/wayland/wayland.xml:1628-1662,1029,2251` | Frame callbacks throttle redraw so "a client will not send excessive updates." The server "should avoid signaling" them when the surface is not visible. Input `time` is millisecond granularity with an undefined base. | Same version caveat as O1. |
| O3 | `unstable/input-timestamps/input-timestamps-unstable-v1.xml` (installed copy) | High-resolution input timestamps are "in the same clock domain" as the core input event timestamp. | Experimental. Compositor support not confirmed. |
| O4 | hyprutils, [`AnimatedVariable.hpp`](https://raw.githubusercontent.com/hyprwm/hyprutils/main/include/hyprutils/animation/AnimatedVariable.hpp) (main branch) | Setting a new goal does `m_Begun = m_Value` and keeps spring velocity scaling (`SPRINGVELOCITYSCALE`). Retargeting starts from the current **sampled** value. | Moving branch, not pinned to the owning ABI tuple. "Sampled" is not the same as "presented." |
| O5 | GTK, [GdkFrameClock (GDK 3)](https://docs.gtk.org/gdk3/class.FrameClock.html) | Paint phases are synced to refresh; painting can stop when frames will not be visible. Frame time is "not the same as g_get_monotonic_time()." Frame timings record presentation times. | Docs only. Whether GTK3 on Wayland fills presentation times for this host is unverified. |
| O6 | xdg-desktop-portal, [Settings](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html) | `org.freedesktop.appearance` key `reduced-motion`: 0 = no preference, 1 = reduced; unknown values are treated as 0. Changes arrive via `SettingChanged`. | The portal backend on Omarchy/Hyprland is unverified. |
| O7 | WebKitGTK, ["2.54 highlights"](https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html) (2026-09-16) | `prefers-reduced-motion` "now follows the dedicated reduced-motion setting introduced in GNOME 50." | Release notes. The WebKitGTK version in the owning tuple is unknown. |

For two papers I found only DOI or listing pages and no author-hosted text: Ng et al. UIST 2012 and Jota et al. CHI 2013. I do not cite them for any claim.

## 3. Adoption proposals (all drafts, all tasks unchecked)

### FI-01 (P0): Staged latency trace with classified presentation evidence

**Reason.** A1 and A2 tie fluid interaction to the time between action and visible effect. A2 shows the time must be split by probes on one clock to find where it comes from. ELM-QA-022 asks for input-to-present samples but does not define the stages (F1, F2).

**Requirement.** Each sampled interaction records these stages, each with its clock domain:
1. native input event time;
2. host dispatch;
3. Elm update/port emission;
4. authority admission and commit receipt;
5. compositor presentation outcome, with O1 flags or `discarded`.

Stages from different clocks are joined only through a measured mapping (as ELM-REN-005 does). A `discarded` or missing feedback never counts as presented. Software-sampled timestamps are labeled as such and are not presented as hardware-timed.

**Implementation choices (separate from the requirement).**
- wp_presentation feedback on the shell surface (O1), with input-timestamps where the compositor offers them (O3).
- A small photodiode or optical-mouse calibration run on part of the samples (A2), as the independent presentation evidence ELM-REN-022 needs.
- Instrumentation is off in release builds, and its overhead is reported (ELM-QA-022).

**Mapping.** Refines ELM-QA-022, ELM-REN-005, ELM-REN-022, ELM-ARC-020 and ELM-REV-021 (S02/S04/S16). Feeds W08 ("native presentation timing") and W05 (where the original start event comes from). It is a refinement, not a duplicate: no current requirement defines the stage split or how evidence is classified.

**Validation.**
- Trace completeness ratio per workload.
- Distribution of hardware-calibrated minus software presented timestamps.
- Count of `discarded` outcomes.
- Freezing task: S02 adds the trace schema, an acceptable calibration tolerance and a completeness floor to `budgets.json` before any host is compared.

**EARS.** WHEN a qualified latency sample is recorded, the performance verifier SHALL attribute each stage from native input to compositor presentation to a declared clock domain or measured mapping, and SHALL classify presentation evidence by its native feedback kind, excluding discarded or absent feedback from presented samples.

#### Scenario: FI-01 superseded-frame
- GIVEN an activation whose first shell repaint is superseded before scanout
- WHEN the compositor reports `discarded` for it and `presented` for a later commit
- THEN the input-to-present sample ends at the later presented commit, and the discarded commit is recorded as such

#### Scenario: FI-01 software-clock (negative)
- GIVEN presentation feedback without the `hw_clock` flag
- WHEN the budget report aggregates latency
- THEN those samples are labeled software-timed and cannot satisfy a hardware-presentation gate on their own

#### Scenario: FI-01 dispatch-delay
- GIVEN a native input event delayed behind host main-loop work
- WHEN its context proof is evaluated
- THEN the trace shows event-to-dispatch delay as its own stage, and the original-deadline rule names which timestamp it uses

### FI-02 (P0): Preview capture must not starve native presentation

**Reason.** F9: the prototype does synchronous readback and encode on the compositor owner thread. O2 says frames should not be wasted, and O5 shows paint is scheduled to refresh. A capture that blocks the compositor loop may delay every output's frames, including the motion that ELM-REN-021 measures. Nobody has measured whether it does.

**Requirement.** Each capture/export route is measured for its effect on compositor presentation on every active output: missed refresh cycles from gaps in O1 `seq`, and presentation delay against the same workload without capture. A route that exceeds its frozen budget is rejected in favor of a qualified route or an explicit unavailable state. This is the same rule ELM-REV-022 already applies to import cost.

**Implementation choices.**
- Asynchronous readback with fences.
- Moving encoding off the compositor thread on an independently owned copy.
- Cropping to the window instead of the monitor plane.
- Pacing capture so it runs only after the consumer has presented.

Each needs its own primary-source check. I could not fetch the Khronos PBO documentation (HTTP 403).

**Mapping.** Refines ELM-REV-022, ELM-REN-012, ELM-QA-023 ("missed frames") and ELM-UI-017 (S11/S16). Extends W06 and the unfinished provider (Provider519). This is a new measured obligation on capture work; the import-route rule already exists.

**Validation.**
- Presentation-gap counts and latency distributions while captures repeat, compared with a no-capture baseline, on the hardware tuple.
- Freezing task: add a "capture-induced presentation impact" row to the ELM-REV-020 matrix.

**EARS.** IF a preview capture or export route causes compositor presentation gaps or delay beyond its frozen budget on any active output, THEN the preview qualification SHALL reject that route and preserve a qualified native route or an explicit unavailable preview state.

#### Scenario: FI-02 motion-during-capture
- GIVEN restore motion is active on output A and a preview capture is requested for a window on output B
- WHEN the capture runs
- THEN output A's presentation-gap and latency samples are recorded and compared with the frozen capture-impact budget

#### Scenario: FI-02 over-budget-route (negative)
- GIVEN a route whose measured capture impact exceeds the frozen budget
- WHEN host qualification evaluates it
- THEN the route is rejected, and the picker shows the documented unavailable state rather than a stale substitute

### FI-03 (P1): Observation refresh must not collapse interaction or silently discard input

**Reason.** F4 and F5. A1: users must see whether an action took effect. Silently ignoring a click, or closing the picker under the pointer because an unrelated refresh arrived, breaks that. `ARCHITECTURE.md:219` already says unrelated scene changes must not block stable dependencies.

**Requirement.**
- While a refresh is in flight and the picker's dependency revision has not changed, the picker stays presented. Its actions show the pending state; they are not removed.
- Every input that arrives while actions are unavailable produces a correlated, accessible "not accepted" result with a reason (pending, reconciling, stale scope).
- No such input is queued, deferred or replayed later.

**Implementation choices.**
- A typed `InputNotAccepted reason` message in the one controller.
- A per-dependency gate instead of the global `phase == Ready` gate.
- Announcement routing through the single W08 announcement owner.

**Mapping.** Refines ELM-UI-015 ("independent controls usable"), ELM-UI-011, ELM-TEA-004 and ELM-ARC-015, and the S07 gate "delayed/refused outcomes". Shares paths with W07 and W09, so it integrates serially in the GUI lane. It is a frontend refinement of `ARCHITECTURE.md:219`.

**Validation.**
- Replay: unrelated `host-refresh` while the picker is open → picker identity and focus unchanged.
- Each click during non-availability gives exactly one not-accepted outcome and zero emitted intents.
- An AT transcript shows a single announcement.
- Freezing task: the S02 feedback threshold (`INTERACTION.md:41`) decides when the pending cue becomes visible.

**EARS.** WHILE window actions are unavailable because an operation or observation refresh is outstanding, the shell SHALL report each primary or picker input as not accepted with its reason, without emitting, queuing or later replaying any intent derived from that input.

#### Scenario: FI-03 unrelated-refresh
- GIVEN a group picker is open for family F
- WHEN `host-refresh` arrives for an unrelated window and the projection response leaves F's dependency revision unchanged
- THEN the picker remains open with the same focus, and no activation is emitted

#### Scenario: FI-03 click-during-pending (race)
- GIVEN a minimize for window W is Pending
- WHEN the user clicks W's taskbar entry again
- THEN no second intent is emitted, a "not accepted: pending" outcome is exposed once, and after Committed the next click is evaluated fresh

#### Scenario: FI-03 dependency-changed (negative)
- GIVEN a picker is open for family F
- WHEN refresh shows F's incarnation was replaced
- THEN the picker entry is retired, and focus follows ELM-UI-011 without activating the replacement

### FI-04 (P1): Preview demand that ends on the latest content

**Reason.** F6. O2's frame-callback model throttles work but never drops the final state. The shell's own dirty bit (`Shell.elm:301-309`) already does this for notifications.

Under the current admission rule (`PreviewLifecycle.elm:258`), a content change that arrives during a capture is not remembered. If nothing changes afterwards, the preview stays stale indefinitely while demand persists. Whether the native provider re-sends triggers is unknown; Provider519 is unfinished.

**Requirement.**
- At most one capture per binding is outstanding.
- If a content revision newer than the current job is observed while demand persists, exactly one follow-up capture is admitted after the current job ends (latest wins).
- No follow-up is admitted once demand closes, or after lock, revoke or reconcile.
- Control and retirement events are never coalesced (ELM-REV-009).

**Implementation choices.**
- A `dirtyContent : Maybe ContentRevision` field in the lifecycle, or a native-side trigger guarantee.
- Optional pacing to consumer presentation, in the style of O2.

**Mapping.** Refines ELM-ARC-015, ELM-REN-012, ELM-UI-017 and ELM-TEA-004 (S09/S11), within W03/W06. This is a new liveness property; the bounds already exist.

**Validation.**
- A Quint liveness/bounded-response property under fairness, with a named mutant that drops the dirty bit.
- Compiled Elm replay comparing commands.
- A native trace where the final commit lands mid-capture.

**EARS.** WHEN a newer source content revision is observed while a capture for the same binding is outstanding and demand persists, the preview lifecycle SHALL admit exactly one subsequent capture for the latest revision after the outstanding job terminates, and SHALL admit none if demand closes or authorization is revoked first.

#### Scenario: FI-04 final-commit-mid-capture (race)
- GIVEN capture job J for content c5 is outstanding
- WHEN commits c6 and c7 arrive and J then completes
- THEN exactly one new Acquire is emitted, bound to c7, and no Acquire exists for c6

#### Scenario: FI-04 close-before-completion (negative)
- GIVEN content is dirty during job J
- WHEN the picker closes before J terminates
- THEN J is cancelled per the existing receipts, and no follow-up Acquire is emitted

### FI-05 (P1): Preview label from source state, freshness separate, swap after load

**Reason.** F7 and F8. A3's object-constancy rule matches ELM-REN-004 (never show another incarnation's pixels). It also argues against blanking or relabeling a live window just because its content moved on.

**Requirement A.** The Live/Historical label comes from source liveness and minimized state, as in ELM-UX-006. Content age is a separate attribute. Freshness changes are never announced on their own.

**Requirement B.** The previously drawn authorized frame stays drawable until the replacement has loaded or been presented, or until the old lease is revoked or expires. Revocation and lock always take precedence over continuity.

**Implementation choices.**
- Elm `Html.Events.on "load"` as a typed message. The native URI service still enforces authorization; no safety logic moves to JavaScript.
- Hold at most two leases per entry. This fits the prototype cap, but that cap is not a release budget.

**Mapping.** Refines ELM-UI-016, ELM-UX-006, ELM-REN-003, ELM-REV-003 and ELM-REV-004 (S09), plus W06 and W08. This also corrects a semantic drift in the current implementation, not only a refinement.

**Validation.**
- Replay: commit after acceptance on a live source → label stays Live and the freshness attribute changes.
- Native WebKit snapshot series around a swap → no frame without image or fallback.
- Revoke during a pending swap → neither image drawable, and both leases retire with receipts.

**EARS.** WHILE a preview source is live and not minimized, the preview view SHALL label its authorized frame as live regardless of newer content revisions, SHALL expose content age separately, and IF the drawn lease is revoked, THEN it SHALL stop drawing that frame before any replacement is presented.

#### Scenario: FI-05 live-content-advances
- GIVEN a live, unminimized source with accepted frame at content c3
- WHEN commit c4 is observed
- THEN the label remains "Live preview," and only the freshness attribute changes, without an announcement

#### Scenario: FI-05 revoke-during-swap (negative race)
- GIVEN old lease L1 is drawn and new lease L2 is loading
- WHEN lock revokes publication
- THEN neither L1 nor L2 is drawable, both retire through receipts, and the locked fallback renders

### FI-06 (P2): Reversal origin, velocity and where the motion preference comes from

**Reason.** F10. Hyprland's own animator retargets from the last *sampled* value and keeps spring velocity (O4). ELM-REN-010 says reversal starts from the *last presented* geometry. Without O1 feedback the two can differ, and the baseline does not say which wins.

On reduced motion: the portal exposes a `reduced-motion` key (O6), while WebKitGTK 2.54 ties its CSS media query to GNOME 50's setting (O7). The webview's media query could therefore disagree with the shell's chosen source.

**Requirement A.** The reversal origin is defined as the geometry of the latest frame reported presented. Any use of a newer sampled value is bounded and documented. Velocity continuity is optional and is off under reduced motion.

**Requirement B.** The native host owns one effective motion preference: system source (declared) plus the versioned override. The renderer and Elm receive it as data. The webview's own media query is never the authority.

**Implementation choices.** Read the portal `SettingChanged` signal natively; pass the effective preference through the existing view packet.

**Mapping.** Refines ELM-REN-010, ELM-REN-011, ELM-UI-014, ELM-UI-018 and ELM-UX-022 (S10), and W12. It keeps restore38/recovery34 and the 2 s restore deadline (ELM-REN-008) unchanged.

**Validation.**
- Quint reversal model with presented/sampled divergence.
- A native campaign reversing at mid-motion with O1 traces.
- A preference-mismatch fixture (portal says reduced, WebKit media query says no-preference): the shell renders the reduced profile everywhere.

**EARS.** WHEN a user reverses an in-progress minimize or restore, the native renderer SHALL begin the new trajectory from the geometry of the latest presented frame of that transaction, and WHILE the effective native reduced-motion preference is enabled, SHALL not apply velocity continuation or decorative motion.

#### Scenario: FI-06 reversal-before-feedback (race)
- GIVEN sampled geometry g9 is committed but presentation feedback is pending, and g8 was the last presented
- WHEN reversal is requested
- THEN the trajectory origin follows the declared rule and is traced, and the original deadline is not renewed

#### Scenario: FI-06 preference-divergence (negative)
- GIVEN the portal reports `reduced-motion = 1` and the webview media query reports no preference
- WHEN a switcher overlay opens
- THEN both the native and Elm views use the reduced profile, with no CSS motion

## 4. Rejected and deferred alternatives

- **Optimistic UI that shows success before the native receipt.** Rejected: it breaks ELM-UI-015 and correlated outcomes. A1 supports immediate *feedback*, not claimed completion.
- **Queueing input taken during Pending for later dispatch.** Rejected: it is effectively replay against stale dependencies.
- **Animating in Elm with `Browser.Events.onAnimationFrame` or CSS as the source of motion.** Rejected: motion clocks stay native (`ARCHITECTURE.md:188`, W12).
- **Latency prediction or forecasting.** Deferred: no evidence it applies to an asynchronous authority, and its error modes are unmeasured.
- **Adopting thresholds from A2 (50 ms, 20–40 ms jitter) as budgets.** Rejected: they are second-hand summaries from other systems. S02 must measure baselines here.
- **Velocity-continuous spring retargeting by default.** Deferred until FI-01 traces and A3-style evaluation show it helps.

## 5. Research unknowns

1. Whether Hyprland on the owning ABI tuple delivers wp_presentation for layer-shell and WebKit surfaces, and whether GTK3 fills presentation times in its frame timings.
2. Whether the compositor's input `time` is CLOCK_MONOTONIC milliseconds; the protocol does not guarantee it.
3. How often `host-refresh` is emitted, and whether the provider re-sends capture triggers.
4. Whether synchronous capture actually causes missed frames, and how cost scales with monitor resolution.
5. Whether a portal backend exists on this desktop, and the WebKitGTK version in the tuple.
6. Whether photodiode and 240 Hz hardware are available (ELM-REN-021 is conditional).

## 6. Consensus note

These are one reviewer's independent drafts. If other reviewers raise the same issues, that is independent overlap, not consensus. In the second round I will vote explicitly on the shared candidate matrix and record any dissent.
