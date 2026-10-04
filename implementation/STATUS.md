# Implementation status — 2026-10-03

Research used three agents and online primary sources fetched with Scrapling. This directory contains fresh derivatives; archived sources and historical acceptance packets are unchanged.

| Component | Status | Evidence / remaining work |
| --- | --- | --- |
| Application metadata cache | Implemented and enabled | taskbar-v3: 24 tests; synthetic benchmark; desktop-file semantics preserved |
| Shared coalesced taskbar observation | Implemented and enabled | taskbar-v3: 45 watcher / 15 unchanged backend checks; actual Qt lifecycle probes; five Quint scenarios / 2,000 traces; real selected-compositor smoke |
| Capture phase profiling | Implemented, staged | capture-profile-v30: seven tests; instrumentation is opt-in and hash-bound; integrate with original native campaign before drawing performance conclusions |
| Independently retained client frames | Implemented prototype, staged | retained-frame-v1: QML lint; source-stop survival and native pixel/family acceptance pending; stock capture excludes decorations and clips popup extent |
| Acknowledged command consolidation | Open | Existing native helpers and action routes retained; observation epoch does not acknowledge native mutation |
| Native hook/ABI simplification | Open | Exact deployed compositor/plugin left intact; requires broader native acceptance |
| Maximized floating stacking | Built and privately tested; activation pending | maximized-stack-v2: built exact native pair; seven isolated rendered pixel/click/pin/max-state checks passed; verified package and session wiring prepared. Activation/restart and broader original regression coverage remain pending |
| Alt-release before switcher readiness | Correction staged | switcher-v1; separately discovered timing race, not established as Brave's reported symptom |

Full parity remains incomplete. Existing original gates remain: hidden restore baseline/fault recovery at unchanged deadlines; pin/input campaign including B11–B24; real popup/runtime-source projection and reliability acceptance; exact source closure/freezing; minimized previews; no-scratchpad minimization semantics; broad multi-output/modal/input/render coverage. See historical `docs/HANDOFF.md` for detailed original state. These entries do not promote CPU/model results into native acceptance.

The first taskbar attempt was rolled back after discovering refresh feedback. v1 evidence remains intact; corrected v3 is installed with verified rollback backup and a fresh widget URL. No main-compositor restart, native-plugin replacement or user-window closure was performed.
