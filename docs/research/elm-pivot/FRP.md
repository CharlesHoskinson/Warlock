# Elm / FRP pivot: semantics and native rendering boundary

Research date: 2026-10-03. Curated primary-source coverage, not an exhaustive survey of FRP. Scrapling `Fetcher.get` fetched 17 documents successfully; raw HTML/source/PDF, extracted text and SHA-256 manifests are preserved at `/home/hoskinson/.cache/elm-pivot/frp/manifest.json`. PDFs were downloaded through Scrapling and extracted with `pdftotext -layout`. Elm source references are tagged `elm/core 1.0.5` and `elm/browser 1.0.2`, not guessed current master semantics. No GUI actions, deployments or native replacements occurred.

## Main conclusion

Elm can make the window-policy model and effect protocol substantially easier to inspect and test. Elm does not provide a ready-made Wayland compositor, native texture owner, frame clock or window-family renderer. A practical pivot starts with a pure Elm reducer and explicit native receipts, preserving the existing rendering and input authority while replacing orchestration incrementally. This recommendation is an engineering inference from the sources and local implementation; no benchmark or working native Elm runtime has been established here.

## Historical FRP and modern Elm are different designs

[Fran, Elliott and Hudak 1997](https://conal.net/papers/icfp97/icfp97.pdf) distinguishes continuous time-varying behaviors from discrete events, making animations descriptions of values over time rather than imperative frame steps. It separates the modeled phenomenon from sampling/presentation. This supplies a useful mathematical model for motion; continuous semantics still need a physical sampling implementation.

[Czaplicki's 2012 Elm thesis](https://elm-lang.org/assets/papers/concurrent-frp.pdf) describes the original signal-graph Elm, with synchronous ordering and selective asynchronous computation. Its word/translation example shows inconsistent output when unequal dependency paths combine different input generations. The thesis's runtime and signal APIs are historical evidence, not documentation for current Elm.

Elm explicitly removed signals in 0.17. [A Farewell to FRP, 2016](https://elm-lang.org/news/farewell-to-frp) explains the move to commands/subscriptions and the Elm Architecture. An implementation based on `Signal`, signal lifting or old `Graphics.Element` tutorials would target the wrong APIs. Contemporary Elm uses a model, discrete messages, pure update/view functions and runtime-managed effects/subscriptions. It should not be sold as a built-in continuous-behavior FRP language.

## Push, pull and coherent updates

[Elliott's push-pull FRP paper, 2009](https://conal.net/papers/push-pull-frp/push-pull-frp.pdf) separates discrete reactive values from time functions, combining event-driven updates with demand-driven sampling. Pure polling can recompute unchanged values and delay reactions until the next sample. This motivates a hybrid here: push discrete state changes and receipt events, then sample only active motion on the native presentation clock. Do not poll every window or regenerate captured pixels every animation frame.

[Flapjax, Meyerovich et al. 2009](https://cs.brown.edu/people/aguha/papers/meyerovich-oopsla2009.pdf), sections 3.4–3.5, describes glitches from inconsistent dependency updates, topological propagation and detached event-listener cleanup. Graph consistency and physical resource cleanup are separate concerns. Its solutions illustrate the problems; they do not give current Elm or QML a distributed transactional guarantee.

[Arrowized FRP/Yampa, Hudak et al.](https://www.cs.yale.edu/homes/external/nilsson/Publications/afp2002.pdf) disciplines signal transformations and switching to avoid common time/space leaks in hybrid systems. That is useful design precedent for bounded motion actors and explicit switching, but a Haskell/Yampa runtime is another architectural choice, not an Elm feature.

For this project, a coherent pure snapshot is only one layer. A native focus event, capture-ready receipt and renderer presentation can arrive in different orders. Merge them using stable identity, actor epoch, command sequence and output generation; never combine an old frame or old hit result with a newly selected window. The existing token/current checks remain necessary.

## What modern Elm guarantees, and what remains explicit

The [core platform implementation](https://raw.githubusercontent.com/elm/core/1.0.5/src/Elm/Kernel/Platform.js) applies `update` to the current model and passes the resulting model to rendering and subscription calculation. This makes one logical update easy to reason about. It does not atomically commit changes to an external compositor or multiple displays.

The [Cmd module](https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Cmd.elm) explicitly gives no result-order guarantee for batched commands. Therefore `Cmd.batch [Capture, Minimize, Retire]` cannot establish capture-before-hide or producer-before-consumer closure. Sequence the workflow through acknowledged messages. A cancellation should advance the epoch and emit retirement intent; completion remains pending until a correlated native retirement receipt arrives.

The [Sub module](https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Sub.elm) and [Browser.Events](https://raw.githubusercontent.com/elm/browser/1.0.2/src/Browser/Events.elm) support model-dependent subscriptions; mouse movement should be subscribed only when needed. Removing an Elm subscription is not proof that a native helper process group, capture buffer, callback or pending external effect has closed.

The official [ports guide](https://guide.elm-lang.org/interop/ports.html) recommends a small message-oriented boundary and explicit state ownership. That fits one typed native command port and one decoded receipt port better than exposing a port for every native function. Treat all incoming data as untrusted: decode identity/generation fields, validate message size and schema, reject stale requests, and retain native policy enforcement. These bridge checks are project requirements, not automatic properties of ports.

## Time and motion reversals

[Browser.Events animation APIs](https://raw.githubusercontent.com/elm/browser/1.0.2/src/Browser/Events.elm) expose POSIX timestamps or elapsed frame deltas. The tagged [browser kernel](https://raw.githubusercontent.com/elm/browser/1.0.2/src/Elm/Kernel/Browser.js) uses `requestAnimationFrame` scheduling and obtains time with `Date.now`; the [animation manager](https://raw.githubusercontent.com/elm/browser/1.0.2/src/Browser/AnimationManager.elm) subtracts consecutive times. These are web animation facilities, not native monotonic presentation feedback. The DOM animator also coalesces asynchronous model changes for rendering; a model update is not a displayed frame receipt.

Recommended native motion record:

```
Motion { epoch, capturedFrameKey, outputGeneration,
         originRect, originVelocity, destinationRect,
         monotonicStart, duration, reducedMotion }
```

Let `sampleMotion(record, nativeMonotonicTime)` return geometry and velocity. On reversal, retain the captured source and retarget from the last *presented* geometry/velocity, preserving the existing continuous-trajectory model and receipts. Elm can choose the destination and epoch; native rendering should sample, upload and report presentation. A frozen frame does not need to be PNG-encoded, decoded or reuploaded for every tick. This maps directly to existing `producer-continuous-dev-v13` behavior and the retained-frame research.

Represent 64-bit native identifiers and absolute nanosecond clocks as strings or explicitly bounded relative units at a JavaScript boundary; do not silently round them into JavaScript numeric values. Clock-domain conversion, timestamp bounds and output-generation changes must be defined in the protocol.

## Mapping to current open work

| Existing concern | Elm model contribution | Native authority/evidence retained |
|---|---|---|
| Minimize/restore reversal | Destination, operation epoch, acknowledged transitions, reduced-motion policy | Monotonic trajectory sampling, family pixels, exact last-presented state and two-second deadline |
| Capture lifetime | `Requested / Ready / Retiring / Retired`, bounded frame keys and leases | DMA-BUF/SHM ownership, scene-graph render thread, helper-group closure, source-stop proof |
| Pin/MAX/modal focus | A single logical family/selection/pin model; pure replayable decisions | Actual mapped/input eligibility, modal parent graph, native stacking and painted/hit agreement |
| Popup cancellation/stale action | Generation/sequence correlation and explicit rejection transitions | Real Qt signals, Quickshell process/receipt ordering and original reliability campaign |
| Multi-display transfer | Output-generation keyed intent and invalidation | Scale/transforms, surface lifecycle, actual per-output presentation and hardware validation |

The MAX stacking bug is concrete evidence of this boundary: an Elm view could say that MAX is selected while the compositor still paints a previously raised float above it. The staged renderer correction fixes native drawing order; adopting a pure model cannot substitute for that fix or its native tests.

## QML comparison and staged pivot

QML already offers declarative dependencies and retained scene-graph animation; [Qt 6.11 property bindings](https://doc.qt.io/qt-6.11/qtqml-syntax-propertybinding.html) cautions against relying on binding evaluation order, while [Qt animation documentation](https://doc.qt.io/qt-6.11/qtquick-statesanimations-animations.html) covers states/transitions and animation facilities. Elm's strongest incremental benefit is centralizing policy and explicit messages; QML's existing advantage is direct native items, input surfaces, capture and rendering integration. Neither declarative syntax alone settles distributed native effects or process lifetime.

Proposed sequence (engineering inference):

1. Encode a small pure Elm state machine for one existing reversible flow; replay existing native observations without issuing commands. Compare its decisions with current behavior and Quint invariants.
2. Add a versioned command/receipt envelope with native epochs and bounded payloads. Fault-test out-of-order, duplicated and stale receipts before enabling effects.
3. Host the policy as an Elm `Platform.worker` or another explicitly tested JavaScript runtime integration; retain QML/native rendering and opaque frame keys. The runtime adapter is work to implement—generated JavaScript must not be assumed to run unchanged inside Qt's JavaScript engine.
4. Move popup/taskbar selection policy first. Keep GPU frames, fullscreen/pin/input truth, motion sampling and native process supervision with their existing owners until equivalent native acceptance passes.
5. Evaluate a browser renderer only as a separate product decision. DOM/webview composition, texture transfer, focus/input routes and presentation timing add costs that require measurement; no source here establishes that browser Elm is faster than the current Qt Quick compositor-facing shell.

Completion criteria remain the original private native campaigns, acceptance deadlines, exact core/plugin pairing, process closure and accessibility/hardware checks. This corpus provides a design foundation and practical migration boundary, not a claim that all FRP literature is collected or that an Elm desktop/window-system implementation exists.
