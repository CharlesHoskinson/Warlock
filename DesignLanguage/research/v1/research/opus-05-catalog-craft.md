# Warlock catalog website: design review (opus-05-catalog-craft)

**Scope.** This is a read-only planning review. I edited no files and started no agents. Impeccable's context launcher was not run, so I read the frozen project context directly, as the user instructed. Every proposal below is a draft by one reviewer. **None of it is consensus.** Consensus only exists after all five reviewers vote on the exact consolidated proposal.

**Evidence labels used throughout:**
- **[SRC]** exists in the provided Elm source or brand files.
- **[ADD]** a proposed addition.
- **[DEMO]** browser demonstration only.
- **[NATIVE]** needs native-authority acceptance. No website demo can supply that.

---

## 1. What exists today, traced to source

### 1.1 Brand and philosophy [SRC]

**Identity** (`inputs/docs/warlock-brand/v1/BRAND-GUIDE.md`, `tokens.json`)
- Tagline: "Crafted for flow."
- Fonts: Space Grotesk for display, Inter for body and controls, JetBrains Mono for code and data.
- Colors are dark-first. `ink #10111A`, `surface #1B1E2B`, `parchment #F5F0E8`, `lilac #B7A2FF`, `mint #7DE2C1`, `gold #F0BE75`, `muted #ABB1C4`, `danger #FF9B9B`, `border #68718C`.
- A separate light set: `background #F5F0E8`, `surface #FFFFFF`, `text #10111A`, `muted #53596C`, `accent #583DA4`, `mint #12644F`, `gold #805010`, `danger #A12A37`, `border #838A9A`.
- Logo sizes: full color at 32 px and above, monochrome silhouette at 24–31 px, plain "W" below 24 px.
- Motion: paused by default, pauses when the page is hidden, honors reduced motion. Product timing is governed by the frozen S02 policy.
- Semantics flags: `colorNeverSoleSignal`, `decorativeDiagramNotProtocolEvidence`.

**What `tokens.json` (schema 1) lacks:** spacing, radius, elevation, focus ring, interaction-state, type-scale, outcome-role and high-contrast tokens.

**Philosophy** (`PHILOSOPHY.md`)
- Keep pending, committed, refused, cancelled, presented and unconfirmed distinct.
- Never replay Unknown automatically.
- Publish the rules that shortcuts, menus, focus and disabled controls follow (Manifesto §8).
- Accessibility is a complete interaction path (§6).

**Workplan** (`WORKPLAN.md`)
- ELM-ADOPT-016, -017, -019, -020, -029 and -030 govern focus identity, accessible names, constrained geometry, action discovery, taskbar keyboard entry and exit, and the disabled-navigation policy.
- No contract there is accepted native behavior.

### 1.2 Widget inventory [SRC]

Path prefix: `inputs/implementation/warlock-preview-provider-v1/src/`

| # | Widget | Source | Observable facts |
|---|---|---|---|
| W1 | Taskbar bar surface | `SurfaceRenderer.elm:64` | `Keyed.node "div"` with class `surface-bar`, keyed `"control:"++identity`. Carries `data-publication` and `data-lease`. At most 259 bar controls (`:29`). |
| W2 | Bar control, 3 kinds | `SurfaceRenderer.elm:61-62` | `control-group` (`bar:group:*`), `control-recovery` (`bar:recovery-refresh`), `control-utility` (everything else). A `<button>` with `aria-label`, `.control-label`, `.control-detail` (≤128 chars) and native `disabled`. |
| W3 | Status line (bar and popup) | `SurfaceRenderer.elm:63-64` | `role=status`, `aria-live=polite`. Text comes from `Shell.status` (`Shell.elm:68-76`). |
| W4 | Popup surface, modes `closed` / `picker` / `applications` / `menu` | `SurfaceRenderer.elm:34,63` | Headings: "Choose a window", "Applications", "Window actions". Container role is `menu` in menu mode, otherwise `group`. At most 2051 popup controls. |
| W5 | Popup menu item | `SurfaceRenderer.elm:62` | `role=menuitem` in menu mode. `aria-current="true"` iff detail is "Selected", otherwise `"false"` on every control. |
| W6 | Picker entry with inline preview | `Popup.elm:27`, `PreviewPresenter.elm:99-101` | `Preview.inlineView {title, application, icon=Nothing}`. Rendered only when the stamp matches publication, lease and mode `picker`. |
| W7 | Window-actions menu lifecycle | `Menu.elm` | 12 actions: Restore, RestoreGeometry, Move, Size, Minimize, Maximize, Close, ExitFullscreen, AlwaysOnTop Bool, PinToTaskbar Bool, Launch, ProviderCommand. 5 statuses: Ready, Pending, Refused, Cancelled, Unknown. 4 targets. Limits: 64 items, 256-unit labels, 64 outstanding, 128 retired. |
| W8 | Taskbar grouping and decision | `Taskbar.elm` | Family flags: `minimized`, `available`, `active`. Decisions: `Launch`, `Picker`, `Apply op`, `Unavailable`. |
| W9 | Applications catalog data | `Catalog.elm` | Entry fields: `id`, `name`, `iconHint`, `wmclass`. At most 2048 entries. Duplicate identity is refused. |
| W10 | Outcome shape | `NativeOutcome.elm:42` | `Committed`, `Refused`, `Unknown`, with reason ≤256. |
| W11 | Shell notices | `Shell.elm:23-29,50-189` | About 20 user-facing strings, e.g. "Applying window change…", "Connection lost. Reconnect to continue.", five recovery-failure notices. |

