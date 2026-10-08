# Current Warlock design guidance

Updated 8 October 2026. Start with the [browser catalog entrance](catalog/index.html), [visual system](DESIGN.md), [contributor workflow](CONTRIBUTING.md) and [remaining implementation](../docs/warlock-roadmap/FEATURE-COMPLETION.md).

## Current product and frozen specimens

[implementation/warlock](../implementation/warlock/README.md) is the editable GUI candidate. It includes taskbar/pickers, launcher search, native Alt-Tab, Task View/workspace transfer, snap selection, appearance and motion preferences, notification center, system menu, installed Files integration, jump lists, attention, high contrast, IME composition and authorized preview states. The pin/MAX draft remains incomplete.

[Catalog v6](catalog/v6/index.html) is a frozen design specimen built from an earlier selected closure: 49 Elm modules and 14 component families. Its source/token/browser evidence applies to that specimen. It does not describe every later module or establish native GUI acceptance. The active candidate currently contains 88 Elm source files, including replay/support modules; that is not a widget or feature count. A full current widget/state registry remains an integration task.

The thirty-contract [design consensus](EARS.md) and fourteen-requirement [layered-window addendum](layered-windows/v1/EARS.md) remain authoritative design targets. This guidance updates their application and navigation without rewriting frozen consensus, specimens or evidence.

## Interaction and outcome

One immutable Elm owner holds ordinary policy. Typed intent crosses the existing bridge; correlated native facts determine confirmed window state. Views and documentation examples do not supply a second authority. Keep focus, selection/candidate, application activity, preview freshness and action outcome distinct.

Reserve stable preview geometry across Loading, Live, Historical and Unavailable. Arrival of pixels must not move a pressed control or reinterpret a gesture. Preserve press-time identity/publication/lease guards and cancel mismatched release; fix layout instead of retargeting the action. The current pin/MAX native failure demonstrates why both protections are needed.

Pending, Refused, Cancelled and Unknown need readable feedback. Unknown uses the existing read-only reconciliation path and cannot automatically replay a mutation. An acknowledgement is not proof of displayed pixels, actual keyboard recipient or completed power transition.

## Color, depth and accessibility

Use the approved [layer roles](layered-windows/v1/DECISIONS.md): the keyboard-recipient halo, active-application contour, candidate tile and family marks have separate meanings. Neutral shadows express separation; opaque owned-chrome shading groups layers. Derive their presentation from current committed native observations. Decorative effects must not change scene order, eligibility or input regions.

Every cue retains a non-color shape or text alternative. High contrast, effects-off, reduced transparency and reduced motion preserve information and usable controls. Measure rendered labels, focus, targets and reflow; a token value or DOM assertion alone is insufficient. Expose complete native control semantics and use one announcement owner. Prefer keyed control identity and explicit focus changes over refocusing on unrelated updates.

Effects-off and reduced transparency are requirements awaiting implementation. Current native shell colors and the snap glow are provisional rather than full layered-token adoption. Inset focus rings avoid clipping but do not close the voted outer-indicator contract. Always on top needs a stable checkable label with observed checked state; current label-swapping and missing checked semantics remain product work. Taskbar Pin/Unpin names application persistence only.

## New and evolving surfaces

Settings, notifications, system controls, Files, jump lists and motion preferences require the same six component sections as the existing catalog: overview, anatomy/states, behavior/keyboard, accessibility, content and evidence. Record their actual implementation route and unsupported capabilities before adding specimens. Label every simulated native outcome as fixture data.

Preserve effective Omarchy keywords, commands, bindings and user overrides. The current implementation is not a claim that every effective binding has been migrated. Resolve shortcut conflicts explicitly and keep dismissible guidance and offline recovery reachable.

## Contributor plugin

The [Warlock contributor plugin](../plugins/warlock-contributor/README.md) supports Claude Code, Codex and Grok through one shared offline checker and skill. It scaffolds original-scenario work, protects source ownership and records bounded evidence. The [design contribution guide](CONTRIBUTING.md) explains how to use it for product design changes and for catalog/documentation work. Checker compliance does not accept a GUI feature, and optional host hooks do not replace explicit loop checks.
