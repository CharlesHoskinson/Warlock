# Foundations

## Overview

Warlock uses Lacquer: opaque mineral-black surfaces, warm ivory text and restrained red identity. Dawn applies the same hierarchy to warm paper. High contrast uses black surfaces and white boundaries. [Color](color.html), [Effects](effects.html) and the [attention specimen](specimen.html) show the system. [Try the desktop](../../test-drive/index.html).

## Color

| Role | Night | Dawn | High contrast |
| --- | --- | --- | --- |
| Canvas | #100E0E | #F6F1EA | #000000 |
| Recessed / surface / raised | #141112 / #191516 / #221D1E | #EFE9E0 / #FFFDF9 / #FFFFFF | #000000 |
| Hover / pressed | #2C2627 / #383032 | #EDE6DC / #E3DBD0 | #000000 |
| Selected / hover / pressed | #331C1E / #3A252A / #423035 | #FCE8E4 / #F4E3DF / #ECDAD5 | #000000 |
| Text / secondary | #F6EFE8 / #BDB2AF | #181314 / #5C5250 | #FFFFFF |
| Brand text | #FCA399 | #A11D22 | #FFB3AC |
| Action / hover / pressed | #B02026 / #C4262D / #961A20 | #A11D22 / #8A181D / #751418 | #FFFFFF |
| On action | #FFF8F5 | #FFFDF9 | #000000 |
| Essential border | #9E9290 | #706562 | #FFFFFF |
| Window edge, unfocused / focused | #707078 / #F6EFE8 | #706562 / #181314 | #767676 / #FFFFFF |
| Focus and information | #8EC8FF | #14539A | #00FFFF / #9ED0FF |
| Positive / warning / danger | #6EE0B8 / #F2C172 / #FF9EB0 | #0E634C / #7D4E0A / #9B1B3B | #9CF5C4 / #FFE08A / #FFB3C1 |

The generated [contrast manifest](contrast.json) records unrounded ratios and color-vision simulations. Text, placeholders and disabled labels meet 4.5:1; essential marks meet 3:1. The focused edge differs from the unfocused edge by at least 3:1 in every appearance. An opaque canvas-colored guard separates each edge from adjacent pixels. Red occupies at most approximately 3% of ordinary chrome. Secondary colors convey specific information with a non-color cue.

## Typography and spacing

Inter supplies body, labels and detail. Space Grotesk Bold supplies titles at 20px and above. JetBrains Mono Regular supplies paths and shortcuts. All fonts load locally with `font-display: swap` and synthesis disabled. The window title is 20/28px at 700; section title 16/24 at 600; body 14/20 at 400; label 14/20 at 500; detail 12/16 at 400. The root applies the committed 100, 125, 150 or 200% text scale once. Padding remains in CSS pixels.

The spacing scale is 0, 2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48 and 64px. Label and detail are 2px apart; related groups are 16px apart; major groups are 24px apart. Controls reserve a 6px focus gutter. Standard controls are at least 36px high, two-line rows 56px and fields 44px. Coarse pointers use 44px, 60px and 44px respectively. Text wraps without shrinking.

## Anatomy and selectors

`SurfaceRenderer.elm` renders `.surface-popup[data-mode]` with a heading, a static `aria-live="off"` status and `.surface-controls`. Controls carry `data-surface-control`; fields carry `data-surface-field`. Labels and details use `.control-label` and `.control-detail`. A bounded flex column places scrolling in `.surface-controls`, with a 10px outer inset and 6px gutter. At short heights the whole popup scrolls. Renderer geometry remains authoritative.

The shared action treatments are affirmative filled, secondary outlined, subtle utility and consequential outlined. One enabled affirmative action appears per independent task block. Destructive confirmation uses danger text and outline on neutral chrome; Cancel precedes Confirm. A disabled control retains its native disabled semantics, secondary text and full opacity. A focus-only unavailable control retains `data-focus-only` and `aria-disabled`; it remains reachable but does not activate. A decorative slash marks unavailable controls; native disabled or aria-disabled semantics remain authoritative. The slashed ring paints as the label's own background in a reserved inline-end slot that every popup label keeps in every state, aligned with the first line. Marking a control unavailable therefore never changes its dimensions, and the cue never shares a pseudo-element with selection bars, checks or diagrams.

## Attention and state

