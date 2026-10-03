# Elm pivot: implementation feasibility and documentation survey

Research date: 2026-10-03. No compiler, dependency, host or desktop changes were installed. Primary sources were fetched using the existing Scrapling Python environment. This note complements the root agent's full official-guide and Elm-author package `docs.json` corpus; it does not claim to contain every Elm ecosystem document.

## Recommendation

**Elm is a strong candidate for the typed state machine behind the GUI. A full Elm-rendered desktop requires a browser/webview host and retains the native window backend.** Start with the taskbar/switcher controller, preserve Quickshell's existing surfaces, and test whether the type system and explicit transitions actually reduce maintenance. Evaluate an Elm-rendered settings panel separately before considering taskbar, previews or Task View migration.

This is an architectural inference from the official [Elm platform API](https://github.com/elm/core/blob/1.0.5/src/Platform.elm), [compiler target/help source](https://github.com/elm/compiler/blob/0.19.2/terminal/src/Main.hs) and [Elm domain roadmap](https://github.com/elm/projects/blob/master/roadmap.md). The official compiler emits JavaScript; its ordinary GUI ecosystem targets the browser. The native Wayland compositor, capture, input focus, layer surfaces, display transfers and process ownership still need their existing native APIs and implementations.

## Current versions: stable and development differ

The [official latest stable release](https://github.com/elm/compiler/releases/tag/0.19.2) is **0.19.2**, published 2026-07-06. **0.19.3-beta** appeared on 2026-10-02 and is explicitly marked prerelease in the [release metadata](https://api.github.com/repos/elm/compiler/releases?per_page=5). Upstream `main` application documentation already recommends 0.19.3, so unqualified repository documentation can describe a beta. Use [tagged 0.19.2 application documentation](https://github.com/elm/compiler/blob/0.19.2/docs/elm.json/application.md) when selecting a stable baseline.

The primary npm registry reports [`elm-test` 0.19.2-1](https://registry.npmjs.org/elm-test/latest). Its [source package metadata](https://github.com/rtfeldman/node-test-runner/blob/master/package.json) agrees. Compiler and runner compatibility still require an actual build/test experiment; neither this survey nor metadata matching establishes that the intended project compiles. Dependencies and test dependencies should be pinned exactly in an application `elm.json`, which also serves as its package lock description.

## Four hosting choices

| Choice | What Elm owns | Existing components retained | Relative implementation cost | Main uncertainty |
|---|---|---|---|---|
| **Headless `Platform.worker` with existing Quickshell UI** | Pure controller state, message decoding, accepted observations and effect requests | QML views, native capture/rendering, compositor adapters and guarded helpers | Lowest; best first experiment | Additional persistent JS host and transport latency |
| Elm HTML in a **Qt WebEngine** view | Controller and DOM/CSS presentation | Qt/Wayland window host and native backend | Medium/high | Host initialization, layered input/focus, graphics/preview transfer |
| Elm HTML in a **Tauri** app | Controller and DOM/CSS presentation | Rust host, native backend, existing Omarchy integration until replaced | High for shell parity | Layer-shell integration and Linux WebKit behavior |
| Direct Elm-generated JS in **QJSEngine/QML** | Headless controller | Native Quickshell rendering | Experimental | Runtime compatibility and timer/global shims |

`Platform.worker` explicitly supports a headless program that sends messages through ports; it is a supported Elm program shape, not an HTML application hidden offscreen. A persistent Node host would be an implementation choice using that API, rather than an official Elm desktop toolkit. [Platform source](https://github.com/elm/core/blob/1.0.5/src/Platform.elm).

For Qt WebEngine, the documented [WebChannel](https://doc.qt.io/qt-6/qtwebchannel-javascript.html) bridge is asynchronous, caches properties on the HTML side, and requires JSON-convertible data. [QtWebEngineQuick initialization](https://doc.qt.io/qt-6/qtwebenginequick.html) also imposes native application startup requirements. Do not assume a new QML plugin can simply import a webview into the installed shell after startup without reviewing its host. This survey has not validated that embedding.

[Tauri's architecture](https://v2.tauri.app/concept/architecture/) offers a native core plus webview frontend. Its [Linux graphics documentation](https://v2.tauri.app/develop/debug/linux-graphics/) says Linux uses WebKitGTK and discusses real renderer/driver differences. Native window hosting is available, but Omarchy-specific layer surfaces, keyboard grabs and minimized previews still require explicit integration; they are not demonstrated by opening an ordinary app window.

[QJSEngine](https://doc.qt.io/qt-6/qjsengine.html) documents an ECMAScript engine and native extensions, not a browser DOM. The Elm [browser kernel](https://github.com/elm/browser/blob/1.0.2/src/Elm/Kernel/Browser.js) uses DOM operations and browser animation facilities. A headless worker avoids that DOM dependency, but the Elm runtime still needs compatible asynchronous scheduling primitives. Treat direct embedding as a compatibility experiment rather than the first architecture.

## Interoperability contract

Use one incoming protocol and one outgoing protocol, with explicit versioned message variants, rather than exposing arbitrary native methods. Decode inbound `Json.Decode.Value` into a domain `Msg` and reject unknown or malformed envelopes in Elm. This retains failure handling inside the model: the [incoming-port kernel](https://github.com/elm/core/blob/1.0.5/src/Elm/Kernel/Platform.js) throws when a JavaScript value violates a port's generated typed converter. Strong Elm types do not eliminate bad foreign input.

An illustrative division, not a built prototype:

```text
native observations/input
        ↓ bounded versioned events
JS host → Elm update(Model, Msg) → new Model + approved Effect values
        ↓ presentation projection       ↓ correlated effect request
Quickshell views                  existing guarded native backend
                                         ↓ acknowledgement/current receipt
                                  Elm update
```

Elm should own discriminated states such as `Idle`, `Preparing Generation`, `Choosing ReadyCandidates`, `ReleasedAwaitingCandidates`, `Restoring Receipt` and `Cancelled`. Bind transitions to compositor session, generation, ordinal, backend lifetime and receipt identity. Keep pending readiness separate from visible overlay state. A pure reducer then becomes straightforward to replay and fuzz.

The host must still validate freshness and native authority immediately before effects, serialize dependent actions through acknowledgement, reject stale replies, close cancelled resources and preserve deadlines. Elm's effect manager queue is not a transaction spanning a foreign backend. The current journal, Keeper ownership, ABI pairing and native-effect uncertainty cannot be replaced by a typed model alone. The recent snap-state feedback loop would also survive a language rewrite unless the host's file-publication boundary remained correct.

For efficiency, keep the single event subscriber and catalog cache, forward coalesced observations, preserve edge events such as modifier release, and never carry PNG pixels through JSON ports. Pass bounded image references/frame identities to a native renderer or webview image path. A browser-rendered preview adds transfer/decoding work; measure cold start, idle CPU/RSS, sustained capture, key-release latency, reduced motion and mixed-monitor scaling before expanding its role. These are proposed measurements, not existing performance results.

## Compiler, debugger, testing and license

The stable compiler offers `elm make --output=...`, `--report=json`, `--debug`, `--optimize` and package `--docs=...`. Its [flag definitions](https://github.com/elm/compiler/blob/0.19.2/terminal/src/Main.hs) describe the debugger's rewind/replay and import/export facilities. [Compiler mode selection](https://github.com/elm/compiler/blob/0.19.2/terminal/src/Make.hs) rejects simultaneous debug and optimize. Optimized builds rename internal record fields, so access Elm only through supported initialization/port interfaces, not generated object internals. Debugger replay does not replay native focus/capture effects safely; replay effect receipts with a stubbed backend.

[`elm-explorations/test`](https://github.com/elm-explorations/test) provides unit/fuzz tests and HTML query/event testing. [`elm-test`](https://github.com/rtfeldman/node-test-runner) offers deterministic seeds, configurable fuzz counts and workers; its default fuzz count is 100. Preserve failing seeds and named original scenarios, and use explicit bounds appropriate to this project. That package states integration/end-to-end tests require tools outside Elm. The original native baseline, recovery, input routes and private Quickshell tests remain mandatory; compiler success and Elm fuzzing establish different claims.

The [compiler license](https://github.com/elm/compiler/blob/master/LICENSE) is BSD-3-Clause, including notice retention, binary redistribution notices and non-endorsement requirements. [The test package](https://github.com/elm-explorations/test/blob/master/LICENSE) and test runner metadata also identify BSD-3-Clause. Host/webview and transitive dependencies need their own license inventory; compiler permission does not determine those licenses.

## Suggested exploration sequence

1. Port one already tested switcher reducer to pure Elm, replay the existing reordering/cancellation cases, and compare its state space and readability against the staged JavaScript reducer.
2. Connect it to a persistent headless worker with a mock native backend. Test malformed input, generation/epoch changes, duplicate/stale acknowledgements, delayed readiness and cancellation.
3. Exercise the worker through an actual private Quickshell controller, preserving the original deadlines and helper ownership requirements.
4. Independently evaluate one Elm-rendered settings panel in a chosen host. Only expand the rendering pivot after measured input, accessibility and resource behavior meets the existing acceptance needs.

No prototype was built, no packages installed, and no desktop changed during this exploration.

## Corpus and integrity

Scrapling artifacts are under `/home/hoskinson/.cache/elm-pivot/implementation/`. `sources.json` records URL, status and SHA-256 for each saved text snapshot. It includes compiler release/project/help/license documents, runtime sources, test runner/package sources and official host documentation. Hashes describe retained text snapshots, not downloaded compiler binaries. Failed/unsuitable retrievals were retained: the initial QtWebEngineQuick URL returned 404, and `elm-lang.org/news/faster-builds` returned a route label rather than a substantive article. Neither supports a recommendation. The corrected Qt page and tagged stable compiler sources were fetched separately.
