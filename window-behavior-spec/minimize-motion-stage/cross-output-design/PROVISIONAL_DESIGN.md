# Smooth reversal while metadata is pending

Current836 retains exact pixels/rectangle but serial family freeze/query/preparation produces a visible64–120+ms hold. The next visual contract must preserve continuous motion without granting a requested but unvalidated intent native authority.

`provisional_motion.qnt/test` specifies8 named scenarios and2000 samples. A captured same-identity request retargets retained pixels from the current global rectangle immediately toward the retained original decorated rectangle/taskbar target. It emits no native ready/done while provisional. Reversals during validation use the current speculative rectangle and same atlas; stale validation and close/reuse cannot promote or settle it. Fresh identity/family validation promotes the existing route in place without resetting rectangle/progress or loading the same image again. Rejection retargets toward the previously accepted endpoint; timeout/reduction settle only the most recent freshly validated native intent.

## Implementation plan

1. Root-owned global route object holds immutable atlas/native metadata and shared from/to/clock; individual output panels project clipped fragments of that object. Captured taskbar action includes the explicit operation and exact identity. A prior accepted family plan may retarget peer visuals provisionally, but only fresh native graph validation authorizes new family native operations.
2. Service early reservation sends newtoken/previousToken/resolvedOperation. QML advances the provisional visual after recording the acknowledged current rectangle. The ACK remains an observation at reservation, not the eventual promotion origin. The driver must compare handover against actual current presented frames rather than assert that a moving route stayed at an old freeze rectangle.
3. Existing retained image/full/native metadata is kept through validation. Begin validates service token/identity/geometry/pixel lineage and promotes the existing item using its loaded texture; avoid replacing/reloading the image and a17ms readiness timer when the same exact frame is already presented. New atlas captures still require real readiness/presentation.
4. Every provisional endpoint is visual-only until promotion. Freshly validated restored native geometry appears once at the endpoint; native readiness for minimizing remains gated on all output participants actually presenting the same atlas epoch. Detached/rejected peers settle only their prior accepted intents with current exact identity checks.
5. Frame telemetry records actual Qt render submissions, synchronized rectangle/progress/token and shared-output route clock. External polling/screenshot counts cannot prove smoothness. A submission is not proof of compositor presentation; cross-output seam skew ultimately requires output presentation feedback.

## Acceptance still open

No implementation or GUI trials for provisional reversal yet. Require actual submitted/presented frame cadence from click through validation/promotion, no metadata pause, no rectangle jump/pixel replacement, no early native commit at a speculative endpoint, repeated requests during third-party slow metadata, rejection/deadline/reuse/reduce/reload, modal family and transformed-output participant loss. Keep836 stable until a separate paired candidate passes these gates.
