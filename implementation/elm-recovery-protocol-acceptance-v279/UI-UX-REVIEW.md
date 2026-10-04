# Resumed UI/UX release review

Reviewers: existing ux_final_motion, ux_final_navigation and
ux_final_window_behavior. Reviews are read-only recommendations, not participant
usability, executed native tests or release acceptance. The 242 requirements and
417 baseline scenarios remain unchanged; component evidence cannot close a
scenario without its original oracle on the accepted release tuple.

Immediate execution order from the motion and window-behavior reviews:

1. Integrate geometry/menu with durable admission/settlement and one broker,
   allocator and Elm model. Inject failure before admission, after native commit
   and during durable settlement. Observe at-most-once mutation/refusal, truthful
   Unknown and reconnect without automatic replay.
2. Close native stationary-pointer routing after output movement/reverse resize
   and surface commits on the owning pair; presented pixels, pointer recipient
   and keyboard recipient must agree without an extra pointer wiggle. Preserve
   original multioutput51/focus159/cursor195/menu68 identities.
3. Validate ordinary/MAX/pinned/fullscreen and nested modal overlap against the
   precedence table with independent pixel, pointer and keyboard oracles. A press
   blocked by a parent must not leak its release after modal retirement.
4. Run original restore38/recovery34 and dragresize52. Require minimized-family
   paint/input exclusion, correct MRU, retained-to-live continuity and one proxy
   retirement. Preserve original time origins and deadlines, including the
   original two-second restore deadline.
5. Toggle reduced motion mid-transaction. At the next valid presentation
   opportunity decorative motion stops while identity, focus and settlement stay
   correct; no repeated effect or restarted deadline.
6. Exercise actual full/read-only/later-fsync storage, legacy provisioning and
   global old-live-broker revocation. Expired authority cannot mutate or publish.
7. Qualify actual integrated rendering and preview synchronization/revocation.
   Retained Intel/WebGL component results do not establish WebGPU or integrated
   preview safety. Lock, renderer/device loss and late callbacks must reveal no
   forbidden pixels; unlock needs fresh authorized publication.
8. Calibrate and freeze numeric budgets with identical baseline/candidate
   workloads, instrumentation overhead and whole-process accounting. Measure
   native input-to-present distributions, quiescence, resource bounds and power.
   Current calibration-only budget files do not constitute pass thresholds.
9. Test unequal fractional scale, rotation, physical high-refresh, hotplug and
   zero outputs while gestures/receipts are held. Include AT/speech/braille and
   actual IME, notifications during held actions, real applications and human
   journeys. Expert review and DOM semantics do not substitute for these gates.
10. Repeat affected journeys on one source/build/ABI/driver tuple and verify
    offline rollback and draft/window preservation before production activation.

Navigation reviewer findings will be appended in a subsequent immutable packet
if they arrive after this packet freezes. No result is implied by this review.
