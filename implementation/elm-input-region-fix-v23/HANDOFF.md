# V23 handoff

## Problem and change

V22 failed `inputHolePassesPointerToUnderlyingMAX`: the peer's committed native
draw contained its real GDK input hole, while actual pressed/released events
still reached the opaque peer at a point inside that hole. Native teardown
completed with `cleanupPassed=true`. Preserve
`../elm-input-region-v22/qa/native-1791066600635179376/report.json` and its
associated evidence as the failed baseline.

The owning hit tester returned the first eligible bounding-box window before
examining client input regions. The input manager then restored its main
surface when the input-aware lookup returned no surface. That fallback is
also used for compositor decorations; removing it indiscriminately could break
border or decoration interactions.

The new `acceptsPoint` predicate first uses the existing input-aware surface
lookup. A point within the Wayland client's current geometric content box with
no eligible surface rejects that window candidate, allowing the existing stack
search to select the underlying window. A point outside client content keeps
existing border/decoration eligibility. X11 behavior is unchanged. The
predicate is used in the three pinned, floating and tiled bounding-box branches.

## Exact source ancestry

Latest owning source inherited by V20:

`../elm-minimize-lifecycle-v14/build-1791060004170871924/inputs/src/desktop/state/ViewHitTester.cpp`

Ancestor SHA-256:
`af35cff65abddce2de7110a41716dbf45818429594f960c0db71b48df5dd699a`

Candidate:
`candidate/src/desktop/state/ViewHitTester.cpp`

Candidate SHA-256:
`01a3130fde8028d8872930383ba6cae610c690b38a3c39159cf75f2246afc2fa`

V18, V19 and V20 replaced renderer objects, so the V14 frozen hit tester remains
the correct source ancestor. Loading a plugin requires the exact frozen
core/plugin ABI pair; source similarity is insufficient.

## Recorded verification

`qa/native-1791066870280313454/report.json` reports 97 passing checks and
`cleanupPassed=true` and `mainDesktopActions=false`: 84 original checks plus
13 new region checks. Original single-output regression identities are
preserved. Added receipts establish opaque green pixels at the hole; a native
draw that excludes that input point; actual underlying MAX pointer/keyboard
delivery; independent peer delivery outside the hole; retained input
immutability; and full-region restoration with peer delivery.

This report is a private, single-output, scale-1, transform-0, animations-disabled
campaign. It does not establish production performance, presentation,
multi-output behavior, complete native input policy or release acceptance.
The root integrator owns final source-closure review and evidence-ledger updates.
No installed desktop changes were made. The frozen native compositor SHA-256 is
`726ed5f8951dad8546989c3fddaa36413572e1c1b3b84c51285ac60401f9bbc7`.

## Open gates

- The new input-hole fixture qualifies the pinned route. Unpinned floating and
  tiled branches changed in source but need independent hole-fixture acceptance.
- The input manager's main-surface fallback remains unchanged. Fullscreen/MAX
  selection paths with a hole in the selected fullscreen window need separate
  policy and native qualification.
- Popup lookup defaults to bounding-box selection in `windowSurfaceAt`; real
  popup input masks need a separate fixture and input-aware policy review.
- Existing surface lookup uses goal-position coordinates while client content
  classification uses current geometry. Animated movement, resize and offsets
  require coordinate-mapping qualification.
- Border resizing, compositor decorations and decorated/content boundary points
  need direct native regression. Preserving the old outside-content path is an
  implementation choice, not acceptance evidence for all decorations.
- Buffer/viewport mapping, fractional scale, rotation, output change and
  multi-output scene admission remain open.

Keep original observation/helper timeouts and all prior accepted/failed
packets. Any further mutation requires a fresh derivative and protected serial
native campaign; never weaken assertions to accept the old routing defect.
