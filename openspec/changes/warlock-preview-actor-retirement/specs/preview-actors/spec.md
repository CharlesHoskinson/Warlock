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

WHEN the trusted native owner activates retained retirement delivery under an
already admitted exact binding before retirement begins, the Elm owner SHALL
select that protocol for its presenter lifetime. Repeating activation SHALL NOT
reset the processing prefix. Late activation, a different binding or receiver
replacement SHALL NOT change an existing channel. WHILE retained delivery is
active, bare legacy completion facts SHALL NOT remove actors or bypass processing
acknowledgment. The new channel SHALL retain original settlement and shared
cutoff rules, and SHALL NOT infer physical retirement from transport admission.

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

WHEN exact original-binding Elm readiness is admitted while an original native
physical, proof or receiver obligation prevents aggregate removal, the bridge
SHALL retain that readiness in its existing observation row. Native polling SHALL
recheck the unchanged original barriers and complete only after they clear,
without requiring another Elm readiness emission, consuming another actor slot,
resetting a counter or interpreting readiness as physical retirement authority.
Readiness persistence and retry SHALL preserve the original receiver epoch and
binding and SHALL NOT replay capture, release or terminal acknowledgment effects.

#### Scenario: Completion lost after native removal
- GIVEN validated native cleanup and a retained final-delivery record
- WHEN the renderer does not receive the first transmission
- THEN the same ordinal and byte-identical fact remain available for retry.

#### Scenario: Retained channel cannot downgrade or reset
- GIVEN an activated original-binding channel with a nonzero processing prefix
- WHEN activation repeats, replacement is proposed, or a bare final fact arrives
- THEN its prefix and retained owners remain unchanged, and no legacy completion
  bypasses the retained acknowledgment protocol.

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

#### Scenario: Readiness waits for another native receiver
- GIVEN settled Elm ownership and exact readiness under the original receiver,
  while another actual native receiver still owns the actor
- WHEN that receiver later retires its membership and native polling continues
- THEN the retained original readiness permits rechecking aggregate removal
  without another Elm control, and every physical and proof barrier still applies.

### Requirement: Bounded fair native readiness polling

EARS WLK-PREVIEW-RETIRE-005: WHEN the original receiver polls readiness, the
bridge SHALL select at most one pending accepted row per call and SHALL rotate
through continuously pending rows without resetting original namespaces or
completion prefixes. Selection SHALL retain the original canonical readiness
correlation and exclude unaccepted observations and completed rows.

EARS WLK-PREVIEW-RETIRE-006: WHILE local physical, producer, backend,
terminal-proof or other receiver ownership prevents retirement, the bridge SHALL
retain readiness without another synchronous native retirement query or partial
erasure. WHEN those barriers clear, aggregate removal SHALL still require a
fresh exact native Retired fact under the original binding and receiver. A
structural per-call bound SHALL NOT establish measured S02 timing acceptance.

#### Scenario: Blocked actor does not starve a neighbor
- GIVEN two accepted readiness rows and a receiver barrier on the first
- WHEN the original receiver polls twice
- THEN the second eligible actor is considered, with at most one candidate per
  call, and the first actor remains intact until its original barriers clear.

#### Scenario: Foreign polling does not rotate ownership
- GIVEN pending readiness and an established transport cursor
- WHEN a foreign receiver or epoch attempts a poll
- THEN no selection, namespace, readiness correlation or completion prefix moves.

#### Scenario: Local terminal proof remains unacknowledged
- GIVEN native Retired and a retained readiness row with an original terminal
  proof that has not been acknowledged
- WHEN polling occurs
- THEN no new native retirement query or owner erasure occurs; after exact proof
  acknowledgment, polling still requires a fresh native Retired fact.

### Requirement: Original receiver outgoing control confirmation

EARS WLK-PREVIEW-CONTROL-001: WHEN an original-binding, original-epoch packet is
the next contiguous ordinal, the dispatcher SHALL retain its exact bytes before
invoking its handler at most once. WHILE that handler is in flight, repeated or
later packets SHALL NOT enter it. A delivery receipt SHALL mean the dispatcher
returned and SHALL NOT assert effect success, physical retirement, terminal proof
acknowledgment or permission to replay an Unknown effect.

EARS WLK-PREVIEW-CONTROL-002: WHEN the latest delivered packet is retried byte for
byte under its original receiver grant, the dispatcher SHALL repeat only its
delivery receipt. Changed bytes, gaps, foreign grants and ordinal exhaustion SHALL
NOT invoke effects, advance the prefix or reset any namespace.

