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

Effects-off and reduced-transparency preferences now have native keyboard save/restart evidence ([scope](../implementation/warlock/qa/evidence/layer-appearance/README.md)). Current native shell colors and the snap glow are provisional rather than full layered-token adoption. Taskbar and Settings now implement the voted outer focus contour, with explicit paint space, scroll reveal and separate active/pressed cues. The taskbar also gates its contour on actual document focus, retaining visible keyboard focus after pointer-menu use when WebKit does not match `:focus-visible`; [native enlarged-scroll evidence](../implementation/warlock/qa/evidence/dense-outer-focus/README.md) covers the fix and inactive-bar suppression. [Scoped evidence](../implementation/warlock/qa/evidence/outer-focus-indicators/README.md) covers browser theme/scale/forced-color geometry and native keyboard/contrast observations; whole-surface AT, output profiles and independent acceptance remain open. Always on top now has one stable checkable label and shape, with typed checked state from the exact captured native pin observation. Actual pointer/keyboard MAX pin/unpin and physical overlap behavior are recorded in [the current evidence](../implementation/warlock/qa/evidence/pin-check/README.md); native AT and full family/fullscreen qualification remain open. Taskbar Pin/Unpin names application persistence only.

Grouped taskbar items retain the running window count while exposing Active when a member is foreground. The same observed state drives the visible detail and native toggle state; opening a grouped item still chooses a window. [Current evidence](../implementation/warlock/qa/evidence/taskbar-group-active-state/README.md) records the production projection and native semantic observations; original AT action, speech/braille and independent acceptance remain separate.

## New and evolving surfaces

Settings, notifications, system controls, Files, jump lists and motion preferences require the same six component sections as the existing catalog: overview, anatomy/states, behavior/keyboard, accessibility, content and evidence. Record their actual implementation route and unsupported capabilities before adding specimens. Label every simulated native outcome as fixture data.

Preserve effective Omarchy keywords, commands, bindings and user overrides. The current implementation is not a claim that every effective binding has been migrated. Resolve shortcut conflicts explicitly and keep dismissible guidance and offline recovery reachable.

## Contributor plugin

The [Warlock contributor plugin](../plugins/warlock-contributor/README.md) supports Claude Code, Codex and Grok through one shared offline checker and skill. It scaffolds original-scenario work, protects source ownership and records bounded evidence. The [design contribution guide](CONTRIBUTING.md) explains how to use it for product design changes and for catalog/documentation work. Checker compliance does not accept a GUI feature, and optional host hooks do not replace explicit loop checks.

Notification arrivals share the root-selected announcement owner with matched refusals. The notification center exposes session DND and critical-interruption consent with pressed state; permitted arrivals are polite unless an explicitly allowed critical arrival uses assertive delivery. Native transport/keyboard/current-node focus observations are recorded [here](../implementation/warlock/qa/evidence/notification-announcements/README.md); speech/braille and full notification relevance remain open.

Matched adapter failures now use the same polite owner and explicit recovery copy ([scope](../implementation/warlock/qa/evidence/adapter-announcements/README.md)). Failed opening reads must preserve the focused control. Notification Refresh stays focusable while reading, displays progress, and uses the Elm pending-request guard to prevent duplicate reads. Current native keyboard evidence covers occupied-service failure and explicit empty-service recovery; other providers and native speech/braille remain open.

Notification expiry and expired-action rejection now follow exact focus/user-invocation relevance and DND ([scope](../implementation/warlock/qa/evidence/notification-relevance/README.md)). Preserve the focused unavailable action as the same keyed node, with aria-disabled, visible unavailable detail and no mutation authority, until the user navigates away. Passive focus observations carry current owner/publication/lease/control guards; they are not a second focus or action policy. Native keyboard focus/relevance and the original nine-surface regression pass; actual speech/braille and wider lifecycle acceptance remain open.

