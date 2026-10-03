# Local documentation corpus

Downloaded with Scrapling on 2026-10-03. Raw sources and original acquisition manifests are retained. [Portable inventory](CORPUS_MANIFEST.json) records SHA-256 for every corpus file. [Official source mapping](corpus/official/portable-manifest.json) uses repository-relative paths. Agent acquisition manifests retain original cache paths as provenance.

## Coverage

- All 40 reachable English official Guide pages.
- All 20 indexed `elm/*` and `elm-explorations/*` packages: 77 published versions, 406 module versions; API JSON, generated readable Markdown, package metadata and README for each.
- Selected tagged runtime, host, Wayland and current compiler/tooling references in the research reports.
- 17 curated FRP/runtime primary sources, including Fran, push-pull FRP, Yampa, Flapjax and Elm’s original thesis. This is not all FRP literature.
- Official translations, the entire third-party ecosystem and unpublished/deleted package versions are outside this collection. HTTP-200 JavaScript shells are retained as evidence, not substantive documentation.

## Read first

- [Elm Architecture](corpus/official/guide/architecture.md)
- [Ports](corpus/official/guide/interop/ports.md)
- [Interop limits](corpus/official/guide/interop/limits.md)
- [Optimization](corpus/official/guide/optimization.md)
- [FRP survey and primary references](FRP.md)
- [Host and window-system architecture](ARCHITECTURE.md)
- [Compiler, runtime and migration](IMPLEMENTATION.md)

## Official packages

| Package | Latest indexed version | Archived versions | API |
| --- | --- | ---: | --- |
| elm-explorations/benchmark | 1.0.2 | 3 | [Modules](corpus/official/packages/elm-explorations/benchmark/1.0.2/docs.md) |
| elm-explorations/linear-algebra | 1.0.3 | 4 | [Modules](corpus/official/packages/elm-explorations/linear-algebra/1.0.3/docs.md) |
| elm-explorations/markdown | 1.0.0 | 1 | [Modules](corpus/official/packages/elm-explorations/markdown/1.0.0/docs.md) |
| elm-explorations/test | 2.2.1 | 12 | [Modules](corpus/official/packages/elm-explorations/test/2.2.1/docs.md) |
| elm-explorations/webgl | 1.1.3 | 6 | [Modules](corpus/official/packages/elm-explorations/webgl/1.1.3/docs.md) |
| elm/browser | 1.0.2 | 3 | [Modules](corpus/official/packages/elm/browser/1.0.2/docs.md) |
| elm/bytes | 1.0.8 | 9 | [Modules](corpus/official/packages/elm/bytes/1.0.8/docs.md) |
| elm/core | 1.0.5 | 6 | [Modules](corpus/official/packages/elm/core/1.0.5/docs.md) |
| elm/file | 1.0.5 | 6 | [Modules](corpus/official/packages/elm/file/1.0.5/docs.md) |
| elm/html | 1.0.1 | 2 | [Modules](corpus/official/packages/elm/html/1.0.1/docs.md) |
| elm/http | 2.0.0 | 2 | [Modules](corpus/official/packages/elm/http/2.0.0/docs.md) |
| elm/json | 1.1.4 | 6 | [Modules](corpus/official/packages/elm/json/1.1.4/docs.md) |
| elm/parser | 1.1.0 | 2 | [Modules](corpus/official/packages/elm/parser/1.1.0/docs.md) |
| elm/project-metadata-utils | 1.0.2 | 3 | [Modules](corpus/official/packages/elm/project-metadata-utils/1.0.2/docs.md) |
| elm/random | 1.0.0 | 1 | [Modules](corpus/official/packages/elm/random/1.0.0/docs.md) |
| elm/regex | 1.0.0 | 1 | [Modules](corpus/official/packages/elm/regex/1.0.0/docs.md) |
| elm/svg | 1.0.1 | 2 | [Modules](corpus/official/packages/elm/svg/1.0.1/docs.md) |
| elm/time | 1.0.0 | 1 | [Modules](corpus/official/packages/elm/time/1.0.0/docs.md) |
| elm/url | 1.0.0 | 1 | [Modules](corpus/official/packages/elm/url/1.0.0/docs.md) |
| elm/virtual-dom | 1.0.5 | 6 | [Modules](corpus/official/packages/elm/virtual-dom/1.0.5/docs.md) |

