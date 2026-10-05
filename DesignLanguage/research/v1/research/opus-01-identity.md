# Warlock identity review — reviewer opus-01-identity

**Scope:** brand, philosophy, semantic tokens, typography, light/dark/high-contrast themes, identity rules and visual assets.
**Mode:** read-only planning and research. I edited no files and started no agents.
**Launcher:** the Impeccable context launcher was unavailable, so I read the frozen inputs directly, as SKILL.md allows.
**Consensus:** none is claimed. Every proposal below is one reviewer's position until all five reviewers vote on the exact consolidated text.

## 0. Evidence levels used in this report

Each item is labelled with one of four levels, and the levels are never merged:

- **[SRC] Existing source.** Text or code in `inputs/`, cited by file and line.
- **[PROP] Proposed addition.** Not implemented anywhere.
- **[DEMO] Browser demonstration.** It could run in the catalog website. It is never native evidence.
- **[NATIVE] Native acceptance.** This needs a receipt from the owning compositor, AT, IME or hardware path. This packet supplies no native receipts, and a website demo cannot qualify native release behaviour.

## 1. Design inventory and source traceability

### 1.1 Identity and philosophy [SRC]

- **Philosophy.** The one-sentence thesis is in `PHILOSOPHY.md:7`. The ten commitments are in `:15–53`. Two of them bind identity work directly:
  - "Appearance changes cannot silently change the target of an action" (`:33`).
  - Customization must keep "identity, accessibility, privacy and recovery guarantees" (`:45`).
- **Brand guide.**
  - Tagline: "Crafted for flow." It is explicitly not a performance claim (`BRAND-GUIDE.md:3`).
  - Flow sigil: a W with folded valleys around a central diamond (`:7`).
  - Size ladder: full colour at 32 px and above, monochrome at 24–31 px, a W letterform below 24 px. Clear space is one diamond-width (`:11`).
  - Six named colours (`:15–22`), and a rule against using dark pastels as text on parchment (`:24`).
  - Faces: Space Grotesk Bold for display and the wordmark, Inter for body and controls, JetBrains Mono for code (`:28`).
  - No blackletter or rune alphabets (`:30`).
  - No glows on the small logo or on controls (`:34`).
  - The motion demo starts paused, stops when the page is hidden and obeys reduced motion. The brand defines no product timing (`:36`).
  - Voice examples (`:40–42`).
  - The marble-diagram grammar is borrowed from ReactiveX, with modern TEA rather than Elm Signals (`:46–48`).
- **tokens.json.**
  - Dark set: 11 colours (`:5–17`). Light set: 9 roles (`:18–28`).
  - Typography faces (`:29–33`), logo rules (`:34–39`), motion flags (`:40–45`).
  - `colorNeverSoleSignal` and `decorativeDiagramNotProtocolEvidence` (`:46–49`).
- **Referenced but not in the frozen inputs:** `tokens.css`, `asset-manifest.json`, `prompts/`, the vector sigil, the raster assets, the font files and the offline preview. I could not check asset hashes, the vector geometry or the font licences. Those checks are open.

### 1.2 Token gaps against what the widgets need [SRC → gap]

tokens.json has no roles for:

- focus ring
- selection, current and pressed states
- disabled
- outcome status (pending, committed, refused, cancelled, unknown)
- scrim or elevation
- spacing, radius or type scale
- high contrast

The dark set uses palette names (`lilac`, `mint`). The light set uses semi-semantic names (`accent`, `text`). The two sets therefore have no shared role vocabulary.

### 1.3 Contrast of existing tokens

I computed these by hand with the WCAG 2 relative-luminance formula. No script was run, so treat each ratio as ±0.05 and verify at build time.