MAX menu selected-state semantics now include the committed state prefix. Actual keyboard focus follows an explicit Elm operation-selection change, while unrelated publications preserve a focused utility. Checked, selected and Pending/Unknown remain separate meanings; a checkmark is never an effect receipt or action grant.

Two floating MAX members now retain their placements while native hit traversal respects actual surface input regions. [The recorded overlap](../implementation/warlock/qa/evidence/max-input-region/README.md) keeps upper pixels at an excluded point and delivers the physical click to the lower eligible application. Keep paint order and input eligibility separate; glows and shadows must not fill input holes or imply a recipient without observed focus. [Shared committed window-scene identity](../implementation/warlock/qa/evidence/committed-max-scene/README.md) is now observed for the original included/excluded native MAX points, with actual GTK press/release owners. Full scene/presentation and transformed/modal/race/exception/AT cases remain open. The stable checked pin/MAX pointer/keyboard regression passes on the new owning tuple.

Native render order is now captured as one window-plane snapshot and published after successful output commit and unchanged structural dependencies. MAX input consumes that snapshot only while its weak owners and structural facts still match. Distinguish this observed scene contract from whole-scene presentation, animated effects, layer/grab policy and AT acceptance. Keep focus/paint cues and input-region eligibility distinct when extending the remaining cases.


The ordinary MAX no-activation branch now suppresses a press and its release when the committed traversal finds no eligible window. Actual both-excluded pixels remain visible, clicking changes neither focus nor stacking and delivers no GTK event, and an eligible later click recovers. The original lower-eligible passthrough and pin/MAX pointer/keyboard regression remain intact. See [scoped evidence](../implementation/warlock/qa/evidence/max-no-activation/README.md). Keep paint, focus and eligibility cues distinct. Cached-pointer/commit races, transformed/modal/grab/layer policy, AT and independent full scene acceptance remain open.


MAX modal activation now uses the shared native family recipient policy against the committed window order. A blocked-parent click focuses and raises the eligible modal without sending the parent press/release to GTK. Native modal pixels, keyboard receipt, unchanged MAX root order/geometry, taskbar activation and retirement recovery are observed; see [current evidence](../implementation/warlock/qa/evidence/max-modal-focus/README.md). Preserve the distinction between painted owner, eligible pointer surface and accepted keyboard recipient in focus cues. Nested/ambiguous native families, transformed outputs, grabs/layers, fullscreen policy, AT and independent acceptance remain open. Two direct visible-owner recordings pass behavior checks but fail host shutdown with outstanding picker custody/journal. The follow-up [picker retirement fix](../implementation/warlock/qa/evidence/picker-preoffer-retirement/README.md) now passes that unchanged direct-owner journey including normal host exit; both historical failures remain retained. The fullscreen/pin/menu follow-up below preserves MAX semantics and native exit/deadline checks.

Picker pre-offer source refusal now retires real mapping/export/producer custody before terminal proof and exact Elm acknowledgement. The unchanged visible-owner modal journey passes normal shutdown; [evidence and remaining limits](../implementation/warlock/qa/evidence/picker-preoffer-retirement/README.md). Keep Pending/Refused/Unknown visually distinct; neither a local exception nor a closed popup proves physical completion. Broader lock/reader/AT and independent full-release acceptance remain open. The fullscreen/pin/menu follow-up is recorded below.

True fullscreen now keeps the owned bar and its window menu reachable above the app while preserving full-output app geometry and pinned-window priority. The capability-explicit **Exit fullscreen** command travels through the immutable Elm prepared menu, typed receipt router, durable journal and current native geometry guards; one committed exit restores ordinary geometry without changing the pinned peer. Actual pixels, GTK input/focus, normal shutdown and the unchanged modal/MAX regression pass in the two-root Wayland fixture. See [evidence](../implementation/warlock/qa/evidence/fullscreen-pin-menu/README.md). ELM-REN-017 remains partial: wider families/policy cells, protected-input races, transformed outputs, native AT/IME and independent acceptance remain open.

