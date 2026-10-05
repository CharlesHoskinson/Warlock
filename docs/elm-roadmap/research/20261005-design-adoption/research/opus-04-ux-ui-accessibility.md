# UX/UI and accessibility review: one controller and its read-only projections

**Reviewer:** opus-04-ux-ui-accessibility · **Snapshot:** head `7acf7a7`, manifest observed 2026-10-05T09:30Z · **Retrieved:** 2026-10-05

This is an independent first-round review. The proposals below are drafts. Nothing here counts as release or native acceptance, and other reviewers may disagree with any of it. I edited no source, config or GUI, and launched no agents.

## 1. Scope and how to read this

I read `INVENTORY.md`, `source-manifest.json`, `INTERACTION.md`, and the accessibility, shell-experience and context-menu specs. I also read `FRP-ELM-WORKPLAN.{md,json}` (W07/W08), the Elm renderer, controller and menu modules, and the native GTK3 host. The host builds against `gtk+-3.0`, `webkit2gtk-4.1` and `gtk-layer-shell-0` (`elm-preview-shared-bridge-v509/qa/build.py:33`).

Each finding is labelled in one of three ways:
- **[impl]** behaviour the frozen source actually implements.
- **[oblig]** an existing frozen obligation.
- **[gap]** an acceptance gap.

One caveat applies throughout. The JavaScript shim served from `elm-shell://app/*` is not in the snapshot. That shim handles click→`requestAction`, keydown→`surface-menu-navigation` and `receiveFocus`. Anything I say about its behaviour is inferred from the native callers and from the W07 notes on candidate690.

Everything below keeps the following constraints:
- one controller with read-only projections;
- native authority, and the original 242 requirements / 417 scenarios;
- S01–S16 and the 13 native preview scenarios;
- restore38 / recovery34 and the original deadlines;
- no Elm Signals, no automatic replay of Unknown, and no native safety logic moved into JavaScript.

## 2. Findings on the current design

**F1. Menu "selection" and keyboard/AT focus are separate, which risks activating the wrong item. [impl/gap]**
- The controller keeps `menu.selected` (`Menu.elm:294-328`).
- The renderer shows it only as `aria-current` plus the visible text "Selected" (`SurfaceRenderer.elm:62`). `aria-current` is not a menu focus mechanism in APG (R2).
- Enter activates `menu.selected` (`Surface.elm:154`). Keyboard context admission, by contrast, trusts `document.activeElement` (`shared-context.h:265`).
- The popup's "Close" control and the recovery control are rendered with `role="menuitem"`, but they sit outside the arrow-key cycle (`Surface.elm:69`, `Menu.elm:278-282`).
- Result: when DOM/AT focus and controller selection differ (for example after a Tab to Close), Enter can act on an item the screen reader did not announce. This partly overlaps W07 05-01/05-03. Space is still missing on both sides: not in the native key allowlist (`shared-context.h:47-49,101-103`) and not in Elm (`Surface.elm:147-155`). That confirms W07 rather than adding a new point.

**F2. The taskbar bar has no keyboard route in the shared multi-output lane. [impl/gap]**
- Each bar is created with `GTK_LAYER_SHELL_KEYBOARD_MODE_NONE` (`v509/native/shared-host.c:325`; same at `v814/native/shared-host.c:322`). Per the protocol, the compositor then "should never assign it the keyboard focus" (R3).
- The legacy single-view path uses `ON_DEMAND` (`host.c:799`), which gives no keyboard entry route of its own.
- When the popup closes, focus-return effects (`Desktop.elm:130,198,309`) are sent to the bar's DOM with no readiness or acknowledgement gating (`host.c:624`). Compare the popup path, which waits for grab, keyboard focus and applied state (`host.c:440-448`).
- So "native and accessibility focus return to the opener" (ELM-UI-011) can only ever be DOM-deep here. The ELM-UX-023 taskbar-groups keyboard route has no entry point.

