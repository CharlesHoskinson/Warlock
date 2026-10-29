# Elm architecture research for Warlock

Research snapshot: October 29, 2026. This is a source-linked design study and proposal set, not adopted implementation or native acceptance. Preserve the original 242 requirements / 417 scenarios and Windows-like taskbar, persistent pins, group selection and preview behavior. The standing [architecture review](ARCHITECTURE-REVIEW.md) owns subsequent decisions; [contracts and fuzzing](FUZZING-CONTRACTS.md) govern migrations.

## Main finding

Keep current Elm's explicit model/message/update/effect boundary. Improve ownership and validated domain values before adding another reactive framework. The first concrete candidate is an opaque `SurfaceSnapshot` value/codec, extracted from `SurfaceRenderer`: policy and presentation coordination should depend on validated protocol data rather than HTML rendering. This is a dependency inversion, not a change to window policy. Astra's source audit also found a remaining policy-to-HTML path through `OutcomeAnnouncements` and `Announcement`; one snapshot extraction cannot honestly claim the entire policy graph is HTML-free.

These are Warlock-specific inferences from current source and the references below. They do not follow automatically from a paper or the Elm compiler.

## Current Elm practice versus historical FRP

The current [Elm Architecture guide](https://guide.elm-lang.org/architecture/) describes an explicit model, view and update. The [effects guide](https://guide.elm-lang.org/effects/) adds commands and subscriptions. Use these documented APIs for the existing application. The 2012 thesis and 2013 paper describe an earlier signal language and scheduling design; their `Signal`, `lift` and `async` examples are historical research, not APIs to introduce into Elm 0.19.

The [official structure guidance](https://guide.elm-lang.org/webapps/structure) recommends modules organized around meaningful types, rather than a global Model/Update/View folder split or a component for every visual fragment. It also cautions against abstraction based merely on anticipated reuse or file length. For Warlock, meaningful candidates include validated snapshots, window identities, shortcut drafts and preview lifetimes. Keep domain transitions together; a small `Main` is already present, so splitting it further would not address the identified coupling.

[Custom types](https://guide.elm-lang.org/types/custom_types) can express mutually exclusive states. [Module exports](https://guide.elm-lang.org/webapps/modules) support hiding constructors behind validation. Our design inference is to represent valid snapshot/lease identities with opaque types and to return explicit errors at wire boundaries. Neither an opaque frontend type nor successful decoding establishes that a native grant remains current; effect admission must still validate actual lifetime and authority.

## Effects, ordering and process boundaries

[Elm ports](https://guide.elm-lang.org/interop/ports) provide explicit outgoing commands and incoming subscriptions. They are a useful boundary for native adapters, not proof of delivery, exactly-once execution or safe replay. The adapter should translate a typed intent into a scoped mechanism and return observed facts. Policy decides whether a later observation still belongs to the current output, incarnation and request.

The pinned [Elm core 1.0.5 command source](https://github.com/elm/core/blob/1.0.5/src/Platform/Cmd.elm) explicitly provides no ordering guarantee for batched command results. Admit dependent work only after the correlated prerequisite observation required by its protocol (receipt, observed state, or retirement), rather than relying on `Cmd.batch` order. A receipt alone may not prove mutation or presentation. Preserve Pending/Unknown/refused distinctions; never replay a window effect merely because a frontend restarts. An atomic decoded presentation packet is also not an atomic native transaction: ledger mutation, opening a surface, queueing and teardown have separate failure boundaries.

A desirable trace shape is: validated event → owning reducer → next model plus proposed effects → current-authority admission → native execution → correlated observation. This is a proposed explanatory contract, not a new parallel runtime or a claim that existing code already implements every step correctly.

## Papers to study, in order

| Primary work | What to study | Warlock question and limitation |
| --- | --- | --- |
| Evan Czaplicki, [Elm: Concurrent FRP for Functional GUIs](https://elm-lang.org/assets/papers/concurrent-frp.pdf), 2012 thesis | Chapter 4: event order, signal graphs, asynchronous updates and responsiveness | Which work can happen outside the UI reducer? Historical concurrency semantics do not describe today's Elm runtime or establish native threading guarantees. |
| Evan Czaplicki and Stephen Chong, [Asynchronous Functional Reactive Programming for GUIs](https://people.seas.harvard.edu/~chong/pubs/pldi13-elm.pdf), PLDI 2013 | Explicit asynchronous boundaries and the cost of globally ordered event processing | Keep catalog/capture computation from delaying input. Tag completions so an old result cannot update a new query or window incarnation. This application is our inference; the paper does not prove Warlock's protocol. |
| Conal Elliott, [Push-Pull Functional Reactive Programming](https://conal.net/papers/push-pull-frp/push-pull-frp.pdf), Haskell Symposium 2009 | Demand-driven versus change-driven work; separation of discrete change from continuous behavior | Feed discrete state changes without polling unchanged policy; request capture/animation work only while a qualified consumer needs it. The paper is not a compositor budget or zero-copy proof. |
| Neelakantan R. Krishnaswami, [Higher-Order Functional Reactive Programming without Spacetime Leaks](https://www.cl.cam.ac.uk/~nk480/simple-frp.pdf), ICFP 2013 | The retained-history example, dynamic networks associated with windows, temporal types and eager retirement | Define who owns each subscription, frame and callback and when it ends. Elm 0.19 does not acquire this paper's temporal type system merely by using immutable values. |

The PLDI paper's motivation is that long work and unnecessary recomputation can harm interactive responsiveness; its calculus lets a programmer choose where ordering relaxes. Warlock should borrow the question, not import obsolete syntax: rendering and search may complete asynchronously, but effect authorization still requires current identities. Study its operational semantics and implementation section alongside actual runtime traces rather than assuming a pure reducer prevents every scheduling problem.

Elliott's push/pull model motivates separating discrete authority facts from continuously sampled motion. A retained minimized frame may remain authorized historical data without recurring acquisition. A revoked frame must not survive merely because no consumer requested a new one. Treat power quiescence and authorization retirement as different contracts, then measure actual acquisition, upload, fence and cleanup behavior.

Krishnaswami's paper shows why retaining an earlier reactive value can retain growing history and why dynamic window-like networks need controlled lifetimes. For Warlock the practical adaptation is explicit lifecycle tables, bounded history and resource retirement verified on native objects. Garbage collection of Elm values is not evidence that a GPU buffer, subscription or native callback was retired. The paper's formal guarantees belong to its own language and semantics.

## Consistency and contracts to preserve

A coherent presentation should derive from one admitted snapshot rather than independently combining a fresh title, old control identities and a new lease. This is our consistency requirement; do not claim that current Elm plus ports guarantees a glitch-free transaction across multiple WebViews. Preserve exact external-action publication rules and the existing same-lease local-edit exception where the original implementation deliberately allows it. A general “reject every older publication” rule would change behavior.

Saved preferences, unsaved edits and live installed bindings are distinct state. A read of an unchanged saved revision must be assessed against draft preservation; a changed revision needs an explicit conflict policy. A persisted choice after restart is not evidence that a fresh native authority installed the binding automatically. Never turn a refresh or replay into an implicit Save or effect execution.

Proposed properties for the first snapshot migration: normalized encode/decode idempotence for valid snapshots (not identity with every raw input encoding); unchanged wire contract/large-identity representation; malformed/boundary input refusal; unchanged action-admission decisions and proposed effects for the same event sequence; preserved local-edit exception; and no new HTML/runtime dependency in the extracted value module. Check duplicate JSON keys at the raw transport/parser boundary; a decoded JSON value may already have discarded that distinction. Generate both valid and invalid cases. Preserve seeds, minimized failures and actual production-route/source correspondence under the [workflow](FUZZING-CONTRACTS.md).

## GNOME/KDE comparison and decisions

[GNOME's shell architecture overview](https://gjs.guide/extensions/overview/architecture.html) describes native Mutter/Clutter integration exposed to JavaScript. [Mutter's documentation](https://gnome.pages.gitlab.gnome.org/mutter/) identifies its compositor-library role. Study that explicit native/toolkit seam, while recognizing that an in-process shell/compositor arrangement has different failure consequences from Warlock's intended scoped frontend boundary.

[KDE's architecture discussion](https://blogs.kde.org/2018/08/02/engineering-plasma-extensions-and-stability--present-and-future/) documents separate shell UI and compositor processes in its 2018 design. It is a historical architectural reference, not a verified claim about every current component. Warlock's proposed lesson is failure containment and explicit service ownership. Do not replace the required Windows-like interactions with GNOME or Plasma UI conventions.

## Evidence and next decisions

The October 29 diagnostic native run observed receiver names and `WebKitJavascriptError` code `601` before host failure; it did not identify the unsupported value or prove the cause of renderer termination. Guidance, saved choices and restart were not reached. Research or refactoring must not relabel this as a repaired runtime.

Review the snapshot extraction's exact API/callers and original invariants, select it deliberately under product WIP=1, compile affected entry points, run the applicable production replays and properties, and record remaining native gates. Then assess the residual announcement value/rendering seam and build/package enumeration separately. Avoid a new actor framework, replacing the compositor, multiple policy authorities, or a broad rewrite solely on the strength of this reading list.

Web research now uses Scrapling per the user's standing instruction. Earlier primary documents were retrieved before that instruction; preserve their provenance. Subsequent Scrapling fetches verified official Elm module and test documentation. Full papers are linked rather than copied into the repository. Source freshness, test results and adopted decisions must be updated as implementation proceeds.
