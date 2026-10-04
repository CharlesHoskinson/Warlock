# Trusted host native popup observation

Fresh592-derived C host source. Existing renderer, native admission, surface gate,
backend, effects and close ordering are unchanged apart from read-only lifecycle
observation hooks. No installed desktop change or native/effect acceptance.

An owner GTK callback may record a mapped popup only when the current active
OutputView owns the bar, the current view/generation still resolves, topology is
current, the original publication/lease/configure/presentation/focus/grab checks
pass and a validated backend binding exists. Popup/root IDs come directly from
actual GdkWayland windows and wl_proxy_get_id; neither ID is accepted from WebKit.
Both widgets must be mapped on the same GDK display with distinct positive IDs.
Actual PID and kernel /proc/self/stat start time identify the process. A random
host-instance UUID scopes diagnostic sequence/map counters, not a secret/grant.

Records contain process, instance, sequence, local map generation, current view/
generation/topology/publication/lease, popup/root IDs and copied backend binding.
Duplicate observations compare every identity field and binding. One cached
packet is retained; no queue. JSON output is bounded to65536 bytes, counters
refuse exhaustion and invalid observations emit no success record. Local map
generation distinguishes observed lease/resource/scope transitions; it does not
prove an unobserved native resource unmap/remap lifecycle by itself.

Before original popup_hide mutates flags or destroys its wrapper, a cached
record can be marked retiring only after current owner/view/topology/pub/lease,
binding and actual popup/root surface IDs match again. After original native
destroy and gdk_display_sync returns, that historical record is emitted once as
host-popup-sync-complete and cleared. Scope-retired/unavailable identities cannot
be upgraded by an old cache. This is an observed host display-sync completion,
not a fresh compositor capability or current grant. The kernel parser correctly
handles whitespace/closing parentheses in comm and rejects absent, overflow,
zero and noncanonical start times.

## Open coherent integration gates

The hook logs diagnostic records. No new renderer method or authority wire is
introduced. A controller-issued current Menu ID/full window target stamp, native
session/read correlation and authenticated host-to-native request transport are
still required. Exact server wl_client identity, popup/root relation, XDG grab
owner (307), all live accepted members (305), negative lock/exclusive/drag/modal
causes and structural field normalization must be independently joined. Same-PID
multiple Wayland client connections remain ambiguous from numeric IDs alone.
The host UUID is not native connection proof. Cached binding/history is never
rebased to new reads; Unknown reservations and native effect guards stay intact.

Do not adopt these diagnostics as303 authenticated Host/Native inputs. Actual
close/resource/grab retirement, separately correlated fresh action/geometry
facts, controller/ReceiptRouter integration and original GTK02/fullGTK/Qt native
deadlines remain mandatory. GDK display-sync completion does not replace them.

## Evidence scope

Full actual changed shared-host.c compiles with strict warnings against installed
GTK3/WebKitGTK/layer-shell/Wayland client libraries. Existing host self-tests,
geometry-carrier, shared-context, context-key and surface tests run unchanged.
Additional compiled identity controls cover actual kernel start parsing plus
forged/missing scope/native facts and valid-but-changed identity comparisons.
These tests do not create a mapped GDK window or observe real popup retirement.
Earlier builds and captured input states remain retained after later corrections.

References consulted: GTK3 Wayland backend guide
https://docs.gtk.org/gtk3/wayland.html and GDK display sync API
https://docs.gtk.org/gdk3/method.Display.sync.html . The actual installed GTK3
gdkwaylandwindow.h and wayland-client-core.h are captured compiler dependencies.
