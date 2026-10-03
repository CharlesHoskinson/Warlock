# Window behavior model

See [requirements.md](requirements.md) for the Windows 11 behavior audit and the implementation status on this desktop.

`window.qnt` is a one-window contract for normal, snapped halves/quarters/thirds/asymmetric splits, maximized, and minimized states. It also models focus, pinning, three workspaces, saved normal geometry, the drag lifecycle, saved normal geometry, direct chooser selection, and logical-width-dependent layout families. The coordinates are abstract screen units. A top-edge release maximizes the window; left/right releases snap it. Moving over an edge only changes the drag candidate.

The invariant `allProps` checks state coherence, snap timing and count, geometry restoration, focus-change cleanup, and pinned/workspace visibility. `window_test.qnt` walks ten named regression scenarios, including dragging snapped and maximized windows away from their edges.

Run from this directory:

```bash
quint typecheck window.qnt
quint typecheck window_test.qnt
quint test window_test.qnt --verbosity 1
quint run window.qnt --invariant allProps --max-steps 100 --max-samples 2000 --seed 20260930 --verbosity 1
```

The simulator explores bounded random traces. This model is a behavior specification; it does not exercise live Hyprland configuration or prove equivalence with an implementation.

## Multi-window and desktop QA

`desktop.qnt` adds address-targeted focus and pin actions, distinct persistent app
pins, app taskbar grouping, minimized windows, group recall, closed-window cleanup,
workspace moves, and disjoint Snap Groups with halves, mixed half/quarters, or
four quarters, three thirds, or asymmetric 2/3+1/3 splits. `desktop_test.qnt` contains ten regressions. `navigation.qnt`
adds minimize batches, Shake, Peek, Show Desktop, Alt+Tab commit/cancel, bounded
virtual desktop creation/closure/moves, per-desktop Show Desktop and minimize batches, and modal child focus; sixteen scenarios are
in `navigation_test.qnt`.

Run the complete reproducible suite with:

```bash
./qa.sh
```

The suite typechecks all included Quint models and their scenario modules,
runs named scenarios and 2,000 seeded random traces per model, and exports
trace artifacts under `qa-traces/`. Latest counts and results are in [QA.md](QA.md). It
and replays exported desktop traces against the actual `hypr-taskbar` and
`hypr-snap-groups` backend functions using isolated temporary state and mocked
compositor clients. It then runs Lua geometry, drag, vertical maximize, Shake, Snap Bar, and pin
regressions against the installed configuration sources, menu/adjacent-resize tests,
and the desktop/taskbar integration suites. These harnesses import
source behind mocks and do not change live desktop state.

`mbt_desktop.py` checks exact app/window/pin sets and taskbar reorder commands;
for Snap Groups it checks disjoint slots, unique membership, window identity,
workspace and monitor cleanup, preserved minimized members, four-quarter and third groups,
and the actual recall CLI's addressed restore/eval commands. The abstract model
permits explicit group creation; the backend automatically creates maximal
groups. Replay therefore checks group safety and target membership rather than
claiming exact equivalence of group IDs or automatic grouping order.

See [QA.md](QA.md) for executed results and remaining limits. Navigation tests
specify intended behavior; they do not establish that every navigation feature
is wired in the desktop. The navigation model abstracts MRU ordering, monitor
selection, desktop reorder/adjacent fallback, and application-specific modal
protocols. Visual layout, capture freshness, popup timing, animation quality,
and application compatibility require live checks.

## Overnight execution

An active continuation goal tracks this work. [Current status](PARITY_STATUS.md)
and [acceptance checklist](requirements.md) determine closure; a passing model
alone does not close a native interaction requirement. Native GUI trials run
serially with a single owner. Offline model, source and copied-app layout work
can run concurrently. Every native fixture must preserve original clients,
focus, cursor, desktop catalog and accessibility connection. Main compositor
restart and physical hardware checks remain separate acceptance gaps.

The current sequence is: repair and verify active minimize reversal, complete
Qt/GTK/maximized/modal animation checks, validate and deploy compact Files GUI,
finish recovery edge cases, then run the full Quint/fuzz/backend suite against
the accepted installed sources. Failed attempts and rollback artifacts remain
available alongside successful reports.
