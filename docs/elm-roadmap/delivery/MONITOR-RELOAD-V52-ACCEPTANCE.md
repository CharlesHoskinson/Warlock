# Monitor reload progress under parent cover V47–V52

The V44 fullscreen-parent-cover failure is corrected in a fresh owning core.
Scale changes now complete while the parent cover owns pointer focus, and an
unchanged parent pointer point reaches the correct GTK child coordinates after
re-entry. The original six-second deadlines and recipient assertions remain.
The installed desktop/compositor was not replaced.

## Source correction

The owning CMonitorRuleManager previously applied a scheduled rule only from
render.preChecks. A nested parent may withhold frame callbacks while its surface
is covered, so a configuration request could remain queued despite IPC being
responsive. V47 schedules the existing rule application on the existing Wayland
event-loop idle queue. The scheduled flag coalesces pending requests; the render
listener still supplies its fallback. Startup without an event-loop manager
retains that fallback, and queued idle work refuses application during shutdown.
The callback resolves the singleton when it runs, retaining no raw manager
pointer or additional public class fields.

The pending flag is consumed at the start of ensureMonitorStatus, before its
callbacks. Clearing it after application or unconditionally after the render
listener could erase a request made during application; those trailing clears
are removed. Reentrant requests therefore remain pending for a subsequent
application. No Aquamarine scheduler, page-flip, buffer-release or frame-callback
implementation was modified to force rendering while hidden.

The exact core changes only MonitorRuleManager.cpp.o relative to accepted V31.
All 432 other ordered archive payloads are byte-identical, including the previous
cursor extent and parent-coordinate corrections. Original owning source/object,
ancestor archive/binary, compiler inputs, dependencies and link command remain
archived. Existing public class headers are unchanged. V49 freshly rebuilds the
unchanged authority against its owning headers and freezes the exact pair.

## Model and CPU evidence

V48 executes six explicitly selected Quint scenarios: coalescing, idle progress
without a render event, render winning without duplicate application, requests
made during idle/render application, and shutdown refusal. A separate seeded
run checks safety for 1,000 samples of up to 40 steps. A typechecked mutation
that clears pending state after application fails its reentrancy scenario.
This models serialized dispatch bookkeeping, not actual monitor/DRM behavior.

V47's extracted scheduleReload body, render-listener body and actual consume
prefix pass 14 typed C++ fixture checks, including absent event-loop startup and
absent/shutting-down compositor guards. The late-clear production mutation is
rejected independently. The fixture stubs the monitor application body; only
the actual compiled core and native campaigns qualify live monitor behavior.

## Native qualification on one exact tuple

- V50: 159 checks pass. It retains the original held-button and capability-loss
  campaigns, then the original V44 full-cover focus/layout/re-entry oracle.
  Both scale 1→2 and 2→1 finish while the parent GTK cover owns focus. Actual
  cover press/release receipts and child wl_pointer.leave establish ownership;
  cover clicks do not reach the child. The saved child anchor is not replayed
  while unfocused. The parent cover exits normally, an actual enter returns to
  the child, and a press/release with no intervening motion reaches the expected
  GTK recipient and coordinates. Those returned coordinates are 179,129 at
  scale 2 and 379,279 at scale 1 in this campaign.
- V51 cursor/stationary input: the original 195 checks pass, including actual
  parent framebuffer cursor extent/hotspot/blank/movement captures and unchanged
  parent coordinates after geometry and scale changes.
- V51 Elm menu: the original 68 checks pass, including effect receipts, geometry
  reflow and the exact rebuilt authority's live mapping.

All three native campaigns pass normal ordered cleanup. The binary tuple is:

- Core V47 build-1791101203494513446, SHA-256
  e79a49fb34b2f3b80b81f61ba62ea9042e7a0c3fe5f4b614fe6544c1d1a61c20.
- Authority V49 build-1791101265875994365, SHA-256
  f1bba468e10cf91ae276e0ca3f890cbdb9282819bd75dfb2871056cff7494f1e.
- Unchanged AQ V30, SHA-256
  1763ba3b38832b67ed70d9470661cdc18073ca0924f1ef962ffcbf61cf754ff5.

The unchanged authority happens to reproduce the earlier plugin binary hash;
its fresh compile/header closure and owning pair descriptor are nevertheless
recorded and its new path is verified in native mappings. V50's copied AQ
descriptor retains an old compatibility text label; actual binary descriptors,
library hashes and mappings bind this run to V49/V30, and V52's authoritative
tuple uses the current V51 descriptor. No acceptance is inferred from that label.

V52's protected freezer verifies source/artifact hashes, owning pair, actual
native mappings, models, checks and cleanup, and archives 905 files. The 422
native check executions are bounded campaign counts, not 422 distinct roadmap
scenarios. V44/V46 failures and V45's historic failed-focus assessment remain
unchanged; they are superseded only for the V50 cases actually rerun here.

## Remaining release work

This closes the bounded full-cover reload-progress and pointer re-entry defect.
It does not establish every hidden-renderer, physical display, DRM reload or
multi-output case. Native parent configure/generation fences, queued backend
publication/callback retirement, multiple outputs/rotation and physical transport
loss still need evidence. The pointer/reload changes need integration with the
latest reviewed geometry and shared-shell source in one coherent owning build;
do not mix frozen plugins with a different compositor ABI. AT/IME, measured
budgets, original user journeys, the full S01–S16/right-click/C00–C06 acceptance
audit and reversible deployment remain open. The automatic goal remains active.