The shared modal selector now resolves current mapped family constraints before evaluating recipient eligibility. A blocked/no-focus deepest modal or ambiguous sibling set refuses instead of falling back to an ancestor. Actual unrelated-window clicks and keys preserve the modal and its unsaved typed draft; native no-focus paint remains distinct from the accepted input recipient. [Evidence](../implementation/warlock/qa/evidence/modal-recipient-eligibility/README.md) includes the original modal/MAX and unchanged fullscreen regressions with normal shutdown. REN-018 remains partial: real input-blocked modal schedules, Qt/Xwayland and wider families/races/AT need observations. That retained original taskbar Escape failure is now repaired by the captured pointer/keyboard entry policy described below.

Popup entry now records pointer or keyboard origin in the single Elm policy and preserves it through the stamped action relay and projection-only renderer. Pointer dismissal yields the bar keyboard lease before native grab teardown; keyboard dismissal retains its eligible bar parent. The unchanged native taskbar Escape assertion now observes actual GTK key receipt, and the unchanged nine-surface keyboard, modal/draft and fullscreen journeys pass normal shutdown. Origin is a UI return policy, not native authority. UI-011/UX-024 remain partial pending wider native lifecycle, AT and independent review. See [entry/return evidence](../implementation/warlock/qa/evidence/popup-entry-keyboard-return/README.md).

Native gesture ownership now waits for a current-binding idle observation before shell input, and the owning key handler preserves active move/resize across ordinary keys and shortcuts until pointer release or explicit Escape. Current two-output input checks pass both crossings, native refusal and exactly-one end; Escape cancellation also ends once. That revision retained a failed final screenshot, so UX-021 remains partial. Keyboard-only and taskbar Escape regressions pass. Caption/edge initiation, broader lifecycle/device/AT and independent acceptance remain open. See [gesture readiness evidence](../implementation/warlock/qa/evidence/pointer-ownership-readiness/README.md).


Native caption moves and edge resizes preserve their original owner, finish once on release and keep the unsaved GTK draft. Admission now rechecks the current shared family recipient and protected-input policy after the actual XDG press grant is consumed. Held presses refused after no-focus or a mapped modal cannot replay when eligibility returns. The one-output native addition, matched core/plugin rebuild, Quint checks and unchanged modal/draft regression pass. That revision retained a failed two-output capture; UX-021 and the release remain partial. See [caption admission evidence](../implementation/warlock/qa/evidence/caption-gesture-admission/README.md).

## Native gesture cancellation and retirement — October 10

Escape now restores captured floating move/resize geometry without committing a drop. Cancellation after crossing outputs also restores the live source workspace. Closing the captured owner retires the gesture before button release; a same-title replacement cannot inherit the old press. A new eligible edge press at the same pixel recovers its actual pointer recipient. The current native caption/lifecycle and modal/draft regressions pass. All original two-output input assertions and the new cross-output rollback assertion pass, with a combined-capture timeout retained from that revision. UX-021 and the release remain partial. See [native gesture evidence](../implementation/warlock/qa/evidence/native-gesture-terminal-reasons/README.md).

Maximized, fullscreen, tiled and snapped restoration, wider device/lifecycle schedules, AT and independent scenario acceptance remain open. Cancellation keeps the original owner and never uses release-time grouping or focus redirection.

## Native caption placement restoration — October 10

Native maximized and committed left-half snapped captions now retain placement on a click without movement, restore ordinary size at the original horizontal press fraction, and restore the captured box/modes/source workspace on Escape. Actual quarter- and three-quarter-width drags, one-output pixels, committed release, unsaved drafts and captured-owner retirement/replacement pass. A released MAX caption retires its exact old ordinary placement so the next maximize/restore captures the new box. The admitted restore effect now applies its saved prospective ordinary box after validating live identity/mode/scope. The final caption/lifecycle and original modal/draft regressions pass. Original two-output input and cross-output rollback assertions pass again after separating caption phase from the shared keybind threshold flag; that revision retained a combined-capture failure at the original five-second limit. UX-021 and the release remain partial. See [caption restoration evidence](../implementation/warlock/qa/evidence/native-caption-placement-restoration/README.md).

