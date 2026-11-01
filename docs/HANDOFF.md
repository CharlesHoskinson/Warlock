# Continuation handoff — 2026-10-03 UTC

This document records the state at the Git snapshot. Historical source and proof
packets remain unchanged. The main desktop is not running the latest candidates.

The follow-up completeness audit additionally preserved earlier native helper
builds, QA evidence and configuration backups from `~/.cache`, Brave launcher
integration/libraries, desktop launchers, taskbar/virtual-desktop settings and
activation links, remaining temporary prototypes/diagnostics, and the user's
original focus-bug screenshot. See `evidence/` and the supplemental provenance
inventories. All original 167,261 captured source files were rechecked against
the originals: no changed or missing files, and no new files inside the mapped
roots. All 468 source-inventory descriptors were scanned for external home paths;
the nine remaining references point to installed mise tool dependencies.

## Requested outcome

Complete Windows 11 window-system parity on Omarchy: reliable click-to-focus even
with a draft/modal window open; maximize/minimize/restore; always-on-top pinning;
taskbar icons at the left with useful previews even while minimized; highlights;
smooth drag, resize and animations; snapping and window navigation. Minimize must
not send windows to a scratchpad. Audit completeness and correctness, fuzz the
implementation, and use Quint for the behavioral models.

## Current results and work

### Capture and restore

- V28: 444 CPU checks passed. The original collector passed 169 CPU checks.
- B14 native restore baseline failed: 19 checks reached, 17 passed. Six focus
  actions and three refreshes completed before metadata at about 692 ms. Three
  captures were produced, but no renderer seed/uploads before the original
  two-second deadline. Helpers exited normally; all 15 main preservation checks
  passed. This is not accepted native restore behavior.
- New V29 fuses thumbnail and composed-window processing into one actual ImageMagick
  command per hidden member. It preserves original pixels, cache/current checks,
  helper ownership, cancellation and deadlines.
- V29 passed **462 CPU tests: all 444 original identities plus 18 new applied
  tests**. Focused 18-test proof also passed. No native run or deployment yet.
- Source ready: `window-integration-qa/hidden-capture-v29-source-handoff-v1.json`.
  Candidate: `window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-hidden-capture-fusion-v29/`.
- Next: root source review/freeze, then original 38-check live baseline and
  34-check fault/recovery campaign without extending deadlines.

### Pin, maximize and focus

- Pin campaign A passed its bounded 14 feature checks.
- Bv4 completed B01–B10, including both MAX pin/unpin/return paths, two overlapping
  window clicks and modal focus. It failed B11 because QA incorrectly treated
  `allows_input=false` as an input blocker. B12 was not run. The first ten cases
  do not establish complete campaign acceptance.
- Fresh genuine blocker uses a monocle-inactive window and independently tests
  the no-focus case. Design passed 14 actual named Quint scenarios and 2,000
  traces, then root source review.
- Unfinished collector: `window-integration-qa/pin-native-input-components-v1/`.
  Original 19 CPU tests and new 11 CPU tests passed separately. Source closure,
  pair refresh, handoff, freezing and live tests remain pending.
- Exact core/plugin ABI pairing is mandatory. Frozen failures and original
  first-ten-case assertions must be preserved. No live input-block acceptance yet.
- B13–B24 and broader masks, ignore, scroll, transfer, outputs, exclusive/render
  and menu predicates remain open.

### Taskbar, popup and process lifetime

- V9 actual Qt-signal fault component and five V10 CPU components independently
  accepted. These do not establish real Quickshell or reliability acceptance.
- Popup/input source composition: 24 actual named Quint cases/2,000 traces,
  28 decoder/controller checks, one receipt-loop check and six QML-as-JavaScript
  checks passed source review. Owning-header native observer build passed 612
  dependencies; it has not been loaded.
- Unfinished real private-Quickshell wrapper:
  `window-integration-qa/pin-private-qs-native-v1/`.
- Full campaign Process JSON would exceed the unchanged 16 MiB input limit.
  A smaller exact runtime-source projection is being prepared while retaining
  the complete campaign inventory for preflight and terminal verification.
  That projection still needs root review.
- `source-ready.json` and `process-runtime-inputs.json` are not generated.
  Latest materialization edits postdate `cpu-report.json`; a fresh durable
  report has not been published. Do not claim updated acceptance from the old
  report.
