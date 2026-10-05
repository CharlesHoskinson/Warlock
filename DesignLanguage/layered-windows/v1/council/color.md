# Layered-window council: color and state language

Status: independent council proposal, 2026-10-05. This document proposes additive requirements. It does not qualify native behavior or alter the frozen thirty-contract design consensus. Ownership is limited to this file.

## Recommendation

Use violet to reveal the current path through a stack: an opaque solid contour identifies the observed active window, a restrained static halo reinforces it, and segmented brackets identify its observed family. Neutral shadows and stepped opaque chrome shading describe depth. Navigation candidates use a visibly different corner marker and the word “Candidate” until native focus is observed. Keep content clear and original colors intact. This is a Warlock interpretation of the references, not a platform specification copied into our renderer.

The underlying axes remain separate: observed focus, candidate selection, observed family, observed stacking, pinned/minimized/modal state, and operation outcome. A rendering treatment cannot confer input eligibility, move a window, declare it active, establish family membership or confirm an operation.

## Proposed semantic tokens

The preserved schema-1 brand palette and catalog v6 role mappings remain unchanged. New tokens resolve through semantic roles into existing reference values; proposed extra raised-surface values are additive and require explicit pair checks before adoption.

| Semantic token | Dark | Light | Meaning and non-color partner |
| --- | --- | --- | --- |
| `layer.active.contour` | existing accent `#B7A2FF` | existing accent `#583DA4` | Solid outline for observed active window; “Active” in navigation/readout. |
| `layer.active.halo` | same accent, bounded alpha | same accent, bounded alpha | Static supplemental glow; never substitutes for opaque contour. |
| `layer.candidate.contour` | existing accent | existing accent | Corner marker on navigation tile, “Candidate” label; cannot replace actual active contour. |
| `layer.family.marker` | existing accent | existing accent | Segmented brackets or linked glyph plus “Family”; no second active ring. |
| `layer.rest.boundary` | existing boundary `#68718C` | existing boundary `#838A9A` | Neutral boundary; inactive windows remain readable and operable according to native facts. |
| `layer.chrome.base` | existing container `#1B1E2B` | existing container `#FFFFFF` | Opaque shell chrome, separate from client-owned content. |
| `layer.chrome.raised` | proposed `#252938` | existing `#FFFFFF` | Elevated shell chrome, with shadow and contour distinguishing levels. |
| `layer.shadow` | neutral black, theme-specific alpha | neutral black, theme-specific alpha | Occlusion/depth, independent of focus and operation outcome. |
| `layer.pin.marker` | existing content | existing content | Pin glyph and “Pinned”; pinning does not imply focus or family. |
| `layer.minimized.marker` | existing secondary | existing secondary | Minimized glyph/label on its taskbar or navigator entry; no desktop halo for absent surface. |
| `layer.blocked.marker` | existing content | existing content | Observed restriction glyph plus reason; any neutral veil is limited to an actually blocked scope. |
| `layer.outcome.*` | existing outcome roles | existing outcome roles | Pending/Unknown/Refused/Committed descriptions independent of every layer treatment. |

Suggested initial halo cap is alpha 0.16, with no pulsing. The depth council should fix spread/radius and render-cost limits consistently across the complete token packet. Alpha and geometry are proposed tuning targets, not native performance acceptance. Avoid one hue per application/window: arbitrary palettes increase cognitive load, are unstable through lifecycle changes and can collide with outcome semantics.

The frozen brand guide says, “Keep glows out of the small logo and ordinary controls.” Retain that rule for buttons, fields, toolbar controls and small identity assets. The user's new direction adds window/family chrome as an explicit major glow scope: a full active halo and a weaker family-context glow may reinforce their corresponding opaque contours/brackets. Neither extends decorative glow to ordinary controls or suggests that family members all have focus. After depth council cross-review, family glow is confined to short relationship brackets with proposed alpha at most 0.06, no enclosing luminous contour, and a Family/Context label. It remains static, bounded, native-relationship-derived and subordinate to the active halo. High contrast and effects-off retain the same meanings without either halo.

Measured arithmetic using WCAG relative luminance gives existing accent against container 7.595978764:1 dark and 8.019840304:1 light; against proposed raised chrome 6.624890615:1 dark. These calculations establish proposed opaque pair feasibility only. They do not establish contrast over wallpaper, application pixels, alpha-composited effects or actual native rendering.

## State and precedence

An observed active surface receives the solid active contour regardless of whether a candidate is selected elsewhere. A window-switcher candidate receives corner markers and a label on the navigator tile; there is no speculative transfer of the desktop active contour. Keyboard-focused controls retain the existing independent two-tone focus treatment. Selection, window activation and control focus must remain distinguishable when simultaneously present.

