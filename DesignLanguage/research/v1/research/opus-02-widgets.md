# Warlock widget and interaction-state inventory, with a Material/Windows-informed catalog plan

**Reviewer:** opus-02-widgets (Claude Opus 5.5, high effort). Planning and research only: I edited no files and started no agents.
**Launcher:** Context loading did not run, so I read the frozen project context directly: the brand, the philosophy, the workplan, the build-loop instructions, 10 Elm sources and the vendored Impeccable files.
**Consensus status:** None of this is consensus. These are one reviewer's proposals. Consensus can only come after all five reviewers vote on the exact consolidated text.

**Evidence legend, used throughout:**
- **[S]** existing source, with a file:line citation
- **[P]** proposed addition
- **[B]** something a browser demonstration can show
- **[N]** native acceptance. I claim none here. Each [N] item is a future gate on the owning ABI tuple. A website demo cannot qualify native release, focus, AT or resource behavior.

---

## 1. Actual design inventory (source-traced)

### 1.1 Scope and traceability gaps

The frozen input set is `inputs/implementation/warlock-preview-provider-v1/src`. It imports 13 modules that were not supplied: `Presentation`, `PreviewLifecycle`, `TaskbarShell`, `Desktop`, `Effects`, `ActionProjection`, `OutputController`, `SurfaceController`, `Inspection`, `GeometryProjection`, `Binding`, `UInt64` and `UnsentOperation`. There is also **no CSS, HTML host or JS bridge** in the inputs. So:

- **No visual state styling can be traced.** Hover, pressed, focus ring, density and radius do not exist in the inputs. `tokens.json` defines only colors, font families, logo rules, motion policy and semantics flags.
- **Elm does not handle activation.** `SurfaceRenderer.viewWithPreview` takes a `send` argument but never uses it (`SurfaceRenderer.elm:58-64`). No `Html.Events` handler is attached. Actions enter through the `requestAction` port (`Bar.elm:11,23`; `Popup.elm:14,29`) and are validated by `Presentation.dispatch`, which is not supplied. Pointer and keyboard activation therefore live in the unsupplied host bridge, and I cannot verify the key bindings from source.
- **The controller is headless.** `Main.elm:64` renders `text ""`. Surfaces are display-only caches: "A display owns only a presentation cache. It cannot run Desktop.update." (`Bar.elm:16`). This is the correct single-policy shape and every proposal below keeps it.

### 1.2 Widget inventory

| # | Widget | Source | Rendered element / role | States present in source | Bounds |
|---|---|---|---|---|---|
| W1 | **Taskbar group button** | `SurfaceRenderer.elm:61-62` (identity prefix `bar:group:`, class `control-group`); decision logic `Taskbar.elm:25-36` | `<button role="button">`, `aria-label`, `aria-current="false"` (always, on the bar) | enabled/disabled (HTML `disabled`); families: active, minimized, available; decision Launch / Picker / Apply(Restore\|Minimize\|Activate) / Unavailable | bar ≤259 controls; label/ariaLabel ≤1024; detail ≤128 (`:23,29`) |
| W2 | **Recovery refresh button** | `SurfaceRenderer.elm:61` (`bar:recovery-refresh` → `control-recovery`) | button | enabled/disabled | same |
| W3 | **Utility button** | `SurfaceRenderer.elm:61` (any other bar identity → `control-utility`) | button | enabled/disabled | same |
| W4 | **Bar status text** | `SurfaceRenderer.elm:64` | `span.surface-status role=status aria-live=polite` | text from the `status` field, ≤1024 | — |
| W5 | **Popup surface** | `SurfaceRenderer.elm:63`; `Popup.elm:27` | `div.surface-popup[data-mode]`, `h1`, `p role=status aria-live=polite`, `div.surface-controls role=menu\|group` | modes `closed\|picker\|applications\|menu` (`:34`); headings "Choose a window" / "Applications" / "Window actions" | popup ≤2051 controls |
| W6 | **Popup item** (picker entry, application entry, menu item) | `SurfaceRenderer.elm:62` | `button`, or `role=menuitem` in menu mode; `aria-current="true"` iff `detail=="Selected"` | enabled/disabled, "Selected" via a detail string | — |
| W7 | **Preview tile** (inside picker items) | `PreviewPresenter.elm:99-101` → `PreviewLifecycle.inlineView` (unsupplied) | unknown (`inlineView`) | shown only when the publication/lease stamp matches and mode is `picker` (`:54`); closing the UI cancels demand but keeps the lifecycle and pending receipts (`:59-60`) | ≤2051 entries (`:91`) |
| W8 | **Context-menu model** | `Menu.elm` | rendered via W5/W6 | Status `Ready \| Pending \| Refused reason \| Cancelled \| Unknown` (`:155-160`); `exhausted` | items ≤64, label ≤256, outstanding ≤64, retired ≤128 (`:27-43`) |
| W9 | **Shell connection/status model** | `Shell.elm` | feeds W4/W5 status text | Phase `Detached \| Reconciling \| Ready \| Exhausted` (`:31`); `available` gate (`:66-67`) | — |
| W10 | **Application catalog entry** | `Catalog.elm:7,13` | rendered in `applications` mode | `name`, `iconHint`, `wmclass` | ≤2048 (`:22`) |
| W11 | **Timed choice windows** | `Main.elm:36-38` | not visual (affects W5/W8) | prepared choice 2000 ms, choice 2000 ms, deadline 10000 ms | — |

### 1.3 Menu action vocabulary

Source: `Menu.elm:122-134`.

