# Validation

The supplied Chromium browser check loads `specimen.html` under `/Warlock/` without console errors, failed requests or external requests. `specimen-chromium.png` records the rendering and was visually inspected. The Settings help capture shows the flat list, expanded help and separate motion state. The existing evidence manifest records the high-contrast, appearance and motion captures. The paired illustrations are generated artwork; their omissions and inaccuracies are recorded in `mockups/prompts.md`.

Four separate iframe documents set the root font size to 100%, 125%, 150% and 200%. They exercise rem-based sizing and high-contrast tokens rather than scaling a nested element. Their selected disabled row demonstrates coexistence; its explicit Unavailable wording is a proposed renderer enhancement, not a claim that the current source emits that wording. Independent static draft fixtures put each save with its associated choice and a documentation heading. The 6px list gap and 18px group margin combine to 24px. Fine-pointer hover is gated and disabled controls retain full opacity. Popup size follows the host allocation without subtracting a fixed taskbar height.

The static browser check does not establish keyboard operation, real save outcomes, root-scale behavior in the actual Elm host, forced colours, 200% zoom, 320px width, text-spacing overrides, WebKitGTK, or native effects cancellation. These remain integration checks. D01 must settle effects immediately when motion or effects preferences make an animation impossible, without waiting for `animationend`.

## Revision checks

The supplied browser command renders the revised specimen at `/Warlock/` in Chromium with no console errors, failed requests or external requests. `/tmp/settings.png` was visually inspected. The Settings help native capture was extracted from the recorded commit and inspected. A Chromium keyboard Tab reaches Close and reports `:focus-visible`; the four iframe roots compute to 16, 20, 24 and 32px respectively, and each retains a selected disabled choice. Ten save groups have an associated caption and none contains a save-detail span. These are static specimen checks, not a test of the Elm interaction model.

`git apply --check` accepts `renderer-settings-captions.patch` against the source checkout. The patch is not applied to the shared runtime and has not been compiled or exercised with Elm; integration and focus stability across keyed updates remain required. The renderer's existing selected wording and On/Off details supply the present non-colour state cue; explicit marks and unavailable cues remain renderer work. Forced colours, browser zoom, long-label interaction, WebKitGTK and native preference/effect transitions remain unverified in this revision.

## Director revision

The canonical shared specimen bootstrap and foundations stylesheet load in the Settings specimen and all four scale documents. The specimen uses shared documentation header styling and links directly to the desktop. Chromium loads the revised specimen with no console errors, failed requests or external requests. The rendered Night and Dawn surfaces were inspected in `/tmp/settings.png`.

Chromium pointer-down checks keep the pointer over each control and compare computed backgrounds with the resolved tokens. Neutral, selected and affirmative controls pass: `rgb(56, 48, 50)`, `rgb(66, 48, 53)` and `rgb(150, 26, 32)` respectively. These checks cover the static specimen.

The refreshed `renderer-settings-captions.patch` applies cleanly to `test-drive/runtime/staged/SurfaceRenderer.elm`. It retains the keyed outer item, original button ID, control identity, enablement and source detail, and combines the caption with any existing preview description. It covers appearance, motion and shortcut saves independently. The shared runtime lies outside D08's owned paths, so the patch is not applied or compiled there. D01 must integrate it and rebuild the renderer before the affirmative hierarchy reaches the running desktop. Actual focus retention and independent save behavior remain integration checks.
