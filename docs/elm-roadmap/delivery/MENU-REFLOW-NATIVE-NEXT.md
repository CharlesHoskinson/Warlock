# Menu reflow native continuation

Thread: 01a101d3-cde7-7370-83b1-3170bdd0c9d1.
The last status-only turn was no progress; this continuation changed production
source and produced new protected build/test evidence. Full S01-S16 and additive
right-click acceptance remain the goal. No release acceptance is inferred.

## Retained failure

`implementation/elm-menu-reflow-v6/qa/native-1791089500194235014/report.json`
is still failed. Native menu reopening/bounds/inner scale checks reached the
restore-mode stage, but AQ's outer 960x640 buffer exceeded its fullscreen parent
800x600 geometry. Cleanup passed. Do not enlarge the parent, relax the reset
wait, discard this failure or replace its acceptance with a smaller fixture.

## Corrections built

`implementation/elm-nested-buffer-size-v7/component-manifest.json` freezes the
actual AQ commit guard, two protected builds, exact captured production/test
sources, dependencies and independent review. Latest build is
`build-1791090614984276025/report.json`; no lost exported parent symbols and
unchanged public headers. It rejects invalid dimensions or buffer/mode mismatch
before swapchain/import/release/frame/attachment mutations. AQ test() remains
unconditional and parent mapping is unqualified. Commit a330275 preserves this
component only; no native acceptance.

`implementation/elm-native-buffer-size-v7/build-1791090562611157328/report.json`
passes 12 extracted production-method checks and the unsafe-guard mutant is
rejected. Only Monitor.cpp.o is replaced; 432 untouched ordered archive payloads
including repeated names and 701 compile dependencies are recorded. Exact core
SHA256 c13e9061375a6e2ecc32cc003f022ab635147472222a585d3463abd12bc8bba4.
Independent review passed and component-manifest.json is frozen; no plugin paired or loaded yet.

## Next integrated tuple

1. Core review/freeze completed; retain its component-manifest.json as the exact base.
2. Fresh authority-plugin derivative from elm-grab-safe-background-v89, rebuilt
   against the exact corrected owning core headers and recorded binary.
3. Fresh AQ parent presentation derivative: common test/commit preflight;
   wp_viewporter binding (stable/viewporter), per-output viewport; separate
   staged/ACKed configure dimensions/state and monotonic callback generation;
   atomic viewport destination + xdg window geometry + buffer commit.
4. Parent pointer normalization uses last committed destination, never newly
   staged/ACKed dimensions; fence ambiguous transition input. AQ absolute motion
   carries output identity but owning Mouse.cpp drops it before PointerManager
   maps across the whole monitor layout: preserve identity for global multioutput
   qualification. Cursor surface/hotspot requires its own mapping policy.
5. Preserve lifecycle/mandatory-Wayland/transport-failure gates. Touch/relative
   pointer/tablets/gestures are currently absent and cannot be claimed.
6. Fresh candidate_host verifies the new AQ build/source/symlink closure and
   loads its private library only into the nested child. Existing v89 host
   prepends the old prefix and must not be reused to imply the new library ran.
7. Run original V6 failed scenario and original native regressions through the
   serialized coordinator/protected launcher on the exact ABI tuple. Require
   actual presentation, input recipient, shrink/grow/shrink, no protocol error,
   original deadlines and ordered cleanup. Keep failed attempts immutable.

Concurrent integration thread owns elm-output-shared-host/qa v146 onward; avoid
editing its source or mutable main ledger. Append per-thread checkpoints only.