Native fullscreen/tiled/grouped restoration, the other snap regions/repeated snaps, nondefault thresholds/key traffic, constraints/scale/rotation and resize-mode placement transitions remain unqualified.

## Nested output capture demand — October 10

The unchanged original two-output move/resize journey now passes native owner retention across taskbar/output, blocked shortcut/effect, exactly-one end, Escape and source-workspace rollback, original five-second combined 1600×600 capture and cleanup. An initial live nested capture requests one real render/commit without waiting for an occluded parent callback. The same pair passes MAX/snap caption placement/lifecycle/draft regression. No parent presentation is fabricated; external hardware/AT and independent acceptance remain open. See [current recording](../implementation/warlock/qa/evidence/native-output-capture-demand/README.md).

The next GUI gap is launcher popup placement and control paint across outputs. Its blank control area in this combined image is not accepted as complete launcher presentation.


Native Apps shortcuts now open on the output of the actual keyboard recipient after a cancelled cross-output drag. The shared Elm controller resolves the press-time live output against current issued view geometry; duplicate, missing, moved, retired, ambiguous and pointer-blocked destinations cannot relocate or replay. A fresh valid shortcut clears only obsolete shortcut-refusal feedback. The original two-output drag/cancel/capture journey passes, followed by actual popup bounds, painted control pixels, physical-keyboard no-match/query/focus retention and Escape without launch or window mutation. The unchanged all-nine-surface keyboard journey passes on the same core/plugin/host tuple with normal cleanup. See [current-output shortcut evidence](../implementation/warlock/qa/evidence/shortcut-current-output/README.md). Native AT and independent acceptance remain open.


Keyboard shortcuts now resolve the actual native keyboard window, mapped shell layer or live popup before choosing an output; an unrecognized focused surface is refused. The real nested output-removal journey dismisses the displaced launcher, preserves workspace identity, keeps the typed query and keyboard recovery on a declared survivor, and operates Refresh with one observed catalog read. Reconnection at identical old bounds receives a new view identity while the retired native shortcut destination stays null. No launch/window-effect replay occurs, and original drag/capture plus all-nine-surface keyboard regressions pass with normal cleanup. See [live output retirement evidence](../implementation/warlock/qa/evidence/live-output-retirement/README.md). UI-019 remains partial pending its wider native/hardware/AT and independent obligations.


## Zero-output shell recovery — October 10

Warlock now suspends shell presentation when every real output disappears: the compositor's internal FALLBACK receives no bar, popup, reserved shell band or Apps shortcut event. A returning nested output flushes its parent initialization immediately, receives a fresh issued view after configure acknowledgement, and restores actual launcher focus, typed query and keyboard Refresh without replaying a launch/window effect. Workspace identity remains unchanged. The original two-output drag/capture journey and nine-surface keyboard regression pass on one mapped core/plugin/Aquamarine/host tuple with normal cleanup. See [zero-output return evidence](../implementation/warlock/qa/evidence/zero-output-return/README.md).

That revision retained an offscreen application placement gap. The placement recovery described below repairs the observed floating-window case. UI-019 remains partial; physical hotplug/AT, delayed fresh old shortcut/native topology ordering, pending custody/Unknown and independent acceptance remain open. Quint retirement and parent-transport models retain named scenarios, positive witnesses and sampled safety checks; neither establishes every cross-channel order or write-backpressure schedule.


## Native application placement recovery — October 10