## Guide pages

- [https://guide.elm-lang.org/](corpus/official/guide/index.md)
- [https://guide.elm-lang.org/appendix/function_types](corpus/official/guide/appendix/function_types.md)
- [https://guide.elm-lang.org/appendix/types_as_bits](corpus/official/guide/appendix/types_as_bits.md)
- [https://guide.elm-lang.org/appendix/types_as_sets](corpus/official/guide/appendix/types_as_sets.md)
- [https://guide.elm-lang.org/architecture/](corpus/official/guide/architecture.md)
- [https://guide.elm-lang.org/architecture/buttons](corpus/official/guide/architecture/buttons.md)
- [https://guide.elm-lang.org/architecture/forms](corpus/official/guide/architecture/forms.md)
- [https://guide.elm-lang.org/architecture/text_fields](corpus/official/guide/architecture/text_fields.md)
- [https://guide.elm-lang.org/core_language](corpus/official/guide/core_language.md)
- [https://guide.elm-lang.org/effects/](corpus/official/guide/effects.md)
- [https://guide.elm-lang.org/effects/http](corpus/official/guide/effects/http.md)
- [https://guide.elm-lang.org/effects/json](corpus/official/guide/effects/json.md)
- [https://guide.elm-lang.org/effects/random](corpus/official/guide/effects/random.md)
- [https://guide.elm-lang.org/effects/time](corpus/official/guide/effects/time.md)
- [https://guide.elm-lang.org/error_handling/](corpus/official/guide/error_handling.md)
- [https://guide.elm-lang.org/error_handling/maybe](corpus/official/guide/error_handling/maybe.md)
- [https://guide.elm-lang.org/error_handling/result](corpus/official/guide/error_handling/result.md)
- [https://guide.elm-lang.org/install/](corpus/official/guide/install.md)
- [https://guide.elm-lang.org/install/editor](corpus/official/guide/install/editor.md)
- [https://guide.elm-lang.org/install/elm](corpus/official/guide/install/elm.md)
- [https://guide.elm-lang.org/interop/](corpus/official/guide/interop.md)
- [https://guide.elm-lang.org/interop/custom_elements](corpus/official/guide/interop/custom_elements.md)
- [https://guide.elm-lang.org/interop/flags](corpus/official/guide/interop/flags.md)
- [https://guide.elm-lang.org/interop/limits](corpus/official/guide/interop/limits.md)
- [https://guide.elm-lang.org/interop/ports](corpus/official/guide/interop/ports.md)
- [https://guide.elm-lang.org/next_steps](corpus/official/guide/next_steps.md)
- [https://guide.elm-lang.org/optimization/](corpus/official/guide/optimization.md)
- [https://guide.elm-lang.org/optimization/asset_size](corpus/official/guide/optimization/asset_size.md)
- [https://guide.elm-lang.org/optimization/keyed](corpus/official/guide/optimization/keyed.md)
- [https://guide.elm-lang.org/optimization/lazy](corpus/official/guide/optimization/lazy.md)
- [https://guide.elm-lang.org/types/](corpus/official/guide/types.md)
- [https://guide.elm-lang.org/types/custom_types](corpus/official/guide/types/custom_types.md)
- [https://guide.elm-lang.org/types/pattern_matching](corpus/official/guide/types/pattern_matching.md)
- [https://guide.elm-lang.org/types/reading_types](corpus/official/guide/types/reading_types.md)
- [https://guide.elm-lang.org/types/type_aliases](corpus/official/guide/types/type_aliases.md)
- [https://guide.elm-lang.org/webapps/](corpus/official/guide/webapps.md)
- [https://guide.elm-lang.org/webapps/modules](corpus/official/guide/webapps/modules.md)
- [https://guide.elm-lang.org/webapps/navigation](corpus/official/guide/webapps/navigation.md)
- [https://guide.elm-lang.org/webapps/structure](corpus/official/guide/webapps/structure.md)
- [https://guide.elm-lang.org/webapps/url_parsing](corpus/official/guide/webapps/url_parsing.md)

## FRP sources

- [elm-farewell-frp](corpus/frp/elm-farewell-frp.txt) — [original](https://elm-lang.org/news/farewell-to-frp)
- [elm-concurrent-frp-thesis](corpus/frp/elm-concurrent-frp-thesis.txt) — [original](https://elm-lang.org/assets/papers/concurrent-frp.pdf)
- [fran-1997-index](corpus/frp/fran-1997-index.txt) — [original](https://conal.net/papers/icfp97/)
- [fran-1997-paper](corpus/frp/fran-1997-paper.txt) — [original](https://conal.net/papers/icfp97/icfp97.pdf)
- [push-pull-2009-index](corpus/frp/push-pull-2009-index.txt) — [original](https://conal.net/papers/push-pull-frp/)
- [push-pull-2009-paper](corpus/frp/push-pull-2009-paper.txt) — [original](https://conal.net/papers/push-pull-frp/push-pull-frp.pdf)
- [yampa-arrowized-2003](corpus/frp/yampa-arrowized-2003.txt) — [original](https://www.cs.yale.edu/homes/external/nilsson/Publications/afp2002.pdf)
- [elm-browser-animation-kernel](corpus/frp/elm-browser-animation-kernel.txt) — [original](https://raw.githubusercontent.com/elm/browser/1.0.2/src/Elm/Kernel/Browser.js)
- [elm-browser-events](corpus/frp/elm-browser-events.txt) — [original](https://raw.githubusercontent.com/elm/browser/1.0.2/src/Browser/Events.elm)
- [elm-core-platform-kernel](corpus/frp/elm-core-platform-kernel.txt) — [original](https://raw.githubusercontent.com/elm/core/1.0.5/src/Elm/Kernel/Platform.js)
- [elm-core-command](corpus/frp/elm-core-command.txt) — [original](https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Cmd.elm)
- [elm-core-subscription](corpus/frp/elm-core-subscription.txt) — [original](https://raw.githubusercontent.com/elm/core/1.0.5/src/Platform/Sub.elm)
- [elm-ports-guide](corpus/frp/elm-ports-guide.txt) — [original](https://guide.elm-lang.org/interop/ports.html)
- [qt-bindings-611](corpus/frp/qt-bindings-611.txt) — [original](https://doc.qt.io/qt-6.11/qtqml-syntax-propertybinding.html)
- [qt-animations-611](corpus/frp/qt-animations-611.txt) — [original](https://doc.qt.io/qt-6.11/qtquick-statesanimations-animations.html)
- [flapjax-2009](corpus/frp/flapjax-2009.txt) — [original](https://cs.brown.edu/people/aguha/papers/meyerovich-oopsla2009.pdf)
- [elm-browser-animation-manager](corpus/frp/elm-browser-animation-manager.txt) — [original](https://raw.githubusercontent.com/elm/browser/1.0.2/src/Browser/AnimationManager.elm)

## Stable compiler supplemental sources

[Compiler source manifest](corpus/compiler-stable/sources.json) covers all eight files in the stable tagged documentation tree, ten installer READMEs, and official reference routes. [Acquisition report](SUPPLEMENT.md) distinguishes extracted content and failed routes.

## Selected GUI library

[elm-ui 1.1.8 API](corpus/elm-ui/docs.md), [README](corpus/elm-ui/README.md), [provenance](corpus/elm-ui/manifest.json). This is an optional third-party layout library, not a native window manager.
