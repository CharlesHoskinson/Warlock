# Additive EARS requirements

## WARLOCK-NEXT-INTENT-001 Explicit successor
WHEN the trusted current picker requests a strictly later publication and lease
for an expired unissued native intent, the system SHALL admit a distinct current
intent with the same owner, incarnation and clock and a native two-second cutoff.

### Scenario: expiry then reopen
After native expiry, a later picker lease may wait for capacity and subsequently
issue its first actual job with the successor's original cutoff.

### Scenario: polling is not renewal
Same-stamp retries before and after expiry retain the current cutoff and cannot
fabricate jobs or terminal proof when capacity is unavailable.

## WARLOCK-NEXT-INTENT-002 Monotonic bounded correlation
WHEN a successor is requested, the system SHALL reject pending, stale, partial
stamp, foreign or clock-changing replacements without altering current history,
issued request floors, receipt delivery or physical ownership.

### Scenario: old request replay
Replaying a prior stamp after succession cannot restore its deadline or replace
the current intent; one predecessor and one current intent remain bounded per actor.

### Scenario: original owners remain
The two-item pool retains its existing job identities until exact native terminal
proof and acknowledgment return capacity; succession consumes no item or proof.
