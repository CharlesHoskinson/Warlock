# Cursor extent V22/V24 and remaining stationary-input failure

The scale-only native cursor clipping defect is corrected in a fresh owning core
and exact authority-plugin pair. No installed desktop or compositor was changed.

## Defect and source correction

Aquamarine's nested cursor plane advertises an unlimited size. The owning core
allocated that buffer using raw cursor-image dimensions while its renderer drew
image dimensions divided by image scale and multiplied by monitor scale. A
24×20 cursor therefore clipped a48×40 rendered image after monitor scale1→2.
V21's fresh single-component color oracle reproduces the failure on the original
core/V17 AQ tuple, excluding the unrelated cyan wallpaper pixel in V20. Its45 CPU
checks include duplicate-cursor rejection and replay of actual retained captures.

V22's private cursor extent helper calculates complete scaled/rotated pixel
bounds, retains finite plane sizes when the rendered cursor fits, and rejects
invalid/overflowing inputs and finite-plane overflow for software fallback. It
passes54,462 deterministic sizing/cap/invalid-input checks; the old raw-size
mutation fails. These are CPU claims, not native rotated-display acceptance.

The incremental core replaces only `PointerManager.cpp.o` in the frozen V7 core
archive. All432 other ordered object payloads are byte-identical. The original
owning pointer object is independently matched to the ancestor archive. Original
source/archive/binary hashes and captured compiler/dependency closure are kept.
V23 rebuilds the unchanged authority against the owning headers and binds it to
this exact core; native menu QA verifies that plugin mapping on the new core.

## Protected native qualification

- V24 cursor:180 checks pass through original800×600, shrink640×480, scaled960×640,
  restore800×600, same-pixel-mode scale1→2 and scale2→1. Existing stationary cursor
  pixels, hotspot/extent, exact GTK recipients after motion, custom/blank and
  movement checks pass. The previous scale-only body bounds303,228,327,248 become
  exactly the expected303,228,351,268.
- Original parent-pointer menu:68 checks pass on the V23 core/plugin and V17 AQ.
- V25 original parent held-button lifecycle:105 checks pass on the V23 core and
  V17 AQ, preserving all original coordinate and quit/EOF/refusal recovery cases.

All native campaigns above exit with normal ordered cleanup. V24 and V25 slice
manifests bind source/report/artifact hashes and the new exact pair. V21's freeze
packet references that pair as the comparison target; its failed native run used
the earlier V8 core/V17 AQ, as recorded in its actual native maps and host inputs.
No component count certifies an entire sprint or release.

## Newly exposed remaining defect

The additive V26 campaign presses/releases at the unchanged parent pointer point
after each geometry change, before any new pointer motion. Shrink, pixel-mode
scale and restore cases pass, but same-pixel-mode scale1→2 fails at the original
six-second deadline. The cursor pixels remain correct, while actual GTK physical
press/release receipts are296,217 rather than expected137.5,98 at parent317,238.
Normal cleanup passes. The failure/source/screenshots are immutable under
`implementation/elm-parent-stationary-click-v26/qa/native-1791097090711114043`.

Next: retain the parent pointer's normalized coordinates and owning output through
logical monitor-layout changes, invalidate them on focus/device retirement and
relative/programmatic movement as appropriate, and test actual stationary clicks
and output routing on a fresh exact core/plugin tuple. Parent configure fences,
capability loss, shared-shell integration, multiple outputs/rotation, physical
hardware, AT/IME, budgets and full S01–S16/C00/release obligations remain open.
