# Native address reuse evidence

## ADDED Requirements

### Requirement: WARLOCK-REUSE-001 — Real native replacement identity

WHEN the original ELM-REN-004 ren-004 fault is qualified, the fixture SHALL independently observe identical old and replacement native window addresses, strictly different monotonically issued incarnations and a still-unexpired original preview under its original native clock. Failure to observe this within the original expiry SHALL fail the added oracle without renewing the job, lease or deadline.

#### Scenario: WARLOCK-REUSE-001 actual-address

- GIVEN a full shared GUI owns a real captured preview and held stream
- WHEN its source closes normally and a replacement is mapped
- THEN native IPC reports the same address and a fresh incarnation before original expiry; a different address or an expired lease cannot satisfy the oracle.

### Requirement: WARLOCK-REUSE-002 — Native refusal before delayed policy effects

WHILE original source polling and validated Elm cleanup effects are delayed in the explicit private fixture, WHEN the source incarnation is replaced, the owning native endpoint SHALL refuse both a held stream read and a fresh open of the original URI while retaining physical resources against the original job until actual reader closure and physical retirement.

#### Scenario: WARLOCK-REUSE-002 held-and-fresh-read

- GIVEN an actual native address replacement and an unexpired old lease
- WHEN held and fresh reads are probed before queued effects run
- THEN both return permission denial, the original mapped bytes/export/producer remain charged and no frontend event supplies a new grant, incarnation or clock.

### Requirement: WARLOCK-REUSE-003 — Full GUI identity, pixels and exact drain

WHEN replacement UI is rendered and the reader is closed, the full GUI SHALL retain the fresh replacement identity without old preview pixels, dispatch each original undispatched cleanup effect once, retire the original mapping/export/producer before its exact terminal acknowledgement, and reach zero physical charge and journal records without recapture, Unknown replay or deadline renewal.

#### Scenario: WARLOCK-REUSE-003 actual-view-and-drain

- GIVEN the original actual popup snapshot contains old source pixels
- WHEN replacement identity enters the actual Elm view and cleanup resumes
- THEN an independently decoded replacement popup snapshot contains no old source pixels, original release/ACK identity is preserved and native cleanup reaches physical0/journal0 before normal exit.

### Requirement: WARLOCK-REUSE-004 — Private bounded stimulus

WHERE the explicit private reader fixture is enabled, the host SHALL accept only exact hold/probe/release bytes from a UID-owned nonsymlink regular single-link 0600 file in a UID-owned nonsymlink 0700 parent, retain at most four validated undispatched Elm effects, and fail malformed input or overflow without inventing native authority or terminal ownership proof.

#### Scenario: WARLOCK-REUSE-004 private-file-boundary

- GIVEN a wrong-mode, linked, symlinked, oversized, malformed or nonregular control file
- WHEN the fixture reads it
- THEN the stimulus is rejected; it cannot choose the URI, grant or native policy facts.