A focused window uses a neutral 2px edge, inner and outer 1px opaque guards, raised titlebar and a 3 × 14px title beacon. An unfocused window uses the unfocused edge, surface titlebar and secondary title text. Activity uses a separate inset brand contour and Active wording. Candidate uses four 12px corner brackets, selected wash and candidate wording. Selection uses a 3px brand bar and check or existing selected wording. Confirmed keyboard recipient uses focus-colored paired chevrons or a recipient label. Control focus uses a 2px focus outline, 2px offset and opaque 2px gap. These facts remain independent.

The renderer projects switcher candidates with `[role="option"][aria-selected="true"]`, menu checks with `[role="menuitemcheckbox"][aria-checked="true"]`, Task View filters with `aria-pressed`, and Settings and snap choices with their mode-specific `aria-current`. Settings and notification toggles use their existing `aria-pressed`; Help uses `aria-expanded`. No global `aria-current` rule assigns meaning. Host observations supply window focus, activity and recipient independently. Missing facts remain neutral.

## Depth and motion

Fields, rows and tiled clients are flush. Floating clients and taskbar use rest elevation, detached popups use raised elevation and separate blocking dialogs use dialog elevation. Shadows remain decorative. Focus changes do not change elevation. High contrast and effects-off remove soft shadows, highlights and glow while retaining guards and outlines.

Shell surfaces enter and leave immediately. Selection, focus, disabled state and outcome changes are immediate. Enabled pointer feedback on a quiet control uses 90ms for hover and for release back to hover and 60ms for press, with `cubic-bezier(.2,0,0,1)`; leaving hover settles at once. The transition exists only while a fine pointer hovers or presses a quiet control: one that is not a candidate, selected, pressed, checked, expanded, busy, focus-only or unavailable. A control that becomes a candidate or selected, pressed, checked, unavailable or busy changes at once, including under the pointer; the one residual case, a selection or candidate leaving a hovered control, settles over the 90ms pointer timing. Motion preference projected by Elm takes precedence; unknown motion starts suppressed. Reduced motion removes the portal and makes durations zero.

The application portal begins only after an observation establishes a newly mapped window or removal of the same incarnation. It never follows launch intent, Submitted, Unknown, a focus change or a shell popup. Opening lasts 520ms: ignite 0–120, expand 120–380, resolve 380–460 and settle 460–520. Closing lasts 360ms: release 0–90, contract 90–270 and extinguish 270–360. The decorative plane never clips, moves or delays live input. Reduced effects use a decorative 120ms opening or 90ms closing fade; off is immediate. One portal runs at a time, with at most one full start in a rolling second. Cancellation and visibility loss settle immediately.

## Accessibility and content

Keyboard focus remains visible at each scroll edge. Forced colors use system colors, actual boundaries and outlines. Reduced transparency preserves opaque surfaces. Static status text stays quiet; the existing announcement owner communicates changes. Pending uses a clock and waiting words, unknown a question diamond and unconfirmed wording, refusal a stop glyph and reason. Untyped text remains neutral and never acquires an inferred outcome. Unknown never retries a mutation automatically.

## Renderer requirements

CSS reads state and never creates authority. Typed projections are required for observed window focus, application activity, confirmed recipient, typed outcome and visible unavailable cues. Keyed identities, composition events, focus return, accessible names, publication and lease stay with Elm. The host validates effect cycle and target completion, handles cancellation and a bounded watchdog, and retires input immediately when removal is observed. The specimen illustrates independent facts; it is not native evidence.

## Executable comparisons

The attention specimen opens with a compact comparison in Night, Dawn and High contrast: focused-window, active-application and candidate cues side by side, repeated with effects off, beside specimen buttons in the shared affirmative and secondary treatments. A readout names the control that holds keyboard focus. Its Settings scenes demonstrate focus loss and effects-off without changing application activity or candidate state. The four depth samples retain their boundaries when effects are off. The effects gallery admits one active effect and one full start per rolling second, and settles on preference changes, cancellation, visibility loss or watchdog expiry. Its paint is clipped outside the live frame.

The runtime loads the shared control sheet and the authoritative D06 preview stylesheet. Documentation scenes, swatches, depth samples and specimen page typography come from `assets/shared/specimen-docs.css`, which specimen pages load after the bootstrap and the runtime never loads. Typed outcome hooks remain a renderer requirement: the existing snapshot contains untyped status text, which stays neutral.