Orphaned workspace placement now includes the destination output origin and wraps negative logical coordinates without changing window size. After the original zero-output shell journey, the returning floating application is at its original reachable x=40/y=230, retains workspace 2 and its unsaved GTK draft, activates through the actual taskbar exactly once, receives client pointer press/release and physical keyboard input, and paints onscreen. Original move/resize/cancel/capture and MAX/snap caption/lifecycle regressions pass on the same core/plugin/Aquamarine/host tuple with normal cleanup. See [placement recovery evidence](../implementation/warlock/qa/evidence/output-placement-recovery/README.md).

The original partially clipped vertical size remains unchanged; this fix restores reachable application origin and input. Smaller/rotated/scaled outputs and minimized/pinned/fullscreen/modal recovery remain unqualified. The delayed fresh old shortcut schedule described below is now observed; wider cross-channel ordering, pending custody/Unknown, physical hotplug/AT/IME and independent original acceptance remain open. The Quint model abstracts integer coordinates and atomic placement; native authority and presentation stay separately observed.


## Delayed shortcut recovery — October 10

A native shortcut reply read before output removal can arrive after a replacement view appears at identical bounds. Shortcut protocol 3 now carries the press-time native output generation. The shared Elm output controller consumes that reply without moving focus or opening a popup unless the generation matches current reconciled observations. Native add/remove signals retire a generation even when names, IDs and geometry match between reads. Unstamped legacy replies can establish/advance the serial watermark but cannot authorize root output routing.

The real nested test holds an actual validated shortcut reply, removes its output, returns a fresh view at the same 800×600 bounds, then delivers the unchanged reply through the original bounded writer. The old reply produces visible refusal without popup or window-effect replay; the next physical shortcut opens the focused launcher normally. Workspace, size and unsaved application draft survive. The existing output/drag/capture journey and nine-surface keyboard regression pass the same core/plugin/host/transport tuple. See [delayed shortcut evidence](../implementation/warlock/qa/evidence/shortcut-generation-recovery/README.md).

UI-019 remains partial. This establishes delivery after host retirement/reconciliation for the observed nested schedule. Native/host observation-before-retirement ordering, other asynchronous schedules, transformed or multiple outputs, minimized/fullscreen/modal recovery, pending custody/Unknown, physical hotplug/AT/IME and independent acceptance remain open. The Quint model separates press, retirement, topology, observation and delivery; sampled safety and compiled root results remain distinct from native acceptance.


## Reachable application area — October 10

Changing a returned output to 400×200 at a negative origin previously left the floating application's input region below the screen. Native workspace transfer and changed usable-area updates now recover the first up-to-32 logical pixels of an ordinary floating window inside the area available after shell reservations and floating gaps. Size, workspace and already reachable placement are preserved. An unchanged-area recalculation leaves deliberate manual placement alone; pinned, fullscreen and grouped targets retain their existing paths.

The observed application is reachable at (-360, -32) after the smaller-output change, with its original 108×440 size and workspace 2. Actual taskbar Minimize/Restore, client pointer press/release, physical keyboard editing and native pixels pass with the unsaved draft preserved. The original output/drag/capture journey, unchanged caption/MAX/snap/lifecycle regression and delayed-shortcut recovery pass on the same core/plugin/host/transport tuple with normal cleanup. See [usable-area evidence](../implementation/warlock/qa/evidence/reachable-output-area/README.md).

UI-019 remains partial. The recovery preserves a reachable input region; it does not fit an oversized client entirely into a smaller screen. Minimized-before-output-change, pinned/fullscreen/grouped/modal families, wider transforms/output combinations, concurrent gestures/custody/Unknown, physical hotplug/AT/IME, independent acceptance and original release/package/rollback gates remain open. Quint and compiled-helper results are separate from native acceptance.


## Minimized application recovery — October 10

