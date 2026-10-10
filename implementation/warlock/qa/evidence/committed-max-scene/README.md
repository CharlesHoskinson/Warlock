# Committed MAX window scene and native input

Rendering and MAX input now share a native window-order snapshot. The renderer captures structural window, output, surface/subsurface, popup, geometry, input-region and transform facts, paints the captured native order, and publishes the snapshot only after a successful output commit and exact unchanged structural dependencies. Native hit traversal consumes that committed order only while its weak owners remain alive and the facts still match. Native hit receipts carry the consumed scene revision. Scene fact/dependency counters and diagnostic render traces remain separate.

The original two-MAX journey passes 73 native checks and normal cleanup. Included-point paint and hit use scene **4** and the upper GTK root. Excluded-point paint and hit use scene **5**: upper pixels remain while the real press reaches the lower GTK root. Releases return to those same GTK press owners; both MAX return placements recover. The 81-check pointer/keyboard pin/MAX regression also passes on this tuple. These observed revisions are specific to this recording, not constants in the implementation.

The new native press guard prevents a stale MAX scene from forwarding a new press to cached pointer focus. Suppressed presses have bounded release suppression; accepted press releases keep their existing route. Layer focus, session locks, owned grabs and pointer constraints retain existing handling. The native recordings qualify accepted releases and the static input-hole journey, not all stale/failed-frame or cache/grab/button race schedules.

## Evidence and remaining acceptance

`manifest.json` binds current source hashes, core/plugin/aquamarine, the unchanged compiled Elm/host output and all reports. Actual images and GTK pressed/released/native-focus observations remain separate from the committed-scene receipt. The read-only scene API uses the existing authenticated native session binding and explicit protocol version; it grants no effect authority and exports no internal pointer addresses.

The source change preserves 430 archive members, existing public headers/object layouts and existing strong exports. A private `CommittedScene.hpp` and its explicitly recorded added exports are compiled into the matched renderer/hit/button core and authority. Only that qualified pair is used. Older pin/MAX and renderer sources are retained by their exact source/object provenance, including XDG-origin and client-maximize fixes.

The installed quint-llm-kit execute-spec workflow uses the unchanged `max-overlap.qnt`: executable initialization, seven named cases, three positive witnesses and 1,000 sampled 30-step safety traces before and after implementation. Its stale-paint rejection is a formal design constraint, not a substitute for physical button-race evidence.

ELM-REN-015 / `max-input-region` remains **partial** pending independent original disposition. Shared identity is observed for this native window-plane recording; output presentation/fences, all transformed/modal cases, explicit passthrough/no-activation exceptions, stale/failed commit and button/grab/layer/retirement schedules, multi-output changes and resource bounds require further native qualification. Native AT, full family/fullscreen policy and release packaging/rollback also remain open. This is not full constrained-scene or release acceptance.

## Retained failures

Initial compile reports retain a missing frozen renderer `.inc` dependency and a serializer helper/indentation error. The build now verifies and copies only the required immutable `.inc` dependencies, and the serializer compiles with warnings as errors. No failing build or stale pair was used for native qualification. Their reports remain under the original local run directories and hashes in the manifest. The earlier immutable input-hole failure remains in the preceding max-input-region evidence.