EARS WLK-PREVIEW-CONTROL-003: WHILE delivery is unconfirmed, the renderer transport
SHALL retain bounded immutable packets, retry their existing ordinals in order,
and validate receipts against the original outstanding packet and receiver grant.
It SHALL NOT recreate commands or infer native effect success from delivery.

EARS WLK-PREVIEW-CONTROL-004: BEFORE native admission creates job or actor
obligations, the native owner SHALL reserve queue capacity and remaining ordinals
for their maximum required original cleanup and acknowledgments. Insufficient
capacity SHALL backpressure or exhaust admission before physical issuance.
Cleanup capacity SHALL remain available under overload. Bounds SHALL derive from
the actual owning Broker, actor, journal and proof contracts and have executable
worst-case witnesses; a renderer queue SHALL NOT silently discard emitted Elm
commands or authorize native admission.

EARS WLK-PREVIEW-CONTROL-005: WHEN an original receiver disappears or reloads with
outstanding controls, the native owner SHALL preserve original obligations and
unknown outcomes. Replacement SHALL require a fresh trusted grant and explicit
reconciliation. It SHALL NOT reset the old prefix or replay effects under the old
grant. Normal close SHALL preserve transport and physical barriers.

#### Scenario: Delivery receipt is lost
- GIVEN a completed dispatcher invocation under its original grant
- WHEN the renderer retries the exact same packet and ordinal
- THEN only the original delivery receipt repeats, without another invocation.

#### Scenario: Same ordinal carries different bytes
- GIVEN the latest delivered packet
- WHEN a retry changes its bytes while retaining its ordinal
- THEN the packet is refused and every effect and prefix remains unchanged.

#### Scenario: Admission approaches transport exhaustion
- GIVEN outstanding cleanup and acknowledgment reservations
- WHEN a new admission cannot reserve its worst-case cleanup capacity
- THEN admission is refused before physical issuance and existing cleanup can
  continue under its original identities.

#### Scenario: Receiver reload has an Unknown effect
- GIVEN an outstanding original control with an unknown native effect outcome
- WHEN a renderer reload requests reuse of its old grant
- THEN the old prefix and obligations remain, and no effect is replayed; a fresh
  receiver requires explicit reconciliation.

EARS WLK-PREVIEW-CONTROL-006: WHILE the native owner lacks confirmation that its
latest delivery receipt reached the original frontend, it SHALL retain and retry
that receipt and keep its transport confirmation barrier open. The frontend SHALL
repeat an idempotent original-grant confirmation for previously processed
receipts without recreating packets or asserting effect success. Confirmation
SHALL NOT exceed the native delivered prefix or confirm an in-flight invocation.
Normal close SHALL independently require this confirmation, admission cleanup
reservations, final actor-delivery confirmation and all physical/proof barriers.

#### Scenario: Physical drain precedes final control receipt delivery
- GIVEN native cleanup has drained but the frontend has not confirmed the final
  outgoing-control delivery receipt
- WHEN the native owner attempts normal close
- THEN its transport confirmation barrier stays open and the original receipt
  remains available for retry, without another effect invocation.

### Requirement: Receiver enrollment and cleanup credits before admission

EARS WLK-PREVIEW-CONTROL-007: BEFORE the first job is issued, the native endpoint
SHALL enroll its original receiver and assign an original epoch without borrowing
a job or inventing an actor. Empty enrollment SHALL authorize no subject access.
Later subject enrollment SHALL preserve that receiver and epoch.

EARS WLK-PREVIEW-CONTROL-008: BEFORE original Coordinator/Broker actor or job
issuance, the native guard SHALL reserve the verified cleanup quota. Insufficient
credits SHALL preserve original intents, request floors, physical reservations
and deadlines. Exceptions after issuance SHALL retain original credits for native
reconciliation and SHALL NOT be interpreted as proof that issuance did not occur.

#### Scenario: Initial receiver has no subjects
- GIVEN a fresh native endpoint and a trusted original receiver
- WHEN the receiver is enrolled before job issuance
- THEN its epoch is assigned and its membership is empty, so it cannot read a URI;
  later original native admission extends that receiver without resetting it.

#### Scenario: Cleanup capacity prevents admission
- GIVEN retained cleanup credits consume the available transport capacity
- WHEN the original native receiver proposes another admission
- THEN the guard refuses before remembering an intent or issuing a physical job,
  preserving the original request floor and deadline.

#### Scenario: Issuance fails after an original job was retained
- GIVEN the guard reserved credits before calling the original native issuer
- WHEN that issuer throws after retaining a job
- THEN the credits remain for native reconciliation and no speculative rollback
  erases the original obligation.