A real taskbar Minimize committed before the returned output changed to 400x200 at (-400,-200). The application remained minimized across reconciliation, then a real taskbar Restore committed exactly once at reachable position (-360,-32), preserving size108x440/workspace2 and its unsaved draft. Actual client pointer press/release, physical keyboard editing and painted pixels pass normal cleanup. Existing production placement already covers this ordinary minimized case; no new production behavior is claimed. See [native restore evidence](../implementation/warlock/qa/evidence/minimized-output-area/README.md).

UI-019 remains partial. Pinned/fullscreen/grouped/modal recovery, actual retirement while minimized, wider transforms, hardware/AT/IME, independent acceptance and release/package/rollback gates remain open. This is qualification of existing behavior, not an additional feature.


## Pinned application recovery — October 10

A pinned floating application previously remained at (-360,30), below the real 400x200 output at (-400,-200). The owning changed-area placement now recovers it at (-360,-32) without unpinning or changing its size108x440/workspace2/draft. Real taskbar Minimize/Restore each submit once; actual client pointer press/release, physical keyboard editing and native painted pixels pass. The unchanged minimized-before-reconfigure and caption/MAX/snap/lifecycle regressions pass the exact tuple with normal cleanup. This advances UI-019 reachable application recovery; independent original acceptance and full release remain open. See [pinned usable-area evidence](../implementation/warlock/qa/evidence/pinned-output-area/README.md).

Pinning a native floating window keeps it visible across workspaces. That state now survives the same-monitor usable-area recovery; it does not exclude the window from recovery. This differs from a persistent catalog launcher pin. Recovery preserves size and a reachable input region; fullscreen, hidden/grouped targets, other-monitor transfers and unchanged-area manual placement retain their existing paths. Quint named/positive/sampled checks remain separate from native GUI and hardware/AT acceptance.

UI-019 remains partial. Actual pin/minimized output retirement, wider transforms/fullscreen/group/modal recovery, custody/Unknown/concurrency, hardware/AT/IME, independent acceptance and release/package/rollback gates remain open.


## Pinned output retirement — October 10

Pinned applications now preserve workspace2, size108x440, pin state and the unsaved draft through the original first output removal, replacement, all-output disappearance and fresh return. Owning workspace migration avoids retired-owner gap callbacks and pinned stay-behind paths; the existing native authority permits explicit same-output navigation to the preserved workspace before pin focus. Actual taskbar Activate/Restore and native pointer/keyboard/draft/pixels pass for pinned and previously minimized applications. Real cross-output pin activation remains Refused without transfer; a live-monitor workspace move retains the pin on its old output. The prior pinned smaller/negative-origin journey passes the exact tuple with normal cleanup. See [native retirement evidence](../implementation/warlock/qa/evidence/pinned-output-retirement/README.md).

A native floating pin follows its preserved workspace when its output retires; moving a workspace from a live output keeps the existing pin behavior. Recovering the pin through the taskbar may explicitly select its preserved workspace on the same output before focus. Another focus output still refuses to avoid implicit membership transfer. Existing membership, recipient, output-generation and Unknown/no-replay guards remain in the admitted effect path.

UI-019 remains partial. Hardware/AT/IME and independent acceptance, fuller transformed/fullscreen/group/modal/custody journeys, the separately observed taskbar activity-cue issue and release/package/rollback gates remain open. Sampled/named models and native evidence are distinct.

## Taskbar activity after output retirement — October 10

After real output removal/replacement, an invisible workspace member now offers Activate/Open rather than Minimize/Active. Actual taskbar Activate, Minimize and Restore each commit once, with native frames showing 27,048 red application pixels after activation/restoration and zero after minimize. Workspace2, size108x440 and the unsaved draft survive; actual client pointer and physical keyboard editing pass. The unchanged keyboard primary journey passes MRU/desktop succession, and pinned retirement/return plus cross-output/live-owner guards pass the same tuple. See [the exact observation packet](../implementation/warlock/qa/evidence/taskbar-output-focus/README.md).