| Action | Kind | Notes |
|---|---|---|
| `Restore`, `RestoreGeometry`, `Move`, `Size`, `Minimize`, `Maximize`, `Close`, `ExitFullscreen` | command | window system-menu set |
| `AlwaysOnTop Bool`, `PinToTaskbar Bool` | **toggle** | No checked-state semantics reach the renderer. `Control` has no `checked` field (`SurfaceRenderer.elm:11`). |
| `Launch DeclaredActionId`, `ProviderCommand DeclaredActionId` | declared | Identifiers come from the authority, never from labels (`Menu.elm:11-14`). |

Menu targets: `Window`, `Application`, `ProviderSelection`, `Background` (`Menu.elm:75-79`).
Native outcome statuses: `Committed | Refused | Unknown`. Protocol 1 covers minimize/restore/activate; protocol 2 covers maximize/restore-geometry (`NativeOutcome.elm:31,42`).

### 1.4 State tables already implied by source

**Taskbar group primary action** (`Taskbar.elm:25-33`):

| Families | pinned | available | minimized | active | Decision |
|---|---|---|---|---|---|
| 0 | yes | — | — | — | Launch |
| 0 | no | — | — | — | Unavailable |
| 1 | — | no | — | — | Unavailable |
| 1 | — | yes | yes | — | Apply Restore |
| 1 | — | yes | no | yes | Apply Minimize |
| 1 | — | yes | no | no | Apply Activate |
| ≥2 | — | — | — | — | Picker |

**Menu status lifecycle** (`Menu.elm:459-518`):

| From | Event | To | Effect |
|---|---|---|---|
| Ready | Activate an enabled item, under the limit | Pending i | `Dispatch i binding action` |
| Ready | Activate an enabled item at the limit | Refused "Outstanding operation limit reached; reconcile existing requests." | none |
| any | Activate while the same target has an outstanding intent | **unchanged (silent)** (`:466-467`) | none |
| Pending/Unknown i | Committed | menu closed | — |
| Pending/Unknown i | Refusal r | Refused r (bounded to 256 units) | — |
| Pending/Unknown i | Cancellation | Cancelled | — |
| Pending i | Uncertain / disconnect | Unknown i (`:253-265`) | the outstanding intent survives dismissal |

**Keyboard navigation in the model** (`Menu.elm:294-328`):
- Up/Down/Home/End move only across **enabled** items, and they **cycle** at both ends.
- Initial selection is the first enabled item (`:438`).
- There is no Escape, typeahead or Enter mapping in the model. `Dismiss` and `Activate` are separate messages. The keys themselves are presumably bound by the bridge, which is unsupplied.

**Shell status copy** (`Shell.elm`): 21 distinct strings. Most follow the brand voice, for example "Connection lost. Reconnect to continue." (`:65`), "Window list changed. Choose again." (`:136`) and the five recovery notices (`:23-29`). Three exceptions:
- `"Geometry refresh pending"` and `"Geometry observation unavailable"` (`:139-140`) are internal phrasing that surfaces as the user-visible notice.
- `"Connected"` is reassigned on every admitted projection (`:189`). The status regions are polite live regions, so this can be re-announced on every refresh, depending on AT diffing.

### 1.5 Findings that matter for the design system

1. **The bar is keyed; the popup is not.** The bar uses `Keyed.node` with `"control:"++identity` (`:64`). Popup controls use plain `List.map control` (`:63`). Popup DOM identity can therefore be reused across reorders, which is the hazard ELM-ADOPT-016 targets.
2. **There are two independent polite live regions with the same `status` text,** one in the bar (`:64`) and one in the popup (`:63`). ELM-ADOPT-017 says that "multiple read-only status regions do not establish a single AT announcement."
3. **The menu uses `aria-current="true"` for selection, driven by the string `detail=="Selected"`** (`:62`). That is a semantic and stringly-typed coupling. ARIA menus convey position through focus (roving tabindex or `aria-activedescendant`), not `aria-current`.
4. **Disabled controls use HTML `disabled`** (`:62`), which removes them from focus. That matches Windows defaults but forecloses the APG `aria-disabled` option that ELM-ADOPT-030 explicitly keeps open per surface.
5. **Toggles exist in the model but not in semantics.** No `menuitemcheckbox` and no `aria-checked`.
6. **Repeat activation while Pending does nothing visible.** This is correct for safety (no second intent), but there is no feedback hook. ELM-ADOPT-020 asks for one.

---

## 2. Reference research and borrow matrix

**Access notes (reported honestly):**
- **m3.material.io returned only page titles** for every page I tried: states overview and applying-states, menus guidelines, density blog. Material claims below come from Google's own `material-components/material-web` repository, which I fetched, or are marked **snippet-only**. Snippet-only means a search-engine excerpt of an m3.material.io URL that I could not fetch. Nothing snippet-only is used as a binding number.
- **Apple HIG HTML returned no body.** I fetched Apple's own content via the developer.apple.com JSON data endpoints instead.
- **Windows' Standard/Compact sizing page** now redirects to "Content layout and spacing", so the compact values are snippet-only.
- **Fluent 2's homepage** had no token or focus content.
- **KDE "Getting input"** has no keyboard content.