### Requirement: Cleanup uses original native packet readiness

EARS WLK-PREVIEW-CONTROL-009: WHEN a retained receiver releases an exact original
job/token whose native packet is ready, the controlled decoder SHALL validate
that native packet even if a delayed Offer still says signaled:false. Frontend
flags SHALL NOT grant native readiness or physical/proof completion. Original
wire bytes SHALL remain immutable for retries. Legacy strict decoding and its
original negative controls SHALL remain unchanged.

#### Scenario: Original Offer arrives after cancellation
- GIVEN a ready original native packet and an actual URI reader retaining storage
- WHEN Elm cancels before receiving its queued Offer, then releases its original
  handle from the late Offer with signaled:false
- THEN the controlled decoder validates the exact native job/token and native
  readiness; native destruction still waits for reader and producer barriers.

#### Scenario: Frontend claims readiness without a ready native packet
- GIVEN the original native packet has not confirmed readiness
- WHEN a renderer sends a cleanup packet with signaled:true
- THEN the controlled decoder refuses that claim and no native barrier advances.

EARS WLK-PREVIEW-CONTROL-010: WHEN ImportedClients opts into cleanup reservations,
attachment SHALL require a fresh empty original receiver and exact owning Broker.
Only one obligation manager SHALL own its issuer. Credits SHALL precede initial
or new-stamp intent advancement and job issuance. Resume SHALL preserve original
mapping/export/backend/proof and old-control confirmation barriers, then reserve
before new intent advancement. Receiverless legacy start/resume SHALL refuse in
controlled mode. Unknown issuance SHALL remain retained for reconciliation.

#### Scenario: Native resume precedes final control confirmation
- GIVEN old native physical and terminal proof obligations are drained, but an
  issued old control ticket has not been confirmed by the original frontend
- WHEN the original receiver requests resume
- THEN resume is backpressured before a new source query or intent change; after
  original confirmation, admission reserves new cleanup and preserves old floors.

#### Scenario: Guard borrows another Broker
- GIVEN a native receiver and a cleanup guard bound to a different native Broker
- WHEN attachment or issuance attempts to use the original receiver's Broker
- THEN the operation refuses before credits, intents, effects or floors move.

EARS WLK-PREVIEW-CONTROL-011: WHEN the original controlled receiver proposes a job
command, native SHALL validate its actual original job, packet or terminal proof,
select a stable native purpose slot and issue an immutable native ordinal from
that job's reserved quota. A previously issued exact body SHALL reuse its
original ticket even after its effect removed the Broker record. Neither a
proposal nor a ticket SHALL establish effect success or physical retirement.
WHEN independent physical/proof barriers and original frontend confirmation
permit releasing the job quota, native SHALL retain at most one confirmed
predecessor per retained actor. An exact predecessor retry SHALL return only an
already-delivered disposition and SHALL NOT authorize another invocation or
consume a new ordinal. Foreign grants, changed bytes, invented sequences and
unretained historical jobs SHALL NOT receive a fabricated delivered disposition.
Reconciliation of unretained or Unknown outcomes remains a separate native gate.

#### Scenario: Terminal ACK proposal repeats after its effect
- GIVEN an original issued ACK whose native handler removed the Broker record
- WHEN its exact command bytes are proposed again on the original receiver
- THEN its original immutable ticket is returned without another ordinal;
  the original delivery prefix still prevents another effect invocation.

#### Scenario: Confirmed predecessor repeats after native resume
- GIVEN independently settled physical/proof ownership and frontend confirmation,
  followed by a newly admitted native job for the same actor
- WHEN the exact confirmed predecessor command is proposed again
- THEN only its original already-delivered identity is returned; its released
  ticket cannot authorize an effect and the new job's namespace stays unchanged.

#### Scenario: Renderer invents a terminal sequence
- GIVEN no matching original native terminal proof
- WHEN a renderer proposes a terminal acknowledgment
- THEN native refuses before consuming reserved cleanup or issuing an ordinal.