Native-confirmed application activation and actual keyboard recipient are also separate. When an admitted chooser/menu keyboard scope makes a Warlock shell surface the recipient, the primary halo belongs to that shell chrome; the previously active application retains an Active application/context contour and label without the recipient halo. If native scope is unavailable or uncertain, present the uncertainty rather than claiming that typing will reach a particular surface. This correction follows depth council cross-review and avoids making a remembered active application appear to receive keys while the chooser owns input.

Family membership is derived from admitted native relationship observations, never a shared PID, application icon, title similarity or proximity. Family brackets are weaker in prominence than the active contour, with explicit linked glyph/text in the navigator. A focused modal uses the same active vocabulary; an observed blocked parent may carry a scoped restriction marker. Do not blanket dim the desktop, imply that an unrelated window is blocked, or rewrite the existing click-to-focus and modal-family rules.

Pinning adds a pin marker without recoloring the whole frame. Minimized entries remain readable and can show the established Live/Historical/Loading/Unavailable preview vocabulary; no rendering may fake a live desktop surface. Inactive windows lose the active halo while preserving chrome text contrast and unmodified client pixels. Neutral shadows reflect actual qualified stacking, not a focus-driven fake reorder.

Warning amber remains uncertainty, danger remains refusal/destructive context and positive remains confirmed positive feedback. None is used as an ordinary focus, candidate, pinned or family identifier. Outcome labels survive even if their hue resembles a chosen personal accent.

## Accessibility and preference behavior

All meaningful layer states have shape or text visible to a sighted person who cannot distinguish colors; accessible names/states alone are insufficient. Text pairs must pass 4.5:1 and required non-text state contours 3:1 against their actual adjacent colors, without rounding below-threshold values upward. A protected opaque two-tone backing must keep required focus/candidate contours distinguishable over arbitrary bright, dark or patterned client content; testing only the default wallpaper is inadequate.

High contrast uses admitted system/preference role mappings and opaque boundaries, with decorative glow and shadow removed. Shape distinctions and state labels remain. Reduced transparency uses opaque shell fills and solid scope markers rather than blur or client-content opacity. Reduced motion removes pulsing, travelling or breathing halos entirely; this proposal requires none even in ordinary mode. An effects-off profile must retain the same navigation information and outcomes.

Theme/accent changes are presentation changes to the one Elm model and view projection. They preserve target/control identity, pending obligations and native dependency-generation changes rather than freezing generations. If a supplied personal accent fails declared pairs, use a contrast-qualified derived role or the preserved default accent; do not alter the user's stored preference silently. Native assistive-technology and actual preference delivery remain release work, independent from browser forced-colors demonstrations.

## Proposed EARS clauses

The parent council should assign final IDs without renumbering frozen requirements.

1. **Observed active state:** When an admitted native observation identifies an active window, Warlock shall derive its solid active contour and navigation Active label from that observation while preserving independently selected candidates and control focus.
2. **Selection without activation:** While a window-navigation candidate differs from the observed active window, Warlock shall identify the candidate with a distinct marker and Candidate label and shall retain the observed active window's contour until correlated native focus changes.
3. **Native family state:** When admitted native observations establish window-family membership, Warlock shall show family markers with a shape/text relationship cue without inferring input eligibility or active state from membership.
4. **Independent layer states:** While pinning, minimization, modal restrictions or Pending/Unknown outcomes are present, Warlock shall display their corresponding observation/outcome cues independently of focus, selection, family and depth.
5. **Contrast and non-color semantics:** When layer tokens are built or rendered, Warlock shall verify declared text/non-text contrast against all applicable adjacent/composited backgrounds and shall provide visible non-color cues for every meaningful layer state.
6. **Preference equivalence:** Where high contrast, reduced transparency, reduced motion or effects-off is requested through the qualified preference route, Warlock shall retain equivalent focus, candidate, family, stacking and outcome information using opaque contours, labels and permitted presentation while preserving target identity and outstanding obligations.
7. **Client-content integrity:** While window-layer effects are rendered, Warlock shall limit chrome shading, glow and restrictions to their qualified visual scopes and shall preserve client-owned pixels and actual native input/occlusion rules.

## Proposed OpenSpec scenarios