**F3. Accessible names change with state and hide counts. [impl]**
- Bar group names are built as operation + label, e.g. "Minimize …", "Choose a window from …" (`Surface.elm:91-98`). The label is the *first family's* window title (`Taskbar.elm:20`, `Surface.elm:97`), not the application.
- The window count and the "Awaiting native confirmation" detail are visible text only. `aria-label` overrides them (`SurfaceRenderer.elm:62`).
- The picker heading is a generic "Choose a window" `h1`. Neither it nor the `role=menu` / `role=group` containers are tied to an accessible name (`SurfaceRenderer.elm:63`).
- Microsoft's UIA guidance says Name "should not be an extended or modified version of the on-screen label" and that status belongs in ItemStatus/FullDescription (R8). KDE's task manager keeps `Accessible.name: model.display` and puts "Activate %1" / "Open textual list of windows for %1" in the description (R7).

**F4. The same polite live region is rendered N+1 times. [impl/gap]**
- `shared_publish` sends the same snapshot, including `status`, to every bar (`shared-host.c:50-53`). Each bar and the popup renders it as `role=status aria-live=polite` (`SurfaceRenderer.elm:63-64`).
- Orca's presenter drops updates from inactive documents unless `present-from-inactive-tab` is enabled. It suppresses identical text only within 0.25 s (R12).
- Because bars never hold focus (F2), what happens today depends on AT configuration and timing: the user may hear nothing, or hear duplicates. Nothing in the design decides which. This is W08's "one announcement owner" problem, now confirmed in source.

**F5. Disabled items cannot be reached by keyboard, and the platform conventions disagree. [impl/oblig]**
- `Menu.navigate` skips disabled items, and the renderer uses the HTML `disabled` attribute, which removes them from the focus order.
- APG says "Disabled menu items are focusable but cannot be activated" (R1, R2).
- Qt's Windows style sets `SH_Menu_AllowActiveAndDisabled` to 1 (R10). GTK3's `_gtk_menu_item_is_selectable` returns FALSE for insensitive items (R11).
- ELM-RC-006 requires disabled-but-supported actions to remain visible. ELM-RC-017 does not settle whether they can be reached.

**F6. There is no text field anywhere in the snapshot. [impl/gap]**
- A search for `Html.input`, `onInput`, `compos` and `preedit` across all `*.elm` finds nothing. The launcher is a list of "Open X" buttons (`Surface.elm:55`). ELM-UI-012 and ELM-UX-028 cannot be exercised yet.
- The native key-proof handler is attached to the engine's generic `event` signal (`shared-host.c:329`, `shared-context.h:52-123`). It therefore sees GDK key presses before WebKit's input-method handling. Today, protection against IME-consumed Enter rests entirely on the unsupplied shim.

**F7. What already works well. [impl]**
- Preview imagery is inert (`alt=""`, `aria-hidden`; `PreviewLifecycle.elm:371-373`).
- Bar controls are keyed (`SurfaceRenderer.elm:64`).
- Focus is expressed as typed `Focus domId` effects with publication/lease gating on the popup.
- Escape is natively owned with release pairing (`shared-context.h:135-196`).
- Keyboard context admission requires a physical key proof plus a DOM `activeElement` check (`shared-context.h:221-268`).

All of these should be preserved.

## 3. Sources (retrieved 2026-10-05)

