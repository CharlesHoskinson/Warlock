# Standing architecture review and refactor track

User requested this track on October 29, 2026 as part of the existing completion loop, alongside the twelve team roles. The full original 242 requirements / 417 scenarios remain the delivery objective. This document records the review process; it does not declare an adopted target architecture or accepted implementation.

## Ownership and coordination

Astra (`/root/astra_architecture`) supervises architecture synthesis. Sol (`/root/sol_lead`) coordinates the five existing Terra implementation threads and five existing Quint companion threads through authenticated AgentBus. The roadmap fidelity role (`/root/roadmap_fidelity`) checks original requirements and sprint progress. These are the twelve existing team roles; Astra is an additional architecture supervisor and root remains the integration/QA executor. Report actual process status and completed work; do not infer perpetual execution from a role assignment or restart threads merely to maintain a count.

Resume completed threads for useful concrete assignments after verifying their previous processes are terminal. Preserve in-flight work, private proposals and independent review. AgentBus carries assignments, scope changes, findings and protected-QA HOLD/RELEASE notices. No new daemon or timer is implied: the active host goal drives continuation.

## Required review output

- Study primary GNOME and KDE architecture sources and cite exact documents: shell/compositor separation, scene/presentation ownership, services, application integration, input, extension boundaries and lifecycle. Distinguish current documented behavior from historical designs and proposals.
- Map the actual current Warlock integration roots, Elm reducers, commands/subscriptions, native effects, preview capture/presentation, storage, packaging and runtime dependencies. Graphify guides navigation; verify findings in source and record partial extraction limits.
- Explain which lessons fit Warlock and which do not. Define concrete FRP/Elm state, event, effect and subscription ownership, with one authoritative policy for each responsibility. Presentation-only Bar/Popup roots must not become competing policy authorities.
- Produce a target dependency/ownership graph, an architecture decision record with tradeoffs, and a staged migration plan. Select the first reversible production change with exact paths, original scenarios, model correspondence and proportional verification. Folder moves, diagrams or review counts alone are not a delivered refactor.
- At each implementation sprint, reconcile findings and decisions with the actual source and record adopted, rejected and deferred recommendations with reasons and evidence. Keep README and the living wiki current when behavior, build or deployment changes.

## Product invariants

The Windows-like interaction target remains binding. Preserve original taskbar zero/single/group semantics, activation/minimize/restore, explicit new-instance behavior, persistent application pins and ordering, application pin versus always-on-top distinction, exact window identity selection, and loading/current-live/authorized-historical/unavailable previews with correct icon/title fallback. GNOME/KDE architecture lessons do not replace those interactions.

Preserve the single Elm policy authority, typed versioned boundaries, grants/incarnations and output identity, Unknown/no-replay, actual resource retirement, draft preservation, accessibility/IME obligations, original deadlines and frozen evidence. Native code owns scoped mechanism and observed facts; it must not acquire a competing window policy. Architecture changes must not relabel an old ABI or promote component/model checks to native acceptance.

## Integration cadence

Architecture research and private proposals may run alongside the selected product slice. Production migration remains WIP=1 and native QA WIP=1. Before each selected refactor, preserve unfinished work and deliberately select the relevant original scenario slice using the contributor workflow; do not mix unrelated public edits into a participant record. Root integrates reviewed deltas and runs protected verification. Refresh Graphify with CUDA embeddings after code/model waves and run its retrieval evaluation before integration.

Review architecture at each sprint boundary and each integration batch: inspect what was actually simplified, what behavior was preserved, remaining lifecycle/packaging coupling, applicable regression evidence and the next migration step. Publish reviewed owned work normally, retain failed evidence, and prepare reversible Omarchy trials with verified rollback/draft preservation when ready. Architecture review is continuous supporting work, not a replacement for implementation or the original release gates.

## Initial status

Review in progress under Astra; GNOME/KDE and current-source Terra briefs requested. No replacement target architecture has yet been adopted. The existing first-use renderer failure remains unresolved. Root is preserving its diagnostic build and evidence while the architecture design is prepared. Subsequent decisions must name their source revision and reviewer; do not treat this initial status as permanent.
