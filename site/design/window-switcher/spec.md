# Window switcher

## Overview

The switcher presents one candidate at a time in a quiet, single-column list. It chooses among observed window families without changing the desktop window focus or stacking while browsing. A committed activation is an intent; a subsequent native observation establishes the resulting focus. The preferred documentation width is 720px; the allocated host surface remains authoritative.

## Anatomy and hierarchy

The actual `.surface-popup[data-mode="switcher"]` contains `h1`, a static `p[role="status"][aria-live="off"]`, and `.surface-controls[role="group"]`. Its first child is `[role="listbox"][aria-label="Switch windows"]`; keyed buttons with `[role="option"]` and `data-surface-control` beginning `switcher:family:` follow the source entry order. Its second child is the separate `Window switcher actions` group. The controls retain source order: `control:close`, `control:reverse`, `control:forward`, `control:commit`. The source names are Cancel window switcher, Previous window, Next window and Activate selected window. Labels wrap, including at enlarged text sizes. Detail is the source's Selected, Open or Minimized. The specimen presents these actual strings.

Each option has at least 3.5rem height, 12px inline and 6px block padding and a 2px label/detail gap. Options have a 6px gap. The action group follows after 16px, uses as many equal columns as fit with a minimum column width of 10rem, capped by the available width. Columns collapse as the available space narrows or text grows; source order and 8px gaps remain intact. The scrollport retains 6px of focus paint and scroll padding. At short heights the popup itself scrolls without a sticky header. Popup bounds follow the host allocation; no preferred width leaves unused host pixels.

## States and attention

`[role="option"][aria-selected="true"]` paints a selected wash and four neutral 12px corner brackets, each 2px thick. The source detail says Selected. Candidate remains visible when focus moves to an action. The shared 2px blue outer focus outline, 2px offset and opaque gap belong to the actually focused control and remain additive. Cancel remains quiet, Previous and Next have secondary outlines, and Activate alone uses the affirmative fill when enabled. The source-disabled button keeps disabled semantics, full opacity and secondary text. Unavailable actions never gain hover or press feedback. High contrast preserves the candidate wording and a sharp boundary; forced colours use corner-clipped real borders on a noninteractive overlay.

The active application uses its separate red desktop contour and activity marker. The observed focused window uses its neutral guarded edge, beacon and taskbar marker. Neither derives from the switcher candidate. Missing typed presentation facts produce neutral desktop treatment. The switcher does not display thumbnails, timestamps or inferred application activity.

## Behaviour and keyboard

Opening, cycling, cancellation and exit are immediate. Native Alt+Tab and Shift+Alt+Tab cycle when delivered; release commits when the native chord is delivered. Local controls expose Previous, Next, Activate and Cancel. The source status describes Tab or Right, Shift+Tab or Left, Enter and Escape. Escape cancels. A pointer or local choice changes the candidate, not the native window. Commit uses the captured identity and authority. A closed or stale publication cannot commit. The frozen entry set excludes later arrivals; retirement reconciles surviving entries. Entry and exit never use a portal or fade. Focus return follows the controller's observed focus policy.

## Accessibility and renderer requirements

Preserve keyed option nodes, `aria-selected`, listbox and option roles, action grouping and `data-surface-control` identities. Do not infer keyboard focus from selection or duplicate the option's accessible name in CSS. Focus paint must stay visible at every scroll edge. Retain source names and activation semantics. The host must provide actual window focus and activity facts to the separate desktop presentation. An unavailable/slashed cue for a disabled action is a shared renderer requirement; CSS alone cannot supply a semantic unavailable indication. At 320px and 200% text, controls wrap and scroll rather than shrink or clip.

## Evidence and references

The native `switcher-native-controls` initial and reopened captures show the existing dense action-first appearance and a blue selected outline. The renderer now groups options first and actions second. The v6 picker is a related frozen reference for independent focus and activation, not a switcher implementation. Material list guidance supports continuous vertical rows; Fluent accessibility, Windows keyboard, GNOME keyboard, KDE layout, Apple motion and WCAG focus-not-obscured captures inform grouping, keyboard access and visible focus. The supplied Warlock foundations govern final values. See [evidence](evidence.json) for exact paths and hashes and the [switcher scenario](scenario.json) for source-backed observations.

## Try it

[Open the switcher scenario on the desktop](../../test-drive/index.html?scenario=switcher) using its visible control or the delivered shortcut. Cycle in both directions, move control focus into the action group and cancel. Activate only when the chosen family is the intended target.

The [Night concept study](mockups/switcher-night.png) and [Dawn concept study](mockups/switcher-dawn.png) are each a **Generated concept study**. The illustrations contain inaccurate activation text, unsupported icons and window controls, and an outlined Cancel. Dawn also omits control focus. The specimen and this specification define the interface. The [image manifest](mockups/manifest.json) classifies the additional generated draft.
