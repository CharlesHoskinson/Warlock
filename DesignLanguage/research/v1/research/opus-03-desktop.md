# Warlock design review: desktop workflow (reviewer opus-03-desktop)

**Scope.** I studied taskbar, window preview, menu, launch, status, settings, snapping and workspace patterns against the Warlock frozen inputs, with KDE Plasma and GNOME as the primary references. I worked read-only from the frozen project context. The Impeccable launcher was not run, so I read the project context directly, as its SKILL.md requires. Because this is planning only, I did not load `craft-floor.md`; SKILL.md says it is only for edits.

**Status.** Everything below is an additive draft from one reviewer. It does not change the 242 requirements / 417 scenarios, S01–S16, right-click24, W01–W12 edges or the original deadlines. No consensus exists until all five reviewers vote on the exact consolidated proposal.

**Evidence levels used throughout.** These four levels stay separate:
- **[S] Existing source**: the code is present in `inputs/implementation/warlock-preview-provider-v1/src`.
- **[P] Proposed addition**: not implemented.
- **[B] Browser demonstration**: catalog or demo behavior. It can show the browser-side policy and rendering only.
- **[N] Native acceptance**: requires owning-ABI compositor, AT, IME or hardware receipts. Nothing in this report has [N] status.

---

## 1. Design inventory and source traceability

### 1.1 Widgets and behaviors in the frozen source

| Widget / behavior | Source | What the code actually does |
|---|---|---|
| **Taskbar bar surface** | `SurfaceRenderer.elm:64`, `Bar.elm:16-25` | A keyed `div.surface-bar` of `button`s plus one `role=status aria-live=polite` span. Bar.elm owns only a presentation cache: "A display owns only a presentation cache. It cannot run Desktop.update" (`Bar.elm:16`). |
| Control classes | `SurfaceRenderer.elm:61` | `control-group` (identity prefix `bar:group:`), `control-recovery` (`bar:recovery-refresh`) and `control-utility` (everything else). |
| Control wire shape | `SurfaceRenderer.elm:11,23` | `{id, domId, label, ariaLabel, detail, enabled}`. Text is bounded at 512/1024/1024/1024/128 characters. Limits: bar ≤259 controls, popup ≤2051. |
| **Popup surface modes** | `SurfaceRenderer.elm:34,63` | `closed \| picker \| applications \| menu`. Headings: "Choose a window", "Applications", "Window actions". There is a polite status paragraph. Items use `role=menuitem` in menu mode and `button` otherwise. |
| **Grouping and primary click** | `Taskbar.elm:14-33` | Windows are grouped by application hint, or by `window:<incarnation>` when the hint is empty. Transient children never add entries. `primary`: no family + pinned → `Launch`; one family that is unavailable → `Unavailable`; minimized → `Restore`; active → `Minimize`; otherwise `Activate`; more than one family → `Picker`. |
| **Picker selection** | `Taskbar.elm:34-36` | Restores the window if minimized, otherwise activates it. Unavailable windows are not acted on. |
| **Window preview** | `PreviewPresenter.elm`, `Popup.elm:27` | A preview is seeded only while mode is `picker` and its publication/lease stamp matches (`:53-54`). Identity is `family:<incarnation>`; a preview cannot take over another window's subject (`:44-51`). Closing the UI cancels demand but keeps the lifecycle (`:59-60`). Capacity is 2051. The inline view takes `{title, application, icon=Nothing}`. |
| **Window actions menu (model)** | `Menu.elm` | Actions: `Restore, RestoreGeometry, Move, Size, Minimize, Maximize, Close, ExitFullscreen, AlwaysOnTop, PinToTaskbar, Launch, ProviderCommand`. Targets: `Window \| Application \| ProviderSelection \| Background`. Status: `Ready \| Pending \| Refused \| Cancelled \| Unknown`. Navigation (Up/Down/Home/End) skips disabled items and wraps (`:294-328`). The initial selection is the first enabled item. `Committed` closes the menu. A second activation on the same target is blocked while one is outstanding (`:466`). Bounds: 64 items / 256-unit labels / 64 outstanding / 128 retired. |
| **Launcher catalog** | `Catalog.elm` | Entries `{id, name, iconHint, wmclass}`, at most 2048, with strict decoding. A launch intent is bound to request/lifetime/generation. |
| **Shell status and recovery text** | `Shell.elm:23-29,68-76` | Phases `Detached \| Reconciling \| Ready \| Exhausted`. Messages include "Applying window change…", "…could not be confirmed.", "…was refused.", "Window list changed. Choose again." and five actionable recovery notices ("…Free space, then reconnect."). |
| **Outcome protocol** | `NativeOutcome.elm:31,42` | Protocol 1 covers minimize/restore/activate; protocol 2 covers maximize/restore-geometry. Status is `Committed \| Refused \| Unknown`. |
| Choice/prepared deadlines | `Main.elm:36-38` | 2000 ms for prepared and choice, 10000 ms for the arm timer. These are existing timers. The catalog must not present them as UX promises. |

### 1.2 Gaps: workflow surfaces with no frozen source

- **Workspaces/virtual desktops**: no source exists.
- **Snapping and tiling**: only `Maximize` and `RestoreGeometry` (geometry protocol 2), plus `Move` and `Size` menu actions, exist.
- **Settings/preferences surface**: none.
- **Notifications, toasts and banners as distinct components**: none. Everything flows through a single status string.
- **Keyboard window switcher (Alt+Tab-class)**: none.
- **Launcher search**: none.
- **Hover thumbnails**: none.
- **Modules not in the inputs**: `Presentation`, `PreviewLifecycle`, `TaskbarShell`, `Desktop`, `Effects` and `OutputController` are imported but not supplied. The catalog's "all current widgets" claim must be generated from the full source tree, not from this packet.