| Family | Borrow | Adapt | Reject | Defer |
|---|---|---|---|---|
| **Material 3** | Component-page structure (overview, guidelines, specs, accessibility) for the catalog; focus is a **ring, not a state layer**: "Focus ripples were removed in the Material spec in favor of focus rings, which are more accessible. Ripples only indicate hover and pressed states now." ([material-web#5566](https://github.com/material-components/material-web/discussions/5566)); focus ring appears with `:focus-visible` heuristics ([focus-ring.md](https://github.com/material-components/material-web/blob/main/docs/components/focus-ring.md)) | State-layer *concept* (hover/pressed overlays as tokens) with Warlock-measured values; density scale as an idea (0 / −1…−3, 4px per step: **snippet-only**, [density](https://m3.material.io/foundations/layout/understanding-layout/density)) | Material visual identity, ripple, tonal palette and Roboto; M3 opacity numerics (unverified, and two secondary sources disagree, 10% vs 12% focus/pressed) | 48px "regardless of density" target (snippet-only): Warlock declares no touch input today |
| **Windows / Fluent** | Two-part high-visibility focus visual: "primary border is **2px** … secondary border is **1px** … default margin is **1px**" ([visual feedback](https://learn.microsoft.com/en-us/windows/apps/design/input/guidelines-for-visualfeedback)); popup cycling: "Down arrow key always sets focus to the first item while the Up arrow key always sets focus to the last … Cycling should be avoided in non-popup UIs" ([keyboard interactions](https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions)); Esc "cancel[s] transient UI"; Enter vs Space semantics; spacing 8/12/16 epx ([content basics](https://learn.microsoft.com/en-us/windows/apps/design/basics/content-basics)); `ToggleMenuFlyoutItem`/`RadioMenuFlyoutItem` item kinds ([menus](https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/menus)) | Control groups with one tab stop plus arrows; F6 region cycling ("You must implement F6 navigation explicitly" ([keyboard accessibility](https://learn.microsoft.com/en-us/windows/apps/design/accessibility/keyboard-accessibility))); compact sizing as opt-in and pointer-oriented (snippet-only via search) | Fluent brand, acrylic/Mica, Segoe; Reveal focus | F6 as a *shell* shortcut (conflicts with the ELM-ADOPT-029 "not a new default shortcut" guardrail) |
| **Apple HIG** | Focus ≠ selection: "In many cases, focusing an item also selects it. The exception is when automatic selection might cause a distracting context shift" ([focus and selection](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/focus-and-selection.json)); checkmarks for in-effect attributes; ellipsis "when the action requires more information" ([menus](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/menus.json)) | Context-menu ordering by proximity to the invoking point | "Hide unavailable menu items, don't dim them" ([context menus](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/context-menus.json)) for the *window* menu (see D1) | "Show keyboard shortcuts … not in context menus" (pending the shortcut policy) |
| **GNOME HIG** | Verbs for commands, adjectives for settings; "Order items logically … top and bottom … are more noticeable" ([menus](https://developer.gnome.org/hig/patterns/controls/menus.html)); "every action should also be possible with the keyboard" ([keyboard](https://developer.gnome.org/hig/guidelines/keyboard.html)) | Access keys (Alt+letter) only after IME/composition policy (ELM-ADOPT-018) | "Provide an access key for every menu item" as a hard rule | Shortcut assignment |
| **KDE HIG** | "Indicate success by visually changing something … not by sending a message" ([status changes](https://develop.kde.org/hig/status_changes/)); actionable errors; focus "visibly different from selected items" and AT names as "label and type", with "no labels … used more than once in the same window" ([accessibility](https://develop.kde.org/hig/accessibility/)) | Error-recovery ordering (prevent → fix-it → describe) | OSD and task-manager badges as product features | — |
| **Impeccable** (vendored @87a6ab0, Apache-2.0) | "The brief wins" (pinned brand overrides its reflex-face list, which names Space Grotesk and Inter); Operate mode: "native controls in an app," world lends "type, palette, density, and one signature move"; craft floor: states "hover, disabled, loading, error, empty … keyboard focus", "errors name the problem and the recovery", theme focus rings and selection | Audit's five dimensions as the catalog's QA rubric; Read mode for the website | Its launcher/comp pipeline for this research packet (unavailable here); glow halos (already banned by the brand) | 44px touch-target audit item (web-mobile oriented) |

The target floor comes from [WCAG 2.2 SC 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html): "at least 24 by 24 CSS pixels". The disabled-focusability option comes from [WAI-ARIA APG](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/): "aria-disabled=\"true\" is applied so that it will remain focusable" for menu items, tabs and options.

**Pattern vs platform requirement:** everything above is borrowed as a *pattern*. None of it creates a WinUI, GTK, Qt or AppKit implementation requirement. Warlock's native authority is its own compositor, AT bridge and IME route. Platform APIs (`IsTabStop`, `UseSystemFocusVisuals`, `Compact.xaml`) are cited only as evidence of the pattern.

---

## 3. Proposals

IDs are stable local IDs, `WLK-WGT-01` to `WLK-WGT-12`. Each one keeps the single immutable Elm policy: proposals change renderer semantics, tokens and the wire *presentation* shape only through versioned, additive decoders.

### WLK-WGT-01: Source-traced widget registry and catalog coverage gate. Decision: **Adopt**

The catalog must be generated from, and checked against, source rather than hand-written.

- [P] `widgets.json` lists each widget W1–W11 with: source file:line, emitted class/role/mode strings, states, bounds, and evidence level per state (S/P/B/N).
- **EARS:** *When the catalog is built, the build shall fail if any class, role, `data-mode` value, identity prefix or Status/Phase constructor present in the referenced Elm sources is absent from the registry.*
- **Acceptance:**
  - (a) Removing `control-recovery` from the registry fails the build.
  - (b) Adding a fifth popup mode to `SurfaceRenderer.elm:34` without a registry entry fails.
  - (c) Each registry state shows its evidence badge, and no state shows [N] without a linked native receipt ID.
- **Dependencies:** access to the full module set (the gap in §1.1). **Risk:** low. Scraping strings from source is brittle, so prefer exported Elm enumerations.

### WLK-WGT-02: Two-axis state model: interaction × outcome. Decision: **Adapt** (Material/Windows have only the interaction axis)

[P] Every actionable widget declares:
- **Interaction axis:** rest, hover, pressed, focus-visible, disabled, selected, checked.
- **Outcome axis:** none, pending, refused, cancelled, unknown. Committed is transient: the menu closes on Committed (`Menu.elm:512`).

The axes are orthogonal. Outcome is never encoded by color alone (`tokens.json` `colorNeverSoleSignal`), and decorative gold/mint never represents outcome (BRAND-GUIDE §Color).

- **EARS:** *While a control's target has an outstanding Pending or Unknown intent, the surface shall render a text outcome indicator on that control and shall not emit a second intent for the same target when the control is activated again.*
- **Acceptance:**
  - [S] already: `Activate` on an outstanding target returns no effect (`Menu.elm:466-467`).
  - [P] the second activation produces exactly one visible, non-announced "Still waiting for the previous request" cue.
  - [B] a demo injects Uncertain and shows Unknown persisting after Dismiss and reopening (`Menu.elm:429-432`).
- **Dependencies:** ELM-ADOPT-011, -020; W07. **Risk:** wire-shape change. `Control` is strictly decoded (`SurfaceRenderer.elm:23`), so this needs `surfaceProtocol` 3 with dual decoding, not a silent field addition.

### WLK-WGT-03: State-layer and disabled tokens. Decision: **Adapt** (concept from M3; values Warlock-measured; M3 numerics rejected)

[P] Add these tokens:
- `state.hover`, `state.pressed`, `state.selected`, `state.disabledContent`, `state.disabledContainer` as parchment-over-surface overlays (dark theme) and ink-over-white overlays (light theme).
- `pressed` must be stronger than `hover`.
- No focus overlay (see WGT-04).
- Selected adds a non-color cue: the existing `control-detail` text, plus a 2px lilac indicator on taskbar groups. This is a small indicator mark, not a side-stripe border, which Impeccable bans for cards and lists.

- **EARS:** *The design system shall define each interaction state as a token whose rendered result meets ≥3:1 non-text contrast for component boundaries and ≥4.5:1 for text against its actual state background, in both themes.*
- **Acceptance:** a contrast table generated from the tokens. My own spot computations from `tokens.json`:
  - lilac `#B7A2FF` on ink `#10111A` ≈ 8.6:1
  - lilac on surface `#1B1E2B` ≈ 7.6:1
  - border `#68718C` on surface ≈ 3.4:1
  - light border `#838A9A` on white ≈ 3.5:1
  
  These are reviewer arithmetic and need tool verification.
- **Dependencies:** a CSS host (not in inputs). **Risk:** disabled text at reduced alpha commonly fails 4.5:1. WCAG exempts inactive components, but Warlock's "explain unavailable actions" voice means the disabled *reason* text must still meet 4.5:1.

### WLK-WGT-04: Two-tone keyboard focus indicator. Decision: **Borrow** (Windows structure; M3 `:focus-visible` behavior)

[P] Tokens:
- `focus.outer` = 2px solid lilac (dark) / `#583DA4` (light)
- `focus.inner` = 1px ink (dark) / white (light)
- `focus.offset` = 1px
- no glow (BRAND-GUIDE: "Keep glows out of … ordinary controls")
- shown on keyboard-modality focus only
- no animation under reduced motion

- **EARS:** *When a control receives keyboard focus, the surface shall draw a 2px outer and 1px inner focus indicator that is visually distinct from the selected and hover states and meets ≥3:1 against adjacent colors.*
- **Acceptance:**
  - [B] Tab through bar and popup demos at 100% and 200% zoom in both themes. The focus indicator differs from the `selected` treatment (KDE: focus "visibly different from selected").
  - [N] compositor-captured frames at 1× and 2× output scale on the owning ABI tuple show the ring unclipped at surface edges.
- **Dependencies:** WGT-03, ELM-ADOPT-019. **Risk:** clipping at popup edges, since the WebView surface bounds are native-owned. Reserve a 4px inset in popup padding.

### WLK-WGT-05: Desktop density and spacing ramp. Decision: **Adapt**

[P] Tokens:
- `space` = 4 / 8 / 12 / 16 / 24 (Windows 8/12/16 epx relationships)
- `size.control.standard` = 40px (Windows 40×40 target)
- `size.control.compact` = 32px, opt-in, pointer/keyboard only
- `size.control.floor` = 24px (WCAG 2.5.8)
- Bar and popup take density from one setting, so customization keeps the same interaction guarantees (PHILOSOPHY §8).

- **EARS:** *Where compact density is selected, the surface shall render no actionable target smaller than 24×24 CSS px and shall preserve label text, focus indicator and outcome indicator without truncating the accessible name.*
- **Acceptance:**
  - [B] a demo toggles density with 64 menu items (`maxItems`) and 256-unit labels (`maxLabel`) at 200% text.
  - [N] constrained-output qualification under ELM-ADOPT-019.
- **Dependencies:** ELM-ADOPT-019; the frozen per-surface budget. **Risk:** 32px compact rows with two text spans (label + detail) can crowd. Detail may need to wrap rather than truncate.

### WLK-WGT-06: Popup menu keyboard and dismissal contract. Decision: **Adapt** (Windows popup rules; APG semantics)

[S] Already present: cycling Up/Down, Home/End, skipping disabled items, initial focus on the first enabled item.
[P] Add, as a published table bound in the bridge:

| Key | Menu mode | Picker / applications mode |
|---|---|---|
| ↓ / ↑ | next/prev enabled; cycles [S] | same (popup ⇒ cycling allowed) |
| Home / End | first/last enabled [S] | same |
| Enter, Space | `Activate` the selected item | `Activate`, selecting the family/entry |
| Esc | `Dismiss`; return focus to the invoker *only if* that invoker identity survives (ELM-ADOPT-016) | same |
| Tab | does not move between items; native policy decides | same |
| Printable char | typeahead (**defer** until ELM-ADOPT-018 composition ownership) | defer |

- **EARS:** *When Escape is pressed while a popup is open, the controller shall dismiss that popup by MenuId without cancelling any Pending or Unknown intent, and the intent shall remain blocking for its binding.*
- **Acceptance:**
  - [B] Activate → Pending → Esc → reopen shows Pending/Unknown (consistent with `Menu.elm:429-432`).
  - [N] keyboard transcript on the native popup with focus return (W07).
- **Dependencies:** W07, ELM-ADOPT-016, -029, -030. **Risk:** Esc in a popup must be consumed natively and must not leak to the focused application.

### WLK-WGT-07: Menu item semantics. Decision: **Adapt** (toggles from Windows/Apple; partially reject Apple's hide rule)

[P] Covers three things:
- **Toggles:** `AlwaysOnTop`/`PinToTaskbar` render as `menuitemcheckbox` with `aria-checked` plus a visible check glyph from the icon set (Impeccable bans Unicode glyph icons).
- **Selection:** replace `aria-current`/`"Selected"` string coupling with a typed `selected` field, using roving tabindex or `aria-activedescendant`.
- **Disabled items:** use a per-surface `disabledPolicy ∈ {skip, focusableAriaDisabled}`, frozen under ELM-ADOPT-030. Default for the window menu: dim and skip, matching current source and Windows. Provider/declared commands: providers omit inapplicable items, following Apple's context-menu rule at the provider layer.

- **EARS:** *Where a menu item's action is a toggle, the popup shall expose its current state as checked or unchecked in both its accessible state and its visible rendering, and that state shall be derived from controller observation, not from the item label.*
- **Acceptance:**
  - [B] the AT tree in browser devtools shows `menuitemcheckbox[aria-checked=true]` for an observed always-on-top window.
  - [N] the native AT transcript reads "Always on top, checked, menu item."
- **Dependencies:** WGT-02 (protocol 3), ELM-ADOPT-017, -030. **Risk:** the "checked" state comes from observation, which can be stale. During Pending it must show the *observed* value plus the pending indicator, never the optimistic one.

### WLK-WGT-08: Keyed popup controls. Decision: **Adopt**

[P] Render popup controls with `Html.Keyed` on `"control:"++identity`, as the bar already does (`SurfaceRenderer.elm:64`).

- **EARS:** *When a popup publication reorders, inserts or removes controls, the renderer shall preserve DOM identity, and therefore focus, for every control whose surface identity persists.*
- **Acceptance:**
  - [B] focus the 3rd picker entry, publish a snapshot inserting one entry above it, and focus stays on the same identity.
  - [N] ELM-ADOPT-016 scenarios.
- **Dependencies:** ELM-ADOPT-016. **Risk:** low. The source rejects duplicate identities, so the keys are unique.

### WLK-WGT-09: Taskbar as one keyboard group (toolbar). Decision: **Defer** native; [B] specification only

[P] The bar becomes `role=toolbar` with one tab stop, Left/Right moving between groups (no cycling, per Windows non-popup guidance), Home/End, and Enter/Space applying `Taskbar.primary`. Entry and exit stay with native scope.

- **EARS:** *While the taskbar holds native keyboard scope, Left and Right arrow keys shall move focus between enabled bar controls without wrapping and without changing activation history.*
- **Acceptance:** [B] demo only. [N] remains ELM-ADOPT-029 P5.
- **Dependencies:** ELM-ADOPT-029 (P5, feasibility-only now), W07. **Risk:** must not introduce a default shortcut or alter MRU (workplan guardrail). I explicitly do **not** propose F6 as a shell binding.

### WLK-WGT-10: Single announcement owner. Decision: **Adopt**

[P] Exactly one live region per controller-designated owner. The other status texts become `aria-live="off"` (still visible). Success is shown visually, not announced: "Connected" is not re-announced on routine refresh (KDE).

- **EARS:** *When the shared status text changes, assistive technology shall receive at most one announcement for that change across bar and popup surfaces, and an unchanged outcome shall not be re-announced.*
- **Acceptance:**
  - [B] the DOM shows one `aria-live` region among the bar and popup documents.
  - [N] a speech/braille transcript per ELM-ADOPT-012 shows one utterance, including when application focus is outside the shell.
- **Dependencies:** ELM-ADOPT-012, -017; W08. **Risk:** a cross-WebView owner needs the native bridge. ARIA alone is insufficient (workplan).

### WLK-WGT-11: Status copy catalog. Decision: **Adopt**

[P] Move all 21 Shell strings and the Menu limit string into a bounded, localizable catalog keyed by reason. Rewrite the two internal geometry strings:
- "Geometry refresh pending" → "Window size information is updating. Try again in a moment."
- "Geometry observation unavailable" → "Window size information is unavailable. Choose another action."

Pending, committed, refused, cancelled, presented and unconfirmed keep distinct wording.

- **EARS:** *The shell shall display only catalog-defined status text, each entry naming the condition and a safe next step, and an unknown reason within a validated Refused class shall use generic refusal text without inventing a reason.*
- **Acceptance:** [B] the catalog page lists every key alongside its source constructor. A lint check ensures no literal user-facing string appears in `Shell.elm`/`Menu.elm` outside the catalog.
- **Dependencies:** ELM-ADOPT-011. **Risk:** low. Translation is not a release gate.

### WLK-WGT-12: Preview tile freshness states. Decision: **Defer**

[P, catalog-only] Document the observable tile states: no tile, pending, shown, closed-but-retained (`PreviewPresenter.elm:59-68`). Do not introduce "live/stale" labels until the frozen historical/live/unavailable policy is reviewed.

- **EARS:** *While a preview frame's freshness is not established by native evidence, the tile shall not be labeled as current or live.*
- **Acceptance:** [B] the catalog shows the tile with a "Browser demonstration: synthetic image" badge. [N] S09 preview13, unchanged.
- **Dependencies:** ELM-ADOPT-028, W03/W06. **Risk:** demo imagery mistaken for capture evidence. Mark it synthetic on the frame itself.

---

## 4. Component API and token sketch [P]

```elm
-- surfaceProtocol 3 (dual-decoded with 2); additive, strict
type Kind = Group | Recovery | Utility | PickerEntry | AppEntry | MenuCommand | MenuToggle
type OutcomeState = NoOutcome | PendingOutcome | RefusedOutcome | CancelledOutcome | UnknownOutcome
type DisabledPolicy = Skip | FocusableAriaDisabled
type alias Control =
    { identity : String, domId : String, label : String, ariaLabel : String
    , detail : String, enabled : Bool, kind : Kind
    , selected : Bool, checked : Maybe Bool, outcome : OutcomeState }
-- per-surface, frozen under ELM-ADOPT-030
type alias SurfacePolicy = { disabled : DisabledPolicy, density : Density, liveOwner : Bool }
```

```json
{"space":{"1":4,"2":8,"3":12,"4":16,"6":24},
 "size":{"control":{"standard":40,"compact":32,"floor":24},"menuIcon":16},
 "focus":{"outerPx":2,"innerPx":1,"offsetPx":1,
          "dark":{"outer":"lilac","inner":"ink"},"light":{"outer":"#583DA4","inner":"#FFFFFF"}},
 "state":{"hover":"TBD-measured","pressed":"TBD-measured>hover","selectedIndicatorPx":2,
          "disabled":"TBD-measured; reason text ≥4.5:1"},
 "density":{"default":"standard","compactRequiresNoTouch":true}}
```

The 16px menu icon size comes from Windows: "The size of the icon in a MenuFlyoutItem is 16x16px" ([menus](https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/menus)).

---

## 5. Accessibility and keyboard contract summary

| Widget | Role / name | States exposed | Keys | Evidence now |
|---|---|---|---|---|
| Taskbar group | button; name = stable label; transient state in description (ELM-ADOPT-017) | pressed? no; `aria-disabled`/disabled per policy; active via text detail | Enter/Space = `primary`; arrows per WGT-09 (deferred) | [S] role/name; [N] none |
| Recovery / utility | button | disabled | Enter/Space | [S] |
| Status | one live owner (WGT-10) | — | — | [S] two regions (gap) |
| Popup | menu or group; heading per mode | — | per WGT-06 table | [S] roles; keys in unsupplied bridge |
| Menu item | menuitem / menuitemcheckbox | disabled, checked, outcome | Enter/Space/Esc/arrows | [S] partial |
| Preview tile | decorative within its button (button name carries the title) | — | none | [S] via unsupplied `inlineView` |

Cross-cutting rules:
- Keyboard, pointer, speech, braille and IME share one contract (PHILOSOPHY §6).
- Focus is never moved by announcements.
- Reduced motion is honored live.
- Name ≠ transient state (ELM-ADOPT-017).
- AT should read "label and type" (KDE).
- No duplicate labels in one surface (KDE). The source already enforces unique identity and domId, but not unique labels. **Proposed lint:** reject duplicate `ariaLabel` within one surface, or disambiguate with the application name.

---

## 6. Proposed catalog website ("Warlock Widgets")

**Mode:** Impeccable *Read*. Docs index is Read, not Persuade. Brand lives in type (Space Grotesk headings, Inter body, JetBrains Mono for wire/IDs only), the ink/parchment palette, and one signature move: **the outcome ribbon**. This is a marble-style strip under each live demo that plots each intent as an event dot transitioning Pending → Committed/Refused/Unknown, using the brand's ReactiveX-derived grammar. It is labeled as a metaphor, not protocol evidence (BRAND-GUIDE §Community).

**Information architecture:**

1. **Overview:** the philosophy sentence, the evidence legend (S/P/B/N), and "what a browser demo cannot prove".
2. **Foundations:** color (both themes, contrast table), typography, density and spacing, focus, the two-axis state model, motion (paused by default, explicit toggle, stops when hidden, reduced-motion live), voice and the status copy catalog.
3. **Widgets** (one page each, with Overview / Anatomy / States / Keyboard & AT / Bounds / Source / Evidence tabs, the structure borrowed from M3 component pages): Taskbar group button, Recovery button, Utility button, Status region, Popup surface (picker / applications / menu modes), Menu item (command / toggle / declared), Preview tile, Application entry.
4. **Patterns:** outcome lifecycle; reconnect and recovery (five recovery notices); "Window list changed. Choose again."; unsent request; limit reached; exhausted.
5. **Accessibility:** a full keyboard map, the AT naming policy, the announcement policy and the disabled policy per surface.
6. **Evidence matrix:** widget × state × {S, P, B, N} with links to source lines and, later, native receipts. All [N] cells are currently empty.
7. **References:** the borrow matrix with URLs, Impeccable provenance (commit 87a6ab0) and inaccessible-source notes.

**Interactive demos (browser [B]):**
- Compile the **actual** `SurfaceRenderer`, `Menu`, `Taskbar` and `Catalog` modules against a synthetic `Presentation` feed. Data is labeled "Synthetic data", and every snapshot passes the real strict decoders, so the demo also exercises the bounds.
- **State scrubber:** pick a Taskbar family row from the §1.4 table and see the rendered decision.
- **Receipt injector:** send Committed / Refusal(256-unit) / Cancellation / Uncertain to `Menu.update`. Shows Unknown surviving dismissal, the silent repeat-activation case, and the limit at 64 outstanding.
- **Capacity stress:** 259 bar controls, 2051 popup controls, 64 menu items, 1024-unit labels.
- **Density and theme toggles,** plus a 200% text toggle.
- Every demo frame carries a "Browser demonstration — not native acceptance" badge. No demo shows a real window capture.

**Coverage gate:** WGT-01 requires one demo cell per (widget, reachable state).

**Distribution:** a static offline build with bundled fonts and their licenses, and no external requests.

---

## 7. Disagreements and tradeoffs for peer review

- **D1. Dim vs hide unavailable items.**
  - Apple says context menus *hide* unavailable items.
  - Apple's regular menus and Windows *dim* them.
  - The current source dims and skips.
  - **My position:** the window menu is a stable, learned set, so dim it; provider items are omitted by the provider. Reviewers favoring Apple may want "hide" everywhere.
- **D2. Disabled focusability.** Windows removes disabled controls from tab order; APG keeps menu items focusable with `aria-disabled`. The current HTML `disabled` prevents the APG option. ELM-ADOPT-030 forbids a universal rule. I propose a per-surface flag; a reviewer may prefer freezing "skip" now to avoid a protocol bump.
- **D3. Shortcut display.** Apple: no shortcuts in context menus. GNOME: an access key for every menu item. Windows: accelerators documented in menus and tooltips. I defer all shortcut display until the shortcut and IME policy exists.
- **D4. Target size.** The M3 snippet implies a 48px floor; Windows compact is pointer-oriented and smaller; WCAG sets 24px. I choose a 40px standard and 32px opt-in compact with a 24px floor, contingent on touch not being a declared input. If touch is in scope, compact must be refused on touch outputs.
- **D5. F6.** It is useful for region cycling, but would be a new default shortcut, which conflicts with the ELM-ADOPT-029 guardrail. I rejected it for now.
- **D6. Impeccable's reflex-face list vs the brand.** Impeccable flags Space Grotesk and Inter. The brand pins them, and "The brief wins." I keep them. A reviewer applying Impeccable mechanically would flag this incorrectly.
- **D7. Announcing success.** KDE says don't announce routine success. The Philosophy asks for honest outcome reporting. My compromise: announce Refused and Unknown always, announce Committed only when the user initiated the action and focus is outside the visual change, and never announce "Connected" on a routine refresh.
- **D8. Optimistic toggles.** Material and Windows toggles typically flip immediately. Warlock must show the observed value plus a pending cue (WGT-07). This is a deliberate divergence from both platforms, required by native authority.
- **D9. Wire change.** WGT-02 and WGT-07 need `surfaceProtocol` 3. Peers may prefer to encode outcome and checked state in `detail` text to avoid a version bump. I argue the stringly-typed `"Selected"` coupling is already a defect.

---

```json
[
 {"id":"WLK-WGT-01","title":"Source-traced widget registry and catalog coverage gate","decision":"adopt","ears":"When the catalog is built, the build shall fail if any class, role, data-mode value, identity prefix or Status/Phase constructor present in the referenced Elm sources is absent from the registry.","acceptance":["Removing control-recovery from registry fails build","New popup mode without registry entry fails","No [N] badge without linked native receipt"],"sourceUrls":["https://github.com/material-components/material-web/blob/main/docs/components/menu.md","https://github.com/pbakaus/impeccable"],"dependencies":["full module set incl. Presentation, PreviewLifecycle"]},
 {"id":"WLK-WGT-02","title":"Two-axis state model: interaction x outcome","decision":"adapt","ears":"While a control's target has an outstanding Pending or Unknown intent, the surface shall render a text outcome indicator on that control and shall not emit a second intent for the same target when the control is activated again.","acceptance":["Repeat Activate on outstanding target yields no Dispatch (Menu.elm:466-467)","Second activation shows one non-announced waiting cue","Unknown persists across Dismiss and reopen (browser demo)"],"sourceUrls":["https://develop.kde.org/hig/status_changes/","https://learn.microsoft.com/en-us/windows/apps/design/input/guidelines-for-visualfeedback"],"dependencies":["ELM-ADOPT-011","ELM-ADOPT-020","W07","surfaceProtocol 3"]},
 {"id":"WLK-WGT-03","title":"Measured state-layer and disabled tokens","decision":"adapt","ears":"The design system shall define each interaction state as a token whose rendered result meets >=3:1 non-text contrast for component boundaries and >=4.5:1 for text against its actual state background, in both themes.","acceptance":["Generated contrast table for every state token in both themes","Disabled reason text >=4.5:1","Selected uses a non-color cue"],"sourceUrls":["https://github.com/material-components/material-web/discussions/5566","https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html"],"dependencies":["CSS host source","ELM-ADOPT-019"]},
 {"id":"WLK-WGT-04","title":"Two-tone keyboard focus indicator","decision":"borrow","ears":"When a control receives keyboard focus, the surface shall draw a 2px outer and 1px inner focus indicator that is visually distinct from the selected and hover states and meets >=3:1 against adjacent colors.","acceptance":["Browser: Tab through bar/popup at 100% and 200% both themes","Focus distinct from selected","Native: unclipped ring in compositor frames at 1x/2x"],"sourceUrls":["https://learn.microsoft.com/en-us/windows/apps/design/input/guidelines-for-visualfeedback","https://github.com/material-components/material-web/blob/main/docs/components/focus-ring.md","https://develop.kde.org/hig/accessibility/"],"dependencies":["WLK-WGT-03","ELM-ADOPT-019"]},
 {"id":"WLK-WGT-05","title":"Desktop density and spacing ramp","decision":"adapt","ears":"Where compact density is selected, the surface shall render no actionable target smaller than 24x24 CSS px and shall preserve label text, focus indicator and outcome indicator without truncating the accessible name.","acceptance":["64 items x 256-unit labels at 200% text in compact","No target <24px","Native constrained-output qualification under ELM-ADOPT-019"],"sourceUrls":["https://learn.microsoft.com/en-us/windows/apps/design/basics/content-basics","https://learn.microsoft.com/en-gb/windows/apps/develop/input/guidelines-for-targeting","https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html","https://m3.material.io/foundations/layout/understanding-layout/density"],"dependencies":["ELM-ADOPT-019","touch-input scope decision"]},
 {"id":"WLK-WGT-06","title":"Popup menu keyboard and dismissal contract","decision":"adapt","ears":"When Escape is pressed while a popup is open, the controller shall dismiss that popup by MenuId without cancelling any Pending or Unknown intent, and the intent shall remain blocking for its binding.","acceptance":["Activate->Pending->Esc->reopen shows Pending/Unknown","Up/Down cycle, Home/End (existing)","Native keyboard transcript with focus return"],"sourceUrls":["https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions","https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/"],"dependencies":["W07","ELM-ADOPT-016","ELM-ADOPT-018","ELM-ADOPT-030"]},
 {"id":"WLK-WGT-07","title":"Menu item semantics: checkable toggles, typed selection, per-surface disabled policy","decision":"adapt","ears":"Where a menu item's action is a toggle, the popup shall expose its current state as checked or unchecked in both its accessible state and its visible rendering, and that state shall be derived from controller observation, not from the item label.","acceptance":["menuitemcheckbox aria-checked reflects observed state","During Pending shows observed value plus pending cue","No aria-current/'Selected' string coupling"],"sourceUrls":["https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/menus","https://developer.apple.com/tutorials/data/design/human-interface-guidelines/menus.json","https://developer.apple.com/tutorials/data/design/human-interface-guidelines/context-menus.json","https://developer.gnome.org/hig/patterns/controls/menus.html"],"dependencies":["WLK-WGT-02","ELM-ADOPT-017","ELM-ADOPT-030"]},
 {"id":"WLK-WGT-08","title":"Keyed popup controls","decision":"adopt","ears":"When a popup publication reorders, inserts or removes controls, the renderer shall preserve DOM identity, and therefore focus, for every control whose surface identity persists.","acceptance":["Focus on 3rd picker entry survives insertion above it","ELM-ADOPT-016 scenarios"],"sourceUrls":["https://developer.apple.com/tutorials/data/design/human-interface-guidelines/focus-and-selection.json"],"dependencies":["ELM-ADOPT-016"]},
 {"id":"WLK-WGT-09","title":"Taskbar as one keyboard group (toolbar)","decision":"defer","ears":"While the taskbar holds native keyboard scope, Left and Right arrow keys shall move focus between enabled bar controls without wrapping and without changing activation history.","acceptance":["Browser demo only","Native remains ELM-ADOPT-029 P5"],"sourceUrls":["https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions","https://learn.microsoft.com/en-us/windows/apps/design/accessibility/keyboard-accessibility"],"dependencies":["ELM-ADOPT-029","W07"]},
 {"id":"WLK-WGT-10","title":"Single announcement owner","decision":"adopt","ears":"When the shared status text changes, assistive technology shall receive at most one announcement for that change across bar and popup surfaces, and an unchanged outcome shall not be re-announced.","acceptance":["One aria-live region across bar and popup documents","Native speech/braille transcript shows one utterance"],"sourceUrls":["https://develop.kde.org/hig/status_changes/"],"dependencies":["ELM-ADOPT-012","ELM-ADOPT-017","W08"]},
 {"id":"WLK-WGT-11","title":"Status copy catalog","decision":"adopt","ears":"The shell shall display only catalog-defined status text, each entry naming the condition and a safe next step, and an unknown reason within a validated Refused class shall use generic refusal text without inventing a reason.","acceptance":["Every Shell/Menu string mapped to a catalog key","Geometry strings rewritten in plain language","Lint rejects literal user-facing strings outside catalog"],"sourceUrls":["https://develop.kde.org/hig/status_changes/","https://github.com/pbakaus/impeccable"],"dependencies":["ELM-ADOPT-011"]},
 {"id":"WLK-WGT-12","title":"Preview tile freshness states","decision":"defer","ears":"While a preview frame's freshness is not established by native evidence, the tile shall not be labeled as current or live.","acceptance":["Catalog tile carries synthetic badge","S09 preview13 unchanged"],"sourceUrls":["https://develop.kde.org/hig/status_changes/"],"dependencies":["ELM-ADOPT-028","W03","W06"]}
]
```
