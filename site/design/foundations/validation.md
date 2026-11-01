# Validation

Source commit: `bc3daf7b80ac7295a1ba1e56639a0e130e520a3c`.

- `python3 design/foundations/generate.py` compiles the shared `assets/shared/tokens.json` source. Two successive runs produce identical SHA-256 hashes for all four foundation exports. The compiler rejects unresolved aliases and cycles.
- `assets/shared/contrast.json` records 309 unrounded comparisons. All standard, protanopia and deuteranopia values meet their listed thresholds. This includes action states, focus gaps and the focused/unfocused edge comparison.
- The supplied Chromium harness loads `design/foundations/specimen.html` beneath `/Warlock/` with no console errors, failed requests or external requests. `/tmp/foundations-final.png` was visually inspected at 1440 × 900. Night and Dawn render side by side; High contrast follows below the viewport.
- The same harness loads `test-drive/index.html` without console errors or external requests. At 1440 × 900 the Elm taskbar fits its toolbar without horizontal overflow: group details are visually hidden and carried by accessible names, no label is truncated, and the tray and status chip sit at the inline end. One viewport is not a passing integrated layout audit.
- `architecture/architecture.json` matches the supplied model byte for byte, SHA-256 `1882bf787bb02dc1fa310ea872e49cc688bb8b3604f8839531eec2b041aec24d`. `node --check architecture/architecture.js` passes.
- The generated Night and Dawn studies are illustrations. Their layouts differ and they do not establish native or browser behaviour. The HTML and tokens specify the design.

## Outstanding evidence and implementation

The static specimen does not exercise portal admission, completion, cancellation or focus loss. Its scene is illustrative and is not a native window. It needs a renderer-backed executable attention and effects gallery, four complete shared action treatments, a visible unavailable cue, renderer-provided field labels and a forced-colour audit of focus separation. The area stylesheet is not yet the single runtime shared-control implementation. The image studies need a matched composition and consistent state details.

The integrated scenario matrix, all-package selector isolation, 100/125/150/200% text scale, 200% zoom, 320px viewport, text-spacing, keyboard scroll edges, forced colours, reduced preferences, WebKitGTK, Firefox, portal performance and native compositor checks have not been performed. A successful initial desktop render does not verify receipts, focus handshakes, operation replay or all registered scenarios. Native decoration and portal integration need native evidence. Taskbar fit is checked at 1440 × 900 only.

## Revision checks

`python3 design/foundations/generate.py`, followed by `python3 assets/shared/authoring/compile.py --check` and `cmp assets/shared/tokens.css design/foundations/tokens.css`, passes. The compiler retains the full precision of numeric token values; the foundation and shared exports match. All 309 recorded comparisons pass their standard and two simulated thresholds.

The Chromium harness loads the foundation specimen at `/Warlock/design/foundations/specimen.html` with no console errors, failed requests or external requests. The 1440 × 900 capture at `/tmp/foundations-revision.png` was inspected. The activity contour is inset independently of the outer guard, the title beacon reserves its slot in both focus states, and the recipient mark is on the receiving window. The disabled glyph in this static study is illustrative markup; the source renderer does not supply it.

The illustrations are a generated Night image and a Dawn edit of that image. They retain a common composition but show invented visual controls and are not evidence of supported Settings anatomy. The manifest records the final files and retained earlier drafts separately.

The focus separation in forced colours uses a double outline and still needs a forced-colours rendering audit. The source renderer needs an unavailable mark projection. The actual desktop integration still lacks the required executable attention and portal lifecycle gallery, verified Elm effect lifecycle, four complete action tiers, unfocused shadow attenuation, and the full test matrix listed above. Other packages' bootstrap files and manifests are outside D01's assigned paths. These checks claim no cross-browser, native or ten-package typography result.

## Current revision

The Chromium harness loaded `design/foundations/specimen.html` and `test-drive/index.html` beneath `/Warlock/` with no console errors, failed requests or external requests. The 1440 × 900 foundation capture at `/tmp/foundations.png` was inspected. It shows Night and Dawn, independent activity, candidate, window focus and recipient marks; High contrast continues below the initial viewport. The dense outer-focus source capture was extracted from the pinned repository using `git show` and inspected. `python3 assets/shared/authoring/compile.py --check` and `node test-drive/checks/component-styles.mjs` pass. Runtime HTML links directly to the canonical area CSS; inactive copies remain on disk and are not linked.

The Color and Effects pages provide reference material and a decorative browser gallery. That gallery is illustrative JavaScript, not the Elm portal lifecycle or an admission test. It has not established the one-per-second admission limit, deterministic capture, or application-window event correctness. The current specimen is static; its focus loss, forced-color treatment, action tiers and projected unavailable/outcome semantics remain incomplete. The selected and disabled Settings examples do not establish live Settings behavior.

The shared bootstrap is applied to the foundation specimen and new pages. Other packages' standalone specimens are outside D01's owned paths, and these checks do not verify them. Runtime direct links remove copy drift, but integration and selector isolation across every package still need verification. The focused and unfocused floating shadow strengths, full popup elevation across all renderers and effects-off coverage need further implementation and checks. The original scale, zoom, 320px, text-spacing, keyboard, forced-colors, preference, Firefox, WebKitGTK and native matrices remain unexecuted. The existing generated images are retained without additional mockups.


## Revision verification

Chromium loaded `specimen.html` and `effects.html` under `/Warlock/` with no console errors, failed requests or external requests. The foundation specimen screenshot was inspected at `/tmp/foundations.png`; the Night and Dawn attention scenes, selected and unavailable rows, and focus markers render. `node --check` passes for `attention.js` and `gallery.js`. The runtime popup references `design/previews-snap/preview.css` directly and loads `assets/shared/controls.css` separately from foundation documentation rules.

The renderer emits the Applications and Files field labels and the Settings save captions. The typed outcome, confirmation grouping, Files action caption and picker geometry admission projections are renderer work. The snapshot exposes untyped status text. No Elm bundle is recompiled for these checks. Native compositor behavior, WebKitGTK, forced-colors rendering, focus-ring contrast under forced colors, gallery timing under all interruption paths, sustained operation and frame-time budgets remain unverified. The portal demo is decorative and does not establish the required Elm effect lifecycle.

## Shared control and comparison checks

Chromium toggles `disabled` with `aria-disabled`, `aria-current`, `aria-pressed`, `aria-checked` and `aria-selected` on every visible popup button in the foundations, Task View, System menus, Settings, switcher, Notifications, Applications, Files and previews specimens (956 toggles) and compares each button's border box and its label's position and size before and after: none changes. The unavailable cue sits at the inline end of the first label line, beside the Task View check and bar and the Settings selection bar.

On the foundations Settings scene with `data-motion="full"`, a quiet row reports `transition-duration` 0s at rest, 0.09s under the pointer and 0.06s while pressed. A hovered row that becomes selected, a hovered selected row, a row in `data-motion="reduced"` and a row without a motion attribute all report 0s. A hovered selected row that loses its selection reports 0.09s, the residual pointer case the specification describes.

The cue comparison renders in Chromium at 1440 and 390px. Activating "Focus the first action" from the keyboard focuses the Night affirmative action with the visible focus ring, and the readout names it. The effects-off tiers keep the focused edge and beacon, the activity contour and the candidate brackets; only soft shadows differ. These are static specimen checks; native windows and the renderer are not exercised.

