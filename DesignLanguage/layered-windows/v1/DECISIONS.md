# Warlock's language for layered windows

Color, glow, shadow and shading are major parts of the ordinary desktop profile.
Each has a stable job: **neutral shadows show separation, opaque chrome shading
groups layers, and a steady violet halo marks the confirmed keyboard recipient.**
Sharp contours and visible labels carry the same information when soft effects
or color distinctions are unavailable.

| Meaning | Appearance | Source of truth |
| --- | --- | --- |
| Active application | Solid violet contour; Active application in navigation | Admitted native active-window observation |
| Keyboard recipient | Primary steady violet halo on eligible window or shell chrome | Admitted native keyboard scope; no halo when unconfirmed |
| Navigation candidate | Violet corner marks or dashed tile contour; Candidate | Existing chooser navigation state, independent from active application |
| Family | Short segmented brackets; Family or Context | Admitted native relationship, never PID, title or icon alone |
| Physical separation | Neutral contact and ambient shadows | Semantic surface role and committed native scene geometry/order |
| Layer grouping | Opaque raised/recessed Warlock-owned chrome | Qualified owned chrome and native relationship/scope |
| Pin, minimization or block | Neutral glyph, label and applicable reason | Corresponding admitted native facts |
| Pending, Refused, Cancelled or Unknown | Existing independent text and outcome cue | Correlated operation state, never decoration |

When the chooser owns typing, its chrome carries the primary halo. The previous
application may retain its qualified Active application contour, while the chosen
tile remains Candidate. A newer valid observation can make B active while C is
the candidate; observation validity comes from native revision/incarnation,
not equality with selection. Cancelling navigation supplies no speculative focus
or raise effect.

The default halo uses the established lilac in dark mode and the established
darker violet in light mode. Its maximum blur is 12 logical UI units; alpha is
0.16 dark and 0.10 light. Family glow, when used, stays on short brackets at alpha
no greater than 0.06. It never encloses a second apparently active window.
Ordinary controls and small logos retain the frozen brand's crisp treatment;
this is an additive window/shell-chrome scope for the user's new glow direction.

Shadows have two neutral components, with rest, raised, dialog and flush recipes.
Blur is capped at 32 logical units. Focus never lifts a window or changes shadow
class. Increasing the number of stacked windows does not create progressively
larger blur kernels. Shading affects opaque Warlock-owned chrome and backplates,
preserving client colors, text and opacity. Effects clip and occlude with their
own qualified scene surfaces and create no input regions.

An essential solid boundary updates immediately when admitted facts change.
An optional decorative opacity transition lasts at most 120 ms, and reduced
motion removes it. There is no pulsing, breathing or travelling glow and no
periodic frame work solely for decoration. High contrast and effects-off use
opaque boundaries, labels and shape distinctions without soft effects. Reduced
transparency uses opaque chrome without a backdrop dependency.

These numbers are design targets. They do not establish actual S02 resource or
presentation acceptance. The token packet, EARS and OpenSpec scenarios preserve
all original measured budgets, native clocks, physical retirement and release
gates. All effective Omarchy words, commands and keybindings—including the user's
chooser and release overrides—retain their existing meanings.

## Reference adoption

| Reference | Adopted concern | Warlock decision |
| --- | --- | --- |
| [Material 3](https://developer.android.com/develop/ui/compose/designsystems/material3) | Tonal surfaces and shadows as separate channels | Opaque owned-chrome tones plus neutral shadows; token depth is independent from native z order |
| [Apple materials](https://developer.apple.com/design/human-interface-guidelines/materials) | Foreground navigation and accessible appearance | Distinct shell foreground with opaque fallback; no refraction requirement |
| [Windows layering](https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/layering) | Contours and separation communicate relationships | Warlock geometry, violet and bounded neutral kernels |
| [Windows acrylic](https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic) | Explicit fallback and rendering cost | No compulsory backdrop capture; measured native costs remain mandatory |
| [GNOME styling](https://developer.gnome.org/hig/guidelines/ui-styling.html) | Light, dark and high-contrast testing | Equivalent shape/label information across preferences |
| [W3C color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) and [contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) | Visible alternatives and adjacent-background contrast | Required opaque contours and labels; soft halo alone cannot carry essential state |
| Omarchy effective configuration | Existing command, chooser and keyboard semantics | User overrides and actual release/consumption behavior remain authoritative |

Independent council reports retain their source hashes, citations, proposals
and disagreements. The frozen earlier design consensus is not rewritten.