| Scenario | Trigger and required result | Evidence needed before native closure |
| --- | --- | --- |
| Candidate A, active B | Navigate to A; A shows Candidate marker, B retains Active contour until admitted focus update. | Actual Elm projection and owning native input/focus observations. |
| Candidate vanishes | Destroy selected A during navigation; clear/retarget through existing eligibility rules without focusing or confirming any target speculatively. | Lifecycle/model replay plus actual native disappearance. |
| Similar titles, different families | Two same-PID windows without native family relation do not receive family brackets. | Native relationship and rendering capture. |
| Modal and unrelated peer | Focused modal is Active; only admitted blocked scope gets restriction; unrelated peer retains existing focus behavior. | Original modal/focus gates plus pixels and input routing. |
| Pin during Unknown | Observed pin glyph and readable Unknown operation remain separate; pin marker does not become active halo. | Actual immutable model and correlated native facts. |
| Minimized Historical | Minimized tile preserves Historical label and authorized retained preview; no desktop glow or fake Live status. | Original preview13, ownership/retirement and minimization gates. |
| Contrast extremes | Required contours remain discernible over black, white, patterned and transparent qualified backgrounds; small text remains readable. | Token math plus actual composited pixels on owning tuple. |
| Color deficiency/grayscale | Active, candidate, family, pinned, blocked and uncertain states remain distinguishable by shape/text. | Catalog inspection and native visual/AT qualification, at their actual scopes. |
| Preference change mid-request | Change theme/high contrast while operation is Pending; identity/outcome survive, decorative effects adapt without confirming/replaying intent. | Actual Elm projection, preferences/native generations and original deadlines. |

## Primary reference adoption

- [W3C Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html): adopt a visible alternative to color for state distinctions. This motivates markers and labels, not a prohibition on expressive color.
- [W3C Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html): adopt the 3:1 threshold for necessary graphical state cues and assess adjacent backgrounds. Decorative shadow cannot carry required focus information alone.
- [Microsoft Color](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/color): adopt restrained semantic accent use and theme-dependent neutral roles. Warlock retains its own violet palette and does not import automatic Windows color generation.
- [Microsoft Layering/Elevation](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/layering): adopt shadows together with contours to communicate relationships. Do not import its numerical elevation scale or allow visual elevation to override compositor stacking.
- [GNOME UI Styling](https://developer.gnome.org/hig/guidelines/ui-styling.html): adopt testing in light, dark and high contrast and use semantic style roles. Warlock's explicit layered navigation and violet halo remain its own design.
- Apple Color and Material color-role pages were opened, but their current web bodies were not accessible to this reviewer; no precise recommendation is attributed to their unread contents.

## Local source identities and retained obligations

Read `AGENTS.md`, `docs/HANDOFF.md`, `docs/warlock-build-loop/design-language-v1/INSTRUCTIONS.md`, `DesignLanguage/WORKPLAN.md` and `docs/warlock-compatibility/omarchy-v1/README.md`.

| Frozen input | SHA-256 |
| --- | --- |
| `DesignLanguage/catalog/v6/tokens.json` | `352eca419c1e1c4150810f02bf5bb6f0b8a2dabd144e8c7077a6ca30b4a988c9` |
| `DesignLanguage/catalog/v6/tokens.css` | `aa1048ae3c79d13c81719cb6f32dc25c37f1a93796770373aa51eaf514a23858` |
| `DesignLanguage/catalog/v6/catalog.js` | `e048cd853021fe55f9b457f40d64d1833ab1df52db064f08f9abd0f3c02b11c5` |
| `DesignLanguage/EARS.md` | `2e0a5d0eace0f4c4aca25f6b205edb8bdd0a6b468fbd10883e96053e44a06f18` |
| `DesignLanguage/CONSENSUS.md` | `5907b395ba7473126976cd6498f63d90add54045778ca5ea7c1f577bac9c9009` |

This additive proposal keeps WARLOCK-DL-002/003/004/005/006/014/015/018 and ELM-ADOPT-016/017/020/029/030 authoritative. Full Omarchy vocabulary and effective bindings, including user overrides, remain required. Original 242 requirements/417 scenarios, separate right-click24/48, preview13/restore38/recovery34/drag-resize52, original deadlines, exact owning ABI, physical ownership, resource budgets and deployment/rollback gates remain mandatory. Browser specimens or token calculations cannot close those gates.

The preserved brand guide identity is `docs/warlock-brand/v1/BRAND-GUIDE.md`, SHA-256 `a4802a89df172c2a3ed618868542b20eb1e5ab4fb52046d4d23c2fd833e61d11`. Actual Omarchy Alt+Tab chooser overrides take precedence over packaged defaults; this proposal does not introduce or repurpose a shortcut.

## Dissent and matters for consensus

Reject continuous animated glow, arbitrary application-colored families, warning-colored pinning, focus-ordered fake depth and whole-client opacity dimming. Retain static bounded violet halo as a major ordinary-mode element, with accessible opaque contours and effects-off equivalence. Candidate markers should primarily live on navigator tiles; do not draw speculative full desktop active rings. Depth token sizes and actual measured GPU/resource budgets require the other council reviewers and owning native qualification.