- Required actual changed/same/cancelled/stale routes must pass before the fixed
  reliability campaign (two Quickshell processes × three slots, 12 helpers).
  Cold baseline and four malformed public-retire stimuli do not substitute for
  those routes. Preserve original helper/worker/receipt/cursor timeouts.

### Quint coverage correction

The default CLI selector only chooses names ending in `Test`. Historical restore
and producer reports had counted 45 and 14 scenarios that it actually skipped.
Both exact models now passed explicit **45 and 14 actual named runs**. Original
invariant traces were retained separately. Earlier incorrect reports remain as
history; do not cite their nominal counts as executed coverage. The independently
selected pin 35, transfer 20, hit 24 and original collector 205 proofs were
checked and unaffected. V29 retains 503 actually executed named scenarios across
39 models; this is retained evidence, not 39 newly rerun models.

## Remaining acceptance checklist

- [ ] Review/freeze V29 and pass native restore baseline38/recovery34.
- [ ] Finish genuine input-block/no-focus components and remaining pin campaign.
- [ ] Complete real Quickshell popup/input/process routes and reliability.
- [ ] Finish original 52 drag/resize/reload cases; earlier held matrix reached
      three passes and failed its fourth minimized-preview movement case.
- [ ] Finish cancellation and reduced-motion native validation.
- [ ] Complete multi-display transfers, hardware cadence and accessibility
      (including audible/braille behavior and compatibility).
- [ ] Run final combined regression against one coherent source/ABI tuple.
- [ ] Deploy accepted changes and verify existing windows and the user's flow.
- [ ] Complete the full requirements audit; passing bounded subcases is not full
      Windows parity.

## Operations

All agents held writes before capture; no active GUI/build/helper process was
reported. Snapshotting made no installed changes. The saved automatic goal was
still marked blocked at the last check; automatic continuation was not rearmed.

The live source roots are still outside this repository. Original absolute paths
and frozen hashes are preserved. Do not modify old proof packets to accommodate a
new location or implementation. Prepare a fresh reviewed derivative for changes.

Run every QA/freezer/proof through the original protected launcher:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  /home/hoskinson/window-integration-qa/qa_run.py -- \
  /usr/bin/python3 -B /absolute/path/to/the/reviewed/runner.py
