# Bounded native menu/viewport integration V8

The full S01-S16 roadmap and right-click contract remain active. This checkpoint
closes the targeted V6 resize/reset failure on a fresh exact native tuple; it
does not establish full feature, wrapper safety, or release acceptance.

## Evidence

- Core buffer guard: `elm-native-buffer-size-v7/component-manifest.json`.
- Rebuilt authority pair: `elm-buffer-authority-pair-v8/qa/build-pair-manifest.json`.
- Private AQ viewport component: `elm-nested-viewport-v8/component-manifest.json`.
- Integration freeze: `elm-menu-native-pair-v8/qa/implementation-manifest.json`.

Protected actual C++ presentation helper: 47 checks plus dimension predicates.
Elm menu replay: 78 checks; inherited 20/27/55, output70 and presenter12 retained.
Full actual Elm/C host compiles. CPU/model evidence is separate from native.

- native: 47 checks, report `/home/hoskinson/omarchy-windows-parity/implementation/elm-menu-native-pair-v8/qa/native-1791092233435555708/report.json`, SHA256 `f4e2a5ecf76b1400c32311760bc3b43ebfcba779401a455be101239edfdcb6ce`.
- regression: 92 checks, report `/home/hoskinson/omarchy-windows-parity/implementation/elm-menu-native-pair-v8/qa/native-1791092311656239871/report.json`, SHA256 `563b30a9b587e060ee8ca19dca37e4dc065bed25f219a722d7cb5f1b84816831`.
- output-regression: 114 checks, report `/home/hoskinson/omarchy-windows-parity/implementation/elm-menu-native-pair-v8/qa/native-1791092426809329808/report.json`, SHA256 `7e329f84a6cd64d725b879fe862fc679ebd717e6956b3d64f88ff7fd5593b20d`.
- menu-reflow: 66 checks, report `/home/hoskinson/omarchy-windows-parity/implementation/elm-menu-native-pair-v8/qa/native-1791092166180880090/report.json`, SHA256 `aa09d08e7ec06d58d0de86d2de766dae694a5605902ee617fba7a2ecd25d961e`.

All four native reports pass and cleanup passes. Counts are overlapping campaigns,
not additive unique coverage. The original parent remains 800x600; the targeted
run shrinks child640x480, grows child960x640 with inner scale2 and restores
child800x600 scale1, without changing the original six-second observation wait.
It verifies fresh authority/menu reopening, inner popup bounds, keyboard-ready
Escape and retirement. The selected V8 AQ mapping and exact plugin are asserted
in actual process mappings; runtime SO selection is not inferred from environment.

Authoritative retained failed report:
`implementation/elm-menu-reflow-v6/qa/native-1791089500194235014/report.json`.
Its original failure, source snapshot and cleanup remain unchanged.

## Next required work

- Actual parent pointer injection and recipient/coordinate checks; current menu
  fixtures inject zwlr_virtual_pointer inside the child compositor.
- Native staged/ACK/queued-commit motion and paired-release fencing, stale idle
  and frame callbacks, pending teardown and transport recovery.
- Nonidentity cursor software fallback and viewport-global-removal scheduler
  bookkeeping, with explicit cursor size/hotspot policy.
- Preserve AQ output identity through owning Mouse/PointerManager for global
  multi-output routing; coordinate with the parallel shared-controller lane.
- Rotation parent campaign remains failed/open; AT, IME, GPU/resource budgets,
  global registry, full window-operation set, release/deployment gates remain open.

The initial README inside the frozen integration tree describes preparation
state; this acceptance note and immutable manifest are the later status evidence.
No main-desktop installation or activation occurred.
