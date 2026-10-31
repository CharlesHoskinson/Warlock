# Warlock visual system

Warlock's visual language is **Lacquer**: mineral black, warm ivory, deep red action surfaces and luminous red details. Black and red are the primary colours. Secondary colours convey information and never compete with red as brand accents. The [brand guide](../docs/warlock-brand/v2/BRAND-GUIDE.md) and the [foundations specification](../site/design/foundations/spec.md) hold the exact values, the [EARS requirements](EARS.md) (Revision 2) state them as requirements, and the [Warlock website](https://charleshoskinson.github.io/Warlock/) shows them as live specimens.

## Appearances and colour

Lacquer has three appearances. **Night** uses opaque mineral-black surfaces and warm ivory text. **Dawn** applies the same hierarchy and state meanings to warm paper, dark ink and deep red. **High contrast** uses black surfaces with white text and white boundaries. Every interface colour is opaque sRGB and is exported as `--wl-sys-color-<role>`.

| Role | Night | Dawn | High contrast |
| --- | --- | --- | --- |
| canvas | #100E0E | #F6F1EA | #000000 |
| surface | #191516 | #FFFDF9 | #000000 |
| surface-raised | #221D1E | #FFFFFF | #000000 |
| surface-selected | #331C1E | #FCE8E4 | #000000 |
| text | #F6EFE8 | #181314 | #FFFFFF |
| text-secondary | #BDB2AF | #5C5250 | #FFFFFF |
| brand-text | #FCA399 | #A11D22 | #FFB3AC |
| action-fill | #B02026 | #A11D22 | #FFFFFF |
| on-action | #FFF8F5 | #FFFDF9 | #000000 |
| border-essential | #9E9290 | #706562 | #FFFFFF |
| window-edge-unfocused | #707078 | #706562 | #767676 |
| window-edge-focused | #F6EFE8 | #181314 | #FFFFFF |
| focus | #8EC8FF | #14539A | #00FFFF |
| info | #8EC8FF | #14539A | #9ED0FF |
| positive | #6EE0B8 | #0E634C | #9CF5C4 |
| warning | #F2C172 | #7D4E0A | #FFE08A |
| danger | #FF9EB0 | #9B1B3B | #FFB3C1 |

The brand guide lists the full set, including the recessed, hover, pressed and selected surface states. Token resolution runs from reference primitives to per-theme semantic roles to component aliases. Components use approved role pairs; artwork may use reference colours.

### Red

Saturated red occupies no more than approximately 3% of ordinary owned chrome. Wallpaper, illustration and the portal have separate decorative budgets. Brand red appears in the sigil, active-application contours, selection bars, the portal and one affirmative filled action per task block. Contours, selection bars and essential brand glyphs use brand-text, never action-fill. A filled affirmative action carries only on-action text and glyphs: red fill with light text in Night and Dawn, white fill with black text in High contrast, and system colours in forced colours. Save, Apply and Activate take that emphasis only when enabled.

Danger is distinct from brand red. It appears on neutral chrome with an octagonal stop glyph, a reason and an explicit action label. Destructive confirmation uses danger outline and danger text, never the affirmative red fill, and keeps Cancel before Confirm under the source-defined focus policy. Resting power and session commands stay neutral. Error surfaces never glow.

### Secondary colours

Each secondary colour carries one kind of information, always with a non-colour cue.

| Meaning | Colour role | Non-colour cue |
| --- | --- | --- |
| Control keyboard focus | focus | Offset outer ring on the focused control |
| Confirmed keyboard recipient | focus | Paired chevrons or a recipient label, with a sharp boundary |
| Information | info | Circled information glyph and explanatory text |
| Confirmed positive outcome | positive | Checkmark and the actual outcome words |
| Warning or attention | warning | Triangle and explicit detail |
| Unknown | warning | Question diamond and unconfirmed wording |
| Refused or error | danger | Octagonal stop glyph and reason |
| Pending | text-secondary | Static clock and waiting wording |
| Submitted | text-secondary | Submission wording, with no completion checkmark |
| Cancelled | text-secondary | Cancellation glyph and wording |

Only outcomes that the relevant protocol defines appear. Colour never classifies free-form text, so untyped status stays neutral. Links stay underlined. Category names and collection icons use neutral text and distinct shapes. An Unknown result never receives a success checkmark or an automatic retry.