EARS WLK-PREVIEW-CONTROL-012: WHEN controlled native actor retirement proceeds,
the original mapping/export/backend/reader/proof and other-receiver barriers
SHALL precede job-credit release. Original job control confirmation SHALL precede
the fresh permanent native retirement query. The existing all-map transaction
SHALL mark control actor retirement without a separate fallible post-commit
operation. Readiness SHALL reference an exact native-issued dispatched ticket;
final processing ACK SHALL reference an exact original completion and a currently
invoking native ticket. Actor credits SHALL remain until both the final native
processing effect and original frontend confirmation have occurred. A confirmed
Unknown final effect SHALL retain the journal and actor credits, SHALL prevent
binding close and SHALL NOT be reinvoked by a transport retry. Completed actor
credit collection SHALL preserve original entry/ordinal/receiver frontiers.
The completed-actor binding-close helper SHALL require all original obligations
and delivery barriers; it SHALL NOT substitute for live-actor binding detachment
or permit a new issuer under the retired original grant.

#### Scenario: Final handler returns Unknown and delivery is confirmed
- GIVEN a native-retired actor and its original final processing ticket
- WHEN the dispatcher returns with an Unknown effect and the original frontend
  confirms that delivery receipt
- THEN the native journal and actor cleanup credits remain, binding close refuses,
  and exact ticket retries repeat delivery metadata without another invocation.

#### Scenario: Native job is settled but its control ACK is unconfirmed
- GIVEN original physical and terminal proof settlement and exact dispatched
  readiness, but no frontend confirmation of the old job's control ACK
- WHEN native actor removal is attempted
- THEN no fresh permanent-retirement query or all-map removal occurs; after
  confirmation the original retained readiness can proceed through native polling.

#### Scenario: Completed actors continue through bounded cleanup capacity
- GIVEN each preceding actor completed its original retirement/final processing
  and frontend confirmation
- WHEN new native actors reuse reclaimed transport capacity
- THEN original receiver epoch, entry issuance and command ordinals continue
  monotonically; previously closed serials never become eligible again.

EARS WLK-PREVIEW-CONTROL-013: WHEN native accepts exact original retirement
readiness, it SHALL retain the immutable accepted command bytes before publishing
acceptance and SHALL use those bytes for subsequent native polling. Equivalent
JSON formatting SHALL NOT reconstruct or replace an existing ticket identity.
The retained readiness SHALL stay bounded and correlated with its original
receiver, actor and observation. Retries SHALL continue to use the original
physical/proof and frontend confirmation barriers.

#### Scenario: Readiness carries valid whitespace and retirement is delayed
- GIVEN a valid original native-issued readiness command with preserved whitespace
  and an unconfirmed preceding job-control ACK
- WHEN native retains readiness, then later receives original ACK confirmation
- THEN polling uses the exact accepted bytes and can complete original retirement
  without reconstructing JSON or assigning another ticket.

EARS WLK-PREVIEW-CONTROL-014: WHEN a controlled C provider opens, it SHALL claim
one namespace on the original native transport only after live legacy preview
providers are absent, enroll its actual receiver before admission and derive its
epoch from the owning endpoint. Reload SHALL retain that owner and its namespace.
Legacy C controls SHALL refuse a controlled owner. The native C dispatcher SHALL
invoke only an original native-owned immutable ticket under its actual target,
binding and epoch, preserve contiguous at-most-once delivery, and return delivery
metadata independently of effect success. An Unknown handler outcome SHALL
preserve both its delivery receipt and original obligations. The actual source
grant-retirement protocol, live-binding detachment and native reconciliation SHALL
remain distinct from permanent incarnation retirement and transport confirmation.

#### Scenario: Raw C controls enter a controlled namespace
- GIVEN one controlled owner on the original transport and receipt endpoint
- WHEN a legacy command, retirement control or bootstrap proof ACK is submitted
- THEN it is refused before effect invocation; a second controlled or legacy
  provider cannot borrow that namespace or reset its receiver epoch.

#### Scenario: An issued command fails during native dispatch
- GIVEN an exact native-owned next ticket for the original receiver
- WHEN its handler returns an error
- THEN the original dispatcher-return receipt remains available, the outstanding
  effect obligations remain owned, and retry can only echo that receipt.

#### Scenario: Original core exits after returning the latest ticket
- GIVEN the latest exact native ticket already returned
- WHEN the original core exits normally before frontend confirmation
- THEN cached receipt access, exact latest-ticket echo and original prefix
  confirmation remain available without another core query or handler invocation.
  New effects require a live original core; confirmation alone grants no cleanup.

#### Scenario: Broker records drain while actor cleanup remains
- GIVEN terminal proofs have drained the actual Broker records
- WHEN the actor still owns a frame, retirement completion or unconfirmed control
- THEN the controlled provider is not empty and close retains the owner.
  Completed-actor binding closure requires original all-map actor retirement,
  final processing, every issued ticket confirmation and quota release.
  Live-window binding detachment remains an independent unmet contract.
