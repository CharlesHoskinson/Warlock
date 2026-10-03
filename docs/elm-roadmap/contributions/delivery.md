# Delivery, release and security contribution

Planning only; 28 atomic EARS requirements are in [delivery.json](delivery.json). Neither documents nor historical CPU/formal evidence qualify a deployed Elm host. The immutable handoff, original native deadlines and five crash-control changes remain binding. This contribution owns packaging, security boundaries, recovery and release operations; presentation/rendering requirements remain separately owned.

## Release order and stop gates

| Stage | Dependencies and delivery work | Stop gate |
| --- | --- | --- |
| P0 baseline | Hash archived failures and named scenarios; map unchanged deadlines; freeze hardware/workload budgets, owners and effort | Missing baseline or unset performance budget blocks comparative host selection |
| P1 host | Build isolated GTK/WebKit and Qt candidates; record GTK/layer-shell major compatibility, Qt initialization, engine/driver tuple, runtime libraries; prove roles, IME, accessibility and bridge confinement | Incompatible dependency graph, unsafe roles, budget failure or absent actual hardware-acceleration proof blocks a GPU claim; retain QML if no full-GUI host passes |
| P2 policy/security | Versioned peer-authenticated allowlisted bridge, least authority, keyring references, redacted logging, schema validation and migration; offline assets and host network policy | Unauthorized effects, remote code execution, secret exposure or unrecoverable settings blocks all migration |
| P3 taskbar/switcher | Qualified host/bridge; feature selector with one owner; changed/same/cancelled/stale routes and native Alt ordering | Pure reducer evidence cannot release an unqualified native slice |
| P4 capture/motion | Accepted consumer, family capture and native leases; original baseline38/fault34 and source-stop/reversal evidence | Missed original deadline, leaked buffer/helper or stale GPU resource blocks preview/motion migration |
| P5 full shell | P3 plus P4 for previews; complete pin/input/popup/drag52, IME/AT/output matrix and user flows | Missing named behavior or assistive-technology evidence blocks full replacement |
| P6 release | All mandatory gates; pinned offline clean builds, SBOM/license review, coherent runtime/ABI tuple, recovery and interruption drills | Any open mandatory gate or unproven rollback blocks production activation |
| P7 feasibility | Separate scope/resources decision; protocol/app/backend and license inventory | No explicit go decision or credible compatibility proof prevents P8 |
| P8 implementation | P7 go decision; separately staffed native compositor project | Equivalent parity plus seat, output, Xwayland, portal and recovery gates are required; shell release never waits on optional track |

Start with a user-owned isolated host, then migrate taskbar/switcher, previews/motion, remaining full-shell components and finally the accepted release. Feature selection must prevent duplicate owners of surfaces, global shortcuts or effects. Keep the working predecessor selectable until the replacement passes its native slice and rollback rehearsal. Production authorization is the final action after the reviewable accepted tuple and recovery artifacts exist; this planning work performs no activation.

## Reproducible and supported artifacts

Pin the stable compiler reference 0.19.2, exact Elm application dependencies, compatible test runner, adapter, host engine, native libraries and toolchain in one hashed input manifest. Verify compatibility with actual builds rather than relying on matching version labels. Build Elm optimized production assets through supported ports without generated-internal coupling. Cache verified dependencies to permit an offline clean build; compare two independent clean-environment artifact manifests and investigate every difference before release.

Split hashed Elm assets, host/authority binaries, user settings and release selection. Install to reviewed user-owned version directories with atomic activation and recovery metadata; never edit `/usr/share/omarchy`. Native compositor/plugin artifacts require an exact frozen accepted pair before load. Rolling Arch updates therefore trigger pair preflight and host/driver requalification rather than an assumed compatible partial update.

Initial support is Arch Linux with Omarchy. Ubuntu is a possible separate distribution target, not an inferred benefit of using GTK or Qt: establish distro package availability, major versions, layer-shell behavior, engine security update policy, hardware drivers, keyring/authorization, service integration and full native acceptance before claiming support. SBOM and license ledger cover compiler, packages, native substrates, host engines, transitive bundled libraries, fonts/icons and other assets; preserve required notices and address redistribution obligations before shipping. Research corpus permissions do not license every copied asset.

## Security and state

