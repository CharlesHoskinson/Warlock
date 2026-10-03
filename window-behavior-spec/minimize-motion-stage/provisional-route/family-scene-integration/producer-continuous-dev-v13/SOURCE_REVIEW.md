# C1 V13 source-stage review

Fresh candidate: producer-continuous-dev-v13. Frozen V10, accepted V12 primitive/checkpoint, main configuration and every native packet remain unchanged. No renderer/compositor/app was launched. The C++ Renderer command fixture includes the real implementation with its main excluded and never connects EGL or Wayland.

## Changes

CommonTrajectoryPlan.hpp computes one duration intersection across at most64 outputs ×64 ordered members, then constructs an unchanged V12 FamilyTrajectory per output and refuses any duration change or unrepresentable interval. Duration remains double seconds; only bounded monotonic integer differences are converted to elapsed seconds. No duration is cast to integer nanoseconds.

CommitLedger.hpp adds per-member analytic velocity and immutable frame timing/epoch. It privately records every issued SceneSample; submission requires exact sample equality and consumes it once. The retained pending frame, successful swap and existing current-output presentation gate store the same geometry/velocity pair. Retarget planning validates exact latest accepted output generation/token/epoch/source order, computes all curves and old-origin allocations before atomic token advancement, then moves the complete plan. Unsafe plans retire without new token/authority. Generic legacy retarget cannot bypass an active continuous plan. Duplicate start never resets a running epoch.

Renderer.cpp selects continuous motion only for ordinary mode. One output sample from the common batch time supplies both GL member drawing and submitted frame. An unconditional post-draw binding check includes velocity and timing. Ordinary telemetry frameKinematics and state.kinematicRecords derive from immutable frames; original diagnostic/member JSON remains exact. Retarget clocks are shared; initial readiness uses zero derivative. No source/cache/texture upload is added for reversal.

## Preserved diagnostic and ownership paths

Pixel/shader/coverage/readback/backend/library/pipeline headers and verifier code are byte-identical to V10. Original linear mix, static geometry, diagnostic sample/validate commands, member JSON, drawQuad/prefix/readback/upload and GL retirement methods remain exact. prepareFamily adds only an ordinary-continuous refusal guard. Diagnostic mode stays const and cannot start/promote native motion. Existing discarded feedback, swap failure, source identity, output generation, timeout, reduced-motion cancellation and normal retirement paths remain required.

Three inherited source-byte assertions were updated because they asserted complete old Ledger/ordinary command byte identity. Their pixel/pair/shader/resource checks remain; 12 explicit preservation and immutable-binding source tests replace the incompatible claims, together with unchanged original80 ledger and73 family consumer checks. All initial preparation/model/build/source-test failures are retained. No raster oracle or numeric tolerance was changed.

## Evidence and limitations

The integration contract/model passed before runtime implementation. Focused tests cover exact origin pairs on40 repeated reversals, mixed displayed output states,64 members across4 outputs, forged geometry/velocity/order/epoch/generation/token, one-use samples, early/stale/discarded feedback, failed swap, global empty duration intersection, missing outputs, zero/unsafe duration, stale clock and duplicate start. The unchanged V12 numeric suite replays2,012,523 checks/2,000 random families. The full inherited offline suite includes all old consumer/pixel/shader/formal gates.

source-ready.json pins source/binary bytes, full modes, links, inherited1847 V10 inputs, V12 primary sources, compiler preprocessing dependencies and loader traces. ldd is trace-only before initialization. It is a review packet, not native authorization. Actual runtime maps, diagnostic44 pixel oracles, ordinary/reversal/mixed-output/reduced-motion campaigns, all main preservation and normal helper lifecycle gates remain pending root's fresh private harness. Mathematical C1 does not establish physical display cadence. Browser V9 strict deleted BrowserMetrics failure remains separately retained.
