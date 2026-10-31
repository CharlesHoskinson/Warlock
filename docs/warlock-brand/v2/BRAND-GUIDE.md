# Warlock brand guide

Warlock's brand is **Lacquer**: mineral black, warm ivory, deep red action surfaces and luminous red details. Black and red are the primary colours; secondary colours convey information and never compete with red as brand accents. The tagline is **Crafted for flow.**

Design tokens: [tokens.json](tokens.json) (W3C design tokens) and [tokens.css](tokens.css). The complete Warlock Design Language, with live specimens for every window, is on the [Warlock website](https://charleshoskinson.github.io/Warlock/) and in [site/design](../../../site/design/).

## Colour directions

**Lacquer** is the foundation: mineral black, warm ivory, deep red action surfaces and luminous red details. Its restrained colour area gives Warlock a crafted, composed character.

**Ember** contributes the brief spark and expansion of the window portal. Its energy belongs to a window transition; ordinary chrome remains still.

**Signal** contributes disciplined geometry, scarce red accents and the clear separation of neutral window focus from red application activity.

**Dawn** brings the same system into warm paper, dark ink and deep red. It preserves the hierarchy and state meanings of Night.

The chosen system is **Lacquer**, with **Night**, **Dawn** and **High contrast** appearances. Secondary colours serve information and never become competing brand accents. Saturated red occupies no more than approximately 3% of ordinary owned chrome. Wallpaper, illustrations and temporary portal effects have separate decorative budgets.

## Colour tokens

All interface colours below are opaque sRGB. Theme names are `night`, `dawn` and `high-contrast`. Token suffixes are exported as `--wl-sys-color-<suffix>`.

| Role | Night | Dawn | High contrast |
| --- | --- | --- | --- |
| canvas | #100E0E | #F6F1EA | #000000 |
| surface-recessed | #141112 | #EFE9E0 | #000000 |
| surface | #191516 | #FFFDF9 | #000000 |
| surface-raised | #221D1E | #FFFFFF | #000000 |
| surface-hover | #2C2627 | #EDE6DC | #000000 |
| surface-pressed | #383032 | #E3DBD0 | #000000 |
| surface-selected | #331C1E | #FCE8E4 | #000000 |
| surface-selected-hover | #3A252A | #F4E3DF | #000000 |
| surface-selected-pressed | #423035 | #ECDAD5 | #000000 |
| text | #F6EFE8 | #181314 | #FFFFFF |
| text-secondary | #BDB2AF | #5C5250 | #FFFFFF |
| brand-text | #FCA399 | #A11D22 | #FFB3AC |
| action-fill | #B02026 | #A11D22 | #FFFFFF |
| action-fill-hover | #C4262D | #8A181D | #FFFFFF |
| action-fill-pressed | #961A20 | #751418 | #FFFFFF |
| on-action | #FFF8F5 | #FFFDF9 | #000000 |
| border-essential | #9E9290 | #706562 | #FFFFFF |
| window-edge-unfocused | #707078 | #706562 | #767676 |
| window-edge-focused | #F6EFE8 | #181314 | #FFFFFF |
| focus | #8EC8FF | #14539A | #00FFFF |
| info | #8EC8FF | #14539A | #9ED0FF |
| positive | #6EE0B8 | #0E634C | #9CF5C4 |
| warning | #F2C172 | #7D4E0A | #FFE08A |
| danger | #FF9EB0 | #9B1B3B | #FFB3C1 |
| shadow | #000000 | #000000 | transparent |

`focus-gap` aliases the opaque containing surface. `window-guard` aliases canvas. Disabled labels and placeholders alias text-secondary and retain opacity 1. Active-application contours, selection bars and essential brand glyphs alias brand-text, never action-fill.

### Approved text and boundary pairs

The following tables enumerate approved foreground/background combinations. Ratios use WCAG relative luminance, rounded to two decimals; acceptance uses unrounded values. Every text pair meets 4.5:1. Essential boundaries and state marks meet 3:1. Warlock applies the text threshold to small labels, placeholders and disabled text as well as body copy.

Columns: **C** canvas, **R** recessed, **S** surface, **E** raised, **H** hover, **P** pressed, **Q** selected, **QH** selected-hover, **QP** selected-pressed. Focus and information share one row in Night and Dawn. Border-essential is a non-text role.

**Night, ratios to 1**

| Foreground | C | R | S | E | H | P | Q | QH | QP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| text | 16.89 | 16.48 | 15.89 | 14.60 | 13.04 | 11.26 | 13.90 | 12.47 | 10.80 |
| text-secondary | 9.30 | 9.07 | 8.75 | 8.04 | 7.18 | 6.20 | 7.66 | 6.87 | 5.95 |
| brand-text | 9.93 | 9.69 | 9.34 | 8.58 | 7.67 | 6.62 | 8.18 | 7.33 | 6.35 |
| focus / info | 10.87 | 10.60 | 10.22 | 9.39 | 8.39 | 7.24 | 8.94 | 8.02 | 6.95 |
| positive | 11.93 | 11.64 | 11.22 | 10.31 | 9.21 | 7.95 | 9.82 | 8.81 | 7.63 |
| warning | 11.59 | 11.30 | 10.90 | 10.02 | 8.95 | 7.73 | 9.54 | 8.56 | 7.41 |
| danger | 9.87 | 9.63 | 9.28 | 8.53 | 7.62 | 6.58 | 8.12 | 7.29 | 6.31 |
| border-essential | 6.39 | 6.23 | 6.01 | 5.52 | 4.93 | 4.26 | 5.26 | 4.71 | 4.08 |
| on-action, action boundary only | 18.33 | 17.88 | 17.24 | 15.84 | 14.15 | 12.22 | 15.09 | 13.53 | 11.72 |

**Dawn, ratios to 1**

| Foreground | C | R | S | E | H | P | Q | QH | QP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| text | 16.36 | 15.24 | 18.10 | 18.39 | 14.84 | 13.40 | 15.59 | 14.80 | 13.62 |
| text-secondary | 6.73 | 6.26 | 7.44 | 7.56 | 6.10 | 5.51 | 6.41 | 6.08 | 5.60 |
| brand-text | 6.89 | 6.41 | 7.62 | 7.74 | 6.25 | 5.64 | 6.56 | 6.23 | 5.73 |
| focus / info | 6.84 | 6.37 | 7.56 | 7.68 | 6.20 | 5.60 | 6.51 | 6.18 | 5.69 |
| positive | 6.43 | 5.98 | 7.11 | 7.22 | 5.83 | 5.27 | 6.12 | 5.81 | 5.35 |
| warning | 6.30 | 5.87 | 6.97 | 7.08 | 5.72 | 5.16 | 6.00 | 5.70 | 5.24 |
| danger | 7.15 | 6.66 | 7.91 | 8.03 | 6.49 | 5.86 | 6.81 | 6.47 | 5.95 |
| border-essential | 5.01 | 4.67 | 5.55 | 5.63 | 4.55 | 4.11 | 4.78 | 4.53 | 4.17 |

**Filled affirmative actions** use only on-action text and glyphs. Night default/hover/pressed ratios are **6.49 / 5.46 / 8.11:1**. Dawn ratios are **7.62 / 9.27 / 11.06:1**. Night actions have a 1px on-action boundary, which meets these same ratios against their fills and the Night boundary row against their surroundings. Dawn actions retain a 1px brand-text boundary in every pointer state; its external contrast is the Dawn brand-text row. High-contrast actions use black on white, **21:1**, with a black focus gap and cyan outer focus ring.

No secondary or status text appears on action fills. Red fill is not used as a small-text foreground. Text does not sit directly on wallpaper, photography, translucent layers or portal effects.

### Colour-vision checks

The supplementary checks use Machado severity-1.0 protanopia and deuteranopia transforms in linear sRGB, with clipping before luminance measurement. These are simulation checks, not a substitute for redundant meaning or user testing. The following are the minimum ratios across all nine neutral backgrounds, shown as **protanopia / deuteranopia**.

| Role | Night minimum | Dawn minimum |
| --- | --- | --- |
| text | 11.01 / 10.67 | 13.32 / 13.46 |
| text-secondary | 6.03 / 5.90 | 5.55 / 5.49 |
| brand-text | 5.79 / 6.71 | 7.43 / 4.88 |
| focus / info | 7.64 / 6.52 | 4.98 / 6.04 |
| positive | 8.44 / 7.11 | 4.87 / 5.57 |
| warning | 7.06 / 7.62 | 5.68 / 4.88 |
| danger | 5.74 / 6.68 | 7.54 / 5.11 |
| border-essential | 4.13 / 4.06 | 4.14 / 4.09 |

Night on-action against default/hover/pressed is **8.80/5.54**, **7.59/4.62**, **10.53/7.06**. Dawn is **10.11/6.55**, **11.79/8.13**, **13.44/9.90**. All meet the text threshold in both simulations.

### Secondary colours and outcome grammar

| Meaning | Colour role | Required non-colour cue | Permitted placement |
| --- | --- | --- | --- |
| Control keyboard focus | focus | Offset outer ring | The actual focused control or field |
| Confirmed keyboard recipient | focus | Paired chevrons or explicit recipient label, plus sharp boundary | Confirmed receiving surface only |
| Information | info | Circled information glyph and explanatory text | Help and informational notices |
| Confirmed positive outcome | positive | Checkmark and actual outcome words | Supported completion feedback |
| Warning or attention | warning | Triangle and explicit detail | Attention markers and consequential notices |
| Unknown | warning | Question diamond and unconfirmed wording | Uncertain operation feedback |
| Refused or error | danger | Octagonal stop glyph and reason | Feedback or inline error region |
| Pending | text-secondary | Static clock and waiting wording | Operation feedback |
| Submitted | text-secondary | Submission wording | Launch feedback; no completion checkmark |
| Cancelled | text-secondary | Cancellation glyph and wording | Supported cancellation feedback |

Only outcomes defined by the relevant protocol appear. Colours never classify free-form strings. Untyped status content uses neutral text. Links remain underlined. Category names and collection icons use neutral text and distinct shapes; the system introduces no extra category palette.

### Brand red and danger

Brand red appears in the sigil, active-application contours, selected-state bars, the portal and one affirmative filled action per task block. Save, Apply and Activate use affirmative emphasis only when enabled.

Danger appears on a neutral surface with an octagonal symbol, a reason and an explicit action label. Destructive confirmation uses a danger outline and danger text on neutral chrome, never the affirmative red fill. Resting power and session commands remain neutral. The confirmation panel keeps Cancel before Confirm and follows the source-defined focus policy. Error surfaces never glow.

### High contrast and forced colours

All high-contrast neutral surfaces are black. Text, secondary text and essential control boundaries are white. Their ratio is **21:1**. Additional foregrounds against black have these standard/protanopia/deuteranopia ratios:

| Role | Ratios to 1 |
| --- | --- |
| brand-text | 12.30 / 11.19 / 13.02 |
| focus | 16.75 / 18.71 / 15.43 |
| info | 12.92 / 13.69 / 12.42 |
| positive | 16.27 / 17.19 / 15.64 |
| warning | 16.28 / 15.47 / 16.78 |
| danger | 12.47 / 11.44 / 13.16 |

High contrast removes shadows, gradients, portal effects, dimming and glow. Shapes, labels, checkmarks, contours and focus gaps remain. Selected controls retain a check and leading bar; disabled controls retain disabled semantics and an unavailable/slashed cue, never candidate brackets.

Under `forced-colors: active`, use Canvas/CanvasText, ButtonFace/ButtonText, Field/FieldText and Highlight/HighlightText. Allow browser colour adjustment. Use actual borders and outlines for essential marks. System colour choices are user-controlled, so fixed sRGB ratios do not describe that mode. Preserve all non-colour distinctions.

## Typography

Bundle Inter Variable, Space Grotesk Bold and JetBrains Mono Regular. Use only real supplied weights and `font-synthesis: none`. Space Grotesk appears at 700 and at sizes of at least 20px. JetBrains Mono appears at 400. Fonts load locally with `font-display: swap`; fallback layouts preserve wrapping and target geometry.

| Role | Family | Size / line height | Weight | Tracking |
| --- | --- | --- | ---: | ---: |
| display | Space Grotesk | 48 / 56px | 700 | -1.44px |
| page-title | Space Grotesk | 32 / 40px | 700 | -0.64px |
| headline | Space Grotesk | 24 / 32px | 700 | -0.36px |
| window-title | Space Grotesk | 20 / 28px | 700 | -0.20px |
| reading-lead | Inter | 18 / 28px | 400 | 0 |
| section-title | Inter | 16 / 24px | 600 | 0 |
| reading | Inter | 16 / 24px | 400 | 0 |
| body | Inter | 14 / 20px | 400 | 0 |
| body-strong | Inter | 14 / 20px | 600 | 0 |
| label | Inter | 14 / 20px | 500 | 0 |
| label-strong | Inter | 14 / 20px | 600 | 0 |
| detail | Inter | 12 / 16px | 400 | 0.12px |
| caption | Inter | 12 / 16px | 500 | 0.12px |
| code | JetBrains Mono | 13 / 20px | 400 | 0 |
| code-compact | JetBrains Mono | 12 / 16px | 400 | 0 |

Export font sizes and tracking in rem relative to 16px, with unitless line heights calculated from the exact table ratios. Spatial padding remains in px. The committed 100/125/150/200% appearance scale applies once at the root. No child applies a second scale multiplier.

Use sentence case, left alignment and tabular lining numerals for counts, percentages and numeric tables. Display typography belongs to documentation. Desktop content uses window-title and smaller roles. Paths and shortcuts may use code typography; ordinary feedback uses Inter.

Reading measure is at most 70ch. Labels, titles and details wrap without line clamps. Taskbar application names may ellipsize when necessary, while their full accessible names remain available. Utility names remain readable. Text never shrinks to fit.

## Identity and content

The folded W retains its two valleys and central diamond. Recolour its existing vector geometry with neutral facets and one red focal diamond. Clear space is one diamond width. Use the detailed mark at 32px and above, monochrome at 24–31px and a plain W below 24px. Essential small identity marks use approved foreground colours. Generated imagery never replaces the vector identity.

Use Warlock in prose and WARLOCK in the wordmark. The tagline is **Crafted for flow.** Utility icons use local SVGs with 20px viewboxes and 1.5px strokes; compact and prominent variants use 16px and 24px. Decorative icons are hidden from accessibility APIs and never replace meaningful names.

Copy uses direct actions and factual outcomes. One announcement owner speaks changes. Static status paragraphs remain `aria-live="off"`. Critical interruption follows the user's consent. An unknown result never receives a success checkmark or an automatic mutation retry.

Project materials carry Apache License 2.0 notices. Bundled fonts retain their separate licence notices.

## Signature portal

The portal is a ring of red ember fragments that ignites, expands and resolves into an application window's frame. Closing reverses that spatial idea. Its short diamond-shaped interruption reflects the central diamond of the Warlock sigil.

A portal starts only after an admitted observation establishes that a new application window is mapped. Launch Pending or Submitted does not start ignition. Refused, Cancelled and Unknown do not start it. Closing starts only after an observation establishes removal of the same window incarnation. A close intent or receipt alone does not erase a still-observed window.

The portal does not play for shell popups, notification arrivals, preview frames, search results, workspace navigation, ordinary focus changes, snapping, minimization or restoration. It does not replay when a window becomes visible on another workspace. Session restoration and bulk mapping settle without multiple portals.

**Full opening: 520ms**

| Phase | Time | Construction and easing |
| --- | --- | --- |
| Ignite | 0–120ms | Ring grows from .04 to .16 of its final extent, opacity 0 to .65; `cubic-bezier(.16,0,.3,1)` |
| Expand | 120–380ms | Extent .16 to 1; ring rotation advances by at most 12 degrees; `cubic-bezier(.2,.72,.2,1)` |
| Resolve | 380–460ms | Decorative aperture changes to the final frame radius; ring opacity .65 to .20; `cubic-bezier(.2,0,0,1)` |
| Settle | 460–520ms | Remaining decorative opacity .20 to 0; `cubic-bezier(0,0,.2,1)` |

**Full closing: 360ms**

| Phase | Time | Construction and easing |
| --- | --- | --- |
| Release | 0–90ms | Non-interactive frame remnant acquires a .65-opacity ring; `cubic-bezier(.4,0,1,1)` |
| Contract | 90–270ms | Extent 1 to .06, rotation no more than 8 degrees in reverse; `cubic-bezier(.4,0,.8,.3)` |
| Extinguish | 270–360ms | Extent .06 to .02 and opacity to 0; `cubic-bezier(0,0,.2,1)` |

The live window and its essential focus cues occupy their final geometry from the admitted observation. The portal animates a separate decorative frame/aperture plane. It never scales, translates, fades or clips the live input plane. The ring has a transparent centre and its paint excludes live text, controls and focus indicators. Native clients use a guarded frame effect rather than an overlay across arbitrary client content. Closing retains only a non-interactive, `aria-hidden` visual remnant; focus and input leave immediately according to observed state.
