# Stable compiler documentation supplement

Scrapling retrieval completed on 2026-10-03 UTC. This supplement extends the implementation survey with the complete `docs/` directory and installer README inventory from the **0.19.2 stable compiler tag**, rather than development-branch documentation. No compiler, package, or desktop component was installed.

The corpus is `/home/hoskinson/.cache/elm-pivot/compiler-stable/`. Its `sources.json` records requested and final URLs, response status and headers, retrieval time, byte length, raw-body SHA256, extracted-text SHA256, and upstream Git blob identity where applicable. `raw/` preserves Scrapling response-body bytes; these are response payloads, not HTTP wire captures. `text/` contains separate readable derivatives. The reproducible fetch script is retained as `fetch.py`.

## Coverage and verification

The [recursive stable Git tree](https://api.github.com/repos/elm/compiler/git/trees/0.19.2?recursive=1) resolves to commit `4b5c983ebe17aafd23f3d5941e7159eeb677574f` and reports `truncated: false`. Every blob under `docs/` and every README under `installers/` was selected: **8 compiler documents and 10 installer READMEs**. All 18 fetched bodies return HTTP 200 and reproduce their listed Git blob SHA1 using Git's `blob <length>\0<body>` encoding. The manifest also supplies SHA256 for each body.

The eight compiler documents are:

- `docs/elm.json/application.md` and `docs/elm.json/package.md`.
- `docs/upgrade-instructions/0.16.md`, `0.17.md`, `0.18.md`, `0.19.0.md`, `0.19.1.md`, and `earlier.md`.

The ten installer READMEs cover the installer root, Linux, macOS, Windows, npm, and five npm platform packages: `darwin_arm64`, `darwin_x64`, `linux_arm64`, `linux_x64`, and `win32_x64`. Historical upgrade documents are retained as historical guidance; their presence at the stable tag does not make obsolete APIs current. Installer READMEs describe distribution/build procedures and must not all be treated as end-user installation instructions.

The resulting corpus contains **24 response records**: the recursive tree, the 18 tag-bound files, and five website responses. There are 23 HTTP 200 responses and one intentionally preserved HTTP 404.

## Official web references and SPA handling

| Requested source | Result | Treatment |
| --- | --- | --- |
| [Elm documentation index](https://elm-lang.org/docs) | HTTP 200; plain HTML extraction yields only `docs` | A SPA shell containing compiler-embedded Markdown. The documentation introduction and additional-resource section are separately extracted from static string literals; they are not mistaken for a server-rendered page. |
| [Elm install route](https://elm-lang.org/install) | Redirects to the guide's installation section; HTTP 200 | Substantive server-rendered guide content is preserved and extracted. |
| [Old bare syntax route](https://elm-lang.org/syntax) | HTTP 404 | Preserved as failed retrieval evidence, excluded from substantive reference coverage. |
| [Current syntax reference](https://elm-lang.org/docs/syntax) | HTTP 200; plain HTML extraction yields only `docs/syntax` | A SPA shell with 5,807 characters of embedded Markdown extracted separately without executing JavaScript. |
| [Actual terminal installation guide](https://guide.elm-lang.org/install/elm.html) | HTTP 200 | Substantive guide instructions and platform download references are preserved. |

The SPA extraction is deliberately supplementary. It decodes identifiable multiline JavaScript string literals with `ast.literal_eval`; it does not evaluate the application or claim to reproduce every rendered component. Raw bodies remain available for inspection, and extracted Markdown has its own hash. The documentation index includes links rendered outside the captured Markdown, so the extracted index alone is not a complete page reconstruction.

This is complete coverage of the selected stable compiler documentation and installer README directories. It complements the root agent's guide and official package-reference corpus; it does not claim to archive every Elm ecosystem website. Website references are current snapshots and are not bound to the compiler tag.
