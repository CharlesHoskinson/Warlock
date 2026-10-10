# Current Warlock design guidance

Updated 8 October 2026. Start with the [browser catalog entrance](catalog/index.html), [visual system](DESIGN.md), [contributor workflow](CONTRIBUTING.md) and [remaining implementation](../docs/warlock-roadmap/FEATURE-COMPLETION.md).

## Current product and frozen specimens

[implementation/warlock](../implementation/warlock/README.md) is the editable GUI candidate. It includes taskbar/pickers, launcher search, native Alt-Tab, Task View/workspace transfer, snap selection, appearance and motion preferences, notification center, system menu, installed Files integration, jump lists, attention, high contrast, IME composition and authorized preview states. The pin/MAX draft remains incomplete.

[Catalog v6](catalog/v6/index.html) is a frozen design specimen built from an earlier selected closure: 49 Elm modules and 14 component families. Its source/token/browser evidence applies to that specimen. It does not describe every later module or establish native GUI acceptance. The active candidate currently contains 92 Elm source files, including replay/support modules; that is not a widget or feature count. A full current widget/state registry remains an integration task.

The thirty-contract [design consensus](EARS.md) and fourteen-requirement [layered-window addendum](layered-windows/v1/EARS.md) remain authoritative design targets. This guidance updates their application and navigation without rewriting frozen consensus, specimens or evidence.

## Interaction and outcome

One immutable Elm owner holds ordinary policy. Typed intent crosses the existing bridge; correlated native facts determine confirmed window state. Views and documentation examples do not supply a second authority. Keep focus, selection/candidate, application activity, preview freshness and action outcome distinct.

Reserve stable preview geometry across Loading, Live, Historical and Unavailable. Arrival of pixels must not move a pressed control or reinterpret a gesture. Preserve press-time identity/publication/lease guards and cancel mismatched release; fix layout instead of retargeting the action. The retained pin/MAX native failure demonstrates why both protections are needed.

Pending, Refused, Cancelled and Unknown need readable feedback. Unknown uses the existing read-only reconciliation path and cannot automatically replay a mutation. An acknowledgement is not proof of displayed pixels, actual keyboard recipient or completed power transition.

## Color, depth and accessibility

Use the approved [layer roles](layered-windows/v1/DECISIONS.md): the keyboard-recipient halo, active-application contour, candidate tile and family marks have separate meanings. Neutral shadows express separation; opaque owned-chrome shading groups layers. Derive their presentation from current committed native observations. Decorative effects must not change scene order, eligibility or input regions.

Every cue retains a non-color shape or text alternative. High contrast, effects-off, reduced transparency and reduced motion preserve information and usable controls. Measure rendered labels, focus, targets and reflow; a token value or DOM assertion alone is insufficient. Expose complete native control semantics and use one announcement owner. Prefer keyed control identity and explicit focus changes over refocusing on unrelated updates.

Effects-off and reduced-transparency preferences now have native keyboard save/restart evidence ([scope](../implementation/warlock/qa/evidence/layer-appearance/README.md)). Current native shell colors and the snap glow are provisional rather than full layered-token adoption. Inset focus rings avoid clipping but do not close the voted outer-indicator contract. Always on top now has one stable checkable label and shape, with typed checked state from the exact captured native pin observation. Actual pointer/keyboard MAX pin/unpin and physical overlap behavior are recorded in [the current evidence](../implementation/warlock/qa/evidence/pin-check/README.md); native AT and full family/fullscreen qualification remain open. Taskbar Pin/Unpin names application persistence only.

## New and evolving surfaces

Settings, notifications, system controls, Files, jump lists and motion preferences require the same six component sections as the existing catalog: overview, anatomy/states, behavior/keyboard, accessibility, content and evidence. Record their actual implementation route and unsupported capabilities before adding specimens. Label every simulated native outcome as fixture data.

Preserve effective Omarchy keywords, commands, bindings and user overrides. The current implementation is not a claim that every effective binding has been migrated. Resolve shortcut conflicts explicitly and keep dismissible guidance and offline recovery reachable.

## Contributor plugin

The [Warlock contributor plugin](../plugins/warlock-contributor/README.md) supports Claude Code, Codex and Grok through one shared offline checker and skill. It scaffolds original-scenario work, protects source ownership and records bounded evidence. The [design contribution guide](CONTRIBUTING.md) explains how to use it for product design changes and for catalog/documentation work. Checker compliance does not accept a GUI feature, and optional host hooks do not replace explicit loop checks.

Notification arrivals share the root-selected announcement owner with matched refusals. The notification center exposes session DND and critical-interruption consent with pressed state; permitted arrivals are polite unless an explicitly allowed critical arrival uses assertive delivery. Native transport/keyboard/current-node focus observations are recorded [here](../implementation/warlock/qa/evidence/notification-announcements/README.md); speech/braille and full notification relevance remain open.

Matched adapter failures now use the same polite owner and explicit recovery copy ([scope](../implementation/warlock/qa/evidence/adapter-announcements/README.md)). Failed opening reads must preserve the focused control. Notification Refresh stays focusable while reading, displays progress, and uses the Elm pending-request guard to prevent duplicate reads. Current native keyboard evidence covers occupied-service failure and explicit empty-service recovery; other providers and native speech/braille remain open.

Notification expiry and expired-action rejection now follow exact focus/user-invocation relevance and DND ([scope](../implementation/warlock/qa/evidence/notification-relevance/README.md)). Preserve the focused unavailable action as the same keyed node, with aria-disabled, visible unavailable detail and no mutation authority, until the user navigates away. Passive focus observations carry current owner/publication/lease/control guards; they are not a second focus or action policy. Native keyboard focus/relevance and the original nine-surface regression pass; actual speech/braille and wider lifecycle acceptance remain open.

MAX menu selected-state semantics now include the committed state prefix. Actual keyboard focus follows an explicit Elm operation-selection change, while unrelated publications preserve a focused utility. Checked, selected and Pending/Unknown remain separate meanings; a checkmark is never an effect receipt or action grant.
