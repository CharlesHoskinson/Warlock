# Elm shell — first implementation slice

A real Elm `Browser.element` application now compiles and renders through a GTK3/WebKitGTK native Wayland host. Both an ordinary xdg window and a layer-shell surface ran in an isolated private compositor. This is a fixture-only implementation with read-only refresh, not a selected production host or a window-effects authority.

## Implemented

- `Protocol.elm`: private lossless identity wrappers, canonical unsigned-64-bit string decoding, version/kind/source checks and duplicate/bounded fixture rejection.
- `Domain.elm`: immutable connecting/inspection states, a pure reducer, explicit read-only effect descriptions and last-valid-state preservation on malformed messages.
- `Main.elm`: declarative accessible markup, a persistent native event subscription, labeled disabled actions and a refresh command. Derived family rows remain separate from native authority.
- A narrow port adapter and local bundled assets. Elm owns DOM rendering; the adapter forwards messages and observes fixture readiness.
- A C host with an ephemeral sandbox-enabled WebKit context, fixed asset allowlist, CSP, denied external navigation/new windows, bounded allowlisted requests and explicit Wayland surface roles. No compositor IPC, shell execution or application-window effects exist in this slice.

Host sizing uses GTK layer-shell's [documented sizing route](https://wmww.github.io/gtk-layer-shell/). Its [initial commit API](https://wmww.github.io/gtk-layer-shell/#gtk-layer-try-force-commit) can publish state when regular deferred commits are unavailable. These are candidate host integration choices, not a proven explanation of every renderer issue.

## Executed evidence

The latest `build/build-report.json` records compiler0.19.2, GTK3.24.52, WebKitGTK2.52.6, layer-shell0.10.1 and JSON-GLib1.10.8. Strict C warnings, Elm compilation, adapter syntax and two native host test groups pass. Fourteen compiled Elm checks exercise real decoder/reducer modules, including numeric identity refusal, safe-integer distinction, u64 limits, duplicate IDs, malformed observations and read-only effects.

`qa/final-pass-*/report.json` retains the final contract review: strict OpenSpec/traceability checks, all 29 architecture Quint named tests and 3,000 sampled traces pass. This pass also corrected the remaining engineer-week obligation in DEL-002 under the user's outcome-driven execution policy; UI/UX/native contracts and prior frozen reviews remain unchanged.

`qa/native-smoke-*.json` retains every native attempt. Successful xdg and layer cases include a fixture DOM/frame report, independent compositor screenshot, mapped native role, host wait status0 and private-runtime cleanup. The host requested hardware acceleration, but this is not proof that the webview's backend was nonsoftware. The successful engine reported a secure context and no exposed WebGPU API. Native action controls stayed disabled throughout.

Initial layer attempts timed out and remain retained. One real adapter issue was observing the mount node that `Browser.element` replaces. Observing a stable parent fixes that issue. Layer startup still failed until explicit sizing/initial-commit/backdrop integration was applied; the successful combined change is recorded, without claiming an isolated root cause for every adjustment. A temporary diagnostic JavaScript edit introduced a syntax error caught in source review and is preserved among build attempts; the build now runs `node --check`.

Private WebKit AT initialization warned that its registry was unavailable. Actual native accessibility, IME, pointer/keyboard input-region passthrough, host crash recovery, resource budgets and accelerated composition remain open gates. Auxiliary retirement receipts distinguish explicit termination/identity disappearance from a wait-status normal-exit proof.

## Reproduce

Run build and tests through protected QA:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-shell-v1/build.py
```

Root owns serial native QA. The private smoke reuses the reviewed Weston/Hyprland candidate host and exact ABI/library manifests outside this implementation directory; those dependencies are hash-checked before launch. It requires the local frozen QA artifacts, render-node access and user systemd/D-Bus. It does not use or restart the main compositor. `--xdg` chooses the ordinary-window comparison; the default tests a layer surface. Follow-on proof runs must retain prior logs and input artifacts before rebuilding. No native smoke should run concurrently.

## Next slice

Freeze the production envelope and authenticated read-only observation adapter; obtain coherent compositor identities/snapshots before enabling any effects. Measure actual webview acceleration and budgets, and qualify native input/IME/AT. Extend the pure reducer and Quint conformance fixtures with real observation sequences. Compare the Qt host before selecting a production engine. Retained captures and all live window operations remain future independently accepted work.
