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

WHEN the Elm owner receives an exact permanent native retirement observation,
it SHALL close demand, cancel current work and request release of accepted and
candidate packets immediately; retain every known job and retiring packet until
its exact terminal proof; and append retirement readiness after cleanup and final
acknowledgments on the same output port. WHILE readiness awaits native completion,
the entry SHALL emit no further controls or reopen demand. The original popup
transport SHALL carry canonical uint64 delivery ordinals and admit only the next
ordinal after its previous handler returns. A delivery ordinal SHALL NOT certify
effect success or physical cleanup. Native removal SHALL independently verify
all original ownership and journal obligations. Foreign receivers, gaps, replay,
reentrant delivery and exhausted ordinals SHALL never advance the prefix.

WHEN native facts for different actors arrive in independent delivery order,
the Elm owner SHALL correlate each completion with that actor's exact pending
observation and settled state. A newer sibling observation or completion SHALL
NOT prevent an older exact completion from settling its own actor. Shared native
clock, catalog and issuance cutoffs SHALL never move backward when an older
completion arrives. No global event-delivery order SHALL be inferred from native
proof identities.

#### Scenario: Delayed completion after sibling observation
- GIVEN one settled actor waiting for completion and a newer sibling observation
- WHEN the first actor's exact native completion arrives afterward
- THEN it settles its own actor and preserves the sibling.

#### Scenario: Older completion after newer sibling completion
- GIVEN independently delayed completions for two settled actors
- WHEN the newer sibling completion arrives first
- THEN both exact completions remain usable and the shared replay cutoff never rewinds.

#### Scenario: Duplicate terminal after readiness
- GIVEN settled Elm ownership and readiness already emitted after its final ACK
- WHEN the original terminal receipt is delivered again
- THEN no subsequent entry control is emitted and native completion remains pending.

#### Scenario: Accepted pixels retire without an expiry tick
- GIVEN an accepted preview packet and exact permanent native retirement
- WHEN no further source observation or clock event occurs
- THEN release is requested immediately and the packet remains retiring until exact proof.

#### Scenario: Readiness cannot overtake cleanup
- GIVEN an original popup control handler still processing its prior ordinal
- WHEN readiness arrives reentrantly or across a missing ordinal
- THEN it is refused without advancing the delivered prefix or asserting cleanup.

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

WHEN native scope admission refuses a newly proposed subject, staged C membership
SHALL consume no active slot or entry serial. WHEN a settled actor is removed,
historical source seeds and catalogs SHALL remain unable to recreate it. The Elm
owner SHALL compare source and retirement time only in their exact native clock
domain; their independent observation sequence counters SHALL NOT be compared.

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

### Requirement: WLK-PREVIEW-RETIRE-004 — Retained completion delivery

WHEN the original receiver is ready for a permanently retired actor, the native
bridge SHALL validate that readiness against its retained exact observation and
all obligations in WLK-PREVIEW-RETIRE-002. Before committing native removal, it
SHALL reserve the complete typed final-delivery record without consuming another
actor slot or abandoning an existing record. A final-delivery ordinal SHALL be
positive, strictly increasing and independent of native observation/proof IDs.
Overflow or unavailable record capacity SHALL preserve existing cleanup and
refuse new issuance without wrap.

WHILE a completion lacks an Elm processing acknowledgment, the bridge SHALL
retain and retry its byte-identical final fact under the original receiver epoch
and binding. The Elm owner SHALL acknowledge a new ordinal only after accepting
that actor's exact completion; duplicate admitted ordinals SHALL produce only
idempotent transport acknowledgment. Missing ordinals, foreign bindings and
receiver replacement SHALL never advance the delivery prefix or discard retained
completion. A transport acknowledgment SHALL NOT confer native resource cleanup,
terminal Broker acknowledgment or permission to replay an effect. The bounded
journal SHALL preserve queued completion on interrupted delivery and retain a
compact nondecreasing acknowledged prefix after removing confirmed records.

WHILE the journal retains an observation or an unacknowledged final completion,
the imported native owner SHALL remain nonempty and refuse normal close. Physical
drain alone SHALL NOT discard transport settlement. Final confirmation SHALL
release only its own retained delivery record; the original physical and terminal
Broker proof barriers SHALL remain independently required.

#### Scenario: Completion lost after native removal
- GIVEN validated native cleanup and a retained final-delivery record
- WHEN the renderer does not receive the first transmission
- THEN the same ordinal and byte-identical fact remain available for retry.

#### Scenario: Processing acknowledgment lost
- GIVEN Elm has processed the next exact completion
- WHEN the original native receiver retries it after losing the acknowledgment
- THEN Elm repeats the transport acknowledgment without recreating the actor or
  emitting a cleanup effect.

#### Scenario: Delivery gap or replacement
- GIVEN a retained completion awaiting its next processing acknowledgment
- WHEN an acknowledgment skips that ordinal or uses a replaced receiver
- THEN the prefix and retained record remain unchanged.

#### Scenario: Final record prepared before actor removal
- GIVEN an exact ready actor and insufficient final-delivery capacity
- WHEN native removal is attempted
- THEN every original actor map and cleanup obligation remain available.

#### Scenario: Shared journal stays bounded during turnover
- GIVEN retained observations and unacknowledged completions
- WHEN later actors are retired
- THEN their combined journal occupancy remains within its declared bound and
  earlier records, delivery ordinals and the acknowledgment prefix never reset.

#### Scenario: Physical drain before final confirmation
- GIVEN every physical job and terminal Broker proof has settled but the last
  completion remains unacknowledged
- WHEN normal native owner close is requested
- THEN close is refused and the original completion remains retryable until its
  exact processing acknowledgment arrives.
