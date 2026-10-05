# sol-04 — UX, interaction identity and native accessibility

Independent draft review, retrieved 2026-10-05. This report examines the frozen manifest at observedUTC 2026-10-05T09:30:58.245501+00:00, HEAD `7acf7a790b6e914ac902e75351da4a059155574f`. References below are relative to `inputs/`. It proposes evidence and incremental adoption, not acceptance or implementation. No source, installed configuration, GUI or compositor was changed. The original 242 requirements/417 scenarios, S01–S16, thirteen native preview scenarios, restore38/recovery34, drag/resize52, original deadlines and one reversible release remain mandatory. Optional C00–C06 stays conditional. Representative application compatibility remains generic.

## Current-design findings

The architecture is appropriate for predictable interaction: one controller owns decisions, while bar and popup project committed state. In `implementation/elm-catalog-input-integrated-gui-v814/src/Popup.elm:19–26`, actions dispatch through `Presentation.dispatch` and incoming presentation is accepted without inventing independent popup authority. This preserves a place to correlate intent with native outcomes. That observation establishes an architectural seam, not end-to-end correctness.

`.../src/SurfaceRenderer.elm:11–34` carries explicit control identity, DOM identity, accessible label, detail and eligibility; its strict decoder rejects duplicate identities and unsupported presentation scope. Lines 51–64 produce button controls and a keyed bar. Popup children still use `List.map control snapshot.popup` under an unkeyed container. Thus a publication that inserts or retires a row warrants a focused-node continuity test. The prior workplan's W07 concern about candidate690 must not simply be copied as a claim that all historical behavior remains in814: current native code has additional gates.

In `.../native/host.c:411–461`, focus is issued only when the popup is ready; application acknowledgements bind publication and lease and must match issued targets. Lines472–476 record native keyboard-focus readiness. This is stronger than indiscriminate refocusing after every mutation. However a `focus-applied` acknowledgement cannot alone establish the physical keyboard recipient, a correct accessibility tree or speech/braille experience. Those require independent native and AT traces. Nor does source inspection establish IME candidate placement across fractional scaling.

The renderer emits polite live status on both popup and bar (`SurfaceRenderer.elm:63–64`). That is a concrete reason to test one announcement owner across simultaneous hosts and outputs, not proof that users currently hear duplicates. Menu buttons change their role to menuitem and expose selection using aria-current. Whether these semantics match the chosen menu pattern, host bridge and AT behavior is an acceptance question; an ARIA attribute does not qualify native accessibility.

The strongest design evidence is already normative. `docs/elm-roadmap/REQUIREMENTS.md:13–121` contains all-control semantics, announcement deduplication, identity-bound restoration, IME generation ownership, measurable geometry and keyboard routes. `INTERACTION.md` freezes primary taskbar actions, modal-family resolution, search ranking, innermost Escape, refusal context and independent recovery. UI007/UI015 require correlated operation feedback. W07/W08 already allocate identity, semantics and announcement work. The adoption opportunity is mostly to make these obligations reviewable across changing views and native hosts, rather than expand the product with a novel interface.

## Verified primary sources

All sources were opened directly on 2026-10-05. Current documentation is not a pinned implementation dependency. Academic support is explanatory, not proof that these interfaces or thresholds work here.