### Contrast and colour vision

Every text pair meets 4.5:1, including small labels, placeholders and disabled text. Essential boundaries, state marks and focus meet 3:1 against their actual adjacent or composited backgrounds. The focused window edge differs from the unfocused edge by at least 3:1 in every appearance. The [contrast manifest](../site/design/foundations/contrast.json) records 309 unrounded comparisons, each with Machado severity-1.0 protanopia and deuteranopia simulations, and every recorded comparison meets its threshold. The simulations supplement redundant cues and user testing.

Disabled labels and placeholders use text-secondary at full opacity. Focus gaps use the opaque containing surface. No secondary or status text sits on an action fill, and red fill is never a small-text foreground. Text never sits directly on wallpaper, photography, translucent layers or portal effects.

High contrast removes shadows, gradients, portal effects, dimming and glow, and keeps shapes, labels, checkmarks, contours and focus gaps. Under `forced-colors: active`, surfaces use Canvas and CanvasText, ButtonFace and ButtonText, Field and FieldText, and Highlight and HighlightText, with real borders and outlines for essential marks.

## Typography and spacing

Warlock bundles Inter Variable, Space Grotesk Bold and JetBrains Mono Regular, loads them locally with `font-display: swap` and disables font synthesis. Inter supplies body, labels and detail. Space Grotesk Bold supplies titles at 20px and above. JetBrains Mono supplies paths, shortcuts and code.

| Role | Family | Size / line height | Weight |
| --- | --- | --- | ---: |
| window-title | Space Grotesk | 20 / 28px | 700 |
| section-title | Inter | 16 / 24px | 600 |
| body | Inter | 14 / 20px | 400 |
| label | Inter | 14 / 20px | 500 |
| detail | Inter | 12 / 16px | 400 |
| code | JetBrains Mono | 13 / 20px | 400 |

Display, page-title and headline roles belong to documentation; desktop content uses window-title and smaller roles. The root applies the committed 100, 125, 150 or 200% text scale exactly once, and padding stays in CSS pixels. Copy uses sentence case, left alignment and tabular lining numerals for counts and tables. Reading measure is at most 70ch. Labels, titles and details wrap without line clamps and never shrink to fit. Taskbar application names may ellipsize while their full accessible names stay available.

The spacing scale is 0, 2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48 and 64px. Label and detail sit 2px apart, related groups 16px and major groups 24px. Controls reserve a 6px focus gutter. Standard controls are at least 36px high, two-line rows 56px and fields 44px; coarse pointers use 44px, 60px and 44px.

## Identity

The folded W keeps its two valleys and central diamond. Its vector geometry uses neutral facets and one red focal diamond. Clear space is one diamond width. The detailed mark appears at 32px and above, the monochrome mark at 24 to 31px and a plain W below 24px. Generated imagery never replaces the vector identity. Prose uses Warlock and the wordmark uses WARLOCK.

Utility icons are local SVGs with 20px viewboxes and 1.5px strokes, with 16px and 24px variants. Decorative icons are hidden from accessibility APIs and never replace meaningful names.

## Attention and the focused window

Each attention fact has its own cue. The cues combine without replacing one another, and host observations supply window focus, application activity and keyboard recipient independently. A missing fact stays neutral.

- **Focused window:** a neutral 2px focused edge with opaque 1px inner and outer guards, a raised titlebar, a 3 × 14px title beacon and a matching neutral taskbar marker. An unfocused window uses the unfocused edge, the surface titlebar and secondary title text. Focus changes render immediately.
- **Active application:** a separate inset brand-text contour with a diamond or Active wording. In the taskbar it is a selected surface with a 3px brand-text bottom marker.
- **Navigation:** candidate corner brackets mark the chooser's prospective window: four neutral 12px brackets, a selected wash and visible wording on its navigation tile. Drawing them never raises or focuses a window.
- **Selection:** a 3px brand-text bar with a check or Selected wording.
- **Control focus:** a 2px focus-coloured outline with a 2px offset and an opaque 2px gap.
- **Confirmed keyboard recipient:** focus-coloured paired chevrons or a recipient label on the confirmed receiving surface. An optional steady halo accompanies the sharp mark only. An unconfirmed recipient shows no recipient mark.
- **Family:** short neutral segmented brackets with a Family or Context label, never inferred from process, title or icon.
- **Pin, minimization and modal block:** a neutral glyph, label and reason. Client content and surrounding windows are never dimmed.

