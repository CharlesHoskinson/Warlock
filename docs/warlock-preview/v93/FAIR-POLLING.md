The native poll processes at most one retained, accepted readiness row per call.
It selects the next entry after its transport cursor and wraps through the
existing bounded journal. Selection advances even when the chosen actor remains
blocked. Removing a row, retrying a delivery, or an empty poll never resets any
actor serial, native request, receiver epoch, job, or completion prefix.

EARS RETIRE-005: WHEN an original receiver polls pending readiness, the native
transport SHALL select at most one pending accepted row, SHALL rotate fairly
through continuously pending rows, and SHALL preserve exact observation
correlation and every existing ownership barrier.

EARS RETIRE-006: WHILE local physical, producer, backend, terminal-proof or other
receiver ownership prevents retirement, the native transaction SHALL retain
readiness without issuing another native retirement query or erasing any owner.
WHEN those barriers clear, final removal SHALL still require a fresh validated
native Retired fact under the original binding and receiver.

Scenarios cover blocked first/eligible second, unaccepted observations excluded,
wrapped selection, completed and acknowledged rows excluded, cursor survival on
empty polls, exact original wire, foreign epoch refusal without cursor movement,
and a native terminal proof that remains unacknowledged. The cursor is transport
bookkeeping; it cannot admit an actor, decide visibility, or grant cleanup.

This is a structural bound, not a measured latency claim. One native query can
still consume its unchanged native timeout. Original S02 policy and measured
GUI pacing/resource acceptance remain required before production qualification.
