I have enough evidence. Compiling the report.

---

# Warlock design review: input, accessibility, IME, motion, feedback and errors

**Reviewer:** opus-04-accessibility-motion (Claude Opus 5.5). This review was read-only and is for planning only. The Impeccable launcher was unavailable, so I read the frozen project context directly.

**Evidence levels used throughout:**
- **[S] Existing source:** in the input packet.
- **[P] Proposed addition:** new in this report.
- **[B] Browser demonstration:** can run on the website. It cannot qualify native behaviour.
- **[N] Native acceptance:** needs evidence from the owning ABI tuple, real assistive technology (AT), real input methods (IME) and hardware.

Nothing below claims consensus. The proposals are mine and are offered for the five-reviewer vote.

## 1. Source access and inaccessible pages

| Family | Access | Notes |
|---|---|---|
| Apple HIG | The HTML pages are client-rendered and came back empty. I read the same content through the DocC JSON endpoints (`developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json`). | Citations below use the canonical HIG URLs. Quotes went through a summarising fetch, so treat wording as near-verbatim, not exact. |
| Material 3 | Every m3.material.io page I tried (motion overview, easing-and-duration tokens, states, structure) came back with no content. | Fallback: Google's own `material-components/material-web` token sources. A third-party search snippet said the focus state layer opacity is 0.10. The primary token file says **0.12**, so I used 0.12. |
| Impeccable | Frozen local copy at commit `87a6ab0` (see `provenance.json`), plus the GitHub README. | |
| KDE | develop.kde.org/hig fetched. | KDE has no dedicated keyboard or motion page. That guidance sits in the Accessibility and Status pages. |
| GNOME | Fetched. My guess at the URL `guidelines/feedback.html` returned **404**. | I used `patterns/feedback/*` instead. |
| Windows / Fluent 2 | Fetched. | Fluent 2 publishes no numeric motion tokens. Its accessibility page says nothing about motion. |
| Supplementary standards | W3C WCAG 2.2 Understanding pages, WAI-ARIA APG, the Wayland text-input-v3 protocol, the XDG Settings portal, GTK 4 docs, WebKitGTK 2.54 notes. | I used these because Warlock's real native stack is Linux/Wayland/WebView. |

## 2. Design inventory and source traceability (existing source [S])

**What exists today**

- **Brand tokens:** colours (dark and light), three font families, logo size rules, a motion policy and a semantics block (`tokens.json:5-49`). There are **no** tokens for:
  - focus rings
  - interaction states
  - outcome states (pending, unknown, refused, cancelled)
  - motion duration or easing
  - spacing or target size

  I checked contrast myself:
  - muted on ink: about 8.8:1
  - border on ink: about 3.9:1
  - lilac on ink: about 8.6:1
  - light accent on parchment: about 7.1:1
  - light border on parchment: about **3.05:1**, which only just passes the 3:1 non-text minimum
- **Brand motion rules:** the brand preview starts still; it has an explicit toggle; it pauses when the page is hidden; and it obeys reduced motion. Product timing is deferred to the frozen S02 policy (`BRAND-GUIDE.md:36`, `tokens.json:40-45`). Decorative gold and mint are never evidence of an outcome (`BRAND-GUIDE.md:24`).
- **Philosophy commitments I tested against:**
  - honest outcome classes (`PHILOSOPHY.md:29`)
  - reduced-motion equivalence (`:33`)
  - one announcement per change without moving focus (`:37`)

**Current widgets, all rendered by `SurfaceRenderer.viewWithPreview`**

| # | Widget | Source | Current accessibility facts |
|---|---|---|---|
| W1 | Bar container (keyed by `control:<id>`) | `SurfaceRenderer.elm:64` | Keyed DOM keeps control identity stable. It has no landmark or toolbar role. |
| W2 | Taskbar group button (`bar:group:*`, class `control-group`) | `:61-62`, `Taskbar.elm:25-36` | Primary action is Launch, Picker, Apply(Restore/Minimize/Activate) or Unavailable. |
| W3 | Recovery refresh button (`bar:recovery-refresh`) | `:61` | |
| W4 | Utility button (`control-utility`) | `:61` | |
| W5 | Bar status region (`role=status`, `aria-live=polite`) | `:64` | |
| W6 | Popup container, three modes: picker "Choose a window", applications "Applications", menu "Window actions" | `:63` | Uses `h1`, `role=menu` or `group`. |
| W7 | Popup status (`role=status`, `aria-live=polite`) | `:63` | **A second live region** alongside W5. |
| W8 | Popup control / menu item: label + detail + preview | `:62` | `aria-label` is a separate field from the visible `label`. `detail` is visible but hidden from AT by the aria-label. HTML `disabled`. `aria-current` is derived from the string `detail=="Selected"`. |
| W9 | Inline window preview | `PreviewPresenter.elm:99-101` | `PreviewLifecycle.inlineView` is not in the packet. |
| W10 | Context-menu model: 12 actions; statuses Ready / Pending / Refused / Cancelled / Unknown | `Menu.elm:122-160` | Up/Down wrap and **skip disabled items**. Home/End go to the first/last *enabled* item (`:294-328`). A Committed outcome **closes** the menu (`:512`). A disconnect turns Pending into Unknown (`:253-265`). |
| W11 | Application catalog entry (name, iconHint, wmclass) | `Catalog.elm:7` | Data only. No view in the packet. |
| W12 | Shell notice and phase: Detached / Reconciling / Ready / Exhausted, plus five recovery-failure messages | `Shell.elm:23-31`, `:68-76` | Text-only status. Pending shows "Applying window change…". |