| Source | Title/year and precise support | Limits |
|---|---|---|
| [S1](https://www.cs.umd.edu/~ben/papers/Shneiderman1983Direct.pdf) | Shneiderman, *Direct Manipulation: A Step Beyond Programming Languages*, 1983, pp57–59: visible objects and incremental, reversible actions support learning and perceived control. | Historical argument and examples; no quantitative shell latency or AT acceptance budget. |
| [S2](https://faculty.washington.edu/wobbrock/pubs/taccess-11.pdf) | Wobbrock et al., *Ability-Based Design: Concept, Principles and Examples*, 2011: designers should account for users' abilities and place adaptation responsibility on the system. | Framework plus examples; does not prescribe this shell's geometry, shortcuts or participant counts. |
| [S3](https://developer.gnome.org/hig/guidelines/keyboard.html) | GNOME HIG, *Keyboard*, current rolling documentation: every action needs a keyboard route; navigation must be logical, standard and tested. | Application guidance. Shell-global shortcut reservations differ; do not blindly copy app shortcut rules. |
| [S4](https://docs.gtk.org/gtk4/method.IMContext.filter_keypress.html) | GTK4, *IMContext.filter_keypress*, current API reference: a handled key event must receive no subsequent processing. | API reference for GTK4; frozen hosts are separate toolkit/ABI lanes. Not an instruction to call this API in an incompatible host. |
| [S5](https://raw.githubusercontent.com/GNOME/gtk/main/gtk/gtkimcontext.h) | GTK maintained source, *gtkimcontext.h*, current main: distinct preedit, commit, focus, reset and cursor-location interfaces. | Header contracts establish mechanisms; application code must still manage field/generation identity and lifecycle. |
| [S6](https://raw.githubusercontent.com/KDE/kirigami/master/src/controls/Action.qml) | KDE Kirigami maintained source, *Action.qml*, copyright2016/2023, current master: action metadata separates visible representation, tooltip, separator and checkable grouping. | Representation must honor metadata; QML abstractions are not proposed as a second shell controller. |
| [S7](https://gnome.pages.gitlab.gnome.org/orca/help/howto_forms.html) | GNOME Orca, *Filling out forms*, current documentation: browse and focus modes route navigation differently; structural navigation differs from interacting with a field. | Documents user behavior, not complete compatibility of the selected embedded web host. |
| [S8](https://docs.gtk.org/gtk4/method.Accessible.announce.html) | GTK4, *Accessible.announce*, introduced4.14: announcements have priority and need not interrupt existing screen-reader output. | Availability is toolkit-version dependent; automatic translation to frozen host APIs is unsupported. |
| [S9](https://learn.microsoft.com/en-us/windows/apps/develop/input/keyboard-interactions) | Microsoft, *Keyboard interactions*, current Windows guidance: distinguish traversal from inner navigation, preserve predictable order, and avoid destructive initial focus. | Windows reference behavior, not a requirement to use WinUI APIs or copy every Windows interaction. |

These include two academic author-hosted papers and maintained GNOME/GTK, KDE Kirigami and Orca documentation/code. Browser failures for alternative GitLab URLs were replaced by directly opened official mirrors/API pages; inaccessible URLs supply no evidence. Paper publication years come from the documents, not search-engine upload dates.

## Draft adoption proposals

### SOL04-01 — Preserve control identity across publication and focus changes

Priority P0; refinement of ELM-UI-011, ELM-UX-023/024 and W07. Sources S3/S9. Maintain a surface inventory of control pattern, focus owner, initial target, traversal, selection, activation and dismissal. Within a surviving focus scope, an unrelated catalog update should preserve the focused control and its identity, even when it is not the currently selected menu row. Retirement must invoke the declared fallback rather than silently adopt a replacement at the same index.

EARS: **WHEN a presentation publication changes while a shell scope retains focus, the host SHALL preserve the focused surviving control identity, reject activation captured for retired or changed-scope identities, and apply the frozen eligible fallback only when that control is no longer eligible.**

The requirement is continuity and safe routing. Keyed Elm children and a press-time publication/lease guard are implementation choices already assigned to W07, not additional authoritative state in JavaScript. Cost: identity propagation, explicit focus transactions and regression evidence for insertion/removal/reordering. The tempting alternative, always refocusing selection, is cheap but disrupts users who tabbed to Close or recovery. Preserving only an index is also insufficient.

Validation retains compiled Elm state/command replay plus independent native recipient and AT focus traces. Include ordinary arrival, reordered rows, nested dismissal, retired opener, output removal and lock override. Qualify both keyboard press/release and pointer press/release; one route cannot stand for the other.

* GIVEN Close is focused while another row is selected, WHEN an unrelated catalog publication arrives, THEN Close keeps focus and the next activation invokes only Close.
* GIVEN an activation press belongs to a window incarnation and lease, WHEN that incarnation retires and the row position is reused before release, THEN release dispatches no replacement action and eligible fallback remains reachable.

### SOL04-02 — Treat native semantics and announcements as a coherent projection

Priority P0; refinement of UI009/UI010, UX025/026 and W08, dependent on W07/W06. Sources S7/S8. Audit each migrated surface's accessible name, role, state, relationships and supported actions against visible controls, including disabled and overflow states. Freeze one logical announcement owner per correlated outcome across bar, popup and output projections. The owner does not replace native AT authority.

EARS: **WHEN a correlated shell outcome is presented on multiple projections, the shell SHALL expose its current control semantics through the native bridge and announce it once under the frozen interruption policy without changing keyboard focus.**

Cost: outcome identity must survive refresh and host restart; native bridge behavior needs inspector, speech and braille evidence. Source-level live regions alone are insufficient. A dedicated native announcer versus host-supported live status is an implementation decision after ABI inspection. Announcing every projection is rejected because it couples speech load to output count; removing all status speech is equally inadequate.

Validation uses two outputs, simultaneously visible popup/bar, duplicated receipts, refusal, expiry and focused notification actions. Capture native tree/events, speech transcript and braille device or approved emulator, with hashes and owner/outcome identities. Observe disabled controls through AT even when normal Tab excludes them. Decorative preview pixels stay inert and the restore action carries the state.

* GIVEN bar and popup show the same pending operation, WHEN the matching refusal arrives twice, THEN one relevant refusal is announced, both projections show the same outcome, and focus remains on the user's control.
* GIVEN a preview image has retired while its restore control survives, WHEN AT explores the control, THEN source state and supported action are available without an actionable image object or stale-incarnation activation.

### SOL04-03 — Qualify composition as native field ownership

Priority P0; duplicate obligation with stronger evidence packaging for UI012/UX028 and W07. Sources S4/S5/S7. IME consumption, generation-bound commit and transformed candidate geometry are already required. Do not introduce a separate approximate frontend composition state as a substitute for native lifecycle. Document the exact host's path from input method through embedded field and shell shortcut dispatch.

EARS: **WHILE an input method owns a shell field composition, the host SHALL preserve native preedit and candidate interaction, suppress shell handling of consumed keys, and accept commits only for the current field identity and composition generation.**

Implementation can use the chosen toolkit's supported text-input facilities. The GTK4 references illustrate contract shape, not an ABI prescription for GUI814 or toolkit391. Cost includes actual input methods, international text, output transforms and restart faults. The alternative of testing only an event's isComposing flag misses native consumption and late callbacks; ASCII-only replay cannot qualify the host.

Validation records native events, preedit, candidate geometry and final text independently. Cover composition-owned Enter, Escape and arrows; moving the candidate between outputs; field deletion; restart; commit after focus loss; and cancellation. Adopt the frozen timing/resource contract rather than a newly invented response threshold.

* GIVEN a launcher field has active preedit, WHEN the input method consumes Enter to commit text, THEN the query receives the commit once and no launch occurs from that consumed key.
* GIVEN composition belongs to a retired field generation, WHEN its delayed commit arrives after a new field takes focus, THEN neither field nor shell action receives the stale commit.

### SOL04-04 — Preserve hierarchy and reachability under constrained geometry

Priority P1; refinement of UI013/UX027/UI019 and W08. Sources S2/S6/S9. Freeze an inventory that distinguishes primary activation, explicit secondary actions, state detail and recovery. Enlarging text or shrinking an output must preserve this relationship, including separately named Close/restore/refresh controls. The target is legibility and complete action reachability, not increased visual density.

EARS: **WHEN output geometry, text scale or label length changes, the shell SHALL preserve readable control names, visible focus, non-color state cues and keyboard-reachable actions using the frozen contrast, geometry and reflow policy.**

Requirement and layout mechanism remain separate: wrapping, scrolling and labeled overflow are acceptable implementations if validated. Icon-only replacement and truncation without an accessible complete name are rejected. Cost is a cross-product of scale, locale and content; sample representative extremes and retain justified coverage rather than claim every combination was tested.

P0 must measure and freeze thresholds before qualification. Use the existing performance spec's workload-budget matrix and INTERACTION.md numeric-freeze obligation: units, devices, distributions, absolute/regression limits and justified exclusions. No new milliseconds, minimum target pixels or text percentages are asserted here. Validate physical hit geometry and accessible bounds, not screenshots alone, while preserving original native deadlines.

* GIVEN enlarged text and long localized labels on a small output, WHEN the picker opens, THEN every action remains reachable and focused labels are legible according to the frozen oracle.
* GIVEN a popup owns focus on a removed output, WHEN surviving-output recovery runs, THEN its declared fallback or rehosted scope is reachable and removed-generation input cannot activate controls.

### SOL04-05 — Make action discovery agree with acknowledged outcomes

Priority P1; refinement of UI005/UI007/UI015/UI020 and W07/W08, coordinated with W01/W02. Sources S1/S6. Reuse the frozen interaction decision tables to present action names, shortcut hints and pending/refused/reconciling detail consistently. First-use guidance must remain dismissible and available again. An uncertainty message should offer observation/recovery without implying that repeating an uncertain mutation is safe.

EARS: **WHEN a user discovers or invokes a shell action, the shell SHALL expose its frozen meaning and correlated outcome, preserve user context on refusal, and offer keyboard-reachable guidance and reconciliation without automatic replay of Unknown operations.**

Cost: labels and help must stay synchronized with decisions, eligibility and preferences. A shared presentation vocabulary is an implementation option; copying Kirigami's runtime is unnecessary. Optimistic success and mandatory tours are rejected. UI success is tied to native confirmation; immediate local selection feedback may still reflect selection rather than committed activation.

Validation compares pointer, keyboard and AT invocation of the same generic family action against the decision-table oracle. Retain input query and focus through failure; exercise shortcut conflicts and offline recovery. Native latency is measured under existing S02 budgets and UI015's frozen feedback threshold.

* GIVEN a minimized generic application family is selected, WHEN activation is refused natively, THEN it is not shown as restored, the reason and next action are reachable, and its preserved identity remains selected.
* GIVEN an operation has Unknown disposition and guidance was dismissed, WHEN the user opens help or recovery with the keyboard, THEN guidance is available without resetting the desktop and reconciliation creates no automatic repeated mutation.

## Deferred alternatives and unresolved evidence

Do not introduce Elm Signals, DOM-derived native eligibility, JavaScript safety authority, broad visual redesign or named-application repairs. Do not upgrade toolkit lanes merely to obtain a convenient accessibility API. A generic command palette, automatic adaptive shortcuts and user-personalized action ranking add behavior and migration questions absent from the frozen scope; defer them until existing routes qualify. Dense-list virtualization needs focus/AT identity and measurements before adoption, and belongs with performance reviewers.

Unknowns remain: actual selected host/bridge AT fidelity, production preview source and drain integration, IME engines and locales admitted to the matrix, measurable geometry/contrast and notification policy freeze artifacts, and whether duplicated status regions generate duplicate native events. Their resolution requires later authorized native/hardware/AT campaigns. Model or source evidence cannot close those gates. All five proposals are draft refinements or duplicate evidence work; independent initial reviews do not imply consensus. All implementation and qualification tasks remain unchecked.
