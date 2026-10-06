# Additive EARS requirements

## WARLOCK-NEXT-RESUME-001 Exact original retirement
WHEN the trusted picker requests a strictly later publication and lease after an
unissued resume intent expires, the system SHALL permit a new native two-second
intent only after the original job's physical/backend/mapping and terminal
receipt retirement is proved, preserving its job identity and request floor.

### Scenario: expired resume then later picker
After exact old-job drain/ACK, capacity prevents a resume from issuing until its
cutoff expires. A later picker lease can create a successor; its actual issued
job uses the next retained request counter and its own original cutoff.

### Scenario: retirement is still pending
An owned reader, backend obligation or terminal journal prevents new capture;
presentation close and elapsed time cannot establish retirement.

## WARLOCK-NEXT-RESUME-002 Bounded monotonic correlation
WHEN resume succession is considered, the system SHALL retain one predecessor
intent, require the same authenticated owner/incarnation/clock and a fresh native
observation, and reject pending, same-stamp, partial-stamp, foreign and older
replacements without issuing a job or resetting the native or Elm counter.

### Scenario: same-intent polling
Retries retain the original cutoff before and after expiry and emit truthful
local feedback; no capture or proof is fabricated by capacity or expiry.

### Scenario: actual issued refusal
A real native-rejected job remains registered in Elm and follows exact native
terminal proof/ACK, while the successor cannot replace that ownership.