Elm and the adapter receive only necessary snapshots and bounded opaque frame references. A local bridge authenticates peer credentials and session lifetime, then validates allowlisted operation schemas and freshness at the native effect boundary. Local identity alone does not make every method safe. Web content cannot execute arbitrary commands, select arbitrary native file paths or turn a native bridge into a general system API.

Package all executable assets locally, verify their hashes and block network fetches/navigation at the host boundary. Enforce CSP without remote origins, eval or unapproved inline scripts; account for the selected engine's local origin semantics in the negative tests. Keep legitimate native integration such as update retrieval outside renderer authority and subject to its own explicit policy.

Settings use a versioned schema, atomic writes, validated migration and preserved old copy. Downgrade chooses a compatible old copy and never guesses how to interpret a future schema. Credentials stay in the established system credential service; native authorization owns the askpass flow. Do not send passwords through Elm/JS or write secrets, drafts or capture pixels to ordinary diagnostics. Existing Files Quint semantics and authorization remain intact.

## Hardware acceleration and optional WebGPU

Available inventory reports Intel Arrow Lake-S with i915 and NVIDIA RTX 5090 Max-Q with nvidia, plus installed Vulkan driver packages. This inventory is not an accepted rendering probe. Qualify the selected pinned engine/driver combination on actual hardware: record selected adapter, device/API/backend, hardware versus software status, GPU submission/presentation evidence, capture transfer cost and whole-process latency/memory. A browser flag, package presence or reducer speed cannot demonstrate native-host acceleration. Cover relevant adapters and multi-output configurations rather than assuming the discrete GPU is selected.

GPU acceleration remains available when the chosen host and target tuple prove it. Explicitly disabled/unavailable acceleration selects an honest software fallback with independent budget evidence; report a failed budget rather than claiming equivalent performance. Engine acceleration and WebGPU are separate capabilities. Optional WebGPU requires an actual qualified adapter/device and limits report in that native host, a supported non-WebGPU route, and device-loss/restart tests that retire stale leases, invalidate frame generations and reconcile before effects resume. Feature/API absence retains the accepted route; it does not waive mandatory shell behavior.

## Recovery and operational ownership

Rehearse host death, authority death, reconnect, suspend/resume, output hotplug, interrupted upgrades and downgrade with populated settings and open drafts. Fresh epochs and native snapshots precede mutating requests after restart; do not replay uncertain effects. Ship an offline command-line rollback path independent of the webview and avoid restarting the main compositor or closing drafts as incidental recovery.

Private QA uses the protected `qa_run.py` launcher serially. Close owned clients/helpers first, prove normal exit and resource retirement, unload owned modules, then stop private compositor/bus. Process disappearance is not a normal-exit receipt. Preserve QA runtime ownership, parent socket, crash-control rules and fixed helper/worker/receipt/cursor deadlines.

A release owner keeps the coherent gate ledger and rollback responsibility. Assign host-engine/security dependency triage, periodic engine upgrades, build-cache/artifact retention, keyring/settings migration review and regression owners. Each engine or driver update has a scope-of-requalification decision; urgent security fixes still require pair integrity, bridge confinement and recovery evidence. Tabletop an urgent engine patch and a broken activation before release.

## Effort and user acceptance

Carry the roadmap ranges: P0 1–2, P1 2–4, P2 2–4, P3 3–5, P4 4–8, P5 5–9 and P6 2–4 engineer-weeks (19–36 total before contingency). Reserve 25–40% contingency, re-estimate at host choice and capture proof, and account for serial native campaigns, hardware access and accessibility expertise. Optional P7 is 3–6 and P8 20–50+ engineer-weeks with separate resources. Delivery/security tasks are included in these ranges rather than additional promised calendar dates. One developer follows dependencies; additional engineers cannot parallelize the serial GUI campaign or remove the host/capture critical path.

Final user acceptance records existing window/draft inventory, demonstrates left taskbar/group previews, click focus with drafts/modals, maximize/minimize/restore, pin, snapping, switcher cancellation and keyboard/IME/accessibility paths, then compares the preserved inventory. User acceptance complements the named technical gates and does not substitute for them. Maintain one ledger with separate CPU, replay/fuzz, Quint, native, hardware, user-flow and release verdicts bound to source/runtime/ABI hashes.

## Integrated estimate authority

The contribution ranges above are preserved first-draft inputs. The reconciled [roadmap phase ledger](../ROADMAP.md) supersedes them for scheduling, after independent audit and scope updates. Do not use a contribution table as an alternative delivery estimate.
