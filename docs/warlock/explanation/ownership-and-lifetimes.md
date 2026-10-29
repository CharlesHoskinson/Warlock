# Why ownership and lifetimes shape Warlock

Warlock combines Elm state transitions, projection-only surfaces and asynchronous native services. The architecture goal is one authoritative policy per responsibility, with explicit boundaries for mechanism and observed facts. It is not a claim that one Elm process owns every resource or that all current code already satisfies every invariant.

```mermaid
flowchart LR
    U[User input / native fact] --> P[Owning Elm transition]
    P --> M[Next model]
    P --> C[Proposed effect]
    M --> V[Bar / Popup projection]
    C --> A[Current native admission]
    A --> N[Scoped mechanism]
    N --> O[Correlated observation]
    O --> P
```

A renderer displays a validated snapshot and reports input. It must not invent a second activation/window policy. A native adapter validates current authority, executes a scoped mechanism and returns facts; it must not decide a competing desktop policy. Ports and typed messages expose that seam, but do not themselves provide exactly-once delivery, ordering or lifetime validity.

## Identity is more than a window number

Binding, request, generation, incarnation and output identify who may act and which observation belongs to which state. Publication and popup lease scope presentation/input; grants and custody scope resources. A well-typed Elm value can be stale by the time a native action is admitted. Keep the actual owner and lifetime checks at their existing authoritative boundary.

Pending means an admitted attempt is unresolved. Unknown is not permission to repeat it. Read-only recovery queries the correlated original outcome; frontend or host restart does not silently replay a window effect. `Cmd.batch` does not promise result ordering: dependent work waits for its protocol's actual prerequisite observation, which may involve state or retirement rather than a receipt alone.

## Coherent data is not an atomic native transaction

A snapshot should avoid combining fresh title/control identity with an unrelated lease. Yet one decoded packet does not make ledger mutation, popup opening, queueing, backend execution and teardown one transaction. Each can fail. Likewise Elm garbage collection is not proof that a native frame, callback, mapping or GPU buffer retired.

Loading, authorized historical, current live and unavailable previews are different visible and accessible states. A minimized historical frame may remain authorized without recurring acquisition; revocation still requires retirement. Never confuse power quiescence with authorization or identity-correct icon/title fallback with live preview delivery. The Windows-like taskbar/group/pin behavior remains a requirement; GNOME/KDE offer architectural lessons rather than a replacement UX.

## Why the first extraction is small

The first migration extracts an opaque pure `SurfaceSnapshot` value/codec and leaves rendering dependent on it. `OutputController` and `Presentation` now use that contract directly, preserving the previous renderer API through forwarding functions. Actual Main/Bar/Popup builds, bounded codec properties and production group/retirement replays pass; see the [evidence](../../../implementation/warlock/qa/evidence/pure-surface-snapshot-20261029/manifest.json). This removes a direct policy-to-HTML dependency without changing the intended wire protocol or native authority. It does not establish new native acceptance. A residual `OutcomeAnnouncements` → `Announcement` HTML dependency remains an explicit later seam; the whole transitive graph is not made HTML-free by the first step.

Preserve existing same-lease local edits and pending-query behavior rather than introducing a blanket stricter rule during extraction. Normalized valid codec idempotence is not equality with every raw encoding; duplicate-key checks belong before a parsed value discards that distinction. [Contracts and fuzzing](../../warlock-build-loop/v2/FUZZING-CONTRACTS.md) make these invariants explicit and exercise the production route; types and sampled properties do not replace native acceptance.

## Research and retrofit

Current Elm 0.19 TEA uses model/message/update, commands, subscriptions and ports. Historical Signal-era FRP papers examine responsiveness, ordering, demand and temporal lifetime questions under their own semantics. Do not introduce removed APIs or infer native correctness from those papers. The [reviewed research](../../warlock-build-loop/v2/ELM-ARCHITECTURE-RESEARCH.md) and [architecture track](../../warlock-build-loop/v2/ARCHITECTURE-REVIEW.md) inform staged decisions with exact source and tradeoffs.

Existing debt needs the same discipline as new work: identify the actual coupling/contract, select one reversible change, preserve frozen evidence and drafts, verify relevant roots and real properties, then assess native gates. A renamed folder, larger research packet or successful diagnostic build is not a delivered architecture improvement. The active goal remains usable native behavior and the complete original scope.