The Active cue refers to an eligible visible desktop family. A bar or popup holding keyboard custody keeps that family active; an invisible member remains available for explicit activation. The existing adapter filters only the action projection's focus from coherent native facts. It does not change raw native focus, window membership, effect admission or replay policy.

UI-004 remains partial: applicable native AT and independent acceptance are still required. Sampled Quint/model results remain separate from actual native observations and release acceptance.

## Single-family taskbar native accessibility — October 10

Actual private GTK/WebKit AT-SPI and Orca now qualify the focused single-family Activate/Minimize/Restore fixture. Five real AT-SPI press actions each commit once, with native focus, MRU/desktop succession, client keyboard recipients and painted/absent application frames preserved. A separate physical-Enter journey passes under actual AT observation. All current taskbar names, native active toggle states and focused controls agree with Orca; the real reader emits Activate/Minimize/Restore names. This verifies existing product behavior; no production code or ABI was changed. See [the exact AT observation packet](../implementation/warlock/qa/evidence/taskbar-primary-at/README.md).

Original UI-004 inactive/active/minimized scenarios remain partial pending independent acceptance. The fixture observes the actual current AT tree before the unchanged physical frame assertion; AT-SPI action acknowledgement alone is not a paint acknowledgement. Original waits and policy remain unchanged. This does not qualify grouped/zero/refusal taskbar AT, audible speech/braille or the whole release.


## Visible taskbar refusal recovery — October 10

The taskbar now puts its existing read-only recovery control first when recovery is needed. The actual Refused frame moved it from x803 outside a 540px action region to x1, width120. Real other-output activation receives one native implicit-transfer-required Refused receipt; pin/workspace/geometry/draft and peer focus remain authoritative. Actual peer keyboard input is preserved before recovery. Clicking the visible recovery issues observations without retry or launch. Current browser and native Pending/Refused/Unknown regressions pass with normal cleanup. See [the exact refusal and recovery evidence](../implementation/warlock/qa/evidence/taskbar-native-refusal/README.md).

Recovery keeps the same identity, accessible label and typed observation-only action. Pending recovery remains disabled; Refused and Unknown retain their native outcome and no-replay policy. Visual feedback stays readable with aria-live off while the existing scoped single announcer owns live reporting. This layout change adds no effect authority or new Quint model; unchanged applicable models ran in the compiled build.

Original UI-004 taskbar-refusal is partial. Primary keyboard/AT refusal, independent acceptance, already-scrolled dense arrangements and release-wide hardware/resource/package/rollback gates remain open. Next: the original zero-window pin primary keyboard journey.


## Stable launcher typing and zero-window keyboard launch — October 10

Typing in the launcher now survives the gap between an accepted Elm publication and its preceding DOM frame. Popup-owned field callbacks preserve bounded text within the same lease and rebase only read-only query messages; external edits/buttons remain publication-strict, and replacement leases retire drafts. The original native pin/reorder/restart journey passes. Physical Enter and real AT-SPI press each launch the zero-window Editor pin once through GIO. Its observed running family then minimizes/restores without another launch, receives actual client keyboard input and paints 268,432 green pixels inside its native window region. Both private native campaigns exit normally. See [the exact native and model evidence](../implementation/warlock/qa/evidence/taskbar-zero-keyboard/README.md).

Input text belongs to its current field lease. The popup distinguishes its own Html callbacks from the external action port; this preserves local typing while ordinary captured actions retain exact-publication checks. The repair uses quint-llm-kit, with executable initialization, seven named positive/negative scenarios, sampled safety runs, fifteen compiled field assertions and the unchanged IME/browser regression. No native ABI, effect admission or Unknown/no-replay policy changed.

Original UI-004 taskbar-zero remains partial pending independent acceptance. The fixture does not qualify every application/AT mode or pin/reorder popup paint. Next: original UI-005 search-race with a genuinely delayed old catalog refresh, current query/selection, native pixels and applicable AT observations.