The compositor values come from [hyprland.json](../site/design/foundations/hyprland.json): border size 2, with active and inactive borders `f6efe8ff` and `707078ff` in Night, `181314ff` and `706562ff` in Dawn, and `ffffffff` and `767676ff` in High contrast. Inactive dimming is off and active, inactive and fullscreen opacity are 1. Floating windows use 8px rounding, snapped and maximized windows use 0, and blur is off.

## Depth, shadows and glow

Elevation follows surface role. Flush level 0 holds fields, rows and tiled, snapped or maximized clients. Rest level 1 holds the taskbar and floating clients. Raised level 2 holds detached popups. Dialog level 3 holds separate blocking surfaces. Each level uses at most two black, zero-spread shadows, a contact shadow and an ambient shadow:

| Level | Shadows | Night alphas | Dawn alphas |
| --- | --- | --- | --- |
| 1 rest | 0 2px 4px, 0 6px 16px | .28 / .20 | .16 / .12 |
| 2 raised | 0 3px 6px, 0 8px 24px | .28 / .20 | .16 / .12 |
| 3 dialog | 0 4px 8px, 0 12px 32px | .28 / .20 | .16 / .12 |

Every surface keeps an explicit boundary, so shadows add separation and never carry state. Focus alone never changes a window's elevation class or stack order; it may change floating shadow opacity. Owned chrome and content have alpha 1, with no backdrop blur and no client dimming.

Glow has three permitted uses: a bounded halo on the confirmed keyboard recipient, short family softness at alpha 0.06 or less, and the temporary portal bloom. Controls, errors, navigation marks and text do not glow. Recipient halo blur stays within 12 logical units, and idle chrome is static with no recurring decorative frame work. Reduced effects removes glow. Effects-off and High contrast also remove soft shadows and highlights while keeping sharp boundaries, labels and focus cues.

## Motion

Shell surfaces enter and leave immediately. Selection, focus, disabled state and outcome changes are immediate. Enabled pointer feedback uses a 60ms press-in and a 90ms state or release transition with `cubic-bezier(.2,0,0,1)`. The motion preference that Elm projects takes precedence, and an unknown motion preference starts suppressed. Reduced motion sets durations to 0ms, removes the portal and velocity-continuation motion, and keeps static depth and sharp state cues.

## Signature portal

The portal is a ring of red ember fragments that ignites, expands and resolves into an application window's frame. Closing reverses that spatial idea. Its short diamond-shaped interruption reflects the central diamond of the sigil.

A portal starts only after an admitted observation establishes a newly mapped eligible application window, or the removal of the same window incarnation. Intent, receipt, Pending, Submitted, Refused, Cancelled and Unknown never start it. Initial snapshots, session restoration, bulk mapping, workspace redisplay, minimization, restoration, focus changes, snapping, shell popups, notifications, preview frames and search results settle without a portal.

| Opening, 520ms | Time | Construction and easing |
| --- | --- | --- |
| Ignite | 0–120ms | Extent .04 to .16, opacity 0 to .65; `cubic-bezier(.16,0,.3,1)` |
| Expand | 120–380ms | Extent .16 to 1, rotation at most 12 degrees; `cubic-bezier(.2,.72,.2,1)` |
| Resolve | 380–460ms | Aperture reaches the final frame radius, opacity .65 to .20; `cubic-bezier(.2,0,0,1)` |
| Settle | 460–520ms | Opacity .20 to 0; `cubic-bezier(0,0,.2,1)` |

| Closing, 360ms | Time | Construction and easing |
| --- | --- | --- |
| Release | 0–90ms | The non-interactive remnant acquires a .65-opacity ring; `cubic-bezier(.4,0,1,1)` |
| Contract | 90–270ms | Extent 1 to .06, reverse rotation at most 8 degrees; `cubic-bezier(.4,0,.8,.3)` |
| Extinguish | 270–360ms | Extent .06 to .02 and opacity to 0; `cubic-bezier(0,0,.2,1)` |

