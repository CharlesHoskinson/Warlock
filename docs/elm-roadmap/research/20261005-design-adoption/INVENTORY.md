# Current design inventory

This is a frozen research input, not an acceptance report. See source-manifest.json for exact bytes and lane-checkpoints.json for observed coordinator state. Old active labels do not establish live processes.

## Architecture

- Modern Elm Architecture, not historical Elm Signals: immutable models, typed messages, pure update transitions, derived views, commands/subscriptions.
- One authoritative controller; bar/popup projections. Native owns Wayland/input/window effects/pixels/authentication/native monotonic clocks/physical retirement. Narrow JS/JSON ports and Python effect endpoint.
- Lossless uint64 counters, compositor lifetime/frontend epoch/window incarnation/output/source revisions; strict decoders and receipt-driven Pending/Committed/Refused/Cancelled/Unknown outcomes. Uncertain operations are reconciled, never automatically replayed.
- Typed preview lifecycle with cancellation, admission, producer/consumer ownership, authorized opaque URI/GIO stream, cleanup receipts/final acknowledgements and replay floors.
- Quint named models and bounded sampling; selected real compiled Elm/C++ state-and-command replay and sanitizer/mutant controls. Separate model/CPU/native/hardware/AT evidence.

## Evidence and remaining limitations

- Full preview lane GUI509 uses optimized Main/bar/popup, shared preview dispatcher and authenticated descriptor hello. Native513 proves fallback popup labels, pointer open/close and normal owned-process cleanup. It does not install the production preview provider or qualify its image ownership/drain in the full GUI.
- Native source492 follows root-surface commits with scoped context; root monitor-plane route explicitly has previewEligible:false. Private capture/render evidence does not establish production client/family/decor/modal/subsurface/color fidelity.
- Producer-refusal model516 and actual broker517/qualification520 cover release of an unadopted reservation and racing cancellation; they do not qualify production integration. Provider519 remains unfinished and is deliberately not supplied as an accepted implementation.
- Primary GUI814 and toolkit391 are separate source/ABI lanes, supplied for interface review only. Never cross-load ABI artifacts or infer their release acceptance from these source snapshots.
- Five earlier actual Opus5.5/high reviews yielded44 findings/12 tasks. Their workplan is preserved as a dependency and duplicate baseline.
- Native preview scenarios13, restore38/recovery34, original deadlines, drag/resize52, multi-output/hardware/AT/IME, performance/resource budgets and one coherent reversible release remain required.

## Scope rules

- Existing frozen242 requirements/417 scenarios, S01-S16 and right-click amendment remain unchanged. C00-C06 compositor replacement is conditional. No new advice is accepted native behavior.
- User removed Brave/Heroic-specific repair targets; representative generic application compatibility remains. Historical docs retain those examples; do not reintroduce named app repair scope.
- Research only: no main compositor restart, installed config writes, GUI campaigns, secret access, source edits or publication by reviewers.
- New drafts must map each recommendation to current requirements/workplan, distinguish duplication versus new behavior, cite primary academic/open-source evidence, include tradeoffs and falsifiable acceptance. All implementation tasks stay unchecked.

## Ten review assignments

Each topic is independently examined by Sol6.1 and Opus5.5: (1) immutable state/replay, (2) typed events/effects/protocols, (3) errors/diagnostics/recovery, (4) UX/UI/accessibility, (5) fluid interaction/presentation/performance. A second review round must address a shared candidate matrix with explicit votes and dissent; coordinator synthesis alone is not unanimous consensus.