| ID | Source (type) | Title / year | Claim used | Limitations |
|---|---|---|---|---|
| R1 | W3C WAI, [APG keyboard interface](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/) (maintained doc) | Developing a Keyboard Interface (undated, live) | Disabled menu items, options, tabs and tree items stay focusable via `aria-disabled`. AT treats the `aria-activedescendant` target as focused. Selection must be visually distinct from focus. | Web authoring guidance. Desktop-shell and WebKitGTK→AT-SPI mapping must be verified. |
| R2 | W3C WAI, [APG Menu/Menubar pattern](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/) | Menu and Menubar Pattern | Escape returns focus to the opener. Menus are labelled with `aria-labelledby`. Enter/Space and Home/End behaviour. `aria-current` is not part of the pattern. | Pattern guidance, not a conformance test. |
| R3 | wlroots, [wlr-layer-shell-unstable-v1.xml](https://raw.githubusercontent.com/swaywm/wlr-protocols/master/unstable/wlr-layer-shell-unstable-v1.xml) (protocol source; GitHub mirror) | wlr layer-shell | `none`: never assign keyboard focus. `on_demand`: focused/unfocused "in an implementation-defined manner". Implementations may need keybindings to switch layers. | Mirror of the freedesktop repo (the primary host blocked automated fetch). Actual Hyprland behaviour is unverified. |
| R4 | [gtk-layer-shell.h](https://raw.githubusercontent.com/wmww/gtk-layer-shell/master/include/gtk-layer-shell.h) (OSS code) | gtk-layer-shell (GTK3) | `ON_DEMAND` is "not supported for protocol version < 4". | Library behaviour only. |
| R5 | GNOME, [ctrlAltTab.js](https://raw.githubusercontent.com/GNOME/gnome-shell/main/js/ui/ctrlAltTab.js) (OSS code) + [GNOME Help: keyboard navigation](https://help.gnome.org/users/gnome-help/stable/keyboard-nav.html.en) | GNOME Shell, current main | `SWITCH_PANELS` binding. `focusGroup()` uses `navigate_focus`. Ctrl+Alt+Tab "Give keyboard focus to the top bar". Esc exits menus and popups. | The code does not save or restore prior window focus. Different toolkit (St). |
| R6 | GNOME, [HIG: Keyboard](https://developer.gnome.org/hig/guidelines/keyboard.html) | GNOME HIG | "every action should also be possible with the keyboard". Menu/Shift+F10 opens a context menu. Super is reserved for system shortcuts. | App-level guidance. |
| R7 | KDE, [Task.qml](https://raw.githubusercontent.com/KDE/plasma-desktop/master/applets/taskmanager/qml/Task.qml) (OSS code) | Plasma task manager, master | `Accessible.name: model.display`. The description holds the action and counts. `activeFocusOnTab`, Menu/Return/Space handlers. | Qt Quick accessibility, a different bridge. |
| R8 | Microsoft, [UIA property identifiers](https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-automation-element-propids) (2025-07-14) | Automation Element Property Identifiers | Name should match the on-screen label and not be extended. ItemStatus/FullDescription for status. `IsPeripheral` for menus and popups. | Windows UIA semantics, used here as a parity reference. |
| R9 | Microsoft, [Keyboard shortcuts in Windows](https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec) | Support article | Win+T cycles taskbar apps. Win+B focuses the notification area. Win+Alt+number opens a jump list. Shift+F10 / Alt+Space. | Product behaviour, not a specification. |
| R10 | Qt, [QStyle docs](https://doc.qt.io/qt-6/qstyle.html) + [qwindowsstyle.cpp](https://raw.githubusercontent.com/qt/qtbase/dev/src/widgets/styles/qwindowsstyle.cpp) | Qt 6 | `SH_Menu_AllowActiveAndDisabled` "Allows disabled menu items to be active". The Windows style returns 1. | Style-dependent. Not the host toolkit. |
| R11 | GTK, [gtkmenuitem.c (gtk-3-24)](https://raw.githubusercontent.com/GNOME/gtk/gtk-3-24/gtk/gtkmenuitem.c) | GTK 3.24 | `_gtk_menu_item_is_selectable` returns FALSE for insensitive items. | Native GTK menus. The shell renders HTML menus. |
| R12 | GNOME Orca, [live_region_presenter.py](https://raw.githubusercontent.com/GNOME/orca/main/src/orca/live_region_presenter.py) (OSS code) | Orca, main | Drops live updates from inactive documents unless `present-from-inactive-tab` is set. Treats identical text as a duplicate only within 0.25 s. Assertive messages purge polite ones. | Current main; the installed version is unknown. |
| R13 | GTK, [gtk_accessible_announce](https://docs.gtk.org/gtk4/method.Accessible.announce.html) | GTK 4.14+ | Native screen-reader announcement that does not interrupt current output. | GTK4 only; the host is GTK3. |
| R14 | W3C, [UI Events WD](https://www.w3.org/TR/uievents/) (2026-02-21) | UI Events | `isComposing` is true between compositionstart and compositionend. Key events may fire during composition. | Working draft. Engine conformance varies. |
| R15 | [text-input-unstable-v3](https://wayland.app/protocols/text-input-unstable-v3) (rendering of the wayland-protocols XML) | Wayland text-input v3 | Leave clears the surface. `done` plus serial applies changes atomically and discards stale ones. Cursor rectangle positions candidates. | Rendered mirror. GTK3/WebKit use of it under layer-shell is unverified. |
| R16 | Cockburn, Gutwin, Greenberg, [CHI 2007 author PDF](https://grouplab.cpsc.ucalgary.ca/grouplab/uploads/Publications/Publications/2007-PredictiveModelMenus.CHI.pdf) (academic) | A Predictive Model of Menu Performance, 2007 | Users move from linear visual search to Hick-Hyman decision time "but only if the interface allows them to do so through predictable and stable item placement". Learnability L=1 when items "do not change locations". | Pointer-based, sighted users, lab calibration. Does not cover AT. |
| R17 | Ge, Peng, Shi, Greenman, Jiang, [arXiv 2609.17959](https://arxiv.org/html/2609.17959) (academic preprint) | A11yLTLNav, 2026 | LTL properties over action-state traces: focus loss after a local change (L2-01); `G(escapeClosesModal(d,v)→X(focus=v))`; activation followed by notifiable feedback (L2-11). | Not peer reviewed. Browser-observable only, tested on generated sites. Exploration budget is not proof that a failure is absent. |

Two candidate academic sources could not be read directly (HTTP 403 or offline): Brown, Jay & Harper, IJHCS 2012, and Findlater & McGrenere, CHI 2004. I did not use them as evidence.

## 4. Draft adoption proposals

Each proposal separates the **requirement** from the **implementation choice**. Every validation reuses the frozen P0 thresholds (INTERACTION.md:41,47; ELM-UI-013/015). Where no threshold is frozen yet, the step is a measurement-and-freeze task. No new numbers are proposed.

### UXA-01: One exposed focus identity per popup scope (P0)

**Why:** fixes F1. APG (R1/R2) says the AT-reported focus *is* the interaction point. The Escape-return and L2-01 properties in R17 are temporal invariants that fit the project's Quint/replay style.

**Mapping:** W07 (explicit focus identity/revision, Enter/Space), ELM-UX-024, ELM-UI-011, ELM-RC-017/018. **Refinement** of W07: it adds the invariant "activated identity = exposed focused identity" and requires every `menuitem` to be in the arrow cycle.

**Requirement (EARS):** WHILE a shell popup focus scope is open, the shell SHALL expose exactly one focused control identity per publication. WHEN Enter or Space is admitted, the shell SHALL activate only that identity, which SHALL equal the control native AT reports as focused. Every control exposed with a menu-item role SHALL be reachable by the menu's arrow navigation.

**Implementation choice (not a requirement):**
- Add a typed `focus` field to the surface packet (protocol bump).
- Use roving tabindex, because native keyboard-context admission already trusts DOM focus.
- Stop expressing selection with `aria-current`.
- Either place Close inside the arrow cycle, or render it outside `role=menu`.

**Alternatives:** `aria-activedescendant` (WebKitGTK→AT-SPI event fidelity unknown); keeping a shim that refocuses on every DOM mutation (the fragile behaviour W07 already flagged).

**Cost and fit:** an Elm/native/shim protocol change inside the existing GUI lane. Requalifies W07 fixtures but needs no new authority.

**Validation:**
- Compiled replay property: activated id = packet `focus` for every admitted Enter/Space, over the retained traces.
- Mutation control: a renderer that moves `aria-current` without moving focus must fail.
- Native AT-SPI transcript: after each navigation, the focus event id = `activeElement` = packet `focus`.

**Scenarios:**
- *GIVEN* a window-actions menu with "Minimize" selected *WHEN* the user Tabs to Close and presses Enter *THEN* only dismissal occurs, zero window intents are dispatched, and focus returns per ELM-UI-011.
- *GIVEN* a focused row whose window retires in publication N+1 between key press and release *WHEN* the release arrives *THEN* nothing is activated, focus moves to the declared fallback in the same scope, and AT reports the new focus exactly once.
- *GIVEN* duplicate Enter key events and one Pending intent *WHEN* both are admitted *THEN* exactly one intent exists (ELM-RC-022).

### UXA-02: Native-owned keyboard entry into and exit from the taskbar (P0 design, P1 build)

**Why:** fixes F2. GNOME (R5), Windows (R9) and KDE (R7) all give a dedicated keyboard route into the panel. The layer-shell protocol leaves focus "implementation-defined" and explicitly mentions keybindings (R3).

**Mapping:** ELM-UX-023 (task P5-ELM-UX-023 "Publish chord map"), ELM-UX-024, ELM-UI-011, ELM-UI-019, W07 "native keyboard scope", INTERACTION.md:51 (shortcut conflicts). **Refinement plus new:** it makes a bounded bar keyboard scope a native obligation and moves it earlier than P5.

**Requirement (EARS):**
- WHEN the user invokes the declared taskbar-focus binding, the native host SHALL give keyboard focus to the bar on the active output and record the previously focused application incarnation.
- WHEN that scope ends with Escape, the host SHALL restore the recorded incarnation if it is still eligible, otherwise the frozen committed-MRU/desktop fallback, without changing activation history.
- WHILE the session is locked, the binding SHALL be inert.

**Implementation choice:**
- Switch the layer's keyboard mode from NONE to EXCLUSIVE (or ON_DEMAND plus a compositor grant) only for the scope's lifetime.
- The binding lives in the native authority or plugin.
- The default chord comes from the conflict policy; nothing assumes Super.
- Reuse the existing Elm `Focus` effect, gated like the popup path at `host.c:440-448`.

**Alternatives:**
- Permanent ON_DEMAND: no keyboard entry and click-to-focus side effects.
- Permanent EXCLUSIVE: starves applications of keyboard input.
- Elm/JS global key handling: rejected, because native owns input.

**Cost:** high. Needs native, plugin and compositor work, lock interaction, and multi-output testing.

**Validation:**
- Keyboard-only native fixture with the pointer unused: chord → AT-SPI focus on a bar group → arrows → Enter → the target receives focus (actual native recipient).
- Escape → the prior app receives focus.
- An event-sequence oracle checks that activation history is unchanged.
- Latency is measured against the frozen feedback contract.

**Scenarios:**
- *GIVEN* app A focused *WHEN* the binding is pressed and then Escape *THEN* bar focus is observed first, then A regains native keyboard focus, and MRU is unchanged.
- *GIVEN* an open bar scope *WHEN* A retires and its address is reused by B *THEN* Escape focuses the eligible fallback and never B.
- *GIVEN* an open bar scope on output 2 *WHEN* output 2 is removed *THEN* the scope ends, removed-generation focus effects are rejected, and focus follows ELM-UI-019.
- *GIVEN* a locked session *WHEN* the binding is pressed *THEN* no bar focus and no input interception.

### UXA-03: Typed semantics with a stable name and separate state/description (P1)

**Why:** fixes F3. Supported by R7 (KDE), R8 (UIA Name/ItemStatus), R2 (menu labelling) and R16 (stable labels help learning).

**Mapping:** ELM-UI-009, ELM-UX-025, ELM-RC-018, ELM-UI-013 (non-colour cues), W08 ("state on its control"). **Refinement.**

**Requirement (EARS):** The shell SHALL derive each control's accessible name from its visible label. It SHALL expose operation, family count, active/minimized/pending/blocked state, popup relationship and container labels through typed role, state and description fields, and SHALL NOT change the name to convey state.

**Implementation choice:**
- Replace the free-form `ariaLabel` string with a closed `Semantics` record (role, name, description, `disabled`, `hasPopup`, `expanded`).
- The heading names the group, and `role=menu` uses `aria-labelledby`.
- The group name comes from the catalog application display name. This depends on the separate native catalog-matching contract (`Taskbar.elm:12-13`).

**Alternatives:** keep verb-first names (simpler, but violates R8); per-control `aria-describedby` pointing at a status node (DOM-local only, since bar↔popup relationships cannot cross documents).

**Cost:** low to moderate, plus localization of description strings.

**Validation:**
- Packet property over replay: name = visible label for every control.
- Name is unchanged across active↔inactive transitions while description or state changes.
- ELM-UI-009 AT transcript.

**Scenarios:**
- *GIVEN* a single-window group that becomes active *WHEN* AT re-reads it *THEN* the name is unchanged, the description changes from "activate" to "minimize", and one change is reported.
- *GIVEN* a blocked (pending) family *WHEN* it is focused and Enter is pressed *THEN* it is reported disabled with the pending description, zero intents are dispatched, and the name is unchanged.
- *GIVEN* a three-window group picker *WHEN* it opens *THEN* the container name includes the application and AT reports the item count.

### UXA-04: One announcement owner in the AT-active document, keyed by outcome (P1)

**Why:** fixes F4. R12 shows the current outcome depends on AT configuration and timing. R13's native announcement API needs GTK4, which this host does not have.

**Mapping:** W08 "one announcement owner/outcome identity" (**duplicate in goal, refinement in rule**), ELM-UI-010, ELM-UX-026, ARCHITECTURE.md:273.

**Requirement (EARS):**
- WHEN an announceable outcome occurs, the shell SHALL publish one accessible status, keyed by operation identity and outcome kind.
- It SHALL publish it only in the surface owning the current keyboard focus scope, or in the declared fallback owner when no shell scope is focused.
- It SHALL NOT republish for repeated receipts or for the same publication on other outputs.

**Implementation choice:** add packet fields `announcement {id, politeness, text}` and `announcementOwner`. Bars render status as non-live text.

**Open policy choice:** where to announce when an application holds focus. Candidates are the next shell scope, a native AT-SPI channel, or silence for outcomes the user did not invoke. This must be frozen. It is not decided here.

**Alternatives:** clear-and-reset live-region text to force re-announcement (rejected; breaks deduplication); GTK4 announce (deferred to a toolkit decision; no cross-loading of ABI artifacts).

**Validation:**
- Two-output Orca transcript, with `present-from-inactive-tab` both off and on: per outcome id, speech and braille count is exactly 1.
- Replay: duplicate receipts leave `announcement.id` unchanged.
- Latency from native receipt timestamp to AT-SPI event, measured against the frozen feedback threshold.

**Scenarios:**
- *GIVEN* two outputs and the popup on output B *WHEN* a launch is refused *THEN* exactly one message and no focus movement.
- *GIVEN* three identical refusal receipts *WHEN* they are processed *THEN* zero extra announcements.
- *GIVEN* the popup closes before the Unknown outcome arrives *WHEN* the outcome arrives *THEN* the declared fallback owner receives it once; it is neither silently lost nor duplicated.

### UXA-05: Frozen policy for reaching disabled actions, with stable positions (P2)

**Why:** fixes F5. The conventions genuinely diverge: APG and Qt-Windows keep disabled items reachable (R1, R2, R10); GTK3 skips them (R11). R16 favours stable placement.

**Mapping:** ELM-RC-006/017/018, INTERACTION.md:3 (policy versioning). **Refinement:** an explicit policy decision under existing requirements.

**Requirement (EARS):**
- The shell SHALL apply one frozen, versioned disabled-item navigation policy per surface class.
- Supported but state-disabled actions SHALL keep their declared positions.
- WHERE the policy makes disabled items focusable, arrow keys SHALL reach them, AT SHALL report them disabled, and keyboard, pointer and AT activation SHALL dispatch nothing.

**Recommendation:** focusable for menus and jump lists (Windows parity, APG). This needs an explicit owner decision.

**Validation:**
- Replay over all key sequences: zero `Dispatch` effects from disabled indices.
- Index invariance of supported operations across the RC-006 state table.
- AT transcript reports "unavailable".

**Scenarios:**
- *GIVEN* a maximized window menu *WHEN* Down reaches Move *THEN* Move is focused and reported disabled; Enter and Space dispatch nothing.
- *GIVEN* an all-disabled menu *WHEN* it opens *THEN* focus lands in the menu, nothing can be invoked, and Escape dismisses it.
- *GIVEN* focus on Close *WHEN* a Pending intent disables it *THEN* the state change is reported once and a subsequent Enter dispatches nothing.

### UXA-06: Composition-aware key admission, required before the first text field (P2 gate)

**Why:** fixes F6. Supported by R14 (`isComposing`) and R15 (leave clears; stale serials are discarded).

**Mapping:** ELM-UI-012, ELM-UX-028, P1-ELM-UI-012, INTERACTION.md:45. **Refinement:** a two-sided admission rule.

**Requirement (EARS):** WHILE a composition session is active for a shell field, neither the native key proof nor the DOM intent path SHALL admit any key as shell navigation, submission or dismissal. Commits SHALL bind to field identity and composition generation.

**Implementation choice:** native proofs check IM-filter results or composition state; the shim rejects `isComposing`. Run a minimal-host spike first, as the task already plans.

**Validation:**
- During composition, zero `surface-*` intents.
- A valid commit writes exactly once.
- Mutation control: removing either guard fails the fixture.

**Scenarios:**
- *GIVEN* candidates are showing *WHEN* Enter confirms a candidate *THEN* exactly one string is written and no launch or dismissal happens.
- *GIVEN* a composition in progress *WHEN* focus is lost and a late commit arrives *THEN* zero writes and zero shell effects.

## 5. Rejected or deferred alternatives

- **Elm `Browser.Events` as keyboard authority:** rejected. Native owns input.
- **Adaptive or frequency-ordered menus:** rejected. They conflict with R16 and the frozen order.
- **Visual redesign of the bar or grouping:** rejected as novelty.
- **Typeahead/mnemonics:** deferred to ELM-RC-017's "where declared".
- **`aria-activedescendant`:** deferred pending WebKitGTK evidence.
- **GTK4 announcements:** deferred. They require a toolkit migration through its own lane, and must not be inferred from toolkit391.

## 6. Research unknowns

1. What the shim actually does (`receiveFocus`, click/keydown routing). It is absent from the snapshot.
2. How Hyprland and the authority plugin handle layer keyboard-mode transitions, and whether they can restore prior focus.
3. WebKitGTK 4.1 AT-SPI events for roving focus, `aria-describedby` and live regions inside `GTK_WINDOW_POPUP`.
4. The installed Orca version and settings, and the braille path.
5. The announcement channel to use when no shell scope is focused.
6. Whether application display names are available through the catalog contract.
7. IME frameworks on the target, and text-input-v3 with GTK3 layer-shell popups.
8. Numeric contrast, target, focus-geometry and scaling thresholds. These remain the P0 freeze task (ELM-UI-013). None are proposed here.

## 7. For the second round

These are one reviewer's first-round positions. Where I am least confident:
- **UXA-05:** the GTK-convention alternative is defensible.
- **UXA-02:** compositor feasibility is unverified.

I expect real overlap with W07/W08 and with the typed-protocol and errors reviewers. I will vote on the shared candidate matrix explicitly and record dissent rather than treat independent overlap as consensus.