The portal paints on a separate decorative plane with a transparent ring centre, at most 8% overscan clipped to the output, and no paint over live text, controls or focus indicators. The live window and its focus cues occupy their final geometry from the admitted observation; the portal never scales, translates, fades or clips the live input plane. Native clients use a guarded frame effect. Closing keeps only a non-interactive, `aria-hidden` remnant, and input retires immediately on observed removal.

The effects tier resolves to full, reduced or off from user preference and host capability. High contrast and forced colours select off. Reduced effects use decorative opacity only, a 120ms opening and a 90ms closing. Off and reduced motion settle immediately. One portal runs at a time, with at most one full start in a rolling 1000ms. Luminous coverage stays below 5% of the viewport, bloom opacity is capped at 0.16 in Night and 0.10 in Dawn, and each portal makes a single rise and fall without repeated flashing. Interrupted, hidden, stale or retired effects settle immediately and never replay.

## CSS architecture

The Elm view owns interaction state and emits semantic elements, classes, ARIA and typed data attributes. CSS owns visual presentation and reads those hooks; it never creates authority or infers state from labels, generated IDs, element order or hover. Adapters transport observations and completion events and keep no competing selection, preference or operation policy.

- **Layers:** legacy, reset, tokens, base, layouts, components, states, effects and accessibility, in that order. The shipped legacy stylesheet sits in the legacy layer once, with no unlayered duplicate; where an unlayered legacy link is required, a scoped compatibility build comes from the same token and component sources.
- **Scope:** runtime rules scope to `html[data-warlock-design="v1"]`, documentation to `.wl-doc-*`, specimens to `.wl-specimen-*`, and area rules to the actual `.surface-popup[data-mode]` or `.surface-bar`. Only shared foundations define document-level rules.
- **Effects attributes:** `data-effects="on"` or `"off"` carries the stored preference, and `data-effects-tier="full|reduced|off"` carries the resolved tier without a new preference owner.
- **Tokens:** compilation resolves typed reference, semantic and component aliases deterministically, rejects cycles, and produces the CSS, the contrast manifest and the Hyprland values.
- **Registered properties:** `--wl-portal-progress`, `--wl-portal-turn`, `--wl-effect-alpha` and `--wl-capture-delay` have `inherits: false` and literal initial values. Ordinary transform and opacity keyframes work without registration, and unsupported masks fall back to reduced effects.
- **Completion:** the bridge validates the sentinel target, animation name and cycle before Elm receives a completion `Msg`, and Elm ignores stale or duplicate events. A watchdog retires the decoration at the animation duration plus 100ms. Completion settles decoration only; it never supplies a native observation or an operation result.

## Website and specimens

The website's navigation is Home, Test drive, Foundations, Styles, Components, Architecture and Get started, with Search. Each component page has Overview, Anatomy, States, Specimen, Behavior, Accessibility, Content, Evidence and Try it sections, and Try it opens the component in the simulated desktop. Evidence stays separately identified and traceable.

A demonstration that claims Elm behaviour runs the shipped Elm decoder, view, update or decision function through an isolated typed wrapper. Manually controlled outcome specimens keep Pending and Unknown unchanged until the reader settles them. The test drive's simulated host returns labelled simulated receipts and observations; it never contacts the compositor, and simulated outcomes establish no native acceptance. Static style specimens are labelled as such and never implement a competing desktop policy in JavaScript. Generated concept studies are illustrations; the specimens and area specifications define the interface.

## Stable targets and observed toggles

Actionable rows reserve stable geometry before asynchronous preview content arrives, and content arrival never moves a target under a held press. Always on top uses one stable checkable label whose checked state comes from the current admitted native observation, and Pin and Unpin name taskbar application pinning only. The [stable-target requirements](INTERACTION-ADDENDUM.md) state both, and the [Always on top evidence](../implementation/warlock/qa/evidence/pin-check/README.md) records the native pointer and keyboard journeys.

The [current guidance](CURRENT.md) applies this system to each window and surface and records the evidence for each behaviour. The [Warlock contributor plugin](../plugins/warlock-contributor/README.md) supports implementation and evidence bookkeeping; a catalog or checker pass closes no native design gate.