### 1.3 Gaps and findings for the catalog

- **F1, accessible name.** `ariaLabel` is a separate field from the visible `label` (`SurfaceRenderer.elm:11,62`). The rendered name can therefore drop the visible text. That conflicts with the ADOPT-017 guardrail ("Keep the visible stable control label as the accessible name").
- **F2, selection semantics.** `aria-current` marks selection on `menuitem`. Meanwhile `AlwaysOnTop Bool` and `PinToTaskbar Bool` are toggles. Apple's HIG treats "Toggled items" as their own topic (https://developer.apple.com/design/human-interface-guidelines/menus). `aria-current="false"` is also emitted everywhere, which adds noise.
- **F3, announcements.** Bar and popup each own a polite live region. Under ADOPT-012, multiple status regions do not establish a single announcement owner.
- **F4, disabled controls.** HTML `disabled` removes them from tab order, and `Menu.navigate` (`Menu.elm:294-328`) skips disabled items and wraps.
- **F5, name collision.** `Catalog.elm` is the *applications* catalog. The website needs a distinct name, e.g. "component catalog".
- **F6, no stylesheet.** The inputs contain no CSS, and `Presentation`, `PreviewLifecycle`, `ActionProjection` and similar modules are imported but absent. Visual specs and the key-to-`Msg` mapping cannot be verified from this packet.
- **F7, deadlines.** `Main.elm:36-38` arms 2000 ms and 10000 ms deadlines. These are frozen deadlines, not UX timing claims, and the catalog must not present them as such.

---

## 2. Reference access log

| Family | Accessed | Not accessible |
|---|---|---|
| Material 3 | Page bodies are client-rendered, so WebFetch returned only titles. These URLs were confirmed through the search index: https://m3.material.io/foundations/design-tokens/overview, https://m3.material.io/components/menus/accessibility, https://m3.material.io/foundations/interaction/states/applying-states, https://m3.material.io/components/navigation-bar/overview | Exact wording on those pages. Claims below rely on search-index excerpts only. I deliberately do not quote state-layer opacity values. |
| Impeccable | https://github.com/pbakaus/impeccable (Apache-2.0; 24 commands; 61 detector rules), plus the local pinned copy at commit `87a6ab0c` | — |
| Apple HIG | Read through the documentation JSON endpoint. Cited as https://developer.apple.com/design/human-interface-guidelines/, …/menus and …/accessibility | The HTML pages themselves are client-rendered. |
| KDE | https://develop.kde.org/hig/, …/accessibility/, …/status_changes/, …/text_and_labels/ | — |
| GNOME | https://developer.gnome.org/hig/, …/guidelines/keyboard.html, …/guidelines/writing-style.html, …/patterns/controls/menus.html | — |
| Windows / Fluent | https://learn.microsoft.com/en-us/windows/apps/design/, https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/, https://learn.microsoft.com/en-us/windows/apps/develop/input/keyboard-interactions, https://fluent2.microsoft.design/, https://fluent2.microsoft.design/design-tokens, https://fluent2.microsoft.design/components/web/react/core/menu/usage | — |

---

## 3. Proposals

### OPUS05-CAT-01: Source-derived widget manifest and coverage gate
**Decision: Borrow and adapt.**