### 1.3 Source findings relevant to design (for peer verification)

These are code-level observations; I did not run anything to confirm them.

- **F1, two live regions.** Both the bar and the popup render `role=status aria-live=polite` (`SurfaceRenderer.elm:63,64`). By the ELM-ADOPT-012/017 guardrail, multiple status regions do not establish a single announcement owner, so double announcement is possible.
- **F2, `aria-current` misuse.** `aria-current="true"` is set on a `menuitem` when `detail=="Selected"` (`:62`). This couples semantics to a display string. For the "current window" meaning, a description or `aria-checked` on a checkable item would be more conventional.
- **F3, separate accessible name.** `ariaLabel` is separate from the visible `label` (`:62`). This risks failing WCAG 2.5.3 Label in Name (Level A: "the name contains the text that is presented visually", https://www.w3.org/WAI/WCAG22/Understanding/label-in-name.html). It also conflicts with the ELM-ADOPT-017 guardrail that the visible stable label is the accessible name.
- **F4, popup not keyed.** Popup controls use `List.map` rather than `Html.Keyed` (`:63`), while the bar is keyed. That leaves a DOM identity-continuity risk under ELM-ADOPT-016.
- **F5, HTML `disabled` removes items from focus.** Disabled items use HTML `disabled`, which takes them out of the focus order. `Menu.navigate` also skips them. That is consistent with a GTK-style "skip" policy, but it differs from WAI-ARIA APG ("Disabled menu items are focusable but cannot be activated", https://www.w3.org/WAI/ARIA/apg/patterns/menubar/). ELM-ADOPT-030 requires that this choice be frozen per surface. The code shows a choice, but I found no declared policy.
- **F6, Pending items look enabled.** While a menu is `Pending`, items stay `enabled` in the model, but `Activate` silently does nothing on the same target (`Menu.elm:466-467`). The renderer therefore shows an enabled control that won't act.

---

## 2. Reference research (primary sources; access notes)

**Accessed:**
- **KDE HIG**: https://develop.kde.org/hig/ and its subpages, cited inline below.
- **KDE UserBase**: https://userbase.kde.org/Plasma/Tasks. This is a user wiki page last updated 31 Oct 2020, so treat it as dated.
- **GNOME HIG**: https://developer.gnome.org/hig/ and its subpages.
- **GNOME Help**: https://help.gnome.org/gnome-help/ shell pages.
- **Microsoft Learn**: menus, keyboard and snap pages.
- **Fluent 2**: the tokens page.
- **Apple HIG**: the HTML is JavaScript-rendered and returned only a title. I retrieved the same content through Apple's own JSON data endpoint (`developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json`) and cite the canonical human URLs.
- **W3C APG and WCAG** pages.
- **Impeccable**: GitHub, plus the frozen local copy at commit `87a6ab0c`.

**Inaccessible or partial:**
- **Material 3**: `m3.material.io` pages (states, menus/accessibility) are JavaScript-rendered, and WebFetch returned no body content. The only Material claims I saw came from a search-engine summary. I treat them as **unverified** and base no decision on Material alone.
- **Fluent 2 homepage**: exposed only partial navigation.
- **KDE window tiling**: I found no KDE primary page. Search returned only third-party articles and scripts, which I do not cite as authority.

**Pattern versus platform implementation.** The rules I borrow are interaction patterns. Implementation mechanics are explicitly *not* borrowed:
- Kirigami `showPassiveNotification`
- `WM_NCHITTEST`/`HTMAXBUTTON` for snap layouts
- AdwBanner
- NSWindow key/main state
- Breeze styling

Warlock's surfaces are WebView documents driven by Elm, while native authority lives in the compositor and broker.

---

## 3. Proposals

All IDs are local and stable. All proposals are additive drafts routed to existing W-lanes. None adds a release gate.

### WLD-DESK-01: Publish the taskbar activation decision table — **Adapt**
**Rationale.** The source already encodes a Windows/KDE-style rule: clicking the active single window minimizes it.
- KDE groups tasks "By program name", and clicking a group "will bring up a list of tabs for individual windows" (https://userbase.kde.org/Plasma/Tasks).
- GNOME's switcher groups "by application" (https://help.gnome.org/gnome-help/shell-windows-switching.html).

Warlock should document `Taskbar.primary` as the canonical contract, not invent a new one. The adaptation is that every row must state its *pending/outcome* presentation, because a click only creates a request.

**EARS.** When the user activates a taskbar group control, the shell shall derive exactly one decision from `Taskbar.primary` (Launch, Picker, Apply op root, or Unavailable). It shall render the targeted control as Pending until a correlated native receipt arrives, and it shall not represent the decision as completed before that receipt.

**Acceptance.**
- One family, active → click → `Apply Minimize root`; the control shows "Minimizing…".
- Native `Committed` → the control returns to its normal state with minimized styling, derived from the next projection rather than from the click.
- `Unknown` → "Could not be confirmed"; no automatic retry.
- Two families → `Picker` opens; no window effect is issued.

**Dependencies.** W07, ELM-ADOPT-020, ELM-ADOPT-008.

**Risk.** Minimize-on-click differs from GNOME, so it is a frozen policy choice. Mis-rendering Pending as success breaks Philosophy §4.

**Evidence.** [S] decision logic → [B] demo of the table → [N] receipt-correlated campaign.

### WLD-DESK-02: Picker previews with an honest freshness vocabulary — **Adapt**
**Rationale.**
- KDE shows "a small preview thumbnail of task" in tooltips (https://userbase.kde.org/Plasma/Tasks).
- GNOME shows window previews when grouped by application (https://help.gnome.org/gnome-help/shell-windows-switching.html).
- Apple prefers "a graphical preview that clarifies the target" of a contextual command (https://developer.apple.com/design/human-interface-guidelines/context-menus).

Warlock already limits preview demand to the open picker. This proposal adds four visible preview states aligned with ELM-ADOPT-028. Hover thumbnails on the bar are **deferred**, because they add demand while no picker is open (ELM-ADOPT-022 pacing).

**EARS.** While the picker is open, each window entry shall present its title and application as text regardless of preview state. Its preview region shall show exactly one of Placeholder, Current, Earlier frame or Unavailable, using a non-color cue and a text description. Stale pixels shall never be labelled current.

**Acceptance.**
- Preview not yet received → icon/initial plus "Preview not available yet".
- Source liveness lost but the last frame is retained → frame dimmed with the badge "Earlier view".
- Revoked → "Preview unavailable"; the entry stays selectable when `available`.
- Closing the picker → demand is cancelled while the lifecycle is retained (existing behavior).

**Dependencies.** W03, W06, ELM-ADOPT-027, ELM-ADOPT-028, original S09 preview13 assertions, which stay unchanged.

**Risk.** Labels must follow the frozen historical/live/unavailable policy. A browser demo uses synthetic images and cannot show freshness.

### WLD-DESK-03: Window-actions menu content policy — **Adapt**
**Rationale.** The sources disagree:
- Apple's menu bar says "Always show the same set of menu items… disable the action instead of hiding it" (https://developer.apple.com/design/human-interface-guidelines/the-menu-bar).
- Apple's context menus say "Hide unavailable menu items, don't dim them" (https://developer.apple.com/design/human-interface-guidelines/context-menus).
- Apple, KDE and GNOME all keep menus short: "between three and twelve items" (https://developer.gnome.org/hig/patterns/controls/menus.html), and "not more than about three groups" (Apple context menus).

**Recommendation: a two-reason rule.**
- If the action is *not supported* for this target class or protocol, omit it. For example, `ExitFullscreen` on a non-fullscreen-capable surface.
- If it is supported but *unavailable now* (state, Pending, Unknown), show it disabled with a plain reason.
- Add up to three groups: window state / arrangement / close, with Close last and separated.
- Use an ellipsis for actions that need more input. KDE: "End an action's label with an ellipsis if it always requires additional user input" (https://develop.kde.org/hig/text_and_labels/). This covers interactive `Move…` and `Size…`.

**EARS.** When the window-actions menu opens, the shell shall omit actions the target's declared capabilities do not support. It shall list supported but currently unavailable actions as disabled, with a description stating why. It shall present at most three separated groups.

**Acceptance.**
- Maximized window → "Maximize" is disabled with "Already maximized" and "Restore" is enabled.
- Target with Pending → all items disabled with "Waiting for the previous window change". This fixes F6.
- Geometry protocol unavailable → "Maximize" and "Restore Size" are omitted.

**Dependencies.** ELM-ADOPT-030, the right-click24 amendment (preserved), and a [P] `Item.group` field.

**Risk.** It changes the item-set semantics that right-click24 may already freeze, so a reconciliation pass is needed.

### WLD-DESK-04: Complete the menu and popup keyboard contract — **Borrow (APG + Windows), adapt the disabled-focus policy**
**Rationale.** The existing wrap-around navigation matches Windows popup "cycling" (https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions). The remaining keys come from these sources:
- Type-ahead and "Escape… return focus to the element… from which the menu was opened" (https://www.w3.org/WAI/ARIA/apg/patterns/menubar/).
- "Menu / Shift+F10: Open context menu" and "Esc: Close transient containers" (https://developer.gnome.org/hig/guidelines/keyboard.html).

Disabled-item focus is a genuine conflict: APG makes disabled items focusable, while the current code and GTK skip them.

**Recommendation.** In the window-actions menu, make disabled items focusable via `aria-disabled` and give them a reason description. The menu is where people learn why an action is unavailable. Keep the picker and the bar on skip.

**EARS.**
- While a Warlock popup menu has keyboard focus, Up/Down shall move with wrap-around. Home/End shall move to the first/last item. A printable character shall move to the next item whose label starts with it. Enter/Space shall activate an enabled item.
- When Escape is pressed, the popup shall close and focus shall return to the invoking control without issuing any window effect.

**Acceptance.**
- Typing "c" moves focus to "Close".
- Escape after an Unknown outcome closes the menu, and the Unknown obligation is preserved (`Menu` outstanding is unchanged).
- A focused disabled item announces its name, "dimmed/unavailable" and its reason; Enter does nothing.

**Dependencies.** W07, ELM-ADOPT-016, ELM-ADOPT-029 and ELM-ADOPT-030. It changes `Menu.navigate` [S→P].

**Risk.** It diverges from GTK expectations. Native AT transcripts are required; an ARIA-only demo is insufficient (ELM-ADOPT-012 guardrail).

### WLD-DESK-05: Taskbar keyboard entry, roving focus and exit — **Adapt (feasibility only; P5 native)**
**Rationale.**
- Windows recommends a single tab stop with arrow "inner navigation" for related controls. On the desktop, "F6 will cycle between parts of the taskbar and the desktop" (https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions).
- GNOME's switcher uses arrows between apps and "↓" for previews (https://help.gnome.org/gnome-help/shell-windows-switching.html).
- KDE requires interacting with every element by keyboard and that "active focus looks visibly distinct from inactive selections" (https://develop.kde.org/hig/accessibility/).

No new default global shortcut is proposed (ELM-ADOPT-029 guardrail).

**EARS.**
- While keyboard focus is in the taskbar, Left/Right shall move focus between group controls (mirrored under RTL), Down shall open the picker for multi-family groups, and Shift+F10/Menu shall open window actions.
- When Escape is pressed, focus shall leave the taskbar to the prior target without recording an activation in MRU history.

**Acceptance.**
- Arrow focus changes produce no `Apply` effect.
- Escape returns focus with zero native activation requests.
- Focus ring and active-window indication are distinguishable in grayscale.

**Dependencies.** W07, ELM-ADOPT-029 (existing P5), ELM-ADOPT-016.

**Risk.** Native keyboard scope belongs to the compositor; the browser demo shows the roving pattern only.

### WLD-DESK-06: Status-surface taxonomy (banner / inline / announcement) with one owner — **Adapt**
**Rationale.**
- GNOME separates *banners* for "ongoing… states" from *toasts* for transient events, and says not to "use a banner to communicate events" (https://developer.gnome.org/hig/patterns/feedback/banners.html, https://developer.gnome.org/hig/patterns/feedback/toasts.html).
- KDE: "All error messages must be actionable," with a ladder from "recover automatically" down to "never" silent failure. KDE also says "Don't rely on color alone" (https://develop.kde.org/hig/status_changes/).

Mapping for Warlock:
- **Shell phase states** (Detached, transport refused, recovery failure, Exhausted) → one persistent **banner** with its single action ("Reconnect"). This uses existing `recoveryNotice` copy.
- **Per-operation Pending/Refused/Unknown** → **inline** on the targeted control or menu.
- **Announcements** → a single controller-owned channel (ELM-ADOPT-012), which fixes F1.

Toasts for Committed outcomes are **rejected**: the window's changed state is the confirmation, and toasts add noise.

**EARS.**
- While the shell phase is Detached or Exhausted, or transport is refused, the surfaces shall show exactly one persistent banner naming the condition and its safe next step.
- When an operation outcome arrives, the shell shall announce it at most once, through one announcement owner, without moving focus.

**Acceptance.**
- Disconnect → the banner reads "Connection lost. Reconnect to continue." with a Reconnect button; the bar and popup do not both announce it.
- Repeated identical Unknown receipts → one announcement.
- A later distinct Refused → a new announcement.

**Dependencies.** W08, ELM-ADOPT-011, 012 and 017.

**Risk.** Removing the popup live region requires a qualified native announcement route when app focus is outside the shell.

### WLD-DESK-07: Outcome-state visual vocabulary and semantic tokens — **Borrow (Fluent token tiers), adapt to the brand**
**Rationale.** Fluent separates "global tokens [that] store raw values" from "alias tokens [that] add semantic meaning" (https://fluent2.microsoft.design/design-tokens). GNOME says to provide information "by at least one other method, such as shape, position or text" (https://developer.gnome.org/hig/guidelines/ui-styling.html). The brand already forbids treating decorative gold or mint as evidence (`BRAND-GUIDE.md`, `tokens.json semantics`).

Warlock needs a state alias tier: see the table in §5. State glyphs must **not** reuse the sigil's diamond, so the brand mark never reads as a status claim.

**EARS.** The shell shall render each of Pending, Committed, Refused, Cancelled, Unknown and Unavailable with a distinct text label and a distinct glyph shape, using alias tokens. It shall not use the brand diamond, mint or gold decoration as an outcome indicator.

**Acceptance.**
- In a grayscale capture, all six states are distinguishable by glyph and text.
- Light-theme text uses the light accents in `tokens.json` (`#583DA4`, `#805010`, `#A12A37`), not the dark-theme pastels.
- Measured contrast meets the frozen ELM-ADOPT-019 budget. I have not computed any contrast numbers.

**Dependencies.** ELM-ADOPT-019, `tokens.json`, W08.

**Risk.** Gold-derived "caution" for Unknown could be confused with the decorative state diamond. Mitigation: use the glyph plus the word "Unconfirmed".

### WLD-DESK-08: Applications launcher with type-to-filter and honest launch outcome — **Adapt**
**Rationale.**
- KDE: "Show something actionable when the app is first launched" and "Anticipate what the user is likely to do next" (https://develop.kde.org/hig/simple_by_default/).
- GNOME reduces effort through search and an overview (https://help.gnome.org/gnome-help/shell-overview.html).

Warlock's `Catalog` already supplies bounded, validated entries. Filtering is pure local view logic over `name` and needs no new native contract.

A launch request is not a launched window. The entry shows "Starting…" until the native catalog launch outcome arrives, and the taskbar shows the window only when the projection observes it.

**EARS.**
- While the applications popup is open, typed printable characters shall filter catalog entries by name without issuing native requests.
- When the user activates an entry, the shell shall show the launch as pending until a correlated native outcome arrives.

**Acceptance.**
- Typing "ter" shows matching entries.
- Escape clears the filter first, then closes on the second press.
- A Refused launch shows the reason inline.
- Unknown is not auto-replayed.

**Dependencies.** The existing Catalog `intent` binding, W04 and ELM-ADOPT-020.

**Risk.** Filtering must follow composition ownership (ELM-ADOPT-018). Keys consumed by an IME must not trigger filtering or shortcuts.

### WLD-DESK-09: Snapping and tiling — **Defer (reject the hover-maximize flyout)**
**Rationale.**
- Windows snap layouts appear when "hovering the mouse over a window's maximize button or pressing Win + Z" and are "tailored to the current screen size" (https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/apply-snap-layout-menu).
- GNOME tiles by dragging "until half of the screen is highlighted" or with Super+Left/Right (https://help.gnome.org/gnome-help/shell-windows-tiled.html).

Warlock's geometry protocol currently supports only maximize and restore-geometry. Window decorations and edge-drag highlighting are compositor-owned. The hover flyout is rejected because it depends on caption-button ownership that Warlock doesn't have.

When this is added, a zone preview must show **native-proposed** geometry and commit only on a receipt.

**EARS (future).** If a snap/tile action is offered, then the shell shall display the native-proposed target geometry before commitment, and it shall show the arrangement as applied only after a correlated Committed receipt.

**Acceptance.** Deferred, with no catalog demo beyond a "Not in Warlock yet" page.

**Dependencies.** The geometry protocol extension, W05, W12, and restore38/drag-resize52 unchanged.

**Risk.** A repository named "windows-parity" may expect snapping soon, which creates scope pressure.

### WLD-DESK-10: Workspaces — **Defer; document host ownership**
**Rationale.** GNOME workspaces are dynamic: an empty one is always available and empty ones are removed (https://help.gnome.org/gnome-help/shell-workspaces.html). KDE uses configurable virtual desktops. No Warlock source exists. The catalog must say plainly that the host compositor owns workspaces and that the taskbar shows windows from the scope the projection provides.

**EARS.** The catalog shall list workspaces as "Not provided by Warlock" and shall not depict workspace switching in Warlock demos.

**Acceptance.** No workspace control appears in any demo.

**Dependencies.** None.

**Risk.** Users might assume the taskbar filters by workspace; a projection-scope note is needed.

### WLD-DESK-11: Settings rules before settings UI — **Borrow (KDE "Powerful when needed")**
**Rationale.**
- "Settings to simply enable or disable a feature entirely are warning signs of sloppy design," and "Don't use customizability to avoid making design decisions" (https://develop.kde.org/hig/powerful_when_needed/).
- GNOME: offer "light, dark, and follow system" (https://developer.gnome.org/hig/guidelines/ui-styling.html).
- This matches Philosophy §8.

The first candidate settings are taskbar grouping ("By application" / "Never", as in KDE), theme (light/dark/system) and reduced motion (follow system only). Each setting declares the behavior it changes and the guarantees it keeps.

**EARS.** Each Warlock setting shall declare the behavior it changes and the accessibility, identity and recovery guarantees it preserves. Changing a setting shall not retarget a pending action.

**Acceptance.** Switching grouping while the picker is open keeps the focused identity per ELM-ADOPT-016, or applies the declared fallback.

**Dependencies.** ELM-ADOPT-016, 019 and 023.

**Risk.** There is no settings source yet, so this is a policy-only draft.

### WLD-DESK-12: The Warlock Design catalog site — **Adapt (Material/Fluent documentation structure, Warlock evidence model)**
See §7. **EARS.** Every component page shall display an evidence badge for each claim ([S] / [P] / [B] / [N]). Every interactive demo shall identify its native outcomes as simulated. No page shall present browser behavior as native acceptance.

**Acceptance.**
- An automated coverage check fails if any exported `Decision`, `Status`, `Outcome`, mode or control kind has no documented state or demo state.
- Every demo panel shows "Simulated authority — not native evidence".

**Dependencies.** All the above, `tokens.json`, and the full source manifest.

**Risk.** Running real Elm modules may lead readers to over-trust the demo; badges mitigate this.

---

## 4. Borrow matrix

| Family | Borrow | Adapt | Reject / Defer |
|---|---|---|---|
| **KDE** (HIG + UserBase) | Actionable-error ladder and "color alone" rule (status_changes); a keyboard-only test, plus a font-size-14 and Orca test (accessibility); settings discipline (powerful_when_needed); ellipsis rule and Title Case for commands (text_and_labels) | Group-by-program + click → list (Plasma/Tasks, dated 2020) → picker; passive vs inline messages → inline + banner | Kirigami/Breeze implementation (platform-specific); hover thumbnails deferred; "remember window position (X11)" is not applicable here (compositor-owned) |
| **GNOME** (HIG + Help) | Banner vs toast semantics; popover rules (Esc closes, ≤⅓ parent, optional heading); 3–12 menu items; Shift+F10/Menu key | Switcher grouping and ↓ for previews → picker keyboard; light/dark/system → setting; reserved system shortcuts (Alt+Tab, Alt+Space, etc.) → no conflicts with host bindings | Dynamic workspaces (deferred, host-owned); access keys on every menu item (deferred: needs localization and IME review); toasts for commits (rejected) |
| **Windows / Fluent 2** | Popup cycling (already in source); single tab stop + inner arrows; F6 region cycling; Esc cancels transient UI only; global/alias token tiers | Context-menu vs menu distinction → Window actions is a context menu | Snap-layout hover flyout (rejected); Win+Z (no new default shortcut); Fluent visual styling and marks (not copied) |
| **Apple HIG** | Dim-not-hide for stable menus; ellipsis; verb labels without articles; ≤3 context-menu groups; previews clarify target | Context-menu "hide unavailable" + menu-bar "disable" → two-reason rule (WLD-DESK-03); key/main/inactive distinction → active-window cue on taskbar | Dock, menu bar and visual idioms; Liquid Glass/vibrancy (decorative chrome conflicts with "keep glows out of ordinary controls") |
| **Material 3** | Nothing verified: m3.material.io was inaccessible | Documentation IA (foundations / components / tabs per component) as a site model only | No unverified claims used |
| **Impeccable** | Operate mode: "Every control is a standard one… Never a costume" (`mode-operate.md`); audit dimensions (`audit.md`); typography verification (`typeset.md`) | Catalog is Read mode with Operate demos | Its reflex-face list (Inter, Space Grotesk) is overridden by "The brief wins" (`SKILL.md`): brand fonts stay |

---

## 5. Tokens, component APIs and state tables [P]

### 5.1 Alias tokens (proposed tier over `tokens.json` globals)

| Alias | Dark | Light | Glyph | Required text |
|---|---|---|---|---|
| `state.pending` | lilac `#B7A2FF` | accent `#583DA4` | open ring (static under reduced motion) | "Applying…" / "Starting…" |
| `state.committed` | parchment `#F5F0E8` | text `#10111A` | check, shown transiently only via the resulting state | none (state itself) |
| `state.refused` | danger `#FF9B9B` | danger `#A12A37` | slashed circle | reason text |
| `state.cancelled` | muted `#ABB1C4` | muted `#53596C` | dash | "Cancelled" |
| `state.unknown` | gold `#F0BE75` | gold `#805010` | question in a triangle (never a diamond) | "Unconfirmed" |
| `state.unavailable` | muted + `border #68718C` | muted + border `#838A9A` | none (aria-disabled) | reason description |
| `focus.ring` | 2 px lilac outline, 2 px offset | 2 px accent | — | must differ from `selection.bg` |
| `selection.bg` | surface `#1B1E2B` + lilac 3 px leading bar | white + accent bar | — | — |

Type roles: display = Space Grotesk (catalog headings only, not in shell controls); body/control = Inter; metadata = JetBrains Mono (identity strings in catalog evidence panels only).

### 5.2 Renderer contract change (proposed; peer decision on protocol bump)
- Accessible name = visible `label`; `detail` → `aria-describedby`; retire or validate `ariaLabel` so it must *contain* `label` (WCAG 2.5.3).
- Add `availability: enabled | unavailable(reason)` rendered as `aria-disabled`, focusable per surface policy.
- Add `group: Int` for menu separators.
- Key the popup (`Html.Keyed`).
- Replace the `aria-current`-from-"Selected" coupling with an explicit boolean field.

### 5.3 Taskbar group control state table (from `Taskbar.primary`)

| Families | Pinned | Single family flags | Decision | Visible detail | Activation |
|---|---|---|---|---|---|
| 0 | yes | — | Launch | "Not running" | Launch intent |
| 0 | no | — | Unavailable | — | none (entry not shown) |
| 1 | — | unavailable | Unavailable | "Unavailable" | none, aria-disabled |
| 1 | — | minimized | Apply Restore | "Minimized" | Restore |
| 1 | — | active | Apply Minimize | "Active" | Minimize |
| 1 | — | other | Apply Activate | — | Activate |
| ≥2 | — | — | Picker | "N windows" | open picker |

### 5.4 Window-actions menu status table (from `Menu.elm`)

| Status | Menu | Items | Announcement (once) | Next safe action |
|---|---|---|---|---|
| Ready | open | per WLD-DESK-03 | — | choose |
| Pending | open | all unavailable: "Waiting for the previous window change" | "Applying…" | wait / Esc |
| (Committed) | closes | — | outcome-specific, e.g. "Window minimized" | — |
| Refused | open | re-enabled | the reason | choose again |
| Cancelled | open | re-enabled | "Cancelled" | choose again |
| Unknown | open | blocked on same target | "The result is still unconfirmed." | wait for reconciliation; never auto-replay |

---

## 6. Accessibility and keyboard contracts [P; native qualification N]

| Surface | Keys |
|---|---|
| Taskbar | Tab enters/leaves (single stop); ←/→ roving (RTL mirrored); Home/End; Enter/Space = primary decision; ↓ = picker (multi-family); Shift+F10 / Menu = window actions; Esc = leave without activation; F6 = next shell region (feasibility only) |
| Picker | ↑/↓ (or ←/→ when laid out horizontally); Home/End; Enter = `selection`; Shift+F10 = actions for the focused window; Esc = close and return focus to the group control |
| Window actions | ↑/↓ wrap (existing); Home/End (existing); type-ahead; Enter/Space activate; disabled items focusable with a reason (menu only); Esc closes and returns focus; no submenus |
| Applications | typing filters; ↑/↓; Enter launches; first Esc clears the filter, second closes |
| Global | No new default shortcuts. Must not collide with GNOME-reserved system bindings as a reference set (https://developer.gnome.org/hig/reference/keyboard.html) or with host compositor bindings. |

**Accessibility invariants:**
- Visible label = accessible name.
- One announcement owner.
- Focus ring differs from selection and from the active-window cue.
- Color is never the only signal.
- Previews always have text equivalents.
- Reduced motion is followed live, with no velocity continuation (ELM-ADOPT-023).
- Text enlargement and constrained geometry keep everything reachable. KDE suggests testing at system font size 14 (https://develop.kde.org/hig/accessibility/).
- Browser checks (axe-style, keyboard scripts) count as [B] only. Native Orca speech/braille transcripts are the [N] requirement.

---

## 7. Catalog website: "Warlock Design"

**Mode.** Per Impeccable, docs are *Read*; demo panels are *Operate*. The world contributes only type, palette, density and one signature move.

**Signature move.** Marble-style **outcome ribbons** in each demo. A request is a dot on a lane; the native receipt lands as Committed, Refused or Unknown, using ReactiveX marble grammar as the brand guide allows. The ribbons are labeled "diagram, not protocol evidence".

**Motion.** Demos start paused, stop when the page is hidden and honor reduced motion (`tokens.json motion`).

**Information architecture.**
1. **Overview**: one-sentence philosophy, the evidence legend [S]/[P]/[B]/[N], and what Warlock is not (no workspaces or snapping yet).
2. **Foundations**: color (globals + aliases, both themes, contrast measured in CI), typography, sigil usage (size rules, clear space), state and outcome vocabulary, motion and reduced motion, voice and writing (status copy catalog from `Shell.elm`), layout and density.
3. **Tokens**: generated from `tokens.json`, downloadable, with a diff history.
4. **Components** (one page each, all current widgets): Taskbar bar · Group control · Utility control · Recovery control · Status (→ banner [P]) · Popup container · Window picker · Window preview · Window actions menu · Applications launcher · Catalog entry.

   Each page has these tabs:
   - Overview
   - Anatomy
   - States (tables like §5)
   - Keyboard
   - Accessibility
   - Writing
   - Evidence: source path + hash, requirement IDs, [B] demo and [N] status (always "not qualified" until receipts exist)
5. **Patterns**: launch, switch, minimize/restore, context actions, disabled actions, unconfirmed outcomes, reconnect/recovery, preview freshness, list changed ("Window list changed. Choose again.").
6. **Desktop workflows (roadmap)**: snapping, workspaces, settings, notifications, each marked "Not in Warlock yet".
7. **Accessibility**: the full keyboard map, AT behavior and the test protocol.
8. **Evidence and coverage**: a matrix of every exported state × demo × native status.
9. **References**: every external citation with retrieval date, plus Impeccable provenance (commit `87a6ab0c`).

**Interactive demos [B].**
- Compile the actual `Taskbar`, `Menu`, `SurfaceRenderer` and `Catalog` modules against a **Simulated authority** panel. Its buttons: deliver Committed / Refused(reason) / Cancelled / Unknown / late receipt / duplicate receipt, disconnect, output retired, binding invalidated, list changed.
- Show a live state inspector that mirrors `Menu.snapshot` / `Shell.encode`.
- Previews use authored synthetic images labeled "Synthetic". Never use real captures: that is the pixels-privacy rule in ELM-ADOPT-013.
- The demo must never call a native port.

**Coverage rule.** CI enumerates the constructors of `Decision`, `Status`, `Outcome` and `Phase`, the popup modes and the control kinds. It fails if any lack a documented state and a demo scenario. The full module set, including the modules missing from this packet, must feed the enumerator.

---

## 8. Disagreements and tradeoffs for peer review

1. **Disabled items** (WLD-DESK-03/04): APG makes them focusable; Apple dims them in menus but hides them in context menus; the current code and GTK skip them. I recommend focusable-with-reason in the actions menu only. Peers may prefer skip-everywhere for GTK fidelity.
2. **Minimize on clicking the active window**: Windows/KDE-like and already in source. GNOME-leaning reviewers may object. Changing it is a frozen-policy decision, not a styling choice.
3. **Capitalization**: Title Case for commands (KDE, Apple, GNOME "header capitalization") versus the brand's plain sentence voice. I propose Title Case for menu commands and sentence case for status messages.
4. **No success toasts**: this could feel quiet. The counter-argument is that the changed window is the confirmation, and toasts risk an announcement storm (ELM-ADOPT-020).
5. **Hover thumbnails**: KDE users expect them; I defer them for pacing and demand-cost reasons.
6. **Snapping deferral** versus the parity goal in the repository's name.
7. **Renderer contract change** (`ariaLabel`, `aria-current`, availability field): renderer-only mapping or a surfaceProtocol 3 bump? This affects frozen ABI pairs, so the owning lane must decide.
8. **Real Elm modules in demos**: more truthful policy, but readers may over-trust them. The mitigations are evidence badges and the simulated-authority label.
9. **Fonts**: Impeccable's reflex-face list conflicts with the brand. I keep the brand ("The brief wins").
10. **Material 3** could not be verified. Another reviewer with JavaScript-capable access should confirm or refute the unverified disabled-item-focus claim.

---

```json
[
 {"id":"WLD-DESK-01","title":"Publish taskbar activation decision table","decision":"adapt","ears":"When the user activates a taskbar group control, the shell shall derive exactly one decision from Taskbar.primary and render the targeted control Pending until a correlated native receipt, never representing the decision as completed before it.","acceptance":["single active family -> Apply Minimize shown Pending","Committed -> state from next projection","Unknown -> 'could not be confirmed', no retry","two families -> Picker, no effect issued"],"sourceUrls":["https://userbase.kde.org/Plasma/Tasks","https://help.gnome.org/gnome-help/shell-windows-switching.html"],"dependencies":["W07","ELM-ADOPT-008","ELM-ADOPT-020"]},
 {"id":"WLD-DESK-02","title":"Picker previews with honest freshness vocabulary","decision":"adapt","ears":"While the picker is open, each entry shall present title and application as text and show exactly one of Placeholder, Current, Earlier frame or Unavailable with non-color cue and text; stale pixels shall never be labelled current.","acceptance":["no frame -> placeholder text","liveness lost -> 'Earlier view' badge","revoked -> 'Preview unavailable', still selectable if available","close -> demand cancelled, lifecycle retained"],"sourceUrls":["https://userbase.kde.org/Plasma/Tasks","https://help.gnome.org/gnome-help/shell-windows-switching.html","https://developer.apple.com/design/human-interface-guidelines/context-menus"],"dependencies":["W03","W06","ELM-ADOPT-022","ELM-ADOPT-027","ELM-ADOPT-028"]},
 {"id":"WLD-DESK-03","title":"Window-actions menu content policy (omit unsupported, disable unavailable with reason, <=3 groups)","decision":"adapt","ears":"When the window-actions menu opens, the shell shall omit capability-unsupported actions, list currently-unavailable supported actions as disabled with a reason, and present at most three separated groups.","acceptance":["maximized -> Maximize disabled 'Already maximized'","Pending -> all items unavailable with waiting reason","no geometry protocol -> Maximize/Restore Size omitted"],"sourceUrls":["https://developer.apple.com/design/human-interface-guidelines/the-menu-bar","https://developer.apple.com/design/human-interface-guidelines/context-menus","https://developer.gnome.org/hig/patterns/controls/menus.html","https://develop.kde.org/hig/text_and_labels/"],"dependencies":["ELM-ADOPT-030","right-click24","W07"]},
 {"id":"WLD-DESK-04","title":"Complete menu/popup keyboard contract","decision":"borrow","ears":"While a Warlock popup menu has focus, Up/Down shall wrap, Home/End jump, printable characters type-ahead and Enter/Space activate enabled items; when Escape is pressed the popup shall close and return focus to the invoker without issuing a window effect.","acceptance":["'c' focuses Close","Esc after Unknown preserves outstanding obligation","focused disabled item announces reason and does not activate"],"sourceUrls":["https://www.w3.org/WAI/ARIA/apg/patterns/menubar/","https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions","https://developer.gnome.org/hig/guidelines/keyboard.html"],"dependencies":["W07","ELM-ADOPT-016","ELM-ADOPT-029","ELM-ADOPT-030"]},
 {"id":"WLD-DESK-05","title":"Taskbar keyboard entry, roving focus and exit","decision":"adapt","ears":"While keyboard focus is in the taskbar, Left/Right shall move between group controls, Down shall open the picker for multi-family groups and Shift+F10/Menu shall open window actions; when Escape is pressed focus shall leave without recording an activation.","acceptance":["arrow focus issues no Apply","Esc returns focus with zero native activations","focus vs active cue distinguishable in grayscale"],"sourceUrls":["https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions","https://help.gnome.org/gnome-help/shell-windows-switching.html","https://develop.kde.org/hig/accessibility/"],"dependencies":["W07","ELM-ADOPT-016","ELM-ADOPT-029"]},
 {"id":"WLD-DESK-06","title":"Status-surface taxonomy with one announcement owner","decision":"adapt","ears":"While the shell is Detached, Exhausted or transport-refused, surfaces shall show exactly one persistent banner naming the condition and safe next step; when an outcome arrives it shall be announced at most once through one owner without moving focus.","acceptance":["disconnect -> single banner with Reconnect","duplicate Unknown -> one announcement","later distinct Refused -> new announcement"],"sourceUrls":["https://developer.gnome.org/hig/patterns/feedback/banners.html","https://developer.gnome.org/hig/patterns/feedback/toasts.html","https://develop.kde.org/hig/status_changes/"],"dependencies":["W08","ELM-ADOPT-011","ELM-ADOPT-012","ELM-ADOPT-017"]},
 {"id":"WLD-DESK-07","title":"Outcome-state visual vocabulary and semantic alias tokens","decision":"adapt","ears":"The shell shall render Pending, Committed, Refused, Cancelled, Unknown and Unavailable with distinct text and glyph shapes via alias tokens, and shall not use the brand diamond, mint or gold decoration as an outcome indicator.","acceptance":["six states distinguishable in grayscale","light theme uses light accents","contrast measured against frozen ELM-ADOPT-019 budget"],"sourceUrls":["https://fluent2.microsoft.design/design-tokens","https://developer.gnome.org/hig/guidelines/ui-styling.html"],"dependencies":["ELM-ADOPT-019","W08","tokens.json"]},
 {"id":"WLD-DESK-08","title":"Applications launcher type-to-filter and honest launch outcome","decision":"adapt","ears":"While the applications popup is open, typed characters shall filter catalog entries locally without native requests; when an entry is activated the launch shall show as pending until a correlated native outcome.","acceptance":["'ter' filters","Esc clears then closes","Refused shows reason","Unknown not replayed"],"sourceUrls":["https://develop.kde.org/hig/simple_by_default/","https://help.gnome.org/gnome-help/shell-overview.html"],"dependencies":["W04","ELM-ADOPT-018","ELM-ADOPT-020"]},
 {"id":"WLD-DESK-09","title":"Snapping/tiling (reject hover-maximize flyout)","decision":"defer","ears":"If a snap/tile action is offered, then the shell shall display native-proposed target geometry before commitment and show the arrangement applied only after a correlated Committed receipt.","acceptance":["catalog shows 'Not in Warlock yet' only"],"sourceUrls":["https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/apply-snap-layout-menu","https://help.gnome.org/gnome-help/shell-windows-tiled.html"],"dependencies":["geometry protocol extension","W05","W12","restore38","drag-resize52"]},
 {"id":"WLD-DESK-10","title":"Workspaces documented as host-owned","decision":"defer","ears":"The catalog shall list workspaces as not provided by Warlock and shall not depict workspace switching in demos.","acceptance":["no workspace control in any demo"],"sourceUrls":["https://help.gnome.org/gnome-help/shell-workspaces.html"],"dependencies":[]},
 {"id":"WLD-DESK-11","title":"Settings rules before settings UI","decision":"borrow","ears":"Each Warlock setting shall declare the behavior it changes and the guarantees it preserves, and changing a setting shall not retarget a pending action.","acceptance":["grouping change with picker open preserves focused identity or applies declared fallback"],"sourceUrls":["https://develop.kde.org/hig/powerful_when_needed/","https://developer.gnome.org/hig/guidelines/ui-styling.html"],"dependencies":["ELM-ADOPT-016","ELM-ADOPT-019","ELM-ADOPT-023"]},
 {"id":"WLD-DESK-12","title":"Warlock Design catalog site with evidence badges and simulated-authority demos","decision":"adapt","ears":"Every component page shall badge each claim as existing source, proposed, browser demonstration or native acceptance, and every interactive demo shall identify its native outcomes as simulated.","acceptance":["CI fails on any undocumented Decision/Status/Outcome/Phase/mode/control kind","every demo shows 'Simulated authority — not native evidence'"],"sourceUrls":["https://fluent2.microsoft.design/design-tokens","https://github.com/pbakaus/impeccable"],"dependencies":["WLD-DESK-01..11","tokens.json","full source manifest"]}
]
```