| Pair | Dark | Light |
|---|---|---|
| Text on background (parchment on ink / ink on parchment) | 16.6:1 | 16.6:1 |
| Text on surface (#1B1E2B / #FFFFFF) | 14.6:1 | 18.8:1 |
| Muted text on background | 8.8:1 | 6.1:1 |
| Accent on background (lilac / #583DA4) | 8.6:1 | 7.1:1 |
| Mint on background | 12.1:1 | 6.3:1 |
| Gold on background | 11.0:1 | 6.0:1 |
| Danger on background | 9.3:1 | 6.4:1 |
| **Border on background** | 3.9:1 | **3.05:1 (marginal)** |
| Border on surface | 3.4:1 | 3.5:1 |
| Ink on a lilac fill | 8.6:1 | — |
| Lilac on parchment (forbidden by the brand) | — | 1.9:1, which confirms `BRAND-GUIDE.md:24` |

All text pairs pass AA. Most pass AAA. The light border on parchment only just clears the 3:1 Non-text Contrast floor ([WCAG 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)), so it cannot also carry hover or pressed shifts.

### 1.4 Current widget inventory, from the Elm sources in `warlock-preview-provider-v1/src` [SRC]

| # | Widget | Source | States in source |
|---|---|---|---|
| W1 | Taskbar bar (`surface-bar`, keyed) | `SurfaceRenderer.elm:64`, `Bar.elm` | publication/lease stamps; status region |
| W2 | Group button (`control-group`) | `SurfaceRenderer.elm:61`; `Taskbar.elm:25–33` | Launch, Picker, Apply(Restore/Minimize/Activate), Unavailable; active/minimized/available |
| W3 | Recovery refresh (`control-recovery`) | `SurfaceRenderer.elm:61` | enabled/disabled |
| W4 | Utility control (`control-utility`) | `SurfaceRenderer.elm:61` | enabled/disabled |
| W5 | Status line (`role=status`, polite) | `SurfaceRenderer.elm:63–64`; `Shell.elm:68–76` | Connecting…, Applying…, refused, unconfirmed, transport full, history full |
| W6 | Popup surface | `SurfaceRenderer.elm:63`; `Popup.elm` | modes closed/picker/applications/menu; headings "Choose a window", "Applications", "Window actions" |
| W7 | Picker entry with inline preview | `PreviewPresenter.elm:99–101` | current stamp vs closed; preview view lives in `PreviewLifecycle.inlineView` (not in inputs) |
| W8 | Applications entry | `Catalog.elm:7` | name, iconHint, wmclass; capacity 2048 |
| W9 | Window-actions menu | `Menu.elm:122–169` | Ready/Pending/Refused/Cancelled/Unknown; selected; exhausted |
| W10 | Menu row `menuitem` | `SurfaceRenderer.elm:62` | enabled/disabled; `aria-current` when detail == "Selected" |
| W11 | Recovery notice | `Shell.elm:23–29` | 5 failure kinds |
| W12 | Connection phase | `Shell.elm:31,50,61,65` | Detached/Reconciling/Ready/Exhausted |
| W13 | Brand assets (sigil, wordmark, wallpaper, preview) | `BRAND-GUIDE.md` | size ladder; paused motion |

"All current widgets" cannot be confirmed from this slice. `TaskbarShell`, `Presentation`, `Desktop`, `PreviewLifecycle` and `ActionProjection` are imported but not included. The catalog's coverage gate (WL-ID-11) has to be run against the full repository.

### 1.5 Source observations relevant to identity and accessibility [SRC]

- **O1 — two announcers.** The bar and the popup each render their own `role="status" aria-live="polite"` (`SurfaceRenderer.elm:63,64`). ELM-ADOPT-012 requires one announcement owner.
- **O2 — accessible name may not match the visible label.** `aria-label` comes from a separate `ariaLabel` field, not the visible `label` (`:62`). This risks failing [WCAG 2.5.3 Label in Name](https://www.w3.org/WAI/WCAG22/Understanding/label-in-name.html) (Level A). ELM-ADOPT-017 also says to keep the visible label as the accessible name.
- **O3 — selection inferred from display text.** Menu selection is derived from the display string `detail=="Selected"` and exposed as `aria-current` (`:62`). For a checked choice, APG uses `menuitemradio` with `aria-checked` ([APG menubar](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/)).
- **O4 — disabled controls leave the tab order.** Disabled controls use the native `disabled` attribute (`:62`). `Menu.navigate` skips disabled rows (`Menu.elm:278–328`). APG says "Disabled menu items are focusable but cannot be activated." This is the GTK-versus-APG split that ELM-ADOPT-030 already freezes per surface.
- **O5 — popup controls are not keyed.** Popup controls are built with `List.map` and are not keyed; the bar is keyed (`:63` vs `:64`). This is relevant to ELM-ADOPT-016, though keyed DOM is an implementation choice.
- **O6 — copy uses jargon.** Most copy already matches the brand voice (`Shell.elm:25–29,73–75`). Two strings use internal terms:
  - "Outstanding operation limit reached; reconcile existing requests." (`Menu.elm:473`)
  - "Waiting for a verified output or capacity update." (`Shell.elm:71`)

## 2. Proposals

Each proposal lists its decision, rationale, EARS requirement, acceptance examples, evidence split, dependencies and risk.

### WL-ID-01 — Three-tier tokens: brand reference → semantic role → component

- **Decision:** Adapt.
- **Basis:**
  - Fluent separates context-free "global tokens" from "alias tokens [that] add semantic meaning" and supports "light, dark, high-contrast, and branded" themes ([Fluent tokens](https://fluent2.microsoft.design/design-tokens)).
  - Windows maps every brush through theme dictionaries, including `HighContrast` ([Contrast themes](https://learn.microsoft.com/en-us/windows/apps/design/accessibility/high-contrast-themes)).
  - GNOME: use "color variables… since these automatically adjust for the light, dark and high-contrast styles" ([GNOME UI styling](https://developer.gnome.org/hig/guidelines/ui-styling.html)).
- **Rationale:** The current hex values stay unchanged as the reference tier, so brand identity is preserved. Themes vary only at the role tier.
- **EARS:** Where a Warlock surface or catalog page renders colour, the renderer shall resolve the colour through a semantic role token. No component style shall reference a reference-tier token or a literal colour value.
- **Acceptance:**
  - (a) A lint over the shell CSS and site CSS finds zero hex, rgb or hsl literals outside the token sources.
  - (b) Switching dark → light → high contrast changes every role and no component rule.
  - (c) `tokens.json` schema 2 keeps all schema-1 keys as reference aliases.
- **Evidence:** [PROP] tokens; [DEMO] theme switcher; [NATIVE] a shell restyle receipt (none yet).
- **Dependencies:** tokens.json/tokens.css owner; W08; ELM-ADOPT-019.
- **Risk:** A schema change could break consumers of schema 1. Mitigation: aliases.

### WL-ID-02 — Paired content-on-container roles with frozen contrast floors

- **Decision:** Borrow the pairing; adapt the names.
- **Basis:**
  - Material pairs container and content roles ("Primary" with "On Primary"; `Error`, `On Error`, `Error Container`, `On Error Container`) and ships three contrast levels ([MDC Color.md](https://github.com/material-components/material-components-android/blob/master/docs/theming/Color.md)).
  - The m3.material.io pages returned only their titles (see §8).
  - Floors come from WCAG 1.4.11 and Apple's ratios: 4.5:1 up to 17 pt, 3:1 at 18 pt and for bold ([Apple Accessibility JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/accessibility.json)).
- **Roles:**
  - `bg`/`on-bg`, `surface`/`on-surface`, `surface-raised`, `on-surface-muted`
  - `accent`/`on-accent`, `danger`/`on-danger`
  - `outline`, `outline-strong`
- **The one addition:** `outline-strong` in light mode, for control boundaries that also need state shifts. The current `#838A9A` reaches only about 3.05:1 on parchment. Existing values are not changed.
- **EARS:** The token build shall refuse any declared foreground/background role pair whose WCAG 2 contrast is below its declared floor (text 4.5:1; large text and non-text 3:1) in every theme.
- **Acceptance:**
  - A generated table matching §1.3 is published on the site.
  - A deliberately bad pair (lilac on parchment) fails the build.
- **Evidence:** [PROP]; [DEMO] live contrast table. [NATIVE] is not applicable to the arithmetic, but rendered-pixel checks remain native.
- **Dependencies:** WL-ID-01.
- **Risk:** Builds that fail hard on contrast could block brand experiments. That is intended.

### WL-ID-03 — Outcome-status roles kept apart from decorative accents, with a copy catalog

- **Decision:** Adapt.
- **Basis:**
  - Fluent: "Don't use color as the only way to communicate" ([Fluent color](https://fluent2.microsoft.design/color)).
  - Apple: "Offer visual indicators, like distinct shapes or icons, in addition to color" (Accessibility JSON above).
  - KDE: "indicate success by visually changing something on screen" rather than a "Task completed" message ([KDE status](https://develop.kde.org/hig/components/assistance/progress/)); "Use plain language and minimize technical jargon" ([KDE text](https://develop.kde.org/hig/text_and_labels/)).
- **Rejected:** Fluent's automatic "green for positive" mapping. The brand says decorative mint and gold "never constitute evidence that a request committed" (`BRAND-GUIDE.md:24`).
- **Proposed status table:**

| Status (source) | Role | Glyph (shape) | Required text (catalog) |
|---|---|---|---|
| Pending (`Menu.elm:157`, `Shell.elm:73`) | `status-pending` = on-surface-muted | open ring, no spinner under reduced motion | "Applying window change…" |
| Committed | `status-committed` = on-surface (neutral) | check | none if the target visibly changed (KDE); the menu closes (`Menu.elm:512`) |
| Refused | `status-refused` = danger | bar-cross | "The window change was refused." + reason |
| Cancelled | `status-cancelled` = muted | dash | "Cancelled." |
| Unknown | `status-unknown` = gold role (dark #F0BE75 / light #805010) | hollow diamond + "?" | "The result is still unconfirmed." |
| Unavailable | `status-unavailable` = muted + outline | slashed outline | "The window is unavailable." |

- **Copy rewrites (proposed):**
  - `Menu.elm:473` → "Too many window changes are waiting. Wait for them to finish, then try again."
  - `Shell.elm:71` → "Window changes are paused until the display is available again."
  - Wording review stays with the ELM-ADOPT-011 owner.
- **EARS:** When the controller reports an outcome status, the surface shall present that status's catalog text and glyph. Colour shall not be the only cue, and the Unknown presentation shall share neither glyph nor role with Committed.
- **Acceptance:**
  - A greyscale screenshot of each state is distinguishable.
  - Unknown never shows a check.
  - Mint never appears as a status role.
- **Evidence:** [PROP] roles; [SRC] statuses exist; [DEMO] state switcher; [NATIVE] AT transcript under ELM-ADOPT-012/017.
- **Dependencies:** ELM-ADOPT-011, 012, 017; W08.
- **Risk:** Gold for Unknown could read as "warning" or as brand decoration. Peer vote requested (§7).

### WL-ID-04 — High-contrast theme mapped to system colours

- **Decision:** Adapt.
- **Basis:**
  - Windows pairs `WindowColor`/`WindowTextColor`, `HighlightColor`/`HighlightTextColor` and `ButtonFaceColor`/`ButtonTextColor`, reserves `GrayTextColor` for disabled UI only, says "Do not hard-code colors in HighContrast" and recommends "2px borders for transitory surfaces such as flyouts" (Contrast themes URL above).
  - GNOME: "All parts of the UI should be correctly rendered in the high-contrast style" ([GNOME a11y](https://developer.gnome.org/hig/guidelines/accessibility.html)).
  - Native signal on Linux: `org.freedesktop.appearance` `contrast` (0 = no preference, 1 = higher contrast) ([portal Settings](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html)).
- **Mapping:**

| Role | High-contrast value |
|---|---|
| bg, surface | Canvas / Window |
| on-* | CanvasText |
| accent, focus, selected | Highlight + HighlightText |
| controls | ButtonFace + ButtonText |
| disabled | GrayText (disabled only) |
| popup border | 2 px CanvasText |
| status-unknown and status-refused | rely on glyph + text; colour falls back to CanvasText |
| sigil | monochrome |

- **EARS:** While the native contrast preference reports higher contrast, Warlock surfaces shall resolve roles to the high-contrast set. They shall keep focus, selection, disabled and every outcome state distinguishable without hue.
- **Acceptance:**
  - [DEMO] Chromium `forced-colors: active` and `prefers-contrast: more` emulation for every widget page.
  - [NATIVE] Portal `contrast=1` flipped on a running shell, with screenshot + AT receipts. Not supplied.
- **Dependencies:** WL-ID-01, 03; the native settings bridge owner; W08.
- **Risk:** WebView forced-colours behaviour on the host engine is not qualified yet.

### WL-ID-05 — Live appearance preference that never moves the action target

- **Decision:** Adapt.
- **Basis:**
  - GNOME: apps "follow the system style"; a per-app choice should offer "light, dark, and follow system preference" (UI styling URL).
  - Apple: "Make sure all your app's colors work well in light, dark, and increased contrast contexts" ([Apple Color JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/color.json)).
  - Portal `color-scheme`: 0 = no preference, 1 = prefer dark, 2 = prefer light.
  - Impeccable: choose light or dark from the use scene, not by habit (`craft-floor.md:42`).
- **Proposal:** Follow the system. When there is no preference, fall back to the brand's dark field. Offer the same three-way choice in settings.
- **EARS:** When the system colour-scheme or contrast preference changes, the shell shall re-resolve role tokens without changing focus, selection, publication/lease identity or the pending action target.
- **Acceptance:**
  - [DEMO] Toggle the theme while a menu row is focused; focus id and selection are unchanged.
  - [NATIVE] The same while a Pending intent exists; the receipt binding is unchanged.
- **Dependencies:** ELM-ADOPT-016; W07.
- **Risk:** The restyle can force a WebView relayout. Measure under S02, not here.

### WL-ID-06 — Role-based type scale with the brand faces scoped

- **Decision:** Adapt; reject replacing the faces.
- **Basis:**
  - Material's 12 roles (display, headline, title, body and label, each large/medium/small) referenced by components ([MDC Typography.md](https://github.com/material-components/material-components-android/blob/master/docs/theming/Typography.md)).
  - Windows ramp in effective pixels (caption 12/16, body 14/20, subtitle 20/28, title 28/36), sentence case, no Bold or Italic in the ramp ([Windows typography](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/typography)).
  - GNOME: "Don't hard-code font styles or sizes"; avoid all-caps; the system font is Adwaita Sans, "a variant of Inter" ([GNOME typography](https://developer.gnome.org/hig/guidelines/typography.html)).
  - KDE: plain `QtQuick.Text` "doesn't respect the system's font settings" (KDE text URL).
  - Apple: a custom font for headlines with system fonts for body copy, supporting at least 200 % enlargement (Branding and Accessibility JSON).
- **Roles:**

| Role | Face | Where it may appear |
|---|---|---|
| `display` | Space Grotesk Bold | wordmark and website hero/headings only |
| `title`, `heading` | Inter Semibold | shell and site |
| `body`, `label` | Inter Regular | shell and site |
| `caption` | Inter, tabular numerals | metadata |
| `mono` | JetBrains Mono | code and identifiers on the site only |

  - All sizes are rem or em of the native text scale.
  - Sentence case in UI.
  - WARLOCK in capitals only inside the wordmark.
- **On Impeccable's face lists:** Impeccable's reflex-face list names Space Grotesk (`new-work.md:67`), and its README says the detector flags Inter. "The brief wins" (`SKILL.md:27`), so the faces stay. Record the detector findings as suppressed with this rationale.
- **EARS:** Where text is rendered in a shell surface, the renderer shall size it from a type role relative to the native text-scale factor. Space Grotesk shall appear only in the wordmark and catalog display roles.
- **Acceptance:**
  - [DEMO] At 100 %, 150 % and 200 % browser text zoom, no label clips in W1–W12.
  - [DEMO] A computed-style audit finds Space Grotesk only under `.wl-display` or the wordmark.
  - [NATIVE] The KDE-style test at system font size 14 and the GNOME large-text setting.
- **Dependencies:** ELM-ADOPT-019; font bundle provenance (not in inputs).
- **Risk:** Users who set a different system UI font get Inter anyway. See §7.

### WL-ID-07 — Sigil asset ladder and the rule that brand defers to content

- **Decision:** Borrow and formalize.
- **Basis:**
  - Apple: "Ensure branding always defers to content"; "Resist the temptation to display your logo throughout your app" ([Apple Branding JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/branding.json)).
  - Brand rules: `BRAND-GUIDE.md:11,34`.
- **Proposal:**
  - No sigil and no wallpaper motifs inside the bar, popups or menus.
  - The sigil appears only on the app icon, the About surface, the wallpaper and the website.
  - An asset selector picks by rendered pixel size: 32 px and above full colour; 24–31 px monochrome; below 24 px the W letterform.
  - High contrast → monochrome in CanvasText.
- **EARS:** Where the sigil is rendered below 32 px, or while high contrast is active, the asset selector shall choose the monochrome silhouette (24–31 px) or the W letterform (below 24 px), and shall keep one diamond-width of clear space.
- **Acceptance:**
  - [DEMO] A size-slider page shows the switch points at 31↔32 and 23↔24 px at device pixel ratios 1 and 2.
  - The manifest hash of each variant is shown next to it.
- **Dependencies:** `asset-manifest.json` and the vector sources (not in inputs).
- **Risk:** It is undecided whether the 32 px threshold means CSS px or device px. I propose device px. Vote needed.

### WL-ID-08 — Focus, selection, current, pressed and disabled as distinct visual states

- **Decision:** Adapt.
- **Basis:**
  - KDE: focused items look "visibly different from selected items in inactive views" ([KDE a11y](https://develop.kde.org/hig/accessibility/)).
  - [WCAG 2.4.13](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html) (AAA, adopted here as the target): an indicator at least as large as a "2 CSS pixel thick perimeter" with 3:1 contrast between focused and unfocused states.
  - APG `aria-checked` for menuitemradio.
- **Tokens:**
  - `focus-ring`: lilac on dark (8.6:1 against ink); #583DA4 on light (7.1:1); Highlight in high contrast. 2 px wide, 2 px offset.
  - `selected`: a tinted surface plus a check glyph.
  - `current` (active window): a 2 px underline mark, not a side stripe; Impeccable bans side stripes above 1 px.
- **Semantic change:** The current `detail=="Selected"` string inference (O3) would be replaced by an explicit structured field. That requires a versioned `surfaceProtocol` bump through the owning lane, because the decoder is strict (`SurfaceRenderer.elm:27,34`). Until then, document the current behaviour as-is.
- **EARS:** While a control has keyboard focus, the surface shall draw a focus indicator at least 2 CSS px thick with at least 3:1 contrast against its unfocused pixels, visually distinct from the selected and current indications.
- **Acceptance:**
  - [DEMO] A pixel diff of focused versus unfocused states in all three themes.
  - A selected-and-unfocused row is distinguishable from a focused-and-unselected row in greyscale.
- **Dependencies:** ELM-ADOPT-016, 017, 030; W07.
- **Risk:** The protocol bump touches native ABI identity. It is deferred to the owner.

### WL-ID-09 — Accessible names and a single announcement owner (cross-system)

- **Decision:** Borrow the WCAG rule and route ownership to W07/W08.
- **Basis:**
  - WCAG 2.5.3: "the name contains the text that is presented visually"; best practice is to put it at the start.
  - GNOME: "All interface elements should have descriptive, accessible names."
- **Proposal:**
  - `ariaLabel` must begin with `label`.
  - Transient detail moves to a description (`aria-describedby`), as ELM-ADOPT-017 requires.
  - The two polite regions (O1) collapse to one controller-owned announcer per ELM-ADOPT-012.
  - Enforce in a QA validator and in catalog lint. Do not add a runtime decoder refusal: fail-closed whole-surface refusal is a worse outcome.
- **EARS:** If a published control's accessible name does not begin with its visible label, then the presentation QA validator shall report the control identity and fail the publication fixture.
- **Acceptance:**
  - Fixture `{label:"Firefox", ariaLabel:"Firefox, 2 windows"}` passes.
  - Fixture `{label:"Firefox", ariaLabel:"Browser group"}` fails.
- **Evidence:** [DEMO] axe-style check; [NATIVE] a screen-reader transcript (ELM-ADOPT-012).
- **Dependencies:** W07, W08.
- **Risk:** This is outside the identity role. I flag it for the owner and make no claim.

### WL-ID-10 — Motion roles bound to native presentation and live reduced motion

- **Decision:** Borrow the pattern; defer the numbers.
- **Basis:**
  - KDE: with animations disabled, elements "either transition instantly… or display a static image" (KDE a11y).
  - Apple: reduce "automatic and repetitive animations, including zooming, scaling, and peripheral motion."
  - Portal `reduced-motion`: 1 = reduced.
  - Brand: `tokens.json:40–45`.
- **Proposal:**
  - Named motion roles (`state-change`, `surface-enter`, `reversal`) with no brand-defined durations. Durations come from the frozen S02 policy.
  - Decorative ribbons are demo-only, paused by default and stopped when the page is hidden.
- **EARS:** While the reduced-motion preference is active, the shell and catalog shall replace decorative and velocity-continuation motion with instant or cross-fade changes that convey the same state information.
- **Acceptance:**
  - [DEMO] With `prefers-reduced-motion` on, every outcome state is still announced visually; ribbon animation never auto-starts.
  - [NATIVE] ELM-ADOPT-023 under the original 38/34/52 cases.
- **Dependencies:** S02, W12.
- **Risk:** Designers may push for timing values the brand forbids.

### WL-ID-11 — "Warlock Design" catalog website with evidence badges and a coverage gate

- **Decision:** Adapt the structure; reject platform marks.
- **Basis:**
  - GNOME splits Principles, Guidelines, Patterns (containers, navigation, controls, feedback) and Reference ([GNOME HIG](https://developer.gnome.org/hig/)).
  - Fluent splits Design, Develop, Components and Tokens ([Fluent 2](https://fluent2.microsoft.design/)).
  - Impeccable treats documentation as Read mode (`SKILL.md:41`).
  - The craft floor bans eyebrow kickers, section numbers and identical card grids (`craft-floor.md:25–28`).
- **EARS:**
  - Where a catalog page shows a widget, the page shall display that widget's evidence level (Source, Demo or Native) and shall not display "Native accepted" without a linked native receipt identifier.
  - The build shall fail if any `Html` view surface in the repository is not catalogued.
- **Acceptance:**
  - A coverage report lists W1–W13 plus any widgets discovered in the full repository.
  - A page with a missing receipt shows "Demo only".
- **Dependencies:** WL-ID-01–10, 12; a full repository scan.
- **Risk:** A demo badge could be read as release evidence. The copy must say plainly that it is not.

### WL-ID-12 — Demos run the real Elm modules against labelled fixtures

- **Decision:** Adopt.
- **Rationale:** The build-loop rule forbids "an independent frontend or native policy model" (`INSTRUCTIONS.md:7`). So the catalog must compile `SurfaceRenderer`, `Menu`, `Taskbar.primary` and the `Shell.status` strings, and drive them through a fixture port adapter. JavaScript may only inject fixture snapshots and synthetic outcomes, and each must be labelled "Synthetic native outcome".
- **EARS:** The catalog shall render every widget demo through the shipped Elm view and update functions. If a demo needs a native outcome, then the page shall inject it as a labelled fixture and shall not compute state transitions outside Elm.
- **Acceptance:**
  - Each demo bundle's module hashes are shown.
  - A grep finds no JavaScript reimplementation of the `Menu` status transitions.
  - Fixtures pass the same strict decoders (`SurfaceRenderer.decode`, `Catalog.decode`).
- **Dependencies:** a source-hash freeze; WL-ID-11.
- **Risk:** Demo fixtures can drift away from native schemas. Mitigation: share the decoders.

## 3. Borrow matrix

| Family | Borrow | Adapt | Reject | Defer |
|---|---|---|---|---|
| Material ([MDC Color](https://github.com/material-components/material-components-android/blob/master/docs/theming/Color.md), [Typography](https://github.com/material-components/material-components-android/blob/master/docs/theming/Typography.md)) | on-pairing (02) | role type scale (06); 3 contrast levels → 2 + forced (04) | dynamic wallpaper colour (overrides identity); Material shapes and marks | m3 token-tier details (site inaccessible) |
| Impeccable ([repo](https://github.com/pbakaus/impeccable), local refs) | Read mode for the site; craft-floor bans; truth binds claims (11, 12) | audit dimensions as the site QA checklist | its face-reflex warning, since the brief pins the faces (06) | the detector run (launcher unavailable) |
| Apple ([Color](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/color.json), [Branding](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/branding.json), [Accessibility](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/accessibility.json)) | brand defers to content (07); 200 % text; shape + colour (03) | Increase Contrast → portal contrast (04) | Liquid Glass and vibrancy materials; SF fonts and symbols | — |
| KDE ([HIG](https://develop.kde.org/hig/), [a11y](https://develop.kde.org/hig/accessibility/), [text](https://develop.kde.org/hig/text_and_labels/)) | focus ≠ selected (08); animations-off test (10); plain language (03) | title case → sentence case for shell copy | Breeze visuals | — |
| GNOME ([styling](https://developer.gnome.org/hig/guidelines/ui-styling.html), [typography](https://developer.gnome.org/hig/guidelines/typography.html), [a11y](https://developer.gnome.org/hig/guidelines/accessibility.html)) | three-way style choice (05); high contrast for all parts (04); catalog taxonomy (11) | system-font guidance → Inter, close to Adwaita Sans (06) | Adwaita visuals | — |
| Windows ([contrast](https://learn.microsoft.com/en-us/windows/apps/design/accessibility/high-contrast-themes), [typography](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/typography)) and Fluent ([tokens](https://fluent2.microsoft.design/design-tokens), [color](https://fluent2.microsoft.design/color)) | SystemColor pairings, GrayText only for disabled, 2 px flyout borders (04); global/alias tiers (01) | ramp sizes as reference (06) | Segoe, Fluent icons, Mica/Acrylic; automatic green = success (03) | user accent override (portal `accent-color`) |

Patterns are borrowed. Implementation requirements stay platform-specific. On Linux the native signals are the portal keys, not XAML or SwiftUI APIs.

## 4. Proposed token roles, component APIs and state tables

**Role tokens** [PROP]. CSS custom properties `--wl-<role>`, generated from tokens.json schema 2:

- `bg`, `on-bg`, `surface`, `surface-raised`, `on-surface`, `on-surface-muted`
- `accent`, `on-accent`, `outline`, `outline-strong`
- `focus-ring`, `selected-bg`, `current-mark`
- `status-{pending,committed,refused,cancelled,unknown,unavailable}`
- `scrim`

**Theme selectors:**

- `:root[data-theme=dark|light]`
- `@media (forced-colors: active)`
- `@media (prefers-contrast: more)`
- On native, the theme attribute is set from the portal keys.

**Component state attributes** [PROP]. These are derived from typed Elm state, never from display strings:

- `data-status` comes from `Menu.Status`.
- `data-decision` comes from `Taskbar.Decision`.
- `data-phase` comes from `Shell.Phase`.
- `data-mode` already exists [SRC `SurfaceRenderer.elm:63`].

**Group button (W2) state table:**

| Taskbar state | Decision [SRC] | Visual | Accessible state |
|---|---|---|---|
| pinned, no windows | Launch | outline icon | button, "Launch" in the description |
| 1 window, active | Apply Minimize | current-mark | `aria-pressed` is not used; the description says "Active" |
| 1 window, minimized | Apply Restore | muted label | description "Minimized" |
| 1 window, other | Apply Activate | default | — |
| more than 1 window | Picker | count badge + `aria-haspopup` | — |
| unavailable | Unavailable | status-unavailable | disabled per the ELM-ADOPT-030 policy |

**Menu (W9) state table:**

| Status | Rows | Status line | Glyph |
|---|---|---|---|
| Ready | enabled | — | — |
| Pending | inert; re-activation ignored (`Menu.elm:466`) | "Applying window change…" | ring |
| Refused | enabled | refusal text | bar-cross |
| Cancelled | enabled | "Cancelled." | dash |
| Unknown | inert for the same target | "The result is still unconfirmed." | ? diamond |
| exhausted | menu closed | recovery copy | — |

## 5. Accessibility and keyboard contracts

The website documents these contracts. It does not define new native behaviour.

- **Bar:** Tab and Shift+Tab follow the frozen per-surface policy. Enter and Space activate. Native keyboard entry and exit is ELM-ADOPT-029 (P5). No new default shortcut.
- **Menu** [SRC `Menu.elm:141–145,294–328`]:
  - Up and Down move with wrap; Home and End are supported.
  - Enter and Space activate. Escape → `Dismiss`.
  - Typeahead: deferred (APG marks it optional).
  - Disabled rows are currently skipped. APG differs, and ELM-ADOPT-030 decides.
  - The right-click24 contract is unchanged.
- **Picker and applications:** keyboard model not visible in these inputs. It is a coverage gap and must not be invented.
- **Announcements:** one owner (WL-ID-09). Status text is in sentence case and is never the only carrier of an outcome.
- **Focus:** WL-ID-08 indicator. Focus is preserved across theme changes (WL-ID-05).
- **Contrast:** WL-ID-02 floors; WL-ID-04 high-contrast mapping.
- **Text scaling:** up to 200 % (WL-ID-06).
- **Motion:** WL-ID-10.
- **Browser demo versus native:** axe checks, emulation and keyboard scripts on the site are [DEMO]. Speech, braille, IME and portal-flip receipts are [NATIVE]. ELM-ADOPT-012 says ARIA alone is insufficient.

## 6. Website structure, demos and coverage [PROP / DEMO]

**Mode:** Read, with the brand world pinned: ink and parchment grounds, lilac accent, the three faces.

**Signature move:** marble-diagram outcome timelines on the Outcomes pattern page. They show request → Pending → Committed/Refused/Unknown, driven by the real `Menu.update` (WL-ID-12). Each is labelled "Illustrative sequence, not protocol evidence" to honour `BRAND-GUIDE.md:7`.

The site has no eyebrow kickers, no numbered sections and no card grids. The widget index is a table with a live thumbnail rendered by the real view.

**Information architecture:**

- `/` Overview: the one-sentence thesis, what is qualified today, and the evidence legend.
- `/foundations/`: philosophy, voice and copy catalog, evidence levels, the decision rule.
- `/identity/`:
  - sigil (with the size-ladder slider)
  - wordmark
  - illustration and wallpaper
  - assets and provenance (manifest hashes, generation prompts, font licences)
- `/styles/`:
  - colour roles, with a live contrast matrix across dark, light and high contrast
  - typography (role ramp with a zoom control)
  - motion (reduced-motion toggle, paused ribbons)
  - high contrast
  - tokens (JSON/CSS download)
- `/widgets/`: one page each for W1–W12, plus any widgets the repository scan adds.
  - Each page has: Overview, Anatomy, States (live toggles over fixtures), Theming roles, Keyboard and AT, Copy, Evidence (source path and hash; demo; native receipt or "none"), and Source trace (ELM-ADOPT and W-item IDs).
- `/patterns/`: outcomes, focus versus selection, disabled actions (ELM-ADOPT-030), recovery and reconnect, preview liveness versus freshness (ELM-ADOPT-028; labels frozen until review).
- `/accessibility/`: keyboard, screen readers, contrast, text scaling.
- `/evidence/`: the coverage matrix (rows: widgets; columns: dark, light, high contrast, reduced motion, 200 %; level per cell).

**Interactive demos:**

- theme and contrast switcher
- outcome state stepper
- menu keyboard playground
- taskbar decision explorer, driving `Taskbar.primary` with fixture families
- recovery notice gallery
- sigil size slider

**Coverage gates:** 100 % of catalogued widgets × 3 themes × reduced motion × 200 % zoom at [DEMO]. Native columns stay empty until receipts exist.

## 7. Disagreements and tradeoffs for peer review

1. **Inter versus the system UI font.** GNOME and KDE favour the system font. Apple splits brand headings from system body text. Inter is close to Adwaita Sans, but KDE users may have set another font. I recommend Inter by default with a "Use system interface font" setting under `PHILOSOPHY.md:45`. Vote needed.
2. **Gold for Unknown.** It reuses a brand hue and could read as decorative. The alternative is a muted role plus a glyph only.
3. **Disabled focusability.** APG and Windows keep disabled items focusable; GTK skips them. This stays with ELM-ADOPT-030. Identity work only styles whichever policy is frozen.
4. **Structured selected/current field.** A clean semantic fix needs a surface protocol version change. The other option is to keep the string inference and document it.
5. **Dark fallback versus GNOME's light default.** Keep the brand dark only when the portal reports no preference.
6. **Light `outline-strong`.** This adds a value instead of changing the brand's `#838A9A`. Peers may prefer simply darkening the existing border.
7. **Marble signature.** Using the brand's event-dot grammar for real outcome sequences risks implying protocol evidence. The mitigation is labelling; the alternative is static ribbons only.
8. **Impeccable detector flags on Space Grotesk and Inter.** Suppress them with the brief rationale. Do not swap the faces.
9. **User accent colour (portal).** Deferred because it weakens brand identity. Peers may favour it as customization.

## 8. Inaccessible or limited sources

- **m3.material.io** (`/styles/color/roles`, `/foundations/design-tokens/overview`): the fetch returned only page titles. Material claims are cited from Material's own `material-components-android` GitHub docs. One search-engine summary of the m3 contrast levels was not relied on as a quotation.
- **Apple HIG HTML pages:** title only. I used Apple's DocC JSON sources of the same pages under `developer.apple.com/tutorials/data/...`.
- **KDE `/hig/style/typography/`:** failed. I used `/hig/text_and_labels/`.
- **Windows typography:** `/design/style/typography` resolved to the canonical `/design/signature-experiences/typography` cited above.
- **Supporting standards** outside the named families, all fetched: WCAG 2.2 Understanding pages, the ARIA APG menubar pattern, and the xdg-desktop-portal Settings documentation.

```json
[
 {"id":"WL-ID-01","title":"Three-tier tokens: brand reference -> semantic role -> component","decision":"adapt","ears":"Where a Warlock surface or catalog page renders color, the renderer shall resolve the color through a semantic role token; no component style shall reference a reference-tier token or literal color value.","acceptance":["Lint finds zero color literals outside token sources","Theme switch changes roles only","Schema-1 keys preserved as aliases"],"sourceUrls":["https://fluent2.microsoft.design/design-tokens","https://learn.microsoft.com/en-us/windows/apps/design/accessibility/high-contrast-themes","https://developer.gnome.org/hig/guidelines/ui-styling.html"],"dependencies":["tokens owner","W08","ELM-ADOPT-019"]},
 {"id":"WL-ID-02","title":"Paired content-on-container roles with frozen contrast floors","decision":"borrow","ears":"The token build shall refuse any declared foreground/background role pair whose WCAG 2 contrast is below its declared floor (text 4.5:1; large text and non-text 3:1) in every theme.","acceptance":["Published contrast table matches computed values","Lilac-on-parchment pair fails build","Light outline-strong added for control boundaries"],"sourceUrls":["https://github.com/material-components/material-components-android/blob/master/docs/theming/Color.md","https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html","https://developer.apple.com/tutorials/data/design/human-interface-guidelines/accessibility.json"],"dependencies":["WL-ID-01"]},
 {"id":"WL-ID-03","title":"Outcome-status roles separate from decorative accents, with copy catalog","decision":"adapt","ears":"When the controller reports an outcome status, the surface shall present that status's catalog text and glyph; color shall not be the only cue, and the Unknown presentation shall share neither glyph nor role with Committed.","acceptance":["Greyscale screenshots distinguish all states","Unknown never shows a check","Mint never used as a status role","Jargon strings at Menu.elm:473 and Shell.elm:71 reviewed"],"sourceUrls":["https://fluent2.microsoft.design/color","https://developer.apple.com/tutorials/data/design/human-interface-guidelines/accessibility.json","https://develop.kde.org/hig/components/assistance/progress/","https://develop.kde.org/hig/text_and_labels/"],"dependencies":["ELM-ADOPT-011","ELM-ADOPT-012","ELM-ADOPT-017","W08"]},
 {"id":"WL-ID-04","title":"High-contrast theme mapped to system colors","decision":"adapt","ears":"While the native contrast preference reports higher contrast, Warlock surfaces shall resolve roles to the high-contrast set and keep focus, selection, disabled and every outcome state distinguishable without hue.","acceptance":["DEMO: forced-colors and prefers-contrast emulation pass for all widgets","NATIVE: portal contrast=1 flip on running shell with screenshot and AT receipts (not supplied)"],"sourceUrls":["https://learn.microsoft.com/en-us/windows/apps/design/accessibility/high-contrast-themes","https://developer.gnome.org/hig/guidelines/accessibility.html","https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html"],"dependencies":["WL-ID-01","WL-ID-03","native settings bridge","W08"]},
 {"id":"WL-ID-05","title":"Live appearance preference that never moves the action target","decision":"adapt","ears":"When the system color-scheme or contrast preference changes, the shell shall re-resolve role tokens without changing focus, selection, publication/lease identity or the pending action target.","acceptance":["DEMO: theme toggle keeps focused menu row and selection","NATIVE: toggle during Pending keeps receipt binding"],"sourceUrls":["https://developer.gnome.org/hig/guidelines/ui-styling.html","https://developer.apple.com/tutorials/data/design/human-interface-guidelines/color.json","https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html"],"dependencies":["ELM-ADOPT-016","W07"]},
 {"id":"WL-ID-06","title":"Role-based type scale with brand faces scoped","decision":"adapt","ears":"Where text is rendered in a shell surface, the renderer shall size it from a type role relative to the native text-scale factor; Space Grotesk shall appear only in the wordmark and catalog display roles.","acceptance":["No clipping at 100/150/200% text zoom for W1-W12","Computed-style audit finds Space Grotesk only in display/wordmark","NATIVE: system font size 14 and large-text checks"],"sourceUrls":["https://github.com/material-components/material-components-android/blob/master/docs/theming/Typography.md","https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/typography","https://developer.gnome.org/hig/guidelines/typography.html","https://develop.kde.org/hig/text_and_labels/","https://developer.apple.com/tutorials/data/design/human-interface-guidelines/branding.json"],"dependencies":["ELM-ADOPT-019","font bundle provenance"]},
 {"id":"WL-ID-07","title":"Sigil asset ladder and brand-defers-to-content rule","decision":"borrow","ears":"Where the sigil is rendered below 32 px, or while high contrast is active, the asset selector shall choose the monochrome silhouette (24-31 px) or the W letterform (below 24 px), and shall keep one diamond-width of clear space.","acceptance":["Size slider switches at 31/32 and 23/24 device px at DPR 1 and 2","No sigil inside bar, popup or menu","Variant manifest hashes displayed"],"sourceUrls":["https://developer.apple.com/tutorials/data/design/human-interface-guidelines/branding.json"],"dependencies":["asset-manifest.json","vector sources"]},
 {"id":"WL-ID-08","title":"Distinct focus, selection, current, pressed and disabled states","decision":"adapt","ears":"While a control has keyboard focus, the surface shall draw a focus indicator at least 2 CSS px thick with at least 3:1 contrast against its unfocused pixels, visually distinct from the selected and current indications.","acceptance":["Pixel diff of focus states in three themes meets 3:1","Selected-unfocused vs focused-unselected distinguishable in greyscale","Structured selected field only via versioned surface protocol"],"sourceUrls":["https://develop.kde.org/hig/accessibility/","https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html","https://www.w3.org/WAI/ARIA/apg/patterns/menubar/"],"dependencies":["ELM-ADOPT-016","ELM-ADOPT-017","ELM-ADOPT-030","W07"]},
 {"id":"WL-ID-09","title":"Accessible name begins with visible label; single announcement owner","decision":"borrow","ears":"If a published control's accessible name does not begin with its visible label, then the presentation QA validator shall report the control identity and fail the publication fixture.","acceptance":["Fixture label Firefox / name 'Firefox, 2 windows' passes","Fixture label Firefox / name 'Browser group' fails","One announcer per ELM-ADOPT-012 (native transcript required)"],"sourceUrls":["https://www.w3.org/WAI/WCAG22/Understanding/label-in-name.html","https://developer.gnome.org/hig/guidelines/accessibility.html"],"dependencies":["W07","W08","ELM-ADOPT-012","ELM-ADOPT-017"]},
 {"id":"WL-ID-10","title":"Motion roles bound to native presentation and live reduced motion","decision":"borrow","ears":"While the reduced-motion preference is active, the shell and catalog shall replace decorative and velocity-continuation motion with instant or cross-fade changes that convey the same state information.","acceptance":["DEMO: outcome states remain perceivable with reduced motion; ribbons never autostart","NATIVE: ELM-ADOPT-023 under original 38/34/52 cases"],"sourceUrls":["https://develop.kde.org/hig/accessibility/","https://developer.apple.com/tutorials/data/design/human-interface-guidelines/accessibility.json","https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html"],"dependencies":["S02","W12","ELM-ADOPT-023"]},
 {"id":"WL-ID-11","title":"Warlock Design catalog website with evidence badges and coverage gate","decision":"adapt","ears":"Where a catalog page shows a widget, the page shall display its evidence level (Source, Demo or Native) and shall not display Native accepted without a linked native receipt identifier; the build shall fail if any repository Html view surface is uncatalogued.","acceptance":["Coverage report lists W1-W13 plus repository-scan additions","Missing receipt renders 'Demo only'","No eyebrows, section numbers or card grids"],"sourceUrls":["https://developer.gnome.org/hig/","https://fluent2.microsoft.design/","https://github.com/pbakaus/impeccable"],"dependencies":["WL-ID-01..10","WL-ID-12","full repository scan"]},
 {"id":"WL-ID-12","title":"Demos run real Elm modules against labelled fixtures","decision":"adopt","ears":"The catalog shall render every widget demo through the shipped Elm view and update functions; if a demo needs a native outcome, then the page shall inject it as a labelled fixture and shall not compute state transitions outside Elm.","acceptance":["Demo bundles display module hashes","No JS reimplementation of Menu status transitions","Fixtures pass SurfaceRenderer.decode and Catalog.decode"],"sourceUrls":["https://github.com/pbakaus/impeccable"],"dependencies":["source hash freeze","WL-ID-11"]}
]
```
