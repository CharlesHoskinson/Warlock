# ADDED Requirements

### Requirement: WARLOCK-RECEIVER-001 — Native membership preserves old receiver

WHEN a new actual native subject actor is enrolled for an existing preview receiver, the native endpoint SHALL authenticate the same receiver identity and own binding, retain the original receiver epoch and previous membership, and add only actors whose current native scope is already enrolled under that binding; metadata inventory SHALL NOT supply a scope or capture grant.

#### Scenario: WARLOCK-RECEIVER-001 held reader and new subject

- GIVEN an original authorized native preview reader held across ordinary picker inventory growth
- WHEN another actual own native actor is added to the receiver
- THEN the original reader retains its original epoch and continues only while its own native authorization remains valid, and the new subject gains no access to foreign resource tokens

### Requirement: WARLOCK-RECEIVER-002 — Atomic refusal

WHEN a receiver membership update contains a foreign binding, absent receiver, zero or unenrolled subject, mixed invalid prefix, or an overbound union, the endpoint SHALL reject the entire update without changing receiver epoch or membership, freeing held readers or fabricating terminal outcomes.

#### Scenario: WARLOCK-RECEIVER-002 no partial authorization

- GIVEN an update containing one own native actor and one foreign native actor
- WHEN the endpoint validates the update
- THEN neither actor is added, previous membership and epoch remain unchanged, and existing physical ownership remains charged

### Requirement: WARLOCK-RECEIVER-003 — Actor inventory and physical bounds

WHILE dynamic subject actors are retained, the provider SHALL bound their inventory by at most256 actors and preserve the shared two live items,128MiB,8 records,4 readers and2 views budget, retain old actor request floors and original jobs/clocks/deadlines until physical retirement and exact terminal ACK, and report local capacity without fabricating a new job, renewing a deadline or replaying an unknown outcome.

#### Scenario: WARLOCK-RECEIVER-003 capacity requires original physical drain

- GIVEN two charged native items and an original held reader with a third valid subject waiting
- WHEN receiver membership grows and the third subject seeks admission
- THEN no allocation is evicted and no terminal refusal is fabricated; third admission follows actual eligible capacity with its own request domain and original deadline while old request floors and cleanup receipts remain retained
