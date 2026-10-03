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