**Gaps and risks I found in the source**

- **Missing modules.** No keyboard or click handlers in Elm: actions arrive through the `requestAction`/`rendererActions` ports (`Popup.elm:14`, `Main.elm:21`). The JS bridge, `Presentation`, `Desktop`, `PreviewLifecycle` and `Effects` are not in the packet. **The keyboard path cannot be traced from this packet.**
- **UI timers.** `Main.elm:36-38` arms Elm `Process.sleep` timers: 2000 ms for prepared/choice deadlines and 10000 ms for `Desktop.Arm`. Two open questions:
  - Their accessibility meaning: if they dismiss something the user can see, that runs into WCAG 2.2.1 Timing Adjustable.
  - Their clock relationship: they are not native monotonic deadlines (ELM-ADOPT-010).

## 3. Proposals

Local ID prefix: **AM**. Decisions: Borrow (B), Adapt (A), Reject (R), Defer (D).

### AM-01 — Outcome feedback ladder (Adapt) [P→B→N]

**What it is:** a single state table that drives every surface's text, glyph, announcement and motion for each operation outcome.

| State | Visible (never colour alone) | Announcement | Motion (full / reduced) | Action offered |
|---|---|---|---|---|
| Ready | Normal control | none | none | — |
| Pending | Control stays put. The status text appears once a frozen S02 delay has passed. The glyph is a hollow ring. | Only when the delay is exceeded: one polite message | Spinner rotates / static ring | Independent controls stay usable |
| Committed | The real state change itself, e.g. the window is gone or the group shows "Minimized" | none for routine actions | Follows native presented geometry / instant | — |
| Refused | Persistent text "The window change was refused." plus a reason | polite, once | none | Choose again |
| Cancelled | "Cancelled." | polite, once | none | — |
| Unknown | Persistent text "The result is still unconfirmed." The glyph is a broken ring. | polite, once per intent | none | Reconcile / Reconnect. **Never** an automatic retry. |
| Unsent (proved) | "The request was not sent. Choose again." | polite | none | Choose again |

