# Validation

## Checks performed

- Inspected the assigned Elm modules, `shell.css`, v6 list projection, best-practice captures, and dense-picker and popup-remap screenshots. The dense-picker screenshot is read from Git and shows equal outlined rows competing with launch actions. Evidence origins and hashes are in `evidence.json`.
- Rendered `specimen.html` with the requested Chromium harness under `/Warlock/`. The final run reports no console errors, failed requests or external requests. The screenshot is [specimen-chromium.png](evidence/specimen-chromium.png).
- The separate `scale-200.html` fixture sets 200% on its document root and renders at 320px wide. Its focused long query, wrapping status and scrollport appear in the Chromium screenshot. Native search inputs scroll long query text horizontally. The fixture retains tab-reachable management and result controls in source order.
- The Night and Dawn generated studies show the same catalog sequence. They are illustrations, not native or browser evidence.

## Limits and renderer requirements

The gallery is static and does not run the Elm controller. Its associated search label is a proposed renderer enhancement; the existing renderer emits the input and accessible name without the visible label. Add the label while retaining the input identity and composition handlers. The renderer also needs typed outcome and unavailable cues; CSS does not infer them from status text. Submitted closes Applications, so its gallery projection documents wording only.

The screenshot does not establish live keyboard traversal, IME, protocol or native behavior. Full 100/125/150/200% root-scale coverage, 200% browser zoom, text-spacing overrides, focus traversal at every scroll edge, forced colours, reduced motion, all effects tiers, reduced transparency and observed-window portal admission remain integration checks. Cross-browser and native parity remain untested.

## Revision checks

- The requested Chromium harness renders the gallery under `/Warlock/` without console errors, failed requests or external requests. [Gallery](evidence/specimen-chromium.png) and [focused field](evidence/field-focus-chromium.png) are Chromium captures.
- Chromium keyboard traversal moves from the search field through Windows, Refresh, Actions for Editor, Pin Editor, Open Editor and Open Files in source order. Every control retains a visible focus outline and at least 4px clearance in the bounded scrollport; the scroll position advances to expose both final results.
- The primary link uses the information token and opens `../../test-drive/index.html?scenario=launcher`. The Night information/canvas pair is 10.87:1 in the shared contrast matrix.
- The visible label is a separately keyed sibling of the input, which keeps its key and handlers. The compiled test drive shows it, and the repository's browser harnesses pass with it. The 200% fixture does not take focus when the gallery loads.
- The existing images remain unchanged as requested. Their text grouping and missing visible label do not establish renderer behavior. Their hashes and classification are recorded in [the manifest](mockups/manifest.json).

## Director revision

- Both specimen documents load `assets/shared/specimen-bootstrap.css` before the foundation and launcher styles. The Chromium harness reports no console errors, failed requests or external requests; the capture is [specimen-chromium.png](evidence/specimen-chromium.png).
- Chromium measures 16px between Refresh or Acknowledge and an immediately following result, including the 6px flex gap. The same rule retains 16px after the existing management controls.
- The staged renderer and the compiled test-drive Popup emit the label; the input remains separately keyed with its original ID, accessible name and composition handlers.

## Acknowledgement and framing checks

The specimen and the 200% fixture load `assets/shared/specimen-docs.css` after the bootstrap for page typography and framing. In Chromium the Unknown example's acknowledgement computes the essential border on the surface fill, directly after Refresh in source order; enabled launch results compute the raised neutral fill and change to the neutral hover fill under the pointer, with no brand fill. Chromium, Firefox and WebKit load both documents at 1440 and 390px with no console errors. These are static specimen checks.
