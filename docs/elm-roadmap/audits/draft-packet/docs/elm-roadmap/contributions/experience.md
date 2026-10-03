# Elm shell experience roadmap contribution

The product target is a complete Elm desktop shell on a native Wayland host,
initially retaining Hyprland and its native window authority. Windows parity is
bounded by the explicit interactions below: left taskbar, launcher, groups and
jump lists, previews, minimized identity, focus/highlights, switcher, Task View,
workspaces, pin/MAX/modal behavior, snapping, gestures, menus, settings,
notifications, accessibility and Files integration. This is a roadmap, not an
acceptance claim. The archived handoff says full parity remains incomplete.

The accompanying `experience.json` supplies 35 EARS requirements and scenario
seeds, ELM-UX-001 through ELM-UX-035. Their phase marks the first required delivery
gate, not permission to omit later regression. All 35 become explicit acceptance
rows; the optional Files replacement row is conditional on a separately approved
migration. Existing evidence identifies inherited behavior and open failures,
not proof that the Elm implementation already passes.

## Product boundary and component ownership

Elm owns the normalized catalog projection, taskbar grouping/pins, highlights,
selection models, launcher/search, jump lists, Task View, snap choice, menus,
preferences and accessible views. Use model/update/view and typed messages,
not historical Signals. A canonical policy owner supplies output projections;
separate output views cannot independently commit conflicting window effects.

Native components own application identity/incarnation, modal relations, actual
focus and input eligibility, stacking, configure/resize, workspace transfers,
global chord capture, layer/popup surfaces, IME integration, accessibility export,
frame capture and motion presentation. The DOM never creates or replaces Brave
application windows. Application drafts remain application-owned. Pin and MAX
presentation derives from committed observations; an optimistic icon does not
prove that paint order, pointer hit order and focus agree.

A preview view accepts opaque identity/revision-bound assets. Minimized windows
retain taskbar identity and native workspace semantics, with historical previews
explicitly marked. Missing frames display the correct icon/title fallback.
Preview transport and native clocks remain outside Elm pixel serialization.

Files integration first invokes `omarchy-files` and reuses its running window.
A standalone Elm Files app is a separate optional scope, not a prerequisite for
replacing shell QML. Its adapter must preserve the installed Quint file-operation
contract: no overwrite, collision suffixes, trash rather than destructive delete,
exit-code handling and permission authorization. Before future `ops.sh` semantic
changes, update the actual installed specification first, run its model-based
suite, and reinstall the accepted root-owned adapter through askpass as required
by the repository instructions. This documentation performs none of those actions.

## Delivery sequence

| Phase | Product slice | UX evidence required to advance |
| --- | --- | --- |
| P0 | Inventory all shell surfaces, supported chords, app fixtures and rollback destinations | Freeze scope and current-shell screenshots, native observations, accessibility tree and deadlines; record unavailable coverage explicitly |
| P1 | Native host vertical slice with taskbar/switcher, keyboard journal, accessibility bridge and IME field | Isolated Wayland evidence for real roles/input regions, pre-ready Alt release, Orca tree, composition/candidate UI and host restart; browser replay alone is insufficient |
| P2 | Canonical identity, family, focus, pin/MAX and workspace policy | Elm replay/model tests plus native painted/hit/focus agreement for overlap and modal fixtures; preserve staged native stacking correction as independent work |
| P3 | Left taskbar, catalog, pins/groups, highlights and complete switcher chord reducer | Group membership, identity reuse, forward/reverse selection, Escape cancellation, release-before-ready and refused effects pass; minimized restore never uses scratchpad |
| P4 | Retained previews, motion, gesture ownership and reduced motion | Original restore38/recovery34 and 52 drag/resize cases retain deadlines and identities; source-stop frames, reversal and cross-output gesture tests have native recordings |
| P5 | Entire shell: launcher/jump lists, Task View, snap chooser, settings, themes, notification center, system menus and Files launcher | Every surface can be reached, operated and dismissed by keyboard; adapter refusal, stale actions, output changes, persisted settings and accessibility fixtures pass |
| P6 | Coherent product release | One frozen source/ABI tuple passes inherited campaigns and all enabled new surface scenarios; native speech/braille evidence and rollback rehearsal are retained |
| P7 | Optional compositor feasibility | Reuse this scope as compatibility obligations; separately inventory protocol, seat, output, capture, Xwayland and application gaps before choosing replacement |
| P8 | Optional compositor implementation | Repeat the entire shell interaction matrix on the new native authority; shell acceptance on Hyprland cannot transfer automatically |

P1 is a product gate: reject a host choice if it cannot export native accessible
roles/states, route composition/candidate UI, or journal global chords before
webview readiness. Evaluate GTK/WebKit and Qt/WebEngine using the research
boundary, without claiming either is faster or less expensive. Freeze measured
baseline budgets before running comparative experiments. Surface migration can
proceed incrementally only while there is one authoritative policy/effect owner.

## UX acceptance and fixture matrix

Run pure Elm reducer/decoder replay first; use concrete window identities and
expected receipt sequences, including refusal and cancellation. Native acceptance
then exercises the same scenario against real surfaces and application windows.
Each record links source hashes, ABI tuple, input sequence, native observations,
presentation evidence and explicit pass/fail. Run GUI campaigns serially through
the protected launcher in `docs/HANDOFF.md`; preserve original timeouts and failed
packets. Nothing in this contribution licenses main-desktop restart or draft closure.

The minimum fixture set includes a maximized Brave draft/modal family, unrelated
terminal, multiple windows of one application, minimized window with retained
frame, expired preview, closed/reused identity, genuine native input blocker,
two populated workspaces and two outputs with different fractional scales and
negative coordinates. Test supported GTK/Qt/Xwayland family cases according to
the frozen compatibility inventory. Include output removal during snap/drag,
fullscreen and pinned overlaps, rapid chord repeats, Alt release before readiness,
Escape before commit and shell restart with uncertain effects.

Keyboard and assistive acceptance covers launcher search, taskbar groups,
switcher, Task View, chooser, menus, notification actions and settings. Publish a
single chord map; verify focus scope, visible focus and return target. Native
Orca speech and braille output must agree with selected identity, not only DOM
attributes. High contrast and enlarged text use frozen supported scale fixtures.
IME tests preserve preedit/candidate interactions and send a launch only after
explicit text commit and action. Notifications and jump lists bind actions to
current identities so expired entries cannot act on reused objects.

## Limits on completion claims

Existing taskbar-v3 tests establish catalog/watcher work, not Elm shell acceptance.
The switcher-v1 release-before-ready correction is staged. Maximized-stack-v2
bounded native checks do not close all pin/input cases. V29 CPU results do not
replace restore native baseline/fault recovery. Audible/braille and broader
hardware/multi-output coverage remain open in the handoff. The roadmap retains
these as release work rather than assuming language migration resolves them.

“Complete Elm GUI” means every surface in the P0 shell inventory has an Elm view
and accepted native integration. It does not mean Elm implements DRM, the Wayland
server, GPU lifetime, app toolkits or the compositor. Native compositor replacement
is separately conditional; third-party application UI and an optional Files app
rewrite are outside the default shell rewrite.