- **Rationale:**
  - Apple: "people typically expect their action or task to succeed, they only need to know when it doesn't" ([Feedback](https://developer.apple.com/design/human-interface-guidelines/feedback)).
  - KDE: indicate success "by visually changing something on the screen… not by sending a message" ([Status changes](https://develop.kde.org/hig/status_changes/)).
  - GNOME: progress is needed beyond "around three seconds", and brief spinners distract ([Spinners](https://developer.gnome.org/hig/patterns/feedback/spinners.html)). The actual delay value is **not invented here**; it is frozen under S02.
- **Gap in current source:** the copy in `Shell.elm:68-76` and `Menu.elm:473` already matches. What is missing is the glyphs, the delay and the dedupe rule.
- **EARS:**
  - When native authority reports Committed for an intent, the surface shall show the resulting state and shall not show a success message for routine window operations.
  - While an intent is Unknown, the surface shall show persistent "still unconfirmed" text and a reconcile action, and shall not issue a replay.
- **Acceptance:**
  - (a) Minimize then Committed: no message, and the group detail reads "Minimized".
  - (b) Disconnect while Pending: Unknown text persists until reconciled (`Menu.elm:253-265`).
  - (c) Refused: the reason is visible and announced once.
- **Dependencies:** ELM-ADOPT-011, 012, 020, 021; S02. **Risk:** different operations may need different copy. Keep the classes shared and the copy per operation (ADOPT-008).

### AM-02 — State and focus tokens (Adapt) [P→B]

**Proposed tokens to add to `tokens.json`:**

- `focus.ring`: a 2 px outer ring in lilac (dark) or `#583DA4` (light), plus a 1 px inner ring in ink or white, offset 1 px. This adapts Windows' two-part focus visual (2 px primary + 1 px secondary, [Visual feedback](https://learn.microsoft.com/en-us/windows/apps/design/input/guidelines-for-visualfeedback)). Material Web's 3 px focus ring is the alternative I considered ([focus-ring.md](https://raw.githubusercontent.com/material-components/material-web/main/docs/components/focus-ring.md)).
- `state.hover`, `state.pressed`, `state.dragged` as overlay opacities. The structure is borrowed from M3: 0.08 / 0.12 / 0.16, with focus 0.12 ([`_md-sys-state.scss`](https://raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/_md-sys-state.scss)). **Focus must use the ring, not only an overlay.**
- `outcome.{pending,unknown,refused,cancelled}`. Each one = glyph shape + text role + colour, with `colorNeverSoleSignal: true`. Apple: "Convey information with more than color alone" ([Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)). GNOME says the same ([UI styling](https://developer.gnome.org/hig/guidelines/ui-styling.html)).
- **Reject:** using the brand's gold diamond as an outcome glyph. `BRAND-GUIDE.md:24` says decorative gold is never evidence.
- `target.min`: 24 × 24 CSS px as the floor ([WCAG 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)). Bar groups should aim for Apple's macOS 28 pt as the recommended size.
- **EARS:** When any control receives keyboard focus, the surface shall draw `focus.ring` with ≥3:1 contrast against adjacent colours and shall not rely on colour alone to show state.
- **Acceptance:** computed contrast of the ring on ink, surface, parchment and white is ≥3:1; a greyscale capture still tells every outcome state apart.
- **Dependencies:** ADOPT-019. **Risk:** light-theme `border` is only 3.05:1, which makes it fragile next to the ring. Consider darkening it.

### AM-03 — Motion roles and the reduced profile (Adapt; Reject bounce and elastic) [P→B→N]

**Roles** (values for the product are frozen under S02; the website may show values clearly labelled as illustrative):

| Role | Full profile | Reduced profile |
|---|---|---|
| `popup.enter` / `popup.exit` | opacity plus a small translate, exit reverses entry | opacity only, or instant |
| `window.geometry` (minimize, restore, maximize) | follows **native last-presented geometry** (W12) | instant snap to the confirmed geometry |
| `state.change` | opacity/colour crossfade only | the same crossfade is allowed, or instant |
| `pending.indicator` | rotation | a static glyph |
| `preview.update` | crossfade | instant swap |

- **Easing and duration vocabulary** to borrow: M3 tokens (e.g. standard `cubic-bezier(0.2,0,0,1)`, durations from 50 to 1000 ms; [`_md-sys-motion.scss`](https://raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/_md-sys-motion.scss)) and the Windows purpose table (83 ms linear fade; exits always combined with a fade-out; [Motion in Windows](https://learn.microsoft.com/en-us/windows/apps/design/motion/)).
- **Reject:** Windows' "Strong Entrance" elastic curve and its minimize "bounce". They clash with Apple's guidance to "avoid adding motion to UI interactions that occur frequently" and "let people cancel motion" ([Motion](https://developer.apple.com/design/human-interface-guidelines/motion)), and Impeccable lists bounce/elastic easing as an anti-pattern ([README](https://github.com/pbakaus/impeccable)).
- **Reduced-profile mapping:**
  - Apple: replace x/y/z transitions with fades and track gestures directly ([Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)).
  - KDE: animations either "transition instantly" or show "a static image" ([Accessibility](https://develop.kde.org/hig/accessibility/)).
  - Impeccable audit: avoid a global 0.01 ms kill that destroys useful feedback (`audit.md:15`).
- **EARS:**
  - While the reduced-motion preference is active, every surface shall replace spatial motion with opacity or an instant change, shall show the pending indicator statically, and shall not continue an animation from its velocity.
  - When a user acts during an animation, the surface shall accept the input without waiting for the animation to finish.
- **Acceptance:**
  - (a) Toggle reduced motion mid-popup-entry: the popup settles at its final position on the next frame.
  - (b) Clicking during the exit animation is never swallowed.
  - (c) [N] native presentation timestamps for the original restore38 / recovery34 / drag-resize52 cases.
- **Dependencies:** ADOPT-023, 024; W12; S02. **Risk:** a gap between geometry the UI has confirmed and geometry that has actually been presented. Motion must follow the presented geometry, never the UI's guess.

### AM-04 — Reduced motion as a typed native observation (Borrow the platform requirement) [P→N]

**Native sources:**
- XDG Settings portal `org.freedesktop.appearance reduced-motion` (0 = no preference, 1 = reduced), with `SettingChanged` for live updates ([portal Settings](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html)).
- GTK ≥4.22 `gtk-interface-reduced-motion` ([GTK](https://docs.gtk.org/gtk4/property.Settings.gtk-interface-reduced-motion.html)).
- The legacy toolkit-wide switch `gtk-enable-animations` ([GTK](https://docs.gtk.org/gtk4/property.Settings.gtk-enable-animations.html)).

**Why a CSS media query is not enough:** WebKitGTK's `prefers-reduced-motion` follows the dedicated setting only as of 2.54 ([WebKitGTK 2.54](https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html)). Each WebView surface could therefore disagree with the others.

**Proposal:**
- The native side supplies `{reducedMotion, contrast, revision}` as a read-only observation into the single Elm policy model.
- Elm projects it into every surface packet.
- CSS media queries are only a fallback on the website.
- The portal's `contrast` key should feed high-contrast tokens through the same path. GNOME and KDE both require high-contrast testing.

**EARS:** When the native reduced-motion observation changes, the controller shall publish the new motion profile to every surface in the next publication, and each surface shall apply it to any in-flight animation.

**Acceptance:** [N] change the portal setting while a popup is open on two outputs; both surfaces switch profile, with a native trace showing the matching revision.

**Dependencies:** ADOPT-017, 023; W08, W12. **Risk:** portal availability on the Omarchy session. A declared fallback order is required.

### AM-05 — Accessible name, description and state contract for surface controls (Adapt) [S-fix→B→N]

**Current problems in `SurfaceRenderer.elm:62`:**
1. `ariaLabel` is independent of the visible `label`. This is a WCAG 2.5.3 risk ([Label in Name](https://www.w3.org/WAI/WCAG22/Understanding/label-in-name.html): "the name contains the text that is presented visually"; best practice is to start the name with it).
2. `detail` (e.g. Minimized, Pending) is visible but replaced by the aria-label, so AT may never hear it.
3. `aria-current` is derived from the display string `"Selected"`.

**Proposal:**
- The accessible name equals the visible label (or starts with it).
- `detail` is exposed through `aria-describedby` or the native description.
- A **typed** state field `{selected, checked: Maybe Bool, outcome}` replaces string matching.
- AlwaysOnTop and PinToTaskbar, which are boolean toggles (`Menu.elm:131-132`), render as `menuitemcheckbox` with `aria-checked` ([APG menu](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/)). Apple suggests a checkmark for attributes in effect ([Menus](https://developer.apple.com/design/human-interface-guidelines/menus)).
- KDE asks for unique labels per window and name/type announcements ("Create New Folder, Button"; [Accessibility](https://develop.kde.org/hig/accessibility/)).

**EARS:** The surface shall expose each control's visible label as the start of its accessible name, and shall expose transient detail and outcome as a description or state, not as part of the name.

**Acceptance:**
- (a) A decoder or projection test rejects or flags any `ariaLabel` that does not start with `label`.
- (b) [N] an Orca transcript reads "Firefox, button, Minimized".
- (c) A toggle announces "checked" or "not checked".

**Dependencies:** ADOPT-017; surface protocol version 2 compatibility. **Risk:** a wire change. Version the surface protocol rather than reinterpreting fields.

### AM-06 — Keyboard contract (Borrow the standard keys; Adapt for the shell) [P→B→N]

| Key | Bar | Picker / Applications | Window-actions menu |
|---|---|---|---|
| Tab / Shift+Tab | Enters/leaves the bar as **one** tab stop (roving) | Moves between the popup's regions | Not used (focus stays in the menu) |
| ←/→ | Moves between groups (no wrap) | Grid/row movement | — |
| ↑/↓ | — | Moves within the list | Next/previous, **wrapping** (already in `Menu.elm:314-326`) |
| Home / End | First / last group | First / last item | First / last item |
| Enter / Space | Primary decision (`Taskbar.primary`) | Activate | Activate, or toggle a checkbox item |
| Shift+F10 / Menu key | Opens the window-actions menu for the focused group | — | — |
| Esc | Leaves the bar keyboard scope (ADOPT-029) | Closes; focus returns to the invoker | Closes; focus returns to the invoker |
| F6 | Cycles bar ↔ popup ↔ application | same | same |
| Printable key | — | Typeahead (only when not composing; AM-10) | Typeahead (optional) |

**Sources:**
- GNOME's standard keys table: Return, Space, F10, Menu/Shift+F10, Esc ([Keyboard](https://developer.gnome.org/hig/guidelines/keyboard.html)).
- Windows: single tab stop plus arrow "inner navigation"; menu cycling allowed in popups, but "Cycling should be avoided in non-popup UIs"; F6 cycles panes; Esc cancels transient UI ([Keyboard interactions](https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions)).
- Apple: avoid overriding system shortcuts ([Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards)).

**Rejected here:** a new global default shortcut. ADOPT-029 forbids it.

**EARS:**
- When Esc is pressed in a popup, the shell shall request dismissal and shall return focus to the invoking control if it still exists; otherwise it shall apply the declared fallback.
- Arrow wrapping shall apply only inside popups.

**Acceptance:** [B] a scripted key table on the website; [N] a native key-route transcript per row, including focus remaining in the application.

**Dependencies:** ADOPT-016, 029, 030; the bridge (not in the packet). **Risk:** the bar's arrow keys may collide with compositor bindings. Native qualification decides.

### AM-07 — Per-surface policy for disabled and unavailable actions (Adapt; resolves ADOPT-030 for my surfaces) [P→B→N]

**The platforms disagree:**
- APG: "Disabled menu items are focusable but cannot be activated."
- Windows: disabled items are not reachable by standard keyboard navigation, though Narrator can reach them ([Keyboard interactions](https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions)).
- Apple: if every item is unavailable, the menu stays openable "so people can… learn about the commands it contains" ([Menus](https://developer.apple.com/design/human-interface-guidelines/menus)).

**Current source:** `Menu.navigate` skips disabled items, and the renderer uses HTML `disabled`, which removes the item from focus and the tab order.

**Proposal (frozen policy v1):**
- **Window-actions menu:** disabled items are focusable, use `aria-disabled`, and carry a reason description ("Unavailable while the window is fullscreen").
- **Bar groups:** never disabled. An `Unavailable` decision (`Taskbar.elm:27-29`) stays focusable and explains itself, because it is the only way to learn about that window.
- **Picker rows:** follow the menu policy.

**EARS:** Where a menu item is unavailable, the menu shall keep it focusable, shall refuse activation without emitting an intent, and shall expose the reason as its description.

**Acceptance:** arrowing over a disabled item announces "Close, unavailable, <reason>". Pressing Enter produces no `Dispatch` (`Menu.elm:488` already holds this).

**Dependencies:** ADOPT-030, right-click24. **Risk:** this changes `Menu.navigate` semantics and the existing scenario oracles. Vote needed.

### AM-08 — Repeated input, time limits and timers (Borrow) [S-question→P→N]

- **Repeated input:** repeated activation while Pending creates no second intent (`Menu.elm:466` already holds). Add a static cue, "Still applying…", with **no** second announcement (ADOPT-020).
- **Timers:** no timer may dismiss or invalidate a choice the user can see. Apple: "auto-dismiss on a timer can be problematic… Prefer dismissing views with explicit actions" ([Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)). For each `Process.sleep` in `Main.elm:36-38`, the owners must document whether it is invisible reservation housekeeping or something the user perceives. It must never settle an outcome.
- **EARS:** If a timer expires for a prepared choice the user can see, then the surface shall keep the choice visible and shall not treat the expiry as Refused or Committed.
- **Acceptance:** a slow screen-reader user (simulated with a 30 s dwell) can still activate a picker row, or sees an explicit, re-armable state.
- **Dependencies:** ADOPT-010, 020; WCAG 2.2.1. **Risk:** prepared reservations may genuinely need to expire. If so, separate the internal expiry from the visible UI.

### AM-09 — One announcement owner and channel selection (Adapt) [S-fix→N]

- **Current source:** there are two polite live regions (`SurfaceRenderer.elm:63-64`), so the same status can be heard twice.
- **Proposal:**
  - The controller owns announcements: keyed by `(intent, outcome class)` and delivered once through one designated route.
  - The status text in the other surfaces becomes a non-live description.
  - Ongoing conditions (Detached, Exhausted, recovery failure, Unknown) are presented as **banners**: persistent and not auto-hidden.
  - One-off events are presented as **toasts**, never used for critical information ([GNOME banners](https://developer.gnome.org/hig/patterns/feedback/banners.html), [toasts](https://developer.gnome.org/hig/patterns/feedback/toasts.html)).
- **EARS:** When an outcome class first applies to an intent, the controller shall emit exactly one announcement through the designated route without moving focus ([WCAG 4.1.3](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)).
- **Acceptance:** [N] an Orca speech/braille transcript shows exactly one utterance per outcome, including while focus is in a different application.
- **Dependencies:** ADOPT-012, 017. **Risk:** cross-document WebView AT routing.

### AM-10 — Composition-safe input (Borrow the protocol; Defer text fields) [P→B→N]

- **Context:** the current widgets have no text field. When typeahead or a launcher search arrives, keys consumed by an IME must never trigger shell shortcuts or typeahead.
- **Native contract:** text-input-v3 application order and the `done` serial. Clients apply preedit/delete/commit in a fixed order, and the serial equals the number of commits issued ([text-input-v3](https://wayland.app/protocols/text-input-unstable-v3)).
- **Browser demo:** respects `isComposing`. It cannot qualify native behaviour.
- **EARS:** While composition is active in a Warlock-owned field, the shell shall not interpret key events as shortcuts or typeahead, and shall bind commits to the native composition epoch.
- **Acceptance:** [N] fcitx5/IBus Japanese and Chinese preedit sessions with candidate windows positioned at the cursor rectangle.
- **Dependencies:** ADOPT-018. **Defer:** the search field until native qualification exists.

### AM-11 — Focus continuity and return (Adapt) [P→N]

- **Current source:** a Committed outcome sets `menu = Nothing` (`Menu.elm:512`), but nothing declares where focus goes next.
- **Proposal:** focus returns to the invoking group if it still exists after republication. Otherwise it goes to the declared neighbour, then the bar's first group. Unrelated publications never move focus. Apple: "Avoid changing focus without people's interaction" ([Focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection)). Fluent: focus must not be lost when temporary UI closes ([Fluent accessibility](https://fluent2.microsoft.design/accessibility)). The focused control must not be entirely hidden ([WCAG 2.4.11](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html)).
- **EARS:** When a popup closes for any reason, the shell shall place keyboard focus on the invoking control if it is still eligible, and otherwise on the frozen fallback.
- **Acceptance:** Committed Close of the last window in a group puts focus on the next group, and AT announces the new focus.
- **Dependencies:** ADOPT-016, 029. **Risk:** focus between native surfaces is owned by the compositor.

### AM-12 — "Warlock Design" catalog website (Adapt the M3 information architecture; Reject copied marks) [P→B]

**Structure:**
- **Foundations:** Philosophy; Outcome semantics (AM-01); Accessibility; Input & keyboard (AM-06); Motion (AM-03/04); Writing & errors.
- **Styles:** Colour (with computed contrast tables); Type; Sigil; Motion tokens; Focus & states (AM-02).
- **Components:** one page each for W1–W12, i.e. all current widgets including all 12 menu actions. Each page has:
  - anatomy
  - a full state table
  - keyboard table
  - AT name/role/state
  - motion with full and reduced profiles
  - copy
  - **source trace (file:line)**
  - an **evidence badge** ([S]/[P]/[B]/[N])
- **Patterns:** Pending→Outcome; Unknown and reconcile; Reconnect and recovery failures; Disabled actions; Focus return.
- **Evidence:** a coverage matrix of widget × state × input mode × evidence level.

**Demos:**
- Compile the pure `Menu.update`, `Taskbar.primary` and `SurfaceRenderer.view` into the site.
- A **"Simulated authority" panel** lets the viewer inject Committed / Refused / Cancelled / Unknown / late receipt / disconnect events.
- A global reduced-motion toggle that also follows the OS setting.
- Marble-diagram event ribbons that pause when hidden. They are labelled as metaphors (`BRAND-GUIDE.md:46`).
- Every demo carries a banner: "Browser demonstration — not native acceptance."

**EARS:** Each component page shall declare its evidence level and shall not present a browser demo as native qualification.

**Acceptance:** 100% of W1–W12 and every `Status`/`Outcome` constructor appear in the coverage matrix; an axe-core and keyboard pass on the site itself; Impeccable's Read mode applies.

**Dependencies:** AM-01–AM-07. **Risk:** demos drifting from the frozen source. Build them from source hashes.

## 4. Borrow matrix

| Family | Borrow | Adapt | Reject | Defer |
|---|---|---|---|---|
| **Material 3** | Duration/easing vocabulary; the state-layer opacity structure | Focus ring tokens (Warlock colours); site IA (Foundations / Styles / Components) | Ripple; dynamic colour (brand palette is fixed); Material marks and imagery | M3 Expressive springs (primary pages inaccessible) |
| **Impeccable** | Operate-mode restraint (the world lends type, palette, density and one move); audit motion rule; craft-floor states | Read mode for the website; P0–P3 audit for the site | Glass and glow on controls; mono-as-costume | Detector run (launcher unavailable) |
| **Apple HIG** | Make motion optional, cancelable and brief; report failure, not routine success; avoid unprompted focus changes; avoid timers; dim but keep menus | Reduce Motion → fades; checkmarked toggles | SF fonts and SF Symbols (brand uses Inter); iOS 44 pt as the desktop floor | Haptics |
| **KDE** | Actionable errors; success shown as a visible change; instant/static under disabled animations; unique labels | OSD-style transient feedback for global window actions | System-tray persistence | Task-manager progress badges |
| **GNOME** | Standard keys (Shift+F10, Esc, F10); banners vs toasts; ~3 s progress threshold as a candidate input to S02; high-contrast testing | Toast undo — only where native supports reversal | Assumed libadwaita widgets in WebView | — |
| **Windows / Fluent** | Single tab stop + arrows; popup-only cycling; F6 regions; dual-border focus | Purpose-based motion table (exits always fade) | Elastic entrance, minimize bounce, Reveal focus | Access keys (Alt+letter) |

The difference between borrowing a pattern and meeting a platform requirement matters here:
- **Platform requirements** (genuinely binding on Linux): the portal `reduced-motion` and `contrast` keys, GTK settings, text-input-v3 and the AT-SPI route. These are proven only at [N].
- **Patterns:** everything else.

## 5. Disagreements and tradeoffs for peer review

1. **AM-07 vs the current `Menu.navigate`:** whether disabled items should be focusable. APG says yes; GTK/Windows keyboard behaviour says no. I chose focusable for menus. Other reviewers may prefer to keep the current oracle unchanged.
2. **Pending threshold:** GNOME's ~3 s is a platform heuristic. The brand forbids inventing deadlines, so S02 owns the number. Is a candidate value acceptable on the website, labelled illustrative?
3. **Committed silence (AM-01):** an AT user may want confirmation. The alternative is to announce the new state (e.g. "Minimized") rather than "succeeded". I lean toward announcing the state change only when focus is on the affected control.
4. **Bar arrows vs compositor bindings (AM-06):** these may need to be scoped to keyboard mode only (ADOPT-029).
5. **Brand signature move:** I confine the event-ribbon motif to the website, wallpaper and illustrations. It is kept out of product controls (Impeccable Operate; `BRAND-GUIDE.md:34`).
6. **AM-05 decoder strictness:** rejecting a snapshot whose label and name disagree would fail closed and hide the bar. I prefer enforcing it in the projection plus QA, not at runtime decode.
7. **Material's focus opacity:** 0.12 in the primary repo vs 0.10 in third-party echoes. Only the primary value is cited.

```json
[
{"id":"AM-01","title":"Outcome feedback ladder","decision":"adapt","ears":"When native authority reports Committed for an intent, the surface shall present the resulting state and shall not present a success message for routine window operations; while an intent is Unknown, the surface shall show persistent unconfirmed text and a reconcile action and shall not replay.","acceptance":["Minimize Committed shows Minimized detail and no message","Disconnect during Pending yields persistent Unknown text","Refused reason visible and announced once"],"sourceUrls":["https://developer.apple.com/design/human-interface-guidelines/feedback","https://develop.kde.org/hig/status_changes/","https://developer.gnome.org/hig/patterns/feedback/spinners.html"],"dependencies":["ELM-ADOPT-011","ELM-ADOPT-012","ELM-ADOPT-020","ELM-ADOPT-021","S02"]},
{"id":"AM-02","title":"State and focus tokens","decision":"adapt","ears":"When any control receives keyboard focus, the surface shall draw focus.ring with at least 3:1 contrast against adjacent colors and shall not rely on color alone for state.","acceptance":["Ring contrast >=3:1 on ink, surface, parchment, white","Grayscale capture distinguishes all outcome states"],"sourceUrls":["https://learn.microsoft.com/en-us/windows/apps/design/input/guidelines-for-visualfeedback","https://raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/_md-sys-state.scss","https://raw.githubusercontent.com/material-components/material-web/main/docs/components/focus-ring.md","https://developer.apple.com/design/human-interface-guidelines/accessibility","https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html"],"dependencies":["ELM-ADOPT-019"]},
{"id":"AM-03","title":"Motion roles and reduced profile","decision":"adapt","ears":"While reduced motion is active, every surface shall replace spatial motion with opacity or instant change, render pending indicators statically, and not continue velocity; when a user acts during an animation, the surface shall accept the input without waiting.","acceptance":["Reduced-motion toggle mid-entry settles at final position next frame","Input during exit animation is not swallowed","Native presentation timestamps for restore38/recovery34/drag-resize52"],"sourceUrls":["https://developer.apple.com/design/human-interface-guidelines/motion","https://developer.apple.com/design/human-interface-guidelines/accessibility","https://develop.kde.org/hig/accessibility/","https://learn.microsoft.com/en-us/windows/apps/design/motion/","https://raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/_md-sys-motion.scss","https://github.com/pbakaus/impeccable"],"dependencies":["ELM-ADOPT-023","ELM-ADOPT-024","W12","S02"]},
{"id":"AM-04","title":"Reduced motion as typed native observation","decision":"borrow","ears":"When the native reduced-motion observation changes, the controller shall publish the new motion profile to every surface in the next publication and each surface shall apply it to in-flight animation.","acceptance":["Portal change with popups on two outputs switches both surfaces with matching revision in native trace"],"sourceUrls":["https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html","https://docs.gtk.org/gtk4/property.Settings.gtk-interface-reduced-motion.html","https://docs.gtk.org/gtk4/property.Settings.gtk-enable-animations.html","https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html"],"dependencies":["ELM-ADOPT-017","ELM-ADOPT-023","W08","W12"]},
{"id":"AM-05","title":"Accessible name, description and typed state contract","decision":"adapt","ears":"The surface shall expose each control's visible label as the start of its accessible name and expose transient detail and outcome as description or state, not name.","acceptance":["Projection test flags ariaLabel not starting with label","Orca reads label, role, then detail","Toggle actions announce checked state"],"sourceUrls":["https://www.w3.org/WAI/WCAG22/Understanding/label-in-name.html","https://www.w3.org/WAI/ARIA/apg/patterns/menubar/","https://developer.apple.com/design/human-interface-guidelines/menus","https://develop.kde.org/hig/accessibility/"],"dependencies":["ELM-ADOPT-017","surfaceProtocol version bump"]},
{"id":"AM-06","title":"Keyboard contract for bar, picker and menu","decision":"adapt","ears":"When Esc is pressed in a popup, the shell shall request dismissal and return focus to the invoking control if it still exists, else the declared fallback; arrow wrapping shall apply only within popups.","acceptance":["Scripted key table passes in browser demo","Native key-route transcript per row including focus retained in application"],"sourceUrls":["https://developer.gnome.org/hig/guidelines/keyboard.html","https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions","https://developer.apple.com/design/human-interface-guidelines/keyboards"],"dependencies":["ELM-ADOPT-016","ELM-ADOPT-029","ELM-ADOPT-030"]},
{"id":"AM-07","title":"Per-surface disabled and unavailable action policy","decision":"adapt","ears":"Where a menu item is unavailable, the menu shall keep it focusable, refuse activation without emitting an intent, and expose the reason as its description.","acceptance":["Arrowing announces unavailable item with reason","Enter on disabled item emits no Dispatch","Unavailable taskbar group remains focusable with explanation"],"sourceUrls":["https://www.w3.org/WAI/ARIA/apg/patterns/menubar/","https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions","https://developer.apple.com/design/human-interface-guidelines/menus"],"dependencies":["ELM-ADOPT-030","right-click24"]},
{"id":"AM-08","title":"Repeated input and user-perceivable timers","decision":"borrow","ears":"If a timer expires for a user-visible prepared choice, then the surface shall keep the choice visible and shall not treat expiry as Refused or Committed.","acceptance":["30-second dwell still permits activation or shows explicit re-armable state","Repeated activation during Pending yields no second intent or announcement"],"sourceUrls":["https://developer.apple.com/design/human-interface-guidelines/accessibility"],"dependencies":["ELM-ADOPT-010","ELM-ADOPT-020"]},
{"id":"AM-09","title":"Single announcement owner and banner/toast channels","decision":"adapt","ears":"When an outcome class first applies to an intent, the controller shall emit exactly one announcement through the designated route without moving focus.","acceptance":["Orca speech/braille transcript shows one utterance per outcome including with focus outside the shell"],"sourceUrls":["https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html","https://developer.gnome.org/hig/patterns/feedback/banners.html","https://developer.gnome.org/hig/patterns/feedback/toasts.html"],"dependencies":["ELM-ADOPT-012","ELM-ADOPT-017"]},
{"id":"AM-10","title":"Composition-safe input","decision":"defer","ears":"While composition is active in a Warlock-owned field, the shell shall not interpret key events as shortcuts or typeahead and shall bind commits to the native composition epoch.","acceptance":["Native fcitx5/IBus CJK preedit sessions with correctly placed candidates and no shortcut leakage"],"sourceUrls":["https://wayland.app/protocols/text-input-unstable-v3"],"dependencies":["ELM-ADOPT-018"]},
{"id":"AM-11","title":"Focus continuity and return","decision":"adapt","ears":"When a popup closes for any reason, the shell shall place keyboard focus on the invoking control if still eligible, otherwise on the frozen fallback, and shall not move focus on unrelated publications.","acceptance":["Committed Close of last group window focuses next group and AT announces it","Unrelated republication leaves focus unchanged"],"sourceUrls":["https://developer.apple.com/design/human-interface-guidelines/focus-and-selection","https://fluent2.microsoft.design/accessibility","https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html"],"dependencies":["ELM-ADOPT-016","ELM-ADOPT-029"]},
{"id":"AM-12","title":"Warlock Design catalog website with evidence badges","decision":"adapt","ears":"Each component page shall declare its evidence level and shall not present a browser demonstration as native qualification.","acceptance":["Coverage matrix includes W1-W12 and every Status/Outcome constructor","Site passes keyboard and automated accessibility checks","Demos built from hashed frozen sources"],"sourceUrls":["https://m3.material.io/","https://github.com/pbakaus/impeccable","https://developer.apple.com/design/human-interface-guidelines/","https://develop.kde.org/hig/","https://developer.gnome.org/hig/","https://fluent2.microsoft.design/"],"dependencies":["AM-01","AM-02","AM-03","AM-05","AM-06","AM-07"]}
]
```

**Sources:**
- [Apple Motion](https://developer.apple.com/design/human-interface-guidelines/motion) · [Apple Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) · [Apple Feedback](https://developer.apple.com/design/human-interface-guidelines/feedback) · [Apple Progress indicators](https://developer.apple.com/design/human-interface-guidelines/progress-indicators) · [Apple Focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection) · [Apple Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards) · [Apple Menus](https://developer.apple.com/design/human-interface-guidelines/menus)
- [material-web motion tokens](https://raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/_md-sys-motion.scss) · [material-web state tokens](https://raw.githubusercontent.com/material-components/material-web/main/tokens/versions/v0_192/_md-sys-state.scss) · [material-web focus ring](https://raw.githubusercontent.com/material-components/material-web/main/docs/components/focus-ring.md)
- [GNOME Keyboard](https://developer.gnome.org/hig/guidelines/keyboard.html) · [GNOME Accessibility](https://developer.gnome.org/hig/guidelines/accessibility.html) · [GNOME UI styling](https://developer.gnome.org/hig/guidelines/ui-styling.html) · [GNOME Toasts](https://developer.gnome.org/hig/patterns/feedback/toasts.html) · [GNOME Banners](https://developer.gnome.org/hig/patterns/feedback/banners.html) · [GNOME Spinners](https://developer.gnome.org/hig/patterns/feedback/spinners.html)
- [KDE Status changes](https://develop.kde.org/hig/status_changes/) · [KDE Accessibility](https://develop.kde.org/hig/accessibility/) · [KDE Getting input](https://develop.kde.org/hig/getting_input/)
- [Windows Keyboard interactions](https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-interactions) · [Windows Motion](https://learn.microsoft.com/en-us/windows/apps/design/motion/) · [Windows Visual feedback](https://learn.microsoft.com/en-us/windows/apps/design/input/guidelines-for-visualfeedback) · [UISettings.AnimationsEnabled](https://learn.microsoft.com/en-us/uwp/api/windows.ui.viewmanagement.uisettings.animationsenabled) · [Fluent 2 Motion](https://fluent2.microsoft.design/motion) · [Fluent 2 Accessibility](https://fluent2.microsoft.design/accessibility)
- [Impeccable](https://github.com/pbakaus/impeccable)
- [XDG Settings portal](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html) · [GTK reduced motion](https://docs.gtk.org/gtk4/property.Settings.gtk-interface-reduced-motion.html) · [GTK enable animations](https://docs.gtk.org/gtk4/property.Settings.gtk-enable-animations.html) · [WebKitGTK 2.54](https://webkitgtk.org/2026/09/16/webkitgtk-2.54-highlights.html) · [text-input-v3](https://wayland.app/protocols/text-input-unstable-v3)
- [APG Menu](https://www.w3.org/WAI/ARIA/apg/patterns/menubar/) · [WCAG 2.5.3](https://www.w3.org/WAI/WCAG22/Understanding/label-in-name.html) · [WCAG 2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) · [WCAG 4.1.3](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) · [WCAG 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) · [WCAG 2.4.11](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html)
