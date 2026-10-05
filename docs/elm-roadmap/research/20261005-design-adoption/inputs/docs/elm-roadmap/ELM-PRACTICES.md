# Elm architecture and reactive design

Use today's Elm Architecture as the reactive core: immutable `Model`, typed `Msg`, pure `update`, declarative `view`, and explicit `Cmd`/`Sub`. Historical `Signal` FRP APIs do not describe the pinned modern compiler. Official primary sources are retained in the Scrapling corpus: [Elm Architecture](https://guide.elm-lang.org/architecture/), [effects](https://guide.elm-lang.org/effects/), [commands and subscriptions](https://guide.elm-lang.org/effects/), [ports](https://guide.elm-lang.org/interop/ports.html), [interop limits](https://guide.elm-lang.org/interop/limits.html), and [Farewell to FRP](https://elm-lang.org/news/farewell-to-frp).

## What we reuse directly

The compiler checks message handling and union constructors; immutable updates remove shared mutable frontend state; views derive from the current model; commands describe external work instead of running it inside the reducer. Subscriptions follow the current desired state, so visibility determines preview demand without ad hoc polling timers. Pure updates support deterministic replay, small fixtures and comparison against the Quint transition model. These benefits reduce frontend infrastructure and make refactoring safer.

Represent lifecycle and receipt state with custom types rather than parallel booleans. Use distinct opaque wrappers for request identity, epoch, window incarnation, output generation and lease token. Keep native observed state separate from user intent. A `Pending` operation carries its captured identity, deadline and intended action; `Unknown` carries reconciliation context rather than a retryable command. Lossless native identity strings stay opaque; never convert them to Elm/JavaScript numbers.

Keep one authoritative native snapshot and derive taskbar groups, eligible selection and displayed state with pure functions. Store only genuine independent UI state such as query, focus scope and frozen chord selection. Avoid shadow copies of native focus, geometry, workspace membership or pin state that drift from receipts. Decoders validate every boundary; malformed observations leave the last valid model intact and initiate the defined reconciliation route.

## Effects and subscriptions

Have domain reducers return a next model and typed effect descriptions. A small interpreter maps those descriptions to ports or host capabilities; native authority performs final validation. A restore-then-focus sequence emits restore first and emits focus only after the matching committed receipt satisfies its dependency. `Cmd.batch` is for independent effects and supplies no sequencing guarantee.

Subscription lifetimes derive from visible consumers and active transactions. Preview demand includes authorization and source/output generations; closing the final consumer removes recurring acquisition demand while preserving authorized retained storage. Native control journals, cancellation, receipts and revocation remain active even when no Elm overlay is visible. Per-frame animation and GPU objects remain renderer-owned; Elm sends semantic targets and profiles, not pixels or per-frame positions.

Persist validated user preferences through commands and correlated outcomes. Coalesce only replaceable observations; ordered modifier/release/cancel/receipt events remain distinct messages. Schedule costly derived computations on snapshot changes rather than every pointer event. Use keyed rendering for changing interactive lists so DOM identity follows the window/control identity, and guard actions with the identity/publication captured at press time. Verify focus and native recipients across list updates. Stable keys use application/window identities, not display positions. Add `Html.Lazy` only after profiling verifies a benefit.

Keep internal reducer inputs, outgoing intents, admission results and refusals typed. Encode/decode at the transport boundary; do not use hand-built JSON as a child reducer API or match error strings for control flow. Every expected observation request must correspond to an emitted or registered request. Keep child effects whenever keeping the model update that allocated them.

Model native resource cancellation, retirement and acknowledgements as well as drawability. Forgetting a job or sending Release does not prove native cleanup. Scope requests by authenticated actor/session identity, define observation reset/exhaustion rules, and preserve the original native event's monotonic deadline across queues and recovery. Native lock/resource revocation must remain effective when the frontend stalls. Image load and DOM-applied receipts remain separate from physical presentation.

## Boundaries and guarantees

Elm does not prove native scheduling, effect ordering, GPU lifetime, Wayland eligibility or lock security. Ports are asynchronous and native observations can arrive late or be lost. Quint models those boundaries; native acceptance measures them. A pure frontend cannot repair a compositor that paints an ineligible surface. Keep hit testing, paint order, focus validation, fences and capability revocation in native authority.

Replay records sanitized typed messages and scenario fixtures, never unrelated text, credential keys, draft contents or pixels. Replay verifies semantic transitions and effect descriptions; it does not assert that an application displayed a frame. Pin compiler/packages and treat source hashes, decoder schema and native ABI as one release tuple.

## Executable learning route

The headless Elm proof of concept exercises custom lifecycle types and pure receipt-driven effects. Quint scene and bridge prototypes explore bounded interleavings and preserve deliberate regression counterexamples. Each prototype documents its simplifications; neither is a production host or proof of all behavior. P1 still must qualify actual view rendering, native input roles, IME, accessibility and hardware acceleration.

The five independent Opus reviews and their implementation/verification priorities
are tracked in [the FRP/Elm workplan](delivery/FRP-ELM-WORKPLAN.md). Preserve the
original roadmap and acceptance identities while implementing that advice.
