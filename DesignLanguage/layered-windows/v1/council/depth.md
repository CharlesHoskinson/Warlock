# Depth council report: glow, shadow and shading

Author role: perceptual depth, materials and rendering cost. This is an additive design proposal dated 2026-10-05, not implementation or native qualification. Existing scenario identities, deadlines, native eligibility and ownership obligations remain authoritative.

## Proposed language

Make the three effects central and give each a stable meaning. Shadows describe separation between eligible surfaces; shading describes the grouping of Warlock-owned chrome; a restrained steady glow reinforces the currently confirmed input recipient. Pair every meaningful effect with a sharp boundary, shape or readable label. Changing appearance must never reorder windows, capture input or settle an operation.

The intent is a dark folded-plane identity with luminous edges, complemented by parchment and ink in light mode. A user should be able to answer “where does my typing go?”, “which window am I choosing?” and “which dialog belongs to this window?” from different cues. The glow is a useful steady edge rather than a recurring animation. Navigation candidates can remain distinct from confirmed focus even when the candidate is a background or pinned window.

These are design recommendations derived from the inspected Warlock material and cited references. Their exact numerical values require rendered review, contrast measurement and native qualification.

## Research and adoption decisions

Material 3 explicitly combines tonal surface elevation and shadows. Borrow the separation of these channels: neutral shadows remain useful in light mode, while slightly lighter raised chrome remains legible in dark mode. Do not equate a color-tinted surface with a higher native layer, and do not import Material's elevation numbers as compositor z indices. [Android's Material 3 implementation guidance](https://developer.android.com/develop/ui/compose/designsystems/material3).

Apple describes materials as a means to distinguish foreground navigation from content, with appearance adapting to accessibility settings. Borrow that separation and preference handling, with opaque chrome available. Warlock does not require Liquid Glass refraction or dynamic wallpaper sampling for its depth language. [Apple materials guidance](https://developer.apple.com/design/human-interface-guidelines/materials).

Microsoft warns that stacked acrylic can introduce optical confusion and that acrylic can increase GPU and power use; it supplies opaque fallbacks for high contrast, transparency preferences and constrained operation. Borrow explicit fallbacks and avoid repeated backdrop effects. A shadow/halo mask derived from window geometry does not need a client screenshot or capture lease. [Microsoft acrylic guidance](https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic).

GNOME advises testing light, dark and high-contrast styles and supplying non-color information. Borrow that testing discipline; keep Warlock's own brand palette and spatial vocabulary. [GNOME UI styling guidance](https://developer.gnome.org/hig/guidelines/ui-styling.html).

WCAG's non-text contrast guidance supports a minimum 3:1 for essential focus/state information against adjacent colors. A soft shadow or halo cannot be the only tested state boundary because arbitrary wallpaper and neighboring client pixels can defeat it. Supply a solid controlled inner/outer backing separator, then measure the essential indicator against that adjacent backing and representative actual compositions. [W3C non-text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).

## Independent visual axes

| Meaning | Effect | Redundant cue | Authority |
| --- | --- | --- | --- |
| Confirmed input recipient | Solid lilac perimeter with a steady low-opacity halo | Solid two-unit boundary and active title/control state | Admitted native focus observation; distinguish shell keyboard scope from app recipient |
| Navigation candidate | Quiet perimeter, no confirmed-focus halo | Dashed perimeter, candidate label/title and selection marker | Existing chooser navigation state; cancellation changes no confirmed focus |
| Ordinary eligible window | Neutral contact and ambient shadow | Neutral solid boundary | Existing committed native scene and geometry |
| Child popup/dialog above owner | Greater neutral separation and raised chrome tone | Owner relation/title plus normal child boundary | Admitted native family relation and committed order |
| Owner blocked by an admitted modal | Recessed Warlock-owned chrome | Blocking-dialog identity/reason in the available shell UI | Actual native modality facts; appearance does not create a block |
| Hover | Neutral local chrome shading | Pointer position and existing hover shape | Local interaction state; no focus halo or raise |
| Pinned/always on top | Retains its normal shadow class | Persistent pin icon/label | Admitted pin observation; not input focus |
| Pending or Unknown operation | Independent status annotation | Existing text and outcome icon | Correlated operation state; no completed-focus or success glow inferred |

Assign shadow class by semantic surface role and current interaction, not every ordinal position in a potentially enormous window stack. Thus ten stacked ordinary windows do not create ten progressively wider shadow kernels. A popup's larger shadow describes physical separation, while the original scene solver determines which eligible surface is actually above another.

The same admitted scene revision must govern surface order, decoration clipping and any relation shown by shading. Decorative effects stay below unrelated covering surfaces, follow output clipping and do not enter input regions. A fully occluded or ineligible surface must not leak its glow through a covering window or survive as a ghost frame. Minimized and inactive nonsticky source windows remain excluded by the original eligibility rules; catalog or historical preview cards have their own explicitly labeled shell framing.

Never dim, desaturate or cover arbitrary application text solely to portray inactivity. Shading belongs to Warlock-owned chrome and intentional shell backplates. Where a client has no Warlock-owned header, show its relation in the chooser/title annotation and boundary. A modal relationship may recess only the blocked owner's owned chrome; unrelated application windows remain unchanged. Any future client-content scrim would require a separately reviewed accessibility/content-preservation contract and native proof.

## Candidate bounded token set

Use the existing reference → semantic → component tiers. Keep all frozen schema-1 palette values intact. Additive depth tokens derive from `container`, `page`, `boundary` and `focus`; derived blends are named component tokens with measured foreground pairs. Units below are logical UI units, mapped explicitly to device pixels per output; CSS pixel equivalence applies only to catalog specimens.

| Component token | Candidate recipe | Intended use |
| --- | --- | --- |
| `depth-rest` | Contact shadow: offset Y 2, blur 4; ambient shadow: offset Y 6, blur 16; spread 0 | Ordinary floating surfaces |
| `depth-raised` | Contact: Y 3, blur 6; ambient: Y 8, blur 24; spread 0 | Presented popup/chooser surface |
| `depth-dialog` | Contact: Y 4, blur 8; ambient: Y 12, blur 32; spread 0 | Presented child dialog |
| `depth-flush` | No outer shadow; preserve boundary | Tiled/maximized screen-edge surfaces where outer geometry is unavailable |
| `shadow-contact` | Neutral ink/black, alpha 0.16 light and 0.28 dark | Tight separation |
| `shadow-ambient` | Neutral ink/black, alpha 0.12 light and 0.20 dark | Broad separation |
| `focus-edge` | Existing theme-specific focus accent, width 2, controlled backing separator 1 | Essential active boundary |
| `focus-halo` | Existing focus accent, blur 12, spread 0, alpha 0.16 dark and 0.10 light | Steady reinforcement of confirmed input focus |
| `candidate-edge` | Existing theme-specific focus accent, width 2, dashed stroke 4 on/3 off, no halo | Navigation choice before confirmation |
| `chrome-recessed` | Existing `container` with `page` blend 6% | Grouped inactive/blocked owner chrome only |
| `chrome-raised` | Existing `container` with `content` blend 4% dark; opaque container in light mode | Popup/dialog chrome only |
| `depth-transition` | At most 120 ms ease-out for optional effect opacity; no recurring cycle | A presentation transition, not an operation deadline |

These recipes are a council starting point, not a claim of contrast or performance acceptance. Surface text uses opaque original contrast-qualified pairs whenever a proposed blend fails. A renderer must choose finite kernel support and documented padding for each blur recipe; cap blur at 32 logical units and halo at 12 for this initial language rather than growing with stack depth. Bounded texture/cache capacities still require explicit measured S02 admission and lifetime checks. No newly invented token cap replaces the existing mandatory resource budget.

Two neutral shadow components plus one focus halo are the maximum normal decorative recipe per eligible surface. Prefer geometry masks, precomputed kernels and reusable nine-slice/cache representations keyed by size, corner geometry, scale, theme and rendering generation where the qualified renderer supports them. Do not claim a specific implementation until it is compiled and measured. Decorations themselves add no backdrop captures, client image leases, CPU readbacks or additional per-window clock. Stable idle scenes do not schedule periodic frames solely to animate a glow. Ordinary app damage may of course still cause compositor frames.

## Preference and display behavior

Reduced motion removes the optional transition; the same solid focused/candidate boundaries and static shadows remain. Native focus/presentation facts still determine the cue, and preference changes preserve pending target identity. Do not delay the essential solid focus boundary while easing the decorative halo. If focus changes again during a transition, derive the new target from the latest admitted observation and native last-presented state; no competing Elm or renderer focus authority.

Reduced transparency uses opaque chrome/backplates and removes backdrop-dependent translucency. High contrast or a low-effects profile can replace soft glows/shadows with crisp contrasting outlines, candidate dashes and relation labels. A person can suppress soft effects without suppressing essential state cues. This is equivalent information, not a second desktop policy. Default glows, shadows and shading remain major visible elements in the ordinary profile.

Dark mode uses a visible tonal distinction as well as shadow because black shadows alone are weak on dark backgrounds. Light mode uses the existing darker lilac accent, restrained halo opacity and a stronger controlled boundary. Do not put the dark-theme pastel focus accent directly on parchment. Avoid broad luminous white scrims, recursive glow amplification or full-window additive lighting. The low-effects option should also serve brightness-sensitive/OLED users, but power savings or burn-in prevention are unmeasured hypotheses and must not be advertised as accepted benefits. Cover very dark adjacent surfaces, white content, patterned wallpaper, HDR/SDR outputs and fractional scale in actual native qualification.

## Proposed EARS additions

The coordinator may assign final requirement identifiers; these paragraphs are proposed normative text, additive to WARLOCK-DL-002/003/004/006/014/015 and the existing scene eligibility requirements.

1. While layered windows are displayed, Warlock shall represent surface separation with bounded neutral shadows and owned-chrome shading, and shall represent confirmed input focus with a distinct solid perimeter and optional steady focus halo derived from admitted native observations.
2. When navigation selects a candidate that is not the confirmed input recipient, Warlock shall expose a distinguishable candidate boundary and stable label without asserting focus, raising the source window or changing native input eligibility through decorative effects.
3. While a native family relationship or modal block is admitted, Warlock shall apply relation shading only to eligible affected owned chrome and shall leave unrelated client content, source paint/hit eligibility and operation outcomes unchanged.
4. When reduced motion, reduced transparency, high contrast or low-effects preferences change, Warlock shall retain equivalent focus, candidate and family information through static opaque boundaries, shapes and labels while preserving existing intent identity, native observations and original deadlines.
5. When a surface's eligibility, committed scene order, output, scale or rendering generation changes, Warlock shall recompute or retire its decoration from the same qualified scene facts, prevent occluded/ineligible effects from leaking, and exclude all decorative extents from input regions.
6. While the desktop is visually idle, decorative effects shall schedule no recurring animation work; before release, actual native effects shall meet the frozen measured resource, presented-geometry, ownership and deadline gates with their original identities.

## OpenSpec scenario proposals and evidence scope

| Scenario | Given / when | Required observation | Evidence |
| --- | --- | --- | --- |
| Focus versus candidate | A has admitted focus; chooser selects B | A remains solid focused; B is dashed/labeled candidate; no candidate-induced source raise; cancel restores existing navigation context | Elm/Quint plus actual chooser/native focus/paint-order evidence |
| Rapid navigation | A→B→C candidate sequence, delayed or stale native focus observations | Decorations represent latest admitted facts; stale B cannot overwrite C; optional halo never fabricates confirmation | Selected Quint/replay plus exact-tuple native campaign |
| Modal family | Owner O, admitted child D, unrelated same-app peer P | D's normal shadow above O; only O's owned chrome recesses; P's pixels/order/focus policy remain unchanged | Native captured pixels and existing family/input facts |
| Occlusion and eligibility | Focused A partially covered by pinned B, then A minimized or changes to inactive nonsticky workspace | A's effects are correctly occluded and later absent; no decoration changes native paint/hit candidates | Native screenshot and committed scene/hit evidence |
| Arbitrary background contrast | White/black/patterned neighboring content in both themes | Essential boundary remains ≥3:1 against its controlled adjacent backing; meaningful state has non-color cue | Measured specimens plus native pixel composition; browser alone insufficient |
| Preference changes in flight | Pending/Unknown focus intent while theme/reduced-motion/contrast preference changes | Same intent/target/outcome; static equivalent cue; no replay; no extension of original operation deadline | Actual Elm publication checks and native continuity/deadline checks |
| Fractional scale and multiple outputs | Window crosses unlike scale/SDR-HDR outputs | Appropriate generation and geometry; no stranded halo, seam or duplicate focused source; no expanded hit region | Actual native output/hardware campaigns |
| Resource and idle | Overlapping window set during drag/resize then stable idle | No decorative animation timers at idle; bounded decoration resources physically retire; original S02 and drag52 remain intact | Native resource/presentation metrics and original campaigns |
| Client text preservation | High-density editor behind focused dialog/peer | Decorative shading alters only owned chrome; source text remains unchanged except actual occlusion | Independent client/source pixel comparison |

Browser specimens can demonstrate tokens, shapes, contrast pairs and preference adaptations. They do not prove native focus, eligibility, family order, presented pixels, hardware behavior, physical retirement, accessibility/IME or original deadlines. New design scenarios supplement rather than rename, reduce or replace the frozen 242/417 and right-click 24/48 baseline.

## Disagreements and convergence notes

The frozen brand guide says to keep glows out of small logos and ordinary controls. This user request adds meaningful window-navigation glow. Resolve the scope additively: no glow in small logo glyphs or routine form controls; a steady halo is permitted on window focus/navigation chrome. Leave the frozen original unchanged and record the extension in the new consensus.

Prefer a distinct dashed candidate boundary with no halo, while retaining the steady halo for confirmed focus. If the color council wants a mint candidate color, reserve it as a separate navigation role rather than recycling the existing `confirmed` outcome role; hue must still have a shape/label cue. Do not use warmth as depth rank if it conflicts with warning/refusal/outcome meanings. Focus and candidate may use the same lilac hue when their shapes remain distinct.

The interaction council independently proposes same-scene composition, occlusion, decorative hit exclusion and preserving Omarchy's effective chooser/cycle dispatch. I agree. No new shortcut, keybinding override or hover-driven raise is introduced by this language.

## Inspected local inputs

All paths are relative to `/home/hoskinson/omarchy-windows-parity`. Hashes were computed directly from the current files; frozen originals were not edited.

| Path | SHA-256 |
| --- | --- |
| `AGENTS.md` | `0b290ba5e79a6be5ab16572741e275384ed47398eece952b9ff515702fd18d02` |
| `docs/HANDOFF.md` | `339f702523fe5f4113700978c14c84e6eaa289ba964053d2d1e7d4954dacdbbd` |
| `docs/warlock-build-loop/design-language-v1/INSTRUCTIONS.md` | `7d6eaf650ea7f5091eace9f17188a6d6bf610c7cb654677b1a185a98b18bdf50` |
| `DesignLanguage/WORKPLAN.md` | `986d257d98c09802759e63ffb0894a22780bbc47b4a4e6279c3316dea090e1cc` |
| `DesignLanguage/CONSENSUS.md` | `5907b395ba7473126976cd6498f63d90add54045778ca5ea7c1f577bac9c9009` |
| `DesignLanguage/catalog/v6/tokens.json` | `352eca419c1e1c4150810f02bf5bb6f0b8a2dabd144e8c7077a6ca30b4a988c9` |
| `DesignLanguage/EARS.md` | `2e0a5d0eace0f4c4aca25f6b205edb8bdd0a6b468fbd10883e96053e44a06f18` |
| `openspec/changes/warlock-design-language/specs/warlock-design-language/spec.md` | `95d0b637e49033860a16f9f6ef27fb9db147ff6fc3d50edf6e7a6c456cb05353` |
| `openspec/changes/elm-desktop-pivot/specs/elm-layering/spec.md` | `685509a72ff963316eb4d70543f6dbc0d5b52fdf09368f0c5a3ce0ee369936e3` |
| `docs/warlock-brand/v1/BRAND-GUIDE.md` | `a4802a89df172c2a3ed618868542b20eb1e5ab4fb52046d4d23c2fd833e61d11` |

The consensus requirement list and source palette were read directly. Original layer-solver contracts were inspected for eligibility, family constraints and matching paint/hit order. Primary web guidance was inspected on 2026-10-05; page links above identify the referenced sources, whose dynamic content was not frozen as repository evidence.
