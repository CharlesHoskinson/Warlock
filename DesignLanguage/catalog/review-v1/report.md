I reviewed all seven captures and the listed files, plus `src/DesignDemo.elm`, `source/assets/context.js` and `tokens.css` to check two findings.

# Verdict: **accept-with-corrections**

Items B1–B3 must be fixed before the acceptance stands. Each one is small and can be confirmed with a targeted check, not another design loop.

The identity holds together: the folded-W mark (detailed at 36px, mono favicon), Space Grotesk / Inter / JetBrains Mono, solid ink/parchment surfaces with lilac actions, and no glass effects or perpetual motion. Source, Proposed, Demo and Evidence are labelled honestly, and `nativeAcceptance:false` / `fullReleaseAccepted:false` are carried through. I spot-checked the contrast pairs and they pass; light border on page is the tightest at about 3.05:1.

## Blockers / required corrections

**B1. Navigation and search can disappear at desktop width. Your own capture shows it.**
- In `forced-colors-focus.png` the left rail shows only the "Crafted for flow" footer. There is no search box and no nav.
- Cause: at ≤720px, `catalog.js:91` sets `#navigation.open=false`. At desktop width, `catalog.css:4` hides the summary (`.rail details>summary{display:none}`). Once the window is widened again, the closed `<details>` has no visible control to reopen it.
- Who hits it: anyone who resizes, rotates or snaps the window narrow and then wide. That is a common case for a window manager's own docs.
- The "Forced colors and reduced motion active" check in `browser-report.json` passed without noticing.
- Fix: add a `matchMedia('(max-width:720px)')` change listener that sets `open=true` above 720px, or only close the disclosure while the narrow query matches. Then add a check for narrow→wide with `#nav` visible.

**B2. The focus ring on `<main>` covers the TOC text.**
- `catalog.js:88` focuses `main` (tabindex −1) on every route change. The global `:focus-visible` rule (`catalog.css:4`: 3px outline, 3px offset, 3px shadow) then draws a ring around the whole main region.
- Desktop: a lilac vertical bar cuts off the first letter of every TOC entry ("n this page", "verview") in `desktop-menu-unknown.png`, `desktop-preview-historical.png` and `desktop-tokens-light.png`.
- Mobile: it shows as a stray thick rule under the summary in `mobile-overview.png` and `narrow-menu.png`.
- Fix: `main:focus{outline:none;box-shadow:none}`, or move focus to a `tabindex=-1` h1 with a contained ring.

**B3. The menu specimen breaks the source's focus/selection behaviour and mislabels Unknown.**
- *Focus doesn't follow selection.*
  - Source keeps focus on the selected row (`source/assets/context.js:72`) and limits Tab to selected ↔ close (`context.js:56-59`).
  - The catalog's adapter (`catalog.js:69-74`) does neither. Arrow keys move `aria-current` while focus stays where it was.
  - Pressing Enter on a focused, unselected row activates a *different* row (`catalog.js:73`).
  - `catalog.js:49` then describes this divergence ("menu arrows operate the selected item, distinct from focus") as if it were the design.
  - Fix: copy the source's focus-follows-selection and Tab behaviour into the specimen, or clearly label the specimen as diverging from source keyboard behaviour.
- *Unknown reads as Pending.*
  - The catalog-authored wrapper `src/DesignDemo.elm:90` shows "Awaiting confirmation" on every row for both Pending and Unknown (`blocked`, lines 74-79). `desktop-menu-unknown.png` shows this.
  - That contradicts the catalog's own vocabulary ("Unknown — unconfirmed; reconcile before repeating") and DESIGN.md's requirement for distinct outcome cues.
  - Fix: give Unknown its own row detail, e.g. "Blocked until reconciled".
  - This copy also isn't in the source inventory (registry has "Awaiting native confirmation"). Mark row details as fixture copy next to the "Actual Elm modules" label.

## Non-blocking defects
1. **Anchors land under the header on small screens.** `html{scroll-padding-top:88px}` (`catalog.css:4`) is never adjusted at ≤720px. At 320px the sticky header wraps to about 104px (`narrow-menu.png`), so headings reached through TOC anchors end up partly underneath it. Raise the padding in the `catalog.css:7` media block, or make the header non-sticky there.
2. **TOC links don't move keyboard focus.** `catalog.js:90` only calls `scrollIntoView()`, so the next Tab starts from the TOC, not the target section. Give the target h2 `tabindex=-1` and focus it.
3. **Two h1s on menu pages.** The popup specimen puts a second `<h1>` ("Window actions") inside the page's h2 Overview section. `catalog.css:4` restyles it (`.surface-popup>h1`) but the heading outline is still broken. Either note it as a source finding on the component's Accessibility section or wrap the specimen with an explanatory label.
4. **Wrong demo on Utility control.** `registry.json:96`: the Utility control page uses the `applications` demo, so it shows app rows ("Text editor", "Terminal") rather than Applications / Close / Refresh / Reconnect utility buttons.
5. **Disabled rows look enabled in forced colors.** The forced-colors block (`catalog.css:9`) has no `button:disabled` mapping (e.g. GrayText). In `forced-colors-focus.png` the disabled "Size" row matches enabled rows except for its detail text.
6. **Nit:** the search placeholder is cut off at 230px rail width ("Widgets, states, princ"; `index.html:15`).

## Evidence scope limitations
- **No dark-theme captures.** All seven screenshots are light (System resolved to light, plus Light). The dark ink appearance is not visually evidenced.
- **The browser report lists check names only.** It has no measured values (overflow widths, focus targets, contrast), so I couldn't confirm results beyond the screenshots.
- **Some states have no captures.** None for 1100px (TOC hidden), the bar/status/picker/applications specimens, or the closed state of Refused/Cancelled.
- **Things I didn't check:**
  - the hashes and content of the 49 source modules
  - the full output of `design-demo.js`
  - the consensus candidate (`candidate-v2.json`)
  - anything native: GTK fallback, compositor, AT/IME
  
  My conclusions are limited to the catalog's browser behaviour and copy. This review makes no claim about native acceptance or release readiness.
