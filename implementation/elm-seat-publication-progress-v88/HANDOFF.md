# AQ seat publication V79–V88: progress, native stationary-input gate open

V79 changes only `src/backend/Wayland.cpp` from frozen AQ V30. Keyboard and pointer
announcements capture weak backend/device references. At callback execution they
require the exact device in the current backend vector, a live ready owning core,
and a healthy specific parent Wayland display. No public header, class layout or
vtable changes. Existing cursor, output, configure-generation and presentation
source is byte-identical. The complete library builds and preserves every prior
exported symbol. No installed desktop was changed.

The original `initSeat()` callback body, compiled with real Hyprutils shared/weak
pointers and typed protocol/event fixtures, reproduces stale publication and
late destruction after capability removal. The guarded body passes 28 checks
and rejects five compiled mutations, including retained retired objects, missing
membership, ready/transport checks and a strong pointer capture. The source-body
replay covers both keyboard and pointer callbacks, weak backend/core retirement,
independent capabilities, bursts and reentrant listener retirement. The fresh
Quint abstraction explicitly executes 10 named cases and 1,000 seeded invariant
samples of up to 40 steps, rejecting seven typechecked mutations. These are
bounded ordering/ownership results, not complete native refinement.

V80 adds protocol-3 `pointer-burst CYCLES FINAL` to the reviewed private Weston
fixture. One server callback queues 1–16 balanced release/init cycles before the
parent event loop resumes. Original capability/input/UID/exclusive-controller
paths remain. V81 fails because the server global still advertises version 2;
V82 corrects that single advertisement in a fresh fixture and recompiles. V83
then exposes an invalid observability assumption: default core logging hides
publication messages. Its failure remains. V86 enables only private diagnostic
logging and calibrates it against one actual device recreation before counting
announcements. Neither observation deadlines nor physical recipient oracles are
extended or removed.

V86 reproduces the real native defect on original AQ V30: three remove/restore
cycles ending without a pointer deliver seven parent capability events and
**three retired-pointer announcements, where zero are required**. Cleanup passes.
This confirms that the original strong queued references announce retired devices.

V87 on guarded AQ V79 and unchanged owning core V72 observes the required zero
announcements for final-off and exactly one for four cycles ending enabled. Its
first restored GTK physical pair succeeds. The second pair, with the parent
pointer at the same coordinates across capability retirement, fails the original
six-second deadline. Actual parent pointer enter and both button events appear
on the child wire, but GTK receives neither physical event. Retain this failed
campaign; the third 16-cycle case is not executed and the complete burst campaign
is not accepted.

The original V76 held-button/capability/full-cover focus-layout and stationary
reentry oracle runs fresh in V85 on V79 AQ, unchanged V72 core and V82 parent
fixture. All **159 original check identities** pass with normal ordered cleanup.
This narrower pass does not cover the newly exposed unchanged-coordinate device
replacement and does not complete any S01–S16 or release gate.

## Immediate next implementation

The actual core InputManager object originates from minimize-lifecycle V14:
`build-1791060004170871924/inputs/src/managers/input/InputManager.cpp`, SHA-256
9aadada4f359a7a8208570147a8ab1d2ad4b49d3ab8787f4c1ef9f00f1fd059f.
Its `onMouseWarp()` routes the absolute point then calls `mouseMoveUnified()`.
The latter returns early for the same floored point without explicit refocus.
V72's parent warp listener records the new device/output but does not refresh
normal hit testing when a new source enters at the unchanged coordinate. This is
the source-supported explanation of V87's missing stationary recipient delivery.

Add a narrowly guarded ordinary hit test for a new live parent device/output
anchor, without making every warp or ordinary window commit steal programmatic
focus. Extend the iterative model and actual callback replay with retirement,
replacement at the same point, first-enter, normal subsequent motion and preserved
programmatic restore focus. Rebuild a coherent core/plugin and rerun V87's exact
original physical recipient/deadline oracle, original159 and original menu68.
The original V87 failure must stay. Do not move the pointer solely to make the
stationary case pass.

The geometry integration worker already owns `elm-geometry-monitor-core-v72`
and its fresh V73 derivative; preserve them. Its merge carries V72 pointer/reload
plus V40 desired-state MAX and XDG limit changes. Handoff the new small parent
warp correction and guarded V79 AQ into that integration rather than replacing
its complete Window.cpp. Adopt only after an exact recorded owning ABI/plugin
and mapped library tuple passes native regressions.

Native configure-generation fencing, parent transport retirement, multiple
physical outputs/rotation/hotplug/zero-output, GPU, AT/IME, durability/global
revocation, restore timing, resource/soak budgets, full requirements audit,
reversible deployment and required activation authorization remain open.
The automatic project goal remains active; no deployment or publication occurred.
