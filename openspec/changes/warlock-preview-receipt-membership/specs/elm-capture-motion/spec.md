# ADDED Requirements

### Requirement: WARLOCK-RECEIPT-001 — Explicit native journal admission

WHEN pixel receiver membership grows, the provider SHALL admit additional terminal receipt subjects only through an explicit trusted native operation reading the same current receiver and actual own scopes under one native critical section, retaining the original receiver epoch, immutable existing entry/incarnation correlations and the single broker journal; frontend metadata SHALL NOT authorize receipt subjects.

#### Scenario: WARLOCK-RECEIPT-001 new terminal waits for native admission

- GIVEN a new own native actor has pixel membership and an actual physically retired job, with an original reader still held
- WHEN its terminal delivery and ACK are attempted before and after explicit native journal admission
- THEN delivery and ACK refuse before admission, and afterward the exact retained new proofs are delivered while the original reader and original job remain owned

### Requirement: WARLOCK-RECEIPT-002 — Atomic immutable subject union

WHEN journal extension encounters a foreign binding, wrong lifetime, changed existing incarnation, duplicate incarnation, removed original member, closed or reused receiver epoch, or overbound union, the provider SHALL reject the whole update without admitting a valid prefix, consuming receipts, replacing the journal or altering existing resource ownership.

#### Scenario: WARLOCK-RECEIPT-002 valid prefix stays unadmitted

- GIVEN one new own actor with a retained terminal proof followed by a foreign native actor in current receiver membership
- WHEN journal extension is attempted
- THEN no new subject becomes deliverable or acknowledgeable, and original subjects retain their exact terminal proofs and physical obligations

### Requirement: WARLOCK-RECEIPT-003 — Original physical settlement and ACK

WHILE receipt subjects grow, the provider SHALL retain original jobs, clocks, deadlines, per-actor request floors and physical charge until actual reader drain, explicit native consumer completion and physical destruction; it SHALL deliver original terminal sequences repeatedly and remove a journal record only on its exact final ACK, without fabricating settlement, renewing a deadline or replaying an unknown operation.

#### Scenario: WARLOCK-RECEIPT-003 old and new jobs drain independently

- GIVEN old and new native frames share the original bounded physical pool
- WHEN the new frame retires and its final ACK arrives while the old reader remains held
- THEN only the new record is removed, the old charge and original job remain, native revocation still blocks old reads, and eventual actual old drain and exact final ACK preserve both request floors
