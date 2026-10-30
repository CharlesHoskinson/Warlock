## ADDED Requirements
> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.

### Requirement: WARLOCK-FEEDBACK-001 Native local outcome
WHEN preview admission returns an unissued local outcome, the system SHALL emit
typed feedback from the original native identity, clock, stamp and cutoff without
fabricating a job, terminal proof, capture or request-floor advance.
#### Scenario: initial capacity
The third selected native subject waits in the original two-item pool; its source
seed and capacity feedback contain no Request or Refused event.
#### Scenario: resume expiry
A same-intent retry after its original cutoff reports Expired without a new job
or renewed deadline. Real issued rejection follows existing registration/proof.

### Requirement: WARLOCK-FEEDBACK-002 Immutable authority
WHEN feedback arrives, the system SHALL admit only current enabled picker,
binding, subject, clock and increasing sequence feedback into its idle Elm entry
without emitting lifecycle effects or clearing ownership obligations.
#### Scenario: stale or foreign feedback
Wrong owner, subject, clock, stamp, duplicate or older sequence changes nothing.
#### Scenario: already owned work
A late local outcome cannot replace an owned image, active capture, cancellation
or retirement, or acknowledge any native terminal proof.

### Requirement: WARLOCK-FEEDBACK-003 Current accessible status
WHILE a current local wait or expiration is admitted, the system SHALL display
its truthful status in the full picker with accessible status semantics and SHALL
clear it on a newer source seed or hide it on close without resetting history.
#### Scenario: capacity then admission
The same source starts after exact unrelated physical drain and ACK, using its
original cutoff. Elm clears waiting and renders the actual owned image.
#### Scenario: close and replay
Closing hides the local status; reopening cannot admit its old stamp or sequence.