```

Root owns serial GUI launch. Require a live verified parent Wayland socket,
private UID-owned nonsymlink 0700 runtime directory, dedicated QA slice/scope and
inherited core limit 1, no Xwayland unless X11 is under test, no DRM fallback.
Stop clients/helpers first, verify empty clients and unload modules, then stop
Hyprland/Weston/private bus. Process disappearance is not proof of normal exit.
All five crash handoff changes remain mandatory. Never revert the crash-watch
override, grim or keyring builds. Do not close the user's drafts or restart the
main compositor as an incidental QA step.

## Current continuation — October31,2026

The user armed the full original Warlock goal and authorized coordinated development beyond setup. Current checkout `/home/charl/code/Warlock` uses the existing authenticated `warlock-20261031-setup` run with ten assigned identities; root is the only coordinator and protected executor. Read current [STATE](warlock-build-loop/v2/STATE.json), [independent readiness](warlock-build-loop/v2/readiness-review-20261031.json) and [current slice record](warlock-build-loop/v2/applications-window-feedback-20261031.json), not the historical Python slice as current production ownership.

Existing Elm Applications feedback source is being integrated through actual source/compiled/pixel regression. Original UI007 remains partial for native/keyboard/AT obligations. All original 242/417, deadlines, failed evidence and stopped probes remain preserved. The private pinned GHC/Cabal SDK and current package checks are now qualified as recorded below; persistent native integration, current DRM/native capability and external Graphify/wiki/Muse runtime remain absent or unready here; scoped existing Elm CPU/component readiness does not promote those gates. No main desktop was changed. Host goal lifecycle is authoritative; no duplicate background coordinator or replacement timer was launched.

Whole original ELM-ARC-005 / architecture-005 is now accepted on immutable tested source `d3a57508ab7974e96e9a631bcd1f5b39b1f6d1d4`, using the original permitted bridge trace. Read [the acceptance](warlock-build-loop/v2/authority-tuple-acceptance-20261031.json), [independent review](warlock-build-loop/v2/authority-tuple-review-20261031.json) and full retained trace. UI007 source and rendered component are implemented/published in `d60fc181d`; its original native/keyboard/AT remains partial. The full host goal stays active; no source-bound verdict transfers to the unintegrated Haskell port or release.

Whole original REV005 / requirement-ownership is now accepted after a real admission bug repair on source `20df98fefb509ca935d34dc044d0e6664d17a45e`. [Canonical acceptance](warlock-build-loop/v2/registry-admission-acceptance-20261031.json) and [review](warlock-build-loop/v2/registry-admission-review-20261031.json) preserve baseline24 wrong admissions/48 failures, passing35 transactions/213 assertions and197 plugin regressions. This is administrative acceptance only. All242/417 remain intact; next advance pinned Haskell tooling and a concrete original backend receipt/cancellation slice without repeating stopped native probes.


Whole original ARC007 and all five exact receipt scenarios are now accepted on immutable source `01ad95b87c7550c8179fd13e907625a5a9b57cb4`. The real Elm `Cancelled` gate/router defect is fixed: matching cancellation settles only its request and its local reservations, while the other request remains unchanged. [Acceptance](warlock-build-loop/v2/receipt-state-acceptance-20261031.json), [independent review](warlock-build-loop/v2/receipt-state-review-20261031.json) and [receipt reference](warlock/reference/receipt-states.md) preserve the mixed 120-failure fixture run, clean 112-failure RED and passing 2,451 assertions/80 matching bridge receipts. Fourteen distinct directed model tests and10,000 sampled50-step traces pass with seven positive witnesses. This is the original permitted bridge-state verdict; physical cancellation/retirement, ARC012, Haskell protocol port and release remain separate.

The private pinned GHC 9.6.7/Cabal 3.12.1.0 SDK is installed without system or desktop changes. The six actual Haskell packages now pass protected offline production `build all` and all 24 controlled suites (36 invocations), with no timeout or forced cleanup. [Current package readiness](warlock-build-loop/v2/haskell-toolchain-readiness-20261031.json) retains the first missing-hsc2hs resolver failure, exact source/revised metadata pins, SDK inventory, plans, freezes and all fixture logs. At that historical package-readiness tuple, the bootstrap was one-frame; no persistent GUI backend or genuine native issuer/ACK path was established. The bounded November1 follow-up below supersedes the bootstrap behavior. Next implement owned persistent authenticated Haskell session delivery and an explicit bridge to existing Elm policy. Keep operations empty until actual native issuer/admission/effect/certificate qualification; preserve HOSTSTOP2 and the main desktop.

Current participant is `.warlock-contributor/receipt-state-integration.json`. The initial receipt record and its root-tooling ownership reconciliation are retained; only declared team-owned sources were adopted, and adoption is not counted as a new production fix. Root remains the only coordinator/protected executor. Completed worker identities and launch receipts are not evidence of still-running jobs. The host goal remains active; no new background coordinator or timer was started.

### November1 bounded authenticated bootstrap

Actual source `367a4899023340bc9cfeb2765a90b7ed37e58109` fixes the one-frame Haskell route and its retained-peer normal-exit defect. Every frame reuses the same approved session/guard/registration and original deadline; the owned nonreaping exit observer ends the retained write half only after confirmed exit and is joined inside scope. Protected production build and all 25 suites / 37 invocations pass, including14 public ordinary-library cases. [Evidence](../implementation/warlock/qa/evidence/persistent-auth-20261101/report.json) retains both production failures, compile/model preparation failures and final complete credential traces. [Reference](warlock/reference/authenticated-bootstrap.md) and [independent dispositions](warlock-build-loop/v2/persistent-auth-review-20261101.json) separate literal scenarios from whole-EARS acceptance.

Whole DEL010 remains partial because real cross-user credential evidence is missing. Verified official uidmap packages remain uninstalled after the single graphical authorization timeout; no retry or privilege workaround occurred. The unexecuted `tools/check_auth_cpu.py` draft is preserved unstaged and archived as a draft, not dispatched or qualified. Original 242/417, deadlines, failures, HOSTSTOP2, concurrent drafts and the main desktop remain preserved. Muse's historical scheduler is absent on this host (inactive/not-found); the current host goal stays active. Next reproduce the source-derived Elm refresh-before-pin-save race through its actual owning route, retaining full TEA003 obligations and the explicit Unknown recovery path.

Independent review now accepts `delivery-010`, `peer-wrong-session` and `peer-approved-session` on the immutable tested source. Whole ELM-DEL-010 remains partial for its separate required cross-user trace; these three scenario verdicts are not a whole-EARS, native GUI or release closure.

Publication reconciled concurrent remote Lacquer presentation and UI007 restore-context commits through an ordinary conflict-free merge. None of the 164 reviewed authentication inputs changed. Preserve those contributors’ source/evidence; refresh the next pin-save investigation against the merged Desktop source. The actual HTTPS remote is named `origin` on this host.

### November1 whole frontend effect contract

Whole original ELM-TEA-003/tea-effects is independently accepted on actual source `b6bfe6146cdbd4a9c3eae06ddc898c93436f5e70`. The real Pins/Desktop fix prevents an earlier read from retiring a later save, keeps conflicting pin controls disabled, and preserves matching Saved and deliberately correlated Unknown recovery. [Acceptance](warlock-build-loop/v2/tea-effects-acceptance-20261101.json), [review](warlock-build-loop/v2/tea-effects-review-20261101.json), [reference](warlock/reference/pin-save-causality.md) and [evidence](../implementation/warlock/qa/evidence/tea-effects-20261101/report.json) retain the 1,531-check / 96-failure RED and passing7,023 checks, three roots/five fixtures, 26 named tests and two separate10,000x50sampled models. All three clauses were qualified; there is no native GUI/input, AT/IME, persistence or release transfer. The main desktop and concurrent drafts remain preserved.

Next implement the real Haskell catalog/pins backend and Elm bridge under ARC003. Existing Haskell codec/framing admits only v1/v2 / 64 KiB and lacks catalog/pin variants; actual Elm uses v3 and historical catalog permits 1 MiB / 2,048 entries. Private UI HTTP/server composition is absent. The named private T3/T4 source-decision artifact is not in this checkout/Git; the adopted direction remains recorded in contributor redesign-flow: private Elm/WebKit plus Haskell UI / local HTTP owner, one host-side Haskell native authority, nativeOperations empty. Reconcile the concrete shared contract in the already authorized preparation scope and implement an actual production entrypoint, not a translator/prototype or silent truncation. Applications Refresh is the first action; durable pins read/write and full GUI composition remain the full target. DEL010 cross-user evidence and original native/release obligations stay open.


### November1 actual Elm/Haskell application stream

Current participant `.warlock-contributor/ui-backend.json` declares whole ARC003/architecture-003 and DEL011/delivery-011 plus arbitrary-path-denied. The [shared contract](warlock-build-loop/v2/shared-desktop-contract-20261101.json) is a newly recorded reviewed source contract, not recovered bytes from the missing historical private decision. Native v1/v2 retains64KiB; trusted Desktop profile validates complete131072-byte Main commits before any handler, with two path-free allowlisted application methods. Actual catalog roots and fixed private CAS pin store are Haskell. Main has exactly `incoming` and `surfaceCommits`; all GUI remains Elm.

The real2048-entry response first exposed an863317-byte presentation defect. Elm now pages all actions with explicit range/total/navigation, switches to a disclosed compact mode for long metadata, and constructs only visible entry controls. A separate32-case owning-route RED exposed transport poisoning after local refusal; exact current-bound application-only unsent cutoff now leaves the next deliberate action available while preserving Unknown recovery, existing batches and native refusal semantics. No byte/deadline limit or fake presentation acknowledgement was introduced.

[The retained evidence](../implementation/warlock/qa/evidence/ui-backend-20261101/report.json) passes actual offline production build and all27suites/39invocations,55 authenticated malicious cases and256pure generated cases. The same compiledMain passes8,010checks with401complete ordered frames, all2048entries over257pages, actual pinSaved/restart, and32names of512UTF16units/32pins with96management actions over129compact pages. Root also passes the unchanged7,023earlier Elm checks,21new guard contracts across32seeds,26named tests and two10,000x50 samples. All six Haskell attempts and the focused32-failure RED remain retained; both180-second workload failures stay failures. Original ARC003/DEL011 and all3scenarios still await independent review against the full immutable source commit.

Private HTTP/WebKit provenance ownership and persistent view-disposition lifecycle remain mandatory next work; the bounded backend does not mint GUI admission acknowledgements or establish a persistent desktop. Native issuer/GUI/input/AT/IME/resource/release obligations remain open. DEL010 realcrossUID evidence is still missing, uidmap remains uninstalled after the oneaskpass timeout, HOSTSTOP2 remains in force, and the unexecuted foreign `tools/check_auth_cpu.py` draft is untouched. The host goal stays active; all registered/completed worker identities are distinct from running processes.
