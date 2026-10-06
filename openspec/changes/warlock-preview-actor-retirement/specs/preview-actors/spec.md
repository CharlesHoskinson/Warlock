## ADDED Requirements

### Requirement: WLK-PREVIEW-RETIRE-001 — Native permanent retirement evidence

WHEN the bridge requests retirement state for a preview subject, the owning
native authority SHALL authenticate the caller and exact lifetime, binding,
request and subject; return a typed Active, Retired or Future state with its
native clock and monotonic incarnation issuance frontier; and classify a subject
as Retired only when its positive incarnation is at or below that frontier and
the authority no longer owns that incarnation. The frontier SHALL never reset
or reuse an incarnation within the lifetime. The bridge SHALL reject malformed,
foreign, stale and mismatched evidence. Catalog omission, minimization, source
suspension, ScopeDenied and elapsed time SHALL NOT establish retirement.

#### Scenario: Live source stays active
- GIVEN a live mapped incarnation
- WHEN native retirement state is requested
- THEN Active is returned and actor history is retained.

#### Scenario: Minimized or suspended source stays owned
- GIVEN a still-owned minimized or suspended incarnation
- WHEN retirement is requested
- THEN retirement is refused and original history remains.

#### Scenario: Permanently closed incarnation
- GIVEN a previously issued incarnation removed by native destruction
- WHEN its authenticated retirement state is requested
- THEN Retired carries the same lifetime and a nondecreasing issuance frontier.

#### Scenario: Future and foreign identities
- GIVEN a future incarnation or a different lifetime, caller or request
- WHEN its retirement state is requested
- THEN no usable Retired evidence is produced.

### Requirement: WLK-PREVIEW-RETIRE-002 — Atomic obligation-preserving removal

WHEN exact native Retired evidence is available, the trusted bridge SHALL remove
the actor only after every original job's actual reader, FD, mapping, export,
producer, backend lock and allocation obligations have retired and every terminal
Broker proof has received its exact final acknowledgment. The original receiver
epoch and binding SHALL be verified before native querying or mutation. Removal
of C identity mapping, native frame/intent history, Coordinator slot, Broker
actor, receiver membership and ReceiptDelivery subject membership SHALL be one
validated operation serialized with capture, URI readers, delivery and receiver
replacement. The Elm owner SHALL retain unsettled jobs and queued controls, and
accept only an exact typed native retirement fact after their settlement.

#### Scenario: Outstanding reader blocks removal
- GIVEN Retired native evidence and an actual URI reader
- WHEN actor removal is attempted
- THEN all actor history and ownership remain.

#### Scenario: Pending backend or terminal proof blocks removal
- GIVEN Retired evidence and an outstanding backend obligation or unacknowledged proof
- WHEN removal is attempted
- THEN original resources, request floor and receiver membership remain.

#### Scenario: Replaced receiver cannot retire history
- GIVEN a receiver with a different epoch or binding
- WHEN retirement is attempted
- THEN native query and actor mutation are refused.

#### Scenario: Fully settled removal
- GIVEN exact Retired evidence and no physical, backend, journal or Elm obligations
- WHEN the original receiver removes the actor
- THEN all corresponding active maps shrink together and live unrelated actors remain.

### Requirement: WLK-PREVIEW-RETIRE-003 — Bounded lifetime turnover without replay

WHILE new windows are introduced in one native provider lifetime, the dynamic
bridge SHALL keep active actor and predecessor counts within the existing256
limit, physically allocated items within two and bytes within128MiB, and issue
each new actor a strictly increasing entry serial. A serial SHALL never be reused
after retirement; a compact issuance frontier SHALL permanently reject previously
issued absent entries. Request floors for retained actors SHALL remain unchanged.
Old job, URI, receipt, feedback and subject replays SHALL never recreate a retired
actor or authorize capture. Overflow SHALL refuse further issuance without wrap.

#### Scenario: More than256 sequential windows
- GIVEN a continuing native/Elm host with successive settled window closures
- WHEN more than256 distinct incarnations are introduced and retired
- THEN new live windows remain usable with bounded active maps and exact cleanup.

#### Scenario: Old entry and native subject replay
- GIVEN a fully retired actor
- WHEN old entry, job, URI, receipt, feedback or closed subject stimuli arrive
- THEN no actor, allocation, counter reset or capture is created.

#### Scenario: Retained neighbor counter continuity
- GIVEN a live neighboring actor during repeated retirement cycles
- WHEN that neighbor starts its next genuine request
- THEN its original counter increases once and its own proofs remain exact.

#### Scenario: Serial exhaustion
- GIVEN an exhausted entry issuance frontier
- WHEN a new actor is requested
- THEN issuance refuses without wrap, floor reset or loss of existing cleanup.