Windows lists every control with a one-line description and points to the WinUI 3 Gallery for hands-on demos (https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/). Material keeps a single components index (https://m3.material.io/components). "All current widgets" can only stay true if the list is generated from source rather than written by hand.

- **[ADD]** A build step extracts a `widget-manifest.json` from the Elm source. It records:
  - surface classes, roles and modes (`SurfaceRenderer`);
  - `Menu.Action`, `Status` and `Navigation` constructors;
  - `Taskbar.Decision` values;
  - `Shell` notice strings;
  - the source path plus SHA-256 for each entry.
- **EARS:** When the catalog builds, the build shall fail if any manifest identity lacks a catalog page or state-table row, or if any catalog page cites an identity or source hash absent from the manifest.
- **Acceptance:**
  - Remove the `ExitFullscreen` row from the menu page. The build fails and names `Menu.Action.ExitFullscreen`.
  - Change `Menu.elm` without regenerating. The build fails on a hash mismatch.
- **Dependencies:** frozen source hashes; owner assignment for the catalog lane.
- **Risk:** Extraction from Elm syntax is brittle. Prefer an exported Elm "describe" module, which must remain read-only with respect to policy.

### OPUS05-CAT-02: Read-mode information architecture with uniform component pages
**Decision: Adapt.**

Impeccable says a docs index is **Read** mode, not Persuade (`SKILL.md` §Modes). Each reference family structures its guidance differently:
- Apple: Getting started / Foundations / Patterns / Components / Inputs / Technologies (https://developer.apple.com/design/human-interface-guidelines/).
- GNOME: Principles / Guidelines / Patterns / Reference, with patterns split into Containers, Navigation, Controls and Feedback (https://developer.gnome.org/hig/).
- Material: component pages tabbed Overview / Specs / Guidelines / Accessibility (search-index evidence, e.g. https://m3.material.io/components/navigation-bar/overview).

- **[ADD]** Top level: Overview · Foundations · Components · Patterns · Accessibility · Tokens · Evidence · Changelog.
- **[ADD]** Every component page has six tabs: **Overview · Anatomy & states · Behavior & keyboard · Accessibility · Content · Evidence.** The Evidence tab is Warlock-specific.
- **EARS:** The catalog shall present every manifest component with the six tabs, in the same order. Where a tab has no verified content, it shall show "Not yet specified" rather than being omitted.
- **Acceptance:**
  - The window-actions menu page shows all six tabs.
  - Its Evidence tab lists only [SRC] and [DEMO] items today.
- **Dependencies:** CAT-01.
- **Risk:** Empty tabs could read as unfinished. That is the honest state, and it complies with Manifesto §10.

### OPUS05-CAT-03: Evidence-level labeling on every behavioral claim
**Decision: Original to Warlock.** Apple's per-page "Change log" (https://developer.apple.com/design/human-interface-guidelines/menus) is a weak precedent. No reference family separates evidence levels. Warlock must, because "a website demo cannot qualify native release behavior."

- **[ADD]** Each claim carries exactly one label. The levels are fixed and ordered:
  1. `Source`: path and hash.
  2. `Browser demo`.
  3. `Model/CPU qualified`: receipt ID.
  4. `Native qualified`: owning ABI tuple, scenario identity and receipt.
- **EARS:**
  - The catalog shall display exactly one evidence level for each behavioral claim.
  - The catalog shall not render `Native qualified` unless the claim links a frozen native receipt and its owning ABI tuple.
  - While a page is rendered in a browser, no demo interaction shall change any claim's evidence level.
- **Acceptance:**
  - The claim "Committed closes the menu" (`Menu.elm:512`) shows `Source` plus `Browser demo`.
  - An attempt to mark it `Native qualified` without a receipt fails the build.
- **Dependencies:** the evidence ledger and receipt format from the build loop.
- **Risk:** Readers may treat the labels as clutter. Use compact labels with text, never color alone.

### OPUS05-CAT-04: Two orthogonal state axes (interaction × outcome)
**Decision: Adapt.**

- **Borrowed:** Material defines interaction states (hover, focus, pressed, dragged, disabled) as a foundation (https://m3.material.io/foundations/interaction/states/applying-states).
- **Rejected:** Material's ripple and state-layer *implementation*.
- **Warlock's addition:** a second axis, outcome state, drawn from `Menu.Status` and `NativeOutcome`.

**[ADD] Outcome foundation page.** Each state gets a word, a glyph shape and a color role:

| State | Source | Word | Glyph | Dark role | Light role |
|---|---|---|---|---|---|
| Ready | `Menu.Ready` | — | none | — | — |
| Pending | `Menu.Pending`, "Applying window change…" | "Applying…" | hollow diamond | `muted` | `muted` |
| Committed | `NativeOutcome`, menu closes | change visible in target | none (state change is the signal) | — | — |
| Refused | `Menu.Refused reason` | reason text | diamond with bar | `danger` | `danger` |
| Cancelled | `Menu.Cancelled` | "Cancelled" | open diamond | `muted` | `muted` |
| Unknown | `Menu.Unknown`, `Shell.elm:74` | "…could not be confirmed." | diamond with "?" | `gold` | `gold` |

- **EARS:**
  - The catalog shall render each outcome state with a text word and a non-color glyph.
  - When a demo is in Unknown, the demo shall not offer automatic retry.
- **Acceptance:**
  - In a grayscale capture of the outcome table, every state stays distinguishable.
  - The Unknown demo exposes no "Retry" control. The "Choose a new window action" copy from `Shell.elm:86` is shown instead.
- **Dependencies:** CAT-05 tokens; the ADOPT-011 reason catalog.
- **Risk:** The brand says gold "never constitutes evidence". Using gold for Unknown must be paired with text. Peer review should confirm gold is acceptable as the color for uncertainty.

### OPUS05-CAT-05: Three-tier token schema 2, additive and contrast-gated
**Decision: Borrow and adapt.**
- Material: reference / system / component tokens, `md.ref`, `md.sys`, `md.comp` (https://m3.material.io/foundations/design-tokens/overview).
- Fluent: global and alias tokens, with light, dark, high-contrast and branded themes (https://fluent2.microsoft.design/design-tokens).

**[ADD]** `tokens.json` schema 2 keeps every schema 1 value byte-identical and adds:
- `ref.*`: the existing palette, unchanged.
- `sys.color.*` (dark and light):
  - `text`, `textMuted`, `surface`, `surfaceRaised`, `border`, `focusRing`;
  - `outcome.{pending,refused,cancelled,unknown}`;
  - `selection`, `disabledText`.
- `sys.type.*` roles: `display`, `title`, `body`, `label`, `detail`, `code` (sizes in rem; body ≥ 1 rem on the website).
- `sys.space.*` on a 4 px base, `sys.radius.{control,popup}`, `sys.elevation.popup` as a single declaration.
- `sys.motion.site.*`: website only. Product motion stays under S02 and is not defined here.
- `comp.barControl.*`, `comp.popup.*`, `comp.menuItem.*`, `comp.statusLine.*`.
- `forcedColors` mapping.

**Contrast check.** These are hand-computed WCAG ratios and the build must recompute them:

| Pair | Ratio |
|---|---|
| muted on ink | ≈ 8.8:1 |
| muted on surface | ≈ 7.8:1 |
| lilac on ink | ≈ 8.6:1 |
| lilac on surface | ≈ 7.6:1 |
| dark border on ink | ≈ 3.9:1 |
| dark border on surface | ≈ 3.4:1 |
| light muted on parchment | ≈ 6.1:1 |
| light accent on parchment | ≈ 7.1:1 |
| light gold on parchment | ≈ 6.0:1 |
| light danger on parchment | ≈ 6.4:1 |
| light mint on parchment | ≈ 6.3:1 |
| **light border on parchment** | **≈ 3.05:1 (marginal)** |
| light border on white | ≈ 3.5:1 |

- **EARS:**
  - When tokens build, the build shall fail if any `sys` text pair is below 4.5:1, or any non-text boundary or focus pair is below 3:1, in either theme.
  - The schema 2 file shall reproduce all schema 1 values unchanged.
- **Acceptance:**
  - A schema 1 consumer still reads `colors.lilac == "#B7A2FF"`.
  - Lowering light `border` to `#9AA0AE` fails the gate.
- **Dependencies:** the brand owner's approval of the additive schema; `tokens.css` regeneration.
- **Risk:** Website tokens do not prove native constrained-geometry or contrast reachability. ADOPT-019 still requires native evidence.

### OPUS05-CAT-06: Live demos run the real Elm modules with an explicit simulated authority
**Decision: Borrow and adapt.** Borrowed: the WinUI 3 Gallery's interactive companion (https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/).

Adaptation:
- The site is a TEA `Browser.application`.
- It imports `SurfaceRenderer` and `Menu` unchanged.
- It feeds fixtures through the real `SurfaceRenderer.decode` and `Menu.update`. Malformed fixtures therefore fail the way production input would.
- Outcomes come only from a reader-operated panel labeled **"Simulated authority"**, with Commit, Refuse, Cancel and Leave unconfirmed. Nothing resolves on a timer.
- This is not a second policy model. It is the same policy code with a fixture source, which respects INSTRUCTIONS.md's single-policy rule.
- **Signature move:** each demo shows a "flow ribbon" beneath it. This is a marble-style transcript of the reader's own simulated events (brand §Community concepts). It is labeled "Demo transcript, not a protocol diagram."

- **EARS:**
  - While a demo is active, the demo shall change outcome state only in response to an explicit reader action on the Simulated authority panel.
  - The demo shall label every outcome "simulated".
  - The demo shall never replay an Unknown request.
- **Acceptance:**
  - Opening the menu, activating Minimize and waiting 60 s leaves the status at Pending.
  - Activating Close while Minimize is pending emits no second `Dispatch` (`Menu.elm:466`).
  - Dismissing the menu and reopening it shows Pending again (`Menu.elm:429-432`).
- **Dependencies:** CAT-01; the site importing frozen modules by hash; the missing `PreviewLifecycle` and `ActionProjection` for W6 and W8.
- **Risk:**
  - The site build couples to component hashes. That is intended, because drift becomes visible.
  - The ribbon could be mistaken for protocol evidence. Peer review should weigh this against the brand's `decorativeDiagramNotProtocolEvidence`.

### OPUS05-CAT-07: Published keyboard contract tables per component
**Decision: Borrow, with the roving bar deferred.**
- Windows popup menus: Down opens on the first item, Up on the last, and focus wraps ("cycling"). Cycling is to be avoided outside popups. Esc cancels transient UI only (https://learn.microsoft.com/en-us/windows/apps/develop/input/keyboard-interactions).
- GNOME: "every action should also be possible with the keyboard"; Tab, Return, Space and Esc (https://developer.gnome.org/hig/guidelines/keyboard.html).
- Material menus: arrow, Enter/Space, typeahead and Escape behavior (https://m3.material.io/components/menus/accessibility, search-index evidence).

`Menu.navigate` already matches Windows cycling [SRC].

- **[ADD]** Publish the tables in §6.
- **Deferred:** a single-tab-stop roving bar and typeahead. These are ELM-ADOPT-029 P5 native keyboard scope, feasibility only.
- **EARS:** The catalog shall publish, for each interactive component, the key, the resulting `Msg`, and its evidence level. Where the key-to-`Msg` binding is not in verified source, it shall label the row "binding unverified".
- **Acceptance:**
  - The menu table shows Down with no selection mapping to the first enabled item and Up to the last, labeled `Source` (`Menu.elm:315-326`).
  - The Esc row reads `Dismiss MenuId — binding unverified` until the bridge source is cited.
- **Dependencies:** bridge and native keymap source; ADOPT-029 and -030.
- **Risk:** Publishing a table may be mistaken for committing to it. Use a version stamp and evidence labels.

### OPUS05-CAT-08: Accessible-name and semantics audit page
**Decision: Adapt.** Supporting guidance:
- KDE: assign text even to icon-only buttons (https://develop.kde.org/hig/text_and_labels/).
- KDE: don't leave important text in hover tooltips (https://develop.kde.org/hig/accessibility/).
- ELM-ADOPT-017 guardrail.

- **[ADD]** For each fixture, the Accessibility tab renders the visible label, `ariaLabel`, role, `disabled` and `aria-current` side by side. A lint check flags F1 (the visible label missing from the accessible name) and F2 (toggle actions without a checked state).
- **EARS:** When a fixture's `ariaLabel` does not contain its visible `label` text (case-insensitive, whitespace-normalized), the catalog build shall report a label-in-name finding against that fixture and component.
- **Acceptance:** A fixture with label "Firefox" and ariaLabel "Switch to window 3" produces a finding.
- **Dependencies:** ADOPT-017 naming policy; the native AT tree for final acceptance [NATIVE].
- **Risk:** Browser ARIA output is not the native AT tree. Under ADOPT-012, ARIA alone is insufficient.

### OPUS05-CAT-09: Content and voice standard with a source string inventory
**Decision: Borrow parts, reject title case.**
- **Borrowed:**
  - GNOME's ellipsis rule: "if further input or confirmation is required" (https://developer.gnome.org/hig/guidelines/writing-style.html).
  - KDE's "All error messages must be actionable" (https://develop.kde.org/hig/status_changes/).
  - Fluent's sentence case and verbs for actions (https://fluent2.microsoft.design/components/web/react/core/menu/usage).
- **Rejected:** title and header capitalization (Apple menus; GNOME; KDE https://develop.kde.org/hig/text_and_labels/). The existing source is sentence case ("Choose a window", "Window actions"). Brand voice is direct, and sentence case localizes more simply.

- **[ADD]** The Content tab shows every source string with its path:line, applicable rule and status. Existing recovery notices already follow problem-plus-recovery (`Shell.elm:25-29`).
- **EARS:** The catalog shall list every user-facing source string with its path:line. When a string violates the published case, ellipsis or actionable-error rule, the catalog shall show it as a finding rather than silently rewriting it.
- **Acceptance:**
  - "Connection lost. Reconnect to continue." passes the actionable-error rule.
  - A hypothetical "Error 42" fails it.
- **Dependencies:** CAT-01; the ADOPT-011 localizable catalog.
- **Risk:** Whether "Move" and "Size" need an ellipsis depends on interactive-mode semantics. Defer that decision to the window-interaction owners.

### OPUS05-CAT-10: Responsive reading layout and website motion
**Decision: Adapt.**
- Impeccable craft floor: body measure 65–75ch, every state shown, browser surfaces themed (`craft-floor.md` §Verify).
- Apple: text enlargement to at least 200 % and Reduce Motion (https://developer.apple.com/design/human-interface-guidelines/accessibility).

**[ADD] Breakpoints:**

| Viewport | Layout |
|---|---|
| ≥ 1200 px | Three panes: navigation rail, content capped at 72ch, on-page contents list. |
| 768–1199 px | Two panes; the contents list collapses into the content header. |
| < 768 px | One column; navigation in a disclosure; demos stacked. |

Demos follow container queries. Brand animation is off until toggled, pauses on `visibilitychange`, and responds live to `prefers-reduced-motion`. Theme follows `prefers-color-scheme` plus a manual switch.

- **EARS:**
  - When the viewport is 320 CSS px wide at 400 % zoom, the catalog shall present all content without two-dimensional scrolling, except inside demo canvases that declare a fixed product size.
  - While reduced motion is preferred, the site shall run no decorative animation.
- **Acceptance:**
  - At 390 px and 1440 px captures, no text overflows.
  - Toggling reduced motion mid-animation stops the animation without a reload.
- **Dependencies:** CAT-05 tokens; self-hosted font files with licenses.
- **Risk:** Website reflow says nothing about native constrained outputs (ADOPT-019). The Evidence tab must say so.

### OPUS05-CAT-11: Visual-library maintenance — versioning, changelog, provenance and finish
**Decision: Borrow.**
- Apple's per-page "Change log" (https://developer.apple.com/design/human-interface-guidelines/menus).
- Impeccable's `document` step, its detector for the web (61 rules), and the separate finish reviewer (https://github.com/pbakaus/impeccable; `new-work.md` §7).

- **[ADD]**
  - Semantic versions for the catalog.
  - A per-component changelog entry linked to a source hash diff.
  - A deprecation state.
  - Illustrations and screenshot goldens labeled "browser render".
  - Raster provenance from `asset-manifest.json`.
  - A `DESIGN.md` documented from the built site.
  - The Impeccable detector runs on website HTML/CSS only. Never present it as a native verdict.
- **EARS:** When a manifest component's source hash changes, the catalog shall require a changelog entry for that component before publishing.
- **Acceptance:** A `Menu.elm` hash bump without a changelog entry blocks the publish step.
- **Dependencies:** CAT-01; existing publication authorization.
- **Risk:** Maintenance load. Mitigate by generating the changelog skeleton automatically.

### OPUS05-CAT-12: Reject platform look-alikes, dynamic color and protected assets
**Decision: Reject.**

The brief pins Warlock's world (Impeccable: "The brief wins"). Operate-mode guidance says a world contributes only type, palette, density and one signature move (`mode-operate.md`).

- **Rejected:**
  - Material dynamic color.
  - Ripple effects.
  - Fluent materials such as Mica and Acrylic.
  - Platform taskbar look-alike themes.
  - Any reproduction of platform marks or screenshots.
- **Borrowed:** platform *behavior conventions*, documented as patterns with links.
- **EARS:** The catalog shall not include platform logos, platform screenshots, or themes named after another platform. Comparisons shall be text and links.
- **Acceptance:** Asset provenance scan shows zero third-party platform rasters.
- **Dependencies:** none.
- **Risk:** Readers lose visual comparisons. Links to the primary sources compensate.

---

## 4. Borrow matrix

"Platform requirement" means implementation detail that belongs to that platform and is never inherited by Warlock.

| Family | Pattern | Decision | Warlock adaptation | Platform requirement (not borrowed) |
|---|---|---|---|---|
| Material | Ref / sys / comp tokens (https://m3.material.io/foundations/design-tokens/overview) | Adapt | Schema 2 tiers (CAT-05) | `md.*` names, dynamic color |
| Material | Component tabs | Adapt | Six tabs plus Evidence (CAT-02) | — |
| Material | Interaction states (https://m3.material.io/foundations/interaction/states/applying-states) | Adapt | Interaction axis (CAT-04) | Ripple, state-layer opacities |
| Material | Menu keyboard and typeahead (https://m3.material.io/components/menus/accessibility) | Borrow arrows and Escape; defer typeahead | CAT-07 | Android IME and Back behavior |
| Impeccable | Read mode for docs; Operate's four contributions | Borrow | Site is Read; demos Operate | — |
| Impeccable | Craft floor (contrast, states, browser surfaces, eyebrow ban) | Borrow | CAT-10, CAT-11 | — |
| Impeccable | Reflex-face list (Space Grotesk, Inter) | Reject | Brand pins these faces | — |
| Impeccable | Detector and documenter | Borrow | Web only (CAT-11) | Native skips the detector |
| Apple | IA: Foundations / Patterns / Components / Inputs | Adapt | CAT-02 | — |
| Apple | All-unavailable menu stays openable | Borrow | Already true: `Menu.Open` accepts all-disabled items | AppKit menu APIs |
| Apple | Title-style capitalization | Reject | Sentence case (CAT-09) | — |
| Apple | 200 % text, Reduce Motion, 4.5:1 / 3:1 contrast | Borrow | CAT-05, CAT-10 | Dynamic Type, SF fonts |
| KDE | Actionable errors; success shown as a state change | Borrow | Committed closes the menu; Shell notices | Plasma OSD, task manager badges |
| KDE | Distinguishing detail first in names | Adapt | Picker entry: title before application | — |
| KDE | Title case | Reject | — | — |
| GNOME | Patterns: containers / navigation / controls / feedback | Adapt | Patterns section | libadwaita widgets |
| GNOME | Ellipsis rule; Tab / Return / Space / Esc | Borrow | CAT-07, CAT-09 | — |
| GNOME | Access key on every menu item; 3–12 items | Defer | Native keyboard scope (ADOPT-029); source allows 64 items | GTK mnemonics |
| Windows / Fluent | Controls index plus Gallery | Borrow | CAT-01, CAT-06 | WinUI APIs |
| Windows / Fluent | Popup cycling; Esc cancels transient UI | Borrow | Matches `Menu.navigate` | `XYFocusKeyboardNavigation` |
| Windows / Fluent | Single tab stop for groups; F6 between panes | Defer | ADOPT-029 feasibility | — |
| Windows / Fluent | Disabled items not in keyboard navigation by default | Record as option | ADOPT-030 per-surface policy | Narrator specifics |
| Windows / Fluent | Global / alias tokens; sentence case | Borrow | CAT-05, CAT-09 | Mica, Acrylic |
| Windows / Fluent | Figma kits | Defer | — | — |

---

## 5. Component APIs and state tables

**Bar control** (existing API, [SRC]): `{identity, domId, label, ariaLabel, detail ≤128, enabled}`

| Kind | Interaction states | Disabled behavior |
|---|---|---|
| `control-group` | rest, hover, focus-visible, pressed | Native `disabled`; not focusable today (F4) |
| `control-utility` | same | same |
| `control-recovery` | same, plus outcome via the status line | same |

**Popup modes:**

| Mode | Heading | Container role | Item role |
|---|---|---|---|
| `closed` | — | — | Popup list must be empty (`SurfaceRenderer.elm:34`) |
| `picker` | "Choose a window" | `group` | `button` plus inline preview |
| `applications` | "Applications" | `group` | `button` |
| `menu` | "Window actions" | `menu` | `menuitem` (F2 open) |

**Taskbar decision** (`Taskbar.primary`, [SRC]):

| Families present | Condition | Decision |
|---|---|---|
| 0 | pinned | Launch |
| 0 | not pinned | Unavailable |
| 1 | `!available` | Unavailable |
| 1 | `minimized` | Restore |
| 1 | `active` | Minimize |
| 1 | otherwise | Activate |
| more than 1 | — | Picker |

**Menu lifecycle** ([SRC], `Menu.update`):

| Event | Ready | Pending i | Unknown i |
|---|---|---|---|
| Activate enabled item, no outstanding request | → Pending, emits `Dispatch` | no-op | no-op |
| Committed i | — | menu closes | menu closes |
| Refusal r | — | → Refused r (≤256) | → Refused r |
| Cancellation | — | → Cancelled | → Cancelled |
| Uncertain / disconnect | — | → Unknown i | stays Unknown |
| Dismiss | closes | closes; obligation retained | closes; obligation retained |
| Invalidate / OutputRetired matching | closes | closes; obligation retained | closes; obligation retained |

**[ADD] Proposed `comp` tokens:** `comp.barControl.{minTarget, gap, labelType, detailType, focusRing}`, `comp.popup.{maxWidth, padding, elevation}`, `comp.menuItem.{height, selectedIndicator}`, `comp.statusLine.{type, outcomeGlyph}`. Values are deferred until the real stylesheet is supplied (F6).

---

## 6. Accessibility and keyboard contracts

| Component | Key | Effect | Evidence |
|---|---|---|---|
| Menu | Down / Up with no selection | First / last enabled item | [SRC] `Menu.elm:315-326` |
| Menu | Down / Up at the end | Wraps (cycling) | [SRC] |
| Menu | Home / End | First / last enabled item | [SRC] |
| Menu | Enter / Space | `Activate`; ignored while the same target is pending | `Msg` [SRC]; binding unverified |
| Menu | Esc | `Dismiss`; pending obligation retained | `Msg` [SRC]; binding unverified |
| Bar | Tab / Shift+Tab | Each enabled control is a tab stop | [SRC] via HTML semantics; [NATIVE] scope needs ADOPT-029 |
| Bar | Enter / Space | Native button activation then `requestAction` | binding unverified |
| Picker / applications | Tab between buttons | Per-button tab stops | [SRC]; arrow navigation deferred |
| All | Disabled | Skipped (HTML `disabled`; `navigate` filters) | [SRC]; ADOPT-030 policy version pending |

**Further contracts:**
- **Focus:** a visible `focusRing` token at ≥ 3:1 on both surfaces. Selection and focus must look different (KDE: https://develop.kde.org/hig/accessibility/).
- **Announcements:** the catalog documents F3 and makes no single-owner claim until ADOPT-012 is qualified [NATIVE].
- **Text and contrast:** CAT-05 contrast gate; 200 % / 400 % zoom (CAT-10).
- **Motion:** reduced motion responds live.
- **Native acceptance** of speech, braille, IME, keyboard scope and AT-tree relationships is out of scope for the website.

---

## 7. Website structure, demos and coverage

```
/                 Overview: one sentence, decision rule, "what is qualified today"
/foundations/     principles · outcome-language · color · typography · sigil-and-icons · motion · voice-and-content · density-and-layout
/components/      taskbar-bar · bar-control · status-line · window-picker · preview-tile · applications-list · window-actions-menu
/patterns/        request-and-confirmation · unavailable-actions · reconnect-and-recovery · grouped-windows · keyboard-entry-exit · constrained-geometry
/accessibility/   keyboard · names-roles-states · announcements · reduced-motion · contrast
/tokens/          tables (both themes) · contrast matrix · JSON/CSS export
/evidence/        levels · ledger links · what a browser cannot prove
/changelog/
```

**Demos** [DEMO], all using the Simulated authority panel:

| Demo | Covers | Status |
|---|---|---|
| Bar with the 3 control kinds | Enabled and disabled; keyed reorder that preserves focus (ADOPT-016 illustration) | Buildable now |
| Popup in all 4 modes | Including the empty `closed` case | Buildable now |
| Menu with all 12 actions | All 5 statuses; navigation; duplicate-activation suppression; dismiss and reopen while Pending/Unknown; invalidation and output retirement; 64-item limit | Buildable now |
| Taskbar decision matrix | Every row of §5 | Needs `ActionProjection` (absent) |
| Shell notice gallery | All ~20 strings and 5 recovery failures, with their trigger `Msg` | Buildable now |
| Picker preview tile | — | Needs `PreviewLifecycle` (absent) |

**Coverage gate (CAT-01):** 100 % of manifest identities across all 12 actions, 5 statuses, 4 targets, 4 modes, 3 kinds, 4 decisions and every notice string.

---

## 8. Disagreements and tradeoffs for peer review

1. **Flow-ribbon signature move vs `decorativeDiagramNotProtocolEvidence`.** I argue a transcript of the reader's own simulated events is factual and labeled. A peer could reasonably reject it.
2. **Sentence case vs title case.** Apple, GNOME and KDE favor title or header case; Fluent and the current source use sentence case. I recommend sentence case.
3. **Disabled focusability (ADOPT-030).** Windows' default and the current source skip disabled controls. Other conventions let disabled items take focus so they can be discovered. The catalog should publish whatever is chosen and not prejudge it.
4. **Roving bar focus.** Per-button tab stops today vs a single tab stop (Windows group pattern). Deferred to P5 feasibility.
5. **Coupling the site to frozen module hashes (CAT-06).** This catches drift, but every component change triggers a catalog rebuild. The alternative, screenshots, drifts silently.
6. **Impeccable reflex-face warning vs pinned brand fonts.** I side with the brand ("The brief wins").
7. **Publishing internal limits** (64 items, 2048 entries, 259/2051 controls). They are useful to integrators but invite treating them as UX promises.
8. **Gold for Unknown.** It is a warm, attention-drawing color, but the brand restricts its meaning.
9. **Light `border` ≈ 3.05:1 on parchment.** It passes, but by a slim margin. Should it darken in schema 2? That changes a schema 1 value only if replaced, so it would need to be added as a separate `sys` token.
10. **F1 and F2 findings.** Should the catalog lint block publication, or only report? I recommend report only, so frozen components are not altered.

---

## 9. Machine-readable proposal records

```json
[
 {"id":"OPUS05-CAT-01","title":"Source-derived widget manifest and coverage gate","decision":"borrow-adapt","ears":"When the catalog builds, the build shall fail if any manifest identity lacks a catalog page or state row, or any page cites an identity or source hash absent from the manifest.","acceptance":["Removing ExitFullscreen row fails build naming Menu.Action.ExitFullscreen","Changing Menu.elm without regeneration fails on hash mismatch"],"sourceUrls":["https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/","https://m3.material.io/components"],"dependencies":["frozen source hashes","catalog lane ownership"]},
 {"id":"OPUS05-CAT-02","title":"Read-mode IA with uniform six-tab component pages","decision":"adapt","ears":"The catalog shall present every manifest component with Overview, Anatomy & states, Behavior & keyboard, Accessibility, Content and Evidence tabs in that order, showing 'Not yet specified' where content is unverified.","acceptance":["Window-actions menu page shows six tabs","Its Evidence tab lists only Source and Browser demo items"],"sourceUrls":["https://developer.apple.com/design/human-interface-guidelines/","https://developer.gnome.org/hig/","https://m3.material.io/components/navigation-bar/overview","https://github.com/pbakaus/impeccable"],"dependencies":["OPUS05-CAT-01"]},
 {"id":"OPUS05-CAT-03","title":"Evidence-level labeling on every behavioral claim","decision":"original","ears":"The catalog shall display exactly one evidence level per behavioral claim and shall not render Native qualified unless a frozen native receipt and owning ABI tuple are linked; while rendered in a browser, demo interaction shall not change any evidence level.","acceptance":["Committed-closes-menu shows Source and Browser demo","Native label without receipt fails build"],"sourceUrls":["https://developer.apple.com/design/human-interface-guidelines/menus"],"dependencies":["evidence ledger","receipt format"]},
 {"id":"OPUS05-CAT-04","title":"Orthogonal interaction and outcome state axes","decision":"adapt","ears":"The catalog shall render each outcome state with a text word and a non-color glyph; when a demo is in Unknown, it shall not offer automatic retry.","acceptance":["Grayscale outcome table remains distinguishable","Unknown demo has no Retry control"],"sourceUrls":["https://m3.material.io/foundations/interaction/states/applying-states"],"dependencies":["OPUS05-CAT-05","ELM-ADOPT-011"]},
 {"id":"OPUS05-CAT-05","title":"Additive three-tier token schema 2 with contrast gate","decision":"borrow-adapt","ears":"When tokens build, the build shall fail if any sys text pair is below 4.5:1 or non-text/focus pair below 3:1 in either theme, and schema 2 shall reproduce all schema 1 values unchanged.","acceptance":["colors.lilac remains #B7A2FF","Lightening light border to #9AA0AE fails gate"],"sourceUrls":["https://m3.material.io/foundations/design-tokens/overview","https://fluent2.microsoft.design/design-tokens","https://developer.apple.com/design/human-interface-guidelines/accessibility"],"dependencies":["brand owner approval","tokens.css regeneration"]},
 {"id":"OPUS05-CAT-06","title":"Live demos on real Elm modules with explicit simulated authority","decision":"borrow-adapt","ears":"While a demo is active, it shall change outcome state only on an explicit reader action on the Simulated authority panel, label every outcome simulated, and never replay an Unknown request.","acceptance":["Minimize stays Pending after 60 s idle","Second activation while pending emits no Dispatch","Dismiss and reopen shows Pending"],"sourceUrls":["https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/"],"dependencies":["OPUS05-CAT-01","PreviewLifecycle and ActionProjection sources"]},
 {"id":"OPUS05-CAT-07","title":"Published per-component keyboard contract tables","decision":"borrow-defer-roving","ears":"The catalog shall publish key, resulting Msg and evidence level for each interactive component, labeling rows 'binding unverified' where the key binding is not in verified source.","acceptance":["Menu Down with no selection maps to first enabled item labeled Source","Esc row reads binding unverified"],"sourceUrls":["https://learn.microsoft.com/en-us/windows/apps/develop/input/keyboard-interactions","https://developer.gnome.org/hig/guidelines/keyboard.html","https://m3.material.io/components/menus/accessibility"],"dependencies":["bridge keymap source","ELM-ADOPT-029","ELM-ADOPT-030"]},
 {"id":"OPUS05-CAT-08","title":"Accessible-name and semantics audit page","decision":"adapt","ears":"When a fixture's ariaLabel does not contain its visible label (case-insensitive, whitespace-normalized), the catalog build shall report a label-in-name finding against that fixture and component.","acceptance":["Label Firefox with ariaLabel 'Switch to window 3' produces a finding"],"sourceUrls":["https://develop.kde.org/hig/text_and_labels/","https://develop.kde.org/hig/accessibility/"],"dependencies":["ELM-ADOPT-017","native AT tree acceptance"]},
 {"id":"OPUS05-CAT-09","title":"Sentence-case content standard with source string inventory","decision":"borrow-reject-title-case","ears":"The catalog shall list every user-facing source string with path:line and shall show rule violations as findings rather than silently rewriting strings.","acceptance":["'Connection lost. Reconnect to continue.' passes actionable rule","'Error 42' fails"],"sourceUrls":["https://developer.gnome.org/hig/guidelines/writing-style.html","https://develop.kde.org/hig/status_changes/","https://fluent2.microsoft.design/components/web/react/core/menu/usage","https://developer.apple.com/design/human-interface-guidelines/menus"],"dependencies":["OPUS05-CAT-01","ELM-ADOPT-011"]},
 {"id":"OPUS05-CAT-10","title":"Responsive reading layout and website motion policy","decision":"adapt","ears":"When the viewport is 320 CSS px at 400% zoom, the catalog shall present content without two-dimensional scrolling except inside fixed-size demo canvases; while reduced motion is preferred, it shall run no decorative animation.","acceptance":["No text overflow at 390 and 1440 px","Reduced-motion toggle stops animation without reload"],"sourceUrls":["https://developer.apple.com/design/human-interface-guidelines/accessibility","https://github.com/pbakaus/impeccable"],"dependencies":["OPUS05-CAT-05","self-hosted licensed fonts"]},
 {"id":"OPUS05-CAT-11","title":"Versioning, changelog, provenance and finish review","decision":"borrow","ears":"When a manifest component's source hash changes, the catalog shall require a changelog entry for that component before publishing.","acceptance":["Menu.elm hash bump without changelog entry blocks publish"],"sourceUrls":["https://developer.apple.com/design/human-interface-guidelines/menus","https://github.com/pbakaus/impeccable"],"dependencies":["OPUS05-CAT-01","publication authorization"]},
 {"id":"OPUS05-CAT-12","title":"Reject platform look-alikes, dynamic color and protected assets","decision":"reject","ears":"The catalog shall not include platform logos, platform screenshots or themes named after another platform; comparisons shall be text and links.","acceptance":["Provenance scan shows zero third-party platform rasters"],"sourceUrls":["https://m3.material.io/","https://fluent2.microsoft.design/","https://developer.apple.com/design/human-interface-guidelines/"],"dependencies":[]}
]
```
