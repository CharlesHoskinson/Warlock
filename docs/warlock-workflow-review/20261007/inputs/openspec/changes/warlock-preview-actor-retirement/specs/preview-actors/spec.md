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

EARS WLK-PREVIEW-CONTROL-015: BEFORE native invokes a capture effect, its owner
SHALL retain the original immutable request, binding, context, command bytes and
deadline. A capture-response or FD-transport exception SHALL preserve this intent
and SHALL NOT authorize acquisition replay, deadline extension or final cleanup
proofs. Exact export/backend ownership SHALL be retained before local mapping or
adoption can fail. A mapping pointer SHALL be published only after actual Broker
adoption; an exception after adoption SHALL retain that pointer, while refusal or
a pre-transfer exception SHALL leave caller-owned storage unrepresented by it.
Actual reconciliation SHALL require independent original native resource proofs.

#### Scenario: Capture response or FD transport fails
- GIVEN an original native-purpose acquisition ticket and native job
- WHEN its capture response is refused or malformed, or its FD transport fails
- THEN the exact original native intent survives, transport retry invokes no
  second capture, and cancellation/polling retain unresolved charge and ownership
  until actual original backend and local-resource proofs are available.

#### Scenario: Local mapping adoption returns or throws
- GIVEN an exact native export and a caller-owned sealed local mapping
- WHEN Broker adoption refuses or throws before transfer
- THEN no retained mapping pointer is published and caller storage remains owned.
- WHEN adoption transfers storage but receipt allocation throws
- THEN the actual Broker mapping remains retained for original reader/FD/proof
  drain, without inventing successful offer delivery or erasing the reservation.

EARS WLK-PREVIEW-CONTROL-016: WHEN original capture or export settlement is
uncertain, native SHALL observe the exact original capture request and subject
under the authenticated original caller binding. Export presence and producer
presence SHALL be reported independently, including after lock, revocation and
expiry. Scoped cleanup SHALL release only the matching original export or
producer, SHALL preserve a different current capture, and SHALL be idempotent
when the target is already absent. Original producer retirement SHALL remain
pending under the existing lock policy. Reply preparation failure SHALL occur
before resource mutation; lost reply SHALL be resolved through fresh original
native observation. Backend zero SHALL NOT establish local mapping/FD/reader,
Broker terminal proof, frontend processing or window incarnation retirement.
Malformed, foreign, regressing or exhausted evidence SHALL retain Unknown.

#### Scenario: Export release succeeded but its acknowledgment was lost
- GIVEN the exact original exported capture and retained local storage
- WHEN native export release commits but the reply is lost
- THEN fresh authenticated original resource observation can confirm export
  absence without acquiring another image, repeating the original capture or
  treating local mapping/readers as closed.

#### Scenario: Original capture is absent and another capture is current
- GIVEN a matching caller binding and a different current capture
- WHEN original target resource observation or cleanup is requested
- THEN only original target absence is certified; the current capture remains
  owned with its original export and producer reservations.

#### Scenario: Resource is revoked, expired or locked
- GIVEN an original producer/export obligation whose pixels are no longer usable
- WHEN native resource settlement is queried
- THEN resource identity and ownership remain observable independently of pixel
  eligibility, export release can follow original policy, and a locked original
  producer remains pending until its original retirement barrier is satisfied.
### Requirement: Canonical binding reconciliation preserves original obligations

EARS CONTROL-017: When original retained families request Reconcile for the same
native binding, the provider SHALL issue the same canonical reserved native
ticket. Actual dispatch on the owning native receiver and borrowed receipt
Endpoint SHALL quarantine source admission. A bounded fair native poll SHALL
re-observe and settle original scoped resources without acquisition replay.
Independent local storage/readers, terminal proofs, incarnation facts, final
processing and transport confirmation SHALL remain required.

#### Scenario: Different families share one native reconciliation purpose
- GIVEN two original retained native family actors on one receiver and binding
- WHEN their typed Reconcile proposals carry that exact binding
- THEN Native returns the same ordinal and immutable canonical ticket
- AND issuance or receipt confirmation alone cannot grant resource settlement.

#### Scenario: A pending capture cannot starve independent cleanup
- GIVEN one attempted capture whose producer is locked or whose response was lost
- AND another original unattempted job on the same binding
- WHEN the original reconciliation ticket has actually dispatched
- THEN the native poll advances its entry cursor before the fallible operation
- AND the next poll can settle the independent unattempted reservation
- AND no original acquisition is replayed or clock/deadline reset.

#### Scenario: A foreign borrowed receipt capability cannot enter cleanup
- GIVEN the original dispatched reconciliation ticket
- WHEN polling supplies a receipt capability from a different native Endpoint
- THEN the provider refuses before querying or mutating original resources
- AND the original charges, observations and terminal proofs remain unchanged.

### Requirement: Immediate read revocation preserves physical imported storage

EARS CONTROL-018: When the actual original binding reconciliation ticket
dispatches, the single native quarantine state SHALL revoke existing and new
URI read authorization before physical polling. Actual readers SHALL retain
their original storage references until close. Backend zero and read denial
SHALL NOT close local mappings or establish terminal proofs. A committed Broker
adoption followed by result allocation failure SHALL retain the original
mapping/packet and settle its actual producer/backend/reader barriers, producing
Released and Cancelled proofs without classifying adopted storage as refused.

#### Scenario: Existing reader loses authorization before cleanup begins
- GIVEN an actual imported sealed capture FD and an active GIO reader
- WHEN the original binding reconciliation ticket actually dispatches
- THEN the next read refuses before the first physical cleanup poll
- AND the reader, local FD/mapping and original Broker charge remain owned.

#### Scenario: Native backend zero is independent of reader completion
- GIVEN the scoped native producer and export are authoritatively absent
- AND an actual reader still owns the original imported mapping
- WHEN native reconciliation polls that job
- THEN local storage and its original charge remain retained
- AND only actual reader drain followed by local mapping/FD close can create
  the original physical terminal proof, whose final acknowledgment remains required.

#### Scenario: Result allocation fails after native buffer adoption
- GIVEN the actual Broker has adopted the original sealed mapping and packet
- WHEN its result allocation throws before the C handler reports an offer
- THEN the original mapping pointer and capture intent remain retained
- AND reconciliation never replays capture or fabricates an unadopted refusal
- AND original local/backend/producer/reader barriers produce actual Released
  and Cancelled proofs before original acknowledgment and actor/control closure.

### Requirement: Confirmed binding purposes suppress stale dispatch

EARS CONTROL-019: When an original binding reconciliation purpose is confirmed,
an exact reproposal SHALL return its original immutable ticket and ordinal with
alreadyDelivered true, including after later job or actor controls. A delivered
but unconfirmed purpose SHALL remain eligible for original receipt retry.
Confirmation SHALL NOT settle resources or authorize repeated acquisition.

#### Scenario: Reconciliation is reproposed after final job acknowledgement
- GIVEN the original reconciliation ticket and independent confirmation
- AND a later final job proof acknowledgement has dispatched and been confirmed
- WHEN a retained family reproposes reconciliation for that exact binding
- THEN the native bank returns the original bytes and ordinal as alreadyDelivered
- AND the caller suppresses stale dispatch without issuing another ticket
- AND original capture and FD transfer counters remain unchanged.

#### Scenario: Handler return has not yet been confirmed
- GIVEN the original reconciliation ticket has dispatched without confirmation
- WHEN a retained family reproposes the same binding purpose
- THEN the original ticket remains available for receipt retry
- AND the retry echoes its original receipt without repeating the handler
- AND polling still requires every original physical retirement barrier.

### Requirement: Preview receiver epochs survive owner replacement

EARS CONTROL-020: A controlled preview realm SHALL obtain a monotonic epoch
from the original Native transport before subject/job admission. Endpoint
replacement SHALL NOT reset this namespace. Failed construction SHALL consume
its allocated epoch and release only its unpublished claim. Exhaustion SHALL
refuse before admission. Only the complete original physical, terminal-proof,
actor, final-processing and independently confirmed control close SHALL release
a published claim. Replacement SHALL retain the shared Native binding, session
and frontend, reject old tickets before handlers, and never downgrade to legacy
preview ownership. Realm closure SHALL NOT imply permanent window retirement
or completed live-window detachment.

#### Scenario: Replacement on the same Native session
- GIVEN a published controlled owner whose original cleanup barriers have passed
- WHEN strict C close releases that owner and another owner opens on the same transport
- THEN the replacement receives a greater native-owned receiver epoch
- AND shared Native binding, session and frontend remain unchanged
- AND the old owner's exact ticket refuses before any replacement handler.

#### Scenario: Failed constructor consumes its epoch
- GIVEN a closed controlled owner and its now-retired native subject
- WHEN a replacement constructor allocates an epoch but native scope refuses admission
- THEN no receiver, job or grant is published and only that unpublished claim is released
- AND the next accepted owner receives an epoch beyond the failed constructor's epoch.

#### Scenario: Incomplete close preserves exclusive ownership
- GIVEN any outstanding physical, terminal-proof, actor, final-processing or confirmation barrier
- WHEN strict C close refuses
- THEN the published native claim remains held
- AND a concurrent factory refuses without releasing or mutating that claim.

#### Scenario: Counter exhaustion and permanent controlled mode
- GIVEN the original transport has issued its final lossless uint64 receiver epoch
- WHEN another controlled factory attempts admission after strict close
- THEN it refuses without wrapping the epoch or resetting the shared Native grant
- AND legacy preview ownership also refuses after any controlled epoch has been issued.

#### Scenario: A delayed legacy atomic claim crosses controlled close
- GIVEN a legacy claim has checked the original zero namespace but has not performed its atomic claim
- WHEN a controlled owner opens and passes every original strict-close barrier
- AND the delayed legacy claim resumes its compare/exchange
- THEN that stale claim refuses against persistent controlled namespace state
- AND a fresh controlled owner still opens without changing the shared Native binding.

### Requirement: Bootstrap receipt ownership follows strict C lifetime

EARS CONTROL-021: The exact owning native Bootstrap SHALL release its borrowed
receipt delivery only after original strict C cleanup and native claim completion,
and before Endpoint destruction. Native preflight SHALL validate transport,
Endpoint, receiver epoch, creator thread and empty receipt membership. Refused
or foreign-owner close SHALL retain the original owner and delivery. Replacement
SHALL attach a fresh delivery under a greater native epoch on the unchanged
shared Native binding. Local release SHALL remain possible after Core death and
SHALL NOT imply live-window detachment or frontend processing.

#### Scenario: Refused close retains the borrowed channel
- GIVEN an outstanding original cleanup, processing or confirmation barrier
- WHEN the Bootstrap-aware C close refuses
- THEN the original borrowed delivery remains available to drain that barrier
- AND a replacement channel cannot replace it.

#### Scenario: Exact settled close releases before Endpoint destruction
- GIVEN all original strict close barriers have passed
- WHEN the exact owning Bootstrap closes that C owner
- THEN its delivery is released before the Endpoint is destroyed
- AND delivery lookup and polling refuse safely until a fresh owner attaches
- AND the new channel uses the new native epoch on the unchanged Native grant.

#### Scenario: A foreign Bootstrap cannot release the original channel
- GIVEN a fully settled controlled C owner and its original borrowed delivery
- WHEN a different native Bootstrap attempts to close it
- THEN close refuses before mutation
- AND the original owner remains closable through its exact Bootstrap.

### Requirement: Scoped preview detachment preserves a live application

EARS CONTROL-022: A native-controlled preview realm SHALL detach its scoped
ownership while the native application incarnation remains Active. Distinct
native-issued reconciliation/readiness and typed preview-binding-detached
completion SHALL preserve every original physical/backend/reader/terminal ACK,
aggregate membership, final-processing and independent-confirmation barrier.
Readiness or a transport receipt SHALL NOT settle physical resources. Existing
permanent incarnation-retirement facts SHALL remain unchanged and SHALL NOT be
fabricated or substituted. Reenrollment of the same still-Active subject SHALL
use a fresh native receiver epoch, channel and opaque URI domain on the unchanged
Native session/frontend, rejecting old events/tickets/completions/URIs without
replaying Unknown or resetting unrelated effects.

#### Scenario: Close previews while the application remains alive
- GIVEN an Active native application and its controlled preview owner
- WHEN canonical reconciliation and distinct detachment readiness are dispatched
- AND every original physical and terminal ACK barrier passes
- THEN native aggregate preview membership is removed with a scoped detached completion
- AND native incarnation state remains Active
- AND strict realm close still waits for final processing and independent confirmation.

#### Scenario: Physical cleanup blocks scoped detachment
- GIVEN retained backend/export/producer/local mapping/reader or final proof ownership
- WHEN detachment readiness is accepted or its ticket transport confirms
- THEN actual aggregate membership remains retained
- AND fair native polling may complete only after the original physical/proof barriers pass
- AND no capture is replayed and no original deadline is renewed.

#### Scenario: The live subject opens in a fresh realm
- GIVEN a fully processed and independently confirmed scoped detachment
- WHEN the original Bootstrap strictly closes that realm and reenrolls the same Active subject
- THEN the Native binding/session/frontend and native window incarnation remain unchanged
- AND receiver epoch, receipt channel and opaque broker URI identity are fresh
- AND old scoped events/tickets/completions/URIs refuse before affecting the new owner.

#### Scenario: Permanent and scoped retirement domains do not substitute
- GIVEN a live subject with scoped detachment pending
- WHEN a permanent-incarnation completion, readiness or acknowledgment is received
- THEN it cannot advance the scoped detachment journal
- AND scoped detachment never publishes a permanent Retired fact or closes the application.

### Requirement: Lifetime-safe URI callbacks across preview realm replacement
The system SHALL implement CONTROL-023 through native lifetime-safe read
capabilities and a reference-counted stable URI router. It SHALL preserve all
original native URI/source/time/token/reader/physical barriers.

#### Scenario: Endpoint disappears while a callback and reader survive
- **GIVEN** an original native read capability and an existing physical reader
- **WHEN** its Endpoint is destroyed while the reader retains storage
- **THEN** new callback reads refuse before allocating another reader
- **AND** existing reader storage remains owned until its actual close

#### Scenario: Receiver replacement retains an obsolete callback
- **GIVEN** a callback bound to one exact native receiver epoch
- **WHEN** that receiver is removed and re-enrolled under a greater epoch
- **THEN** the old capability refuses even on the same Shared state and view ID
- **AND** only a fresh trusted capability may request current pixels

#### Scenario: Router clear does not reset authority history
- **GIVEN** a native router bound to a controlled Native binding and realm
- **WHEN** native code clears that route and proposes an old or foreign realm
- **THEN** the router refuses without changing its monotonic frontier
- **AND** creator-thread rebind to a greater epoch retains original Native binding

#### Scenario: WebKit context retains callback lifetime
- **GIVEN** a WebKit context that owns a native router reference
- **WHEN** the C owner clears and releases its own reference
- **THEN** the callback remains a valid object and refuses unavailable pixels
- **AND** context destruction releases its independently owned reference

### Requirement: Retained native-issued renderer control transport

The system SHALL implement EARS CONTROL-024. Native owns purpose reservations,
ordinals and immutable ticket bytes; the renderer owns only bounded transport
retention, observed delivery and independent confirmation. Existing physical,
terminal-proof, processing, Unknown and original deadline barriers remain.

#### Scenario: Lost transmission and receipt retry exact native bytes
- **GIVEN** an original native-issued ticket and a later queued ticket
- **WHEN** transmission or its native delivery receipt is dropped
- **THEN** the renderer retries the oldest exact wire without reserialization
- **AND** the native dispatcher echoes its receipt without invoking the effect again
- **AND** the later ticket waits for the original head receipt

#### Scenario: A native proposal is not a delivery receipt
- **GIVEN** a retained ticket and an alreadyDelivered proposal advisory
- **WHEN** the renderer receives that proposal again
- **THEN** it retains the pending row and retries the original oldest packet
- **AND** changed bytes, gaps, foreign realms and invalid counters cannot advance it

#### Scenario: Confirmation survives an empty data queue
- **GIVEN** a trusted native receipt observed by the renderer
- **WHEN** its independent confirmation transmission is dropped
- **THEN** the exact compact confirmation prefix remains available for retry
- **AND** delivery and confirmation alone do not settle the physical job

#### Scenario: Synchronous receipt yields to the next host poll
- **GIVEN** two original native-issued tickets retained in order
- **WHEN** the first post synchronously delivers its native receipt
- **THEN** the callback cannot recursively post the next data packet
- **AND** the next bounded host transport poll advances the retained neighbor

#### Scenario: Fresh realm rejects the old native ticket
- **GIVEN** strict completed scoped detachment and independently confirmed controls
- **WHEN** the same Active subject opens on the unchanged Native grant in a greater epoch
- **THEN** the new outbox and actual native dispatcher reject old tickets and receipts
- **AND** the renderer does not allocate ordinals or reset the shared Native grant

#### Scenario: Renderer reload waits for original realm recovery
- **GIVEN** a controlled realm with outstanding native tickets or a retained prefix
- **WHEN** its renderer context reloads
- **THEN** the host recovers those original tickets and prefix before resuming controls
- **AND** an empty constructor does not establish recovery or permit replay of Unknown

### Requirement: Readonly native realm recovery after renderer context loss

The system SHALL implement EARS CONTROL-025. Recovery preserves the original
native realm, purpose reservations, prefixes and physical/Unknown obligations.

#### Scenario: Native retains an unconfirmed issued neighbor
- **GIVEN** an original dispatched ticket and another native-issued pending ticket
- **WHEN** the renderer context is lost before receipt observation or confirmation
- **THEN** readonly recovery pages retain both original ticket bytes and native prefixes
- **AND** a new context retries the oldest original packet before its neighbor
- **AND** native issuance and the Native grant remain unchanged

#### Scenario: Inventory changes while pages are collected
- **GIVEN** captured issued, delivered and confirmed native frontiers
- **WHEN** any captured frontier changes before the next page
- **THEN** the native owner refuses that inconsistent page
- **AND** inventory itself does not invoke an effect or change a reservation

#### Scenario: Incomplete recovery cannot post or confirm
- **GIVEN** incomplete, mixed, foreign, noncontiguous or misplaced recovery pages
- **WHEN** a new renderer transport context validates that inventory
- **THEN** construction refuses without a data or confirmation callback
- **AND** the original native owner and obligations remain retained

#### Scenario: Confirmed recovery preserves the distinction from a past wire
- **GIVEN** a native confirmed prefix and no old JavaScript object
- **WHEN** a new transport context recovers that original prefix
- **THEN** it may retry the compact independent confirmation without replaying old data
- **AND** it does not claim to have retained a past wire or recovered the Elm model
- **AND** actual typed host and WebKit reload acceptance still requires separate evidence

### Requirement: One typed Elm policy for native preview realm detachment

The system SHALL implement EARS CONTROL-026 in the existing PreviewPresenter.
Scoped preview membership completion is distinct from permanent Native retirement.

#### Scenario: A current outer wrapper contains a foreign inner binding
- **GIVEN** an enrolled controlled realm and an otherwise valid native envelope
- **WHEN** its source, catalog or lifecycle carries another Native binding
- **THEN** the policy refuses before enrollment, retargeting or command emission
- **AND** all original member state and counters remain unchanged

#### Scenario: Scoped close retains unresolved original jobs
- **GIVEN** an original known job or cold metadata member in the controlled realm
- **WHEN** the exact native scoped seed or trusted quarantine arrives
- **THEN** display and new demand stop while original obligations remain retained
- **AND** no permanent Retired fact is fabricated
- **AND** exact terminal ACKs precede scoped readiness in the emitted command list

#### Scenario: Lost final delivery and processing acknowledgement
- **GIVEN** original settled lifecycle state and matching scoped readiness
- **WHEN** the final scoped delivery or its processing ACK is lost
- **THEN** the retained native delivery removes the member only at its contiguous prefix
- **AND** an exact duplicate re-emits only the original processing ACK
- **AND** changed entries, floors, facts or delivery gaps cannot advance that prefix

#### Scenario: A same live subject opens under a greater realm
- **GIVEN** completed scoped membership, independent confirmation and strict native close
- **WHEN** native supplies a greater receiver epoch on the unchanged Native grant
- **THEN** the same single policy can enroll the still Active subject in that realm
- **AND** old envelopes, tickets and receipts remain refused
- **AND** permanent retirement chronology and unrelated shared-host state are preserved

#### Scenario: Cold members have zero request floors
- **GIVEN** a bounded metadata-only native catalog with no fabricated capture jobs
- **WHEN** its realm is quarantined and the original zero-floor seeds arrive
- **THEN** UI closure retains each member until its own scoped completion
- **AND** one readiness and ordered processing ACK applies to each original member
- **AND** a new UI publication and greater closed realm can re-enroll the live members

#### Scenario: Transport context recovery retains the existing Elm policy
- **GIVEN** one retained Elm policy and an unconfirmed native-issued control ticket
- **WHEN** the JavaScript transport context is recreated
- **THEN** original native inventory restores transport without resetting that policy
- **AND** ticket retry returns original delivery evidence without replaying acquisition
- **AND** this does not qualify recovery of an Elm model lost with an actual WebKit context

### Requirement: Exact native ingress for original Elm policy proposals

The system SHALL implement EARS CONTROL-027 without changing the original
purpose reservations, physical barriers or Native grant.

#### Scenario: A foreign outer proposal contains a current command
- **GIVEN** an actual admitted original native job and its current command body
- **WHEN** the outer proposal carries a foreign binding or receiver epoch
- **THEN** native refuses before issuance and retains its original issued frontier
- **AND** the original job and physical resource obligations remain identical

#### Scenario: An aggregate or malformed proposal reaches native
- **GIVEN** a bounded original native owner and its authenticated receipt capability
- **WHEN** an envelope is aggregate, empty, oversized, malformed or contains extra fields
- **THEN** native refuses atomically without issuing its first row as a partial result
- **AND** renderer ordinal fields cannot enter the native-issued namespace

#### Scenario: The same exact policy purpose is proposed again
- **GIVEN** a previously issued original native purpose ticket
- **WHEN** native receives the same valid singleton policy proposal
- **THEN** its original ticket bytes and ordinal remain unchanged
- **AND** ingress does not invoke the effect or settle a physical obligation

#### Scenario: Pure packetization validates the complete policy output
- **GIVEN** ordered commands emitted by the one existing Elm Presenter
- **WHEN** any singleton would exceed the original shape, quota or byte budget
- **THEN** packetization refuses before returning any wires to post
- **AND** valid output preserves original order, binding, epoch and command bodies
- **AND** it allocates no renderer ordinal and mutates no Elm state

#### Scenario: Actual Popup receives typed native realm data
- **GIVEN** a trusted native realm grant and the existing compiled Popup policy
- **WHEN** exact realm events, quarantine or native-close notifications arrive
- **THEN** Popup delegates to that same immutable PreviewPresenter
- **AND** bare events cannot downgrade an already controlled realm
- **AND** compilation alone does not establish real host or WebKit activation

#### Scenario: A proposal is lost before native can issue its ticket
- **GIVEN** a policy command emitted once and no native-issued ticket for it
- **WHEN** the proposal transport is lost before native ingress
- **THEN** an explicitly retained ingress handoff is required before host activation
- **AND** a post-issuance ticket inventory or emitted readiness flag cannot prove delivery
- **AND** recovering transport does not reconstruct a lost Elm policy

### Requirement: Retain original Elm intent before native ticket issuance

The system SHALL implement EARS CONTROL-028 in the existing immutable Elm model.
Transport bookkeeping SHALL contain no second window policy or native ordinal issuer.

#### Scenario: A readiness proposal never reaches native
- **GIVEN** a settled original lifecycle and an emitted scoped readiness proposal
- **WHEN** the proposal is lost before the actual native issuer receives it
- **THEN** the same Elm model retains its exact original intent for trusted retry
- **AND** an empty native recovery inventory cannot remove that intent or permit close

#### Scenario: Native issuance is independent of effect completion
- **GIVEN** an original retained acquisition or cleanup intent
- **WHEN** an exact native-issued ticket matches its realm and original command body
- **THEN** Elm removes only that proposal intent
- **AND** its known job, Unknown outcome and physical settlement remain unchanged

#### Scenario: A ticket changes its inner purpose or domain
- **GIVEN** an exact pending original intent and a current outer ticket domain
- **WHEN** the ticket wire changes its identity, command, inner domain or ordinal
- **THEN** the pending intent remains available for exact retry
- **AND** malformed, foreign, aggregate and unknown ticket facts also refuse

#### Scenario: A full native-facing queue receives cleanup
- **GIVEN** original pending intents occupying the native-granted queue capacity
- **WHEN** quarantine generates reconciliation and cleanup from the same policy
- **THEN** the candidate revokes demand/display and retains the deferred output
- **AND** further policy input waits until exact issued facts and retry free capacity
- **AND** every retry preserves the original order without losing a command

#### Scenario: Quarantine arrives while ordinary output is already deferred
- **GIVEN** an original acquisition intent and another member's deferred acquisition
- **WHEN** trusted quarantine arrives before either native issuance handoff completes
- **THEN** the same policy immediately revokes demand/display for both members
- **AND** both original Unknown jobs and ordered pending/deferred acquisitions remain
- **AND** one bounded reconciliation/cleanup batch follows those older intents
- **AND** repeated quarantine cannot append a second safety batch

#### Scenario: Retained unissued work prevents realm replacement
- **GIVEN** empty physical membership but outstanding original proposal intents
- **WHEN** a close notification or greater receiver grant arrives
- **THEN** Elm retains the original realm until its ingress is empty
- **AND** native strict physical close and independent confirmation remain separate gates

#### Scenario: Retry is bounded and requires the original native domain
- **GIVEN** a pending queue and at most one deferred original transition batch
- **WHEN** trusted retry arrives under the same native binding and receiver epoch
- **THEN** Elm transfers only available slots and emits the oldest bounded pending rows
- **AND** a foreign retry neither transfers deferred rows nor emits original controls
- **AND** real host input backpressure and full context recovery require their own evidence

### Requirement: Own the retained Elm policy outside renderer transport contexts

The system SHALL implement EARS CONTROL-029 without introducing another window
policy or changing the original native issuer and settlement authorities.

#### Scenario: Renderer transport is recreated while intent remains
- **GIVEN** the original creator-owned JavaScriptCore Elm worker and a retained intent
- **WHEN** the renderer transport context is recreated
- **THEN** the same worker retains the same original model and exact intent
- **AND** native purpose issuance and recovery preserve the original grant and epoch
- **AND** a renderer view SHALL receive a projection without another lifecycle policy

#### Scenario: Native input cannot enter the original policy
- **GIVEN** a policy owner and its original creator thread
- **WHEN** a foreign thread or malformed closed-union input attempts invocation
- **THEN** the owner refuses before invocation and remains usable by its creator
- **AND** neither an emitted projection nor a refusal establishes an effect outcome

#### Scenario: Deferred cleanup blocks ordinary inputs
- **GIVEN** original pending acquisition and deferred reconciliation/cancellation
- **WHEN** another ordinary native, presentation or legacy input arrives
- **THEN** native returns explicit WOULD_BLOCK without changing the same Elm state
- **AND** the caller retains and retries that original input after capacity admits it
- **AND** trusted quarantine still revokes demand through the block
- **AND** current synthetic-ticket tests do not establish real host input custody

#### Scenario: The worker cannot provide an exact processed output
- **GIVEN** original held compiled worker bytes and private native scheduling
- **WHEN** initialization throws, output is missing, duplicated or malformed,
  or the original asynchronous processing limit expires
- **THEN** processing is classified as Unknown with no successful output
- **AND** constructor cleanup before a grant supplies no live-policy recovery authority
- **AND** the desktop default scheduling context is not pumped by the worker

#### Scenario: Normal destruction is requested too early
- **GIVEN** an open controlled realm or retained policy membership/intent
- **WHEN** destruction is requested before its trusted close notification and empty ingress
- **THEN** native refuses while retaining the original owner
- **AND** final processing intent still blocks destruction after membership empties
- **AND** original native physical close and independent confirmation remain separate

#### Scenario: The policy execution context itself is lost
- **GIVEN** transport recovery qualified with a persistent worker
- **WHEN** the JavaScriptCore context or owning process is lost or uncertain
- **THEN** this component provides no model reconstruction or native grant reset authority
- **AND** full context/process recovery and real WebKit/Core activation remain explicit gates

### Requirement: Project visuals from the single immutable preview policy

The system SHALL implement EARS CONTROL-030 while retaining the original
preview/window lifecycle transitions and native effect/settlement authorities.

#### Scenario: The same policy shows live and historical content
- **GIVEN** an original authorized drawable and current presentation stamp
- **WHEN** the original policy selects live or historical status
- **THEN** the existing popup view and typed projection share that exact decision
- **AND** the projection contains only the original drawable token and fidelity
- **AND** it neither reconstructs a lifecycle model nor settles its known job

#### Scenario: Preview metadata becomes concealed
- **GIVEN** an original known job and owned frame pending physical retirement
- **WHEN** locked scope, quarantine or exact detachment conceals the preview
- **THEN** the projection removes its drawable and concealed preview metadata
- **AND** original Unknown/retiring resources survive until exact terminal settlement
- **AND** full desktop/surface-control concealment retains its separate policy gates

#### Scenario: A projection changes domain or ordered membership
- **GIVEN** an original native binding/epoch and ordered popup presentation
- **WHEN** a projection changes its domain, duplicates/reorders rows or omits a row
- **THEN** the pure decoder refuses the complete projection
- **AND** it preserves original popup2051/bar259 and lossless UInt64 boundaries

#### Scenario: Visual shape attempts an arbitrary URI or concealed metadata
- **GIVEN** a closed live/historical/loading/unavailable visual union
- **WHEN** a drawable lacks its original token/fidelity, fallback contains a frame,
  or extra metadata, fields, malformed tokens or arbitrary URI values arrive
- **THEN** the pure decoder refuses before producing a rendered projection
- **AND** accepted labels render as bounded text through the shared view helper

#### Scenario: CPU projection evidence is ready for integration
- **GIVEN** compiled policy/decoder coupling and unchanged original control assertions
- **WHEN** the actual host is prepared to switch away from its legacy Popup policy
- **THEN** native authentic delivery order, current projection custody, renderer reload,
  URI ownership and actual WebKit/Core/DOM behavior require separate acceptance
- **AND** only one window/lifecycle policy may be activated

### Requirement: Read committed visual data without advancing policy

The system SHALL implement EARS CONTROL-031 while preserving the original policy,
native ordinal issuer, effects and physical retirement authorities.

#### Scenario: The creator reads the same committed projection twice
- **GIVEN** an open controlled native-owned policy and a successful output
- **WHEN** its original creator requests two visual copies
- **THEN** both contain only the same six typed visual fields
- **AND** no JavaScript invocation, model transition, command or ordinal occurs

#### Scenario: A caller alters an owned visual copy
- **GIVEN** a separately allocated copy of committed visual data
- **WHEN** the caller mutates its bytes and requests another copy
- **THEN** the new copy and original private policy output remain unchanged

#### Scenario: Ordinary input is blocked after quarantine
- **GIVEN** original deferred proposals and a committed concealed projection
- **WHEN** ordinary input receives WOULD_BLOCK and the creator reads visuals
- **THEN** the read returns exactly that last committed projection
- **AND** refused input, known jobs and pending custody remain unsettled

#### Scenario: The read has no valid authority
- **GIVEN** a foreign caller, missing destination, absent or closed authority,
  or inflight or uncertain processing
- **WHEN** a visual copy is requested
- **THEN** the owner refuses with no projection and the caller conceals
- **AND** no refusal authorizes grant reset, worker reconstruction or settlement

#### Scenario: A component copy is prepared for a renderer
- **GIVEN** accepted bounded read-only copy evidence
- **WHEN** host integration is prepared
- **THEN** authenticated current delivery, order, renderer leases and reload
  concealment require separate qualification before activation
- **AND** actual WebKit/Core/DOM/URI and full release gates remain required

### Requirement: Retain ordered native visual custody across renderer replacement

The system SHALL implement EARS CONTROL-032 without advancing the single
window/lifecycle policy or native control ordinals when delivering visuals.

#### Scenario: Native replaces a renderer instance
- **GIVEN** an original attached context and issued visual sequence
- **WHEN** native detaches it and attaches its replacement
- **THEN** a new positive native renderer lease uses the retained sequence floor
- **AND** the original context reference is released only at detach
- **AND** old callbacks and packets cannot accept or seed the replacement

#### Scenario: Renderer delivery is retried or reordered
- **GIVEN** native retained one current visual snapshot and exact receipt
- **WHEN** duplicate or older packets arrive at the pure renderer
- **THEN** duplicates repeat only the same acceptance receipt
- **AND** older packets cannot revive visuals or acknowledge a newer snapshot
- **AND** native retry retains the original exact bytes and sequence

#### Scenario: The committed policy changes before a receipt arrives
- **GIVEN** an issued visual snapshot and its eventual renderer receipt
- **WHEN** the original policy's latest visual data or domain changes
- **THEN** native refuses acceptance/retry/current status of that stale snapshot
- **AND** it clears visual custody while retaining policy/effect/resource obligations

#### Scenario: A renderer encounters conflicting current data
- **GIVEN** a fixed native grant and accepted visual sequence
- **WHEN** malformed current data or different visuals with that same sequence arrive
- **THEN** the pure renderer conceals and latches uncertainty
- **AND** later packets cannot reset it or introduce another lifecycle policy

#### Scenario: A visual counter exhausts
- **GIVEN** an original native visual sequence or renderer lease at UInt64 maximum
- **WHEN** another snapshot or renderer grant would require advancing it
- **THEN** native refuses without resetting it or consuming a control ordinal

#### Scenario: The ordered component is prepared for actual host use
- **GIVEN** native custody and pure receiver component evidence
- **WHEN** a real WebKit route is prepared
- **THEN** native callback identity, physical concealment before transitions,
  async completion barriers, DOM/frame application and URI ownership need acceptance
- **AND** pure receipts do not qualify ongoing freshness or full release behavior

### Requirement: Retain native driver inputs and original issued tickets

The system SHALL implement EARS CONTROL-033 with one persistent original Elm
policy, original native issuance/effects and independent confirmation. Native
driver custody SHALL survive renderer replacement within the owning process.

#### Scenario: Driver initialization encounters a constructor fault
- **GIVEN** the exact empty original native controlled namespace
- **WHEN** private outbox or worker construction fails before policy admission
- **THEN** only constructor-owned contexts and its registry entry are released
- **AND** the original native namespace and grant remain unchanged
- **AND** another driver cannot bind an already owned or nonempty namespace

#### Scenario: An ordinary input exceeds custody capacity
- **GIVEN** 1065 retained inputs or insufficient remaining serialized byte capacity
- **WHEN** native attempts to admit another event batch or presentation
- **THEN** WOULD_BLOCK leaves original queued representations and policy unchanged
- **AND** the producer retains unadmitted bytes and pauses further production

#### Scenario: Quarantine arrives while ordinary input is full
- **GIVEN** full ordinary custody and a known or Unknown original job
- **WHEN** the original native creator quarantines the original epoch
- **THEN** quarantine reaches the single policy through its urgent lane
- **AND** queued inputs and job/resource obligations remain retained

#### Scenario: JavaScript receives a native-issued ticket
- **GIVEN** an original policy proposal and its original native ticket
- **WHEN** the private outbox stages a post callback
- **THEN** the driver already owns exact ticket bytes and performs no native effect
- **AND** a separate issuance notification precedes subsequent native dispatch

#### Scenario: A dispatched effect returns a receipt with an Unknown outcome
- **GIVEN** original native dispatch and its returned data receipt
- **WHEN** the private outbox observes that exact receipt
- **THEN** native returned events are retained before transport custody is released
- **AND** confirmation remains a separate native action
- **AND** receipt or confirmation alone cannot settle the original physical/job duty

#### Scenario: Shutdown encounters original outstanding custody
- **GIVEN** retained inputs, events, tickets, confirmations or policy/native duties
- **WHEN** native requests normal driver closure
- **THEN** closure refuses while those duties remain
- **AND** only the original strict native closure and trusted policy closure permit exit

#### Scenario: Component driver evidence is prepared for host activation
- **GIVEN** native C/JSC driver checks with a synthetic native peer
- **WHEN** an actual browser host route is prepared
- **THEN** output bounds, paused producer scheduling, WebKit callback identity,
  async frame/concealment/URI and delayed proposal outcome gates remain required
- **AND** in-process custody does not establish process-loss recovery or full release

### Requirement: Reserve bounded original native output custody before effects

The system SHALL implement EARS CONTROL-034 under the held original native
producer contract, preserving original policy, issuer, physical and closure gates.

#### Scenario: Original dispatch produces maximum-field wire data
- **GIVEN** maximum UInt64 fields and the original fixed 64-character token
- **WHEN** original C serializers produce a two-frame batch or next journal completion
- **THEN** that fixed output fits the 8192-byte pre-effect reservation
- **AND** journal completion dispatch returns only its next retained wire

#### Scenario: Output capacity is unavailable before dispatch
- **GIVEN** an original native ticket already notified to the policy
- **WHEN** another batch or 8192 bytes cannot be reserved
- **THEN** WOULD_BLOCK retains the exact original ticket and existing custody
- **AND** no original native capture or effect counter advances

#### Scenario: Quarantine arrives through output pressure
- **GIVEN** an original held ticket and unavailable output reservation
- **WHEN** the original creator quarantines the same native epoch
- **THEN** the single policy revokes demand while retaining known physical duties
- **AND** the ticket remains exact and no effect runs until capacity is available

#### Scenario: Capacity becomes available for the held ticket
- **GIVEN** refusal occurred before native dispatch
- **WHEN** the reservation becomes available
- **THEN** the original ticket proceeds once through the original C dispatcher
- **AND** its data receipt and independent confirmation do not settle physical duties

#### Scenario: An offer and fence await policy admission
- **GIVEN** an original C acquisition returned two original frame events
- **WHEN** the unchanged policy's deferred gate permits input
- **THEN** one action processes the offer and another processes the fence
- **AND** those admitted events precede further output-producing dispatch
- **AND** processing them performs no additional native effect

#### Scenario: A producer violates its fixed output contract
- **GIVEN** native dispatch returned an unexpected original outcome
- **WHEN** its size or shape violates the held producer contract
- **THEN** exact events, ticket and receipt remain in live uncertain custody
- **AND** no truncation, grant reset or normal bounded success is claimed

#### Scenario: A bounded first-ticket pressure trace is qualified
- **GIVEN** maximum-field checks and selected C/JSC/model traces
- **WHEN** component output custody is reviewed
- **THEN** actual output exhaustion, workload progress, RSS/performance and paused host producers remain separate gates
- **AND** actual GUI/WebKit/frame/concealment/URI and full release acceptance remain open


### Requirement: Connect the native policy through actual controlled GTK/WebKit custody

The system SHALL implement EARS CONTROL-035 with original native admission and
closure authorities. The QA-only route keeps its curtain closed until actual
physical reveal is separately qualified.

#### Scenario: Native GTK admission is not yet complete
- **WHEN** current publication/lease/configuration/grab/application proof is absent
- **THEN** only the presentation-only placeholder runs
- **AND** no controlled native owner, grant or second window policy is created

#### Scenario: Original GTK admission establishes the controlled route
- **GIVEN** actual current native subject and admitted GTK publication/lease
- **WHEN** the owning host opens the controlled factory
- **THEN** one persistent native Elm policy retains the original grant and inputs
- **AND** the native channel supplies a fixed one-time pure renderer initialization

#### Scenario: Producer input is refused under pressure
- **WHEN** exact host input cannot enter the driver
- **THEN** the original bytes remain retained and another producer poll is paused
- **AND** original driver work continues draining so pressure can clear

#### Scenario: A new surface commit would exceed host presentation custody
- **WHEN** native preflight cannot reserve the exact frame before effects
- **THEN** the original commit remains preflight-unsent with its original disposition
- **AND** no accepted current GTK frame is silently dropped

#### Scenario: A navigation invalidates an asynchronous renderer initialization
- **WHEN** the original view navigates after live native policy admission
- **THEN** native conceals and retains the original live policy and obligations
- **AND** an old navigation callback cannot initialize or reconstruct the receiver

#### Scenario: A renderer acknowledges decoded and applied display bytes
- **GIVEN** the original manager/view and exact latest native visual receipt
- **WHEN** DOM/RAF and native current-projection checks pass
- **THEN** that receipt remains distinct from physical Wayland frame acceptance
- **AND** the unqualified controlled route keeps its native opacity curtain closed

#### Scenario: Actual WebKit context routes a preview URI
- **WHEN** the original receiver requests its native-issued preview capability
- **THEN** the context-owned router checks the native endpoint/receiver/epoch
- **AND** stream closure cannot settle original physical or journal obligations

#### Scenario: Shutdown encounters live uncertain or undrained host custody
- **WHEN** normal shutdown is requested
- **THEN** the original driver/native closure refuses and retains obligations
- **AND** the run reports failure without a grant reset or normal-exit claim

#### Scenario: Original scoped detachment removes the native subject mapping
- **GIVEN** the original native actor inventory reports no controlled subject
- **WHEN** the host schedules its next producer action
- **THEN** identity-based polls and detachment seeds stop
- **AND** original pending terminal, retirement and detachment delivery continues
- **AND** mapping absence does not settle policy, input, ticket, confirmation or physical custody


### Requirement: Close the actual compiled page asset package before native admission

The system SHALL implement EARS CONTROL-036 using the actual compiled asset
package and the owning scheme's closed local allowlist.

#### Scenario: A controlled page names an unbuilt renderer script
- **WHEN** a page reference has no regular file in the exact compiled package
- **THEN** packaging preflight fails before native host qualification
- **AND** a successful compiler command alone cannot establish page readiness

#### Scenario: A page references an asset outside the owning allowlist
- **WHEN** a script or stylesheet name is absent from the actual owning scheme table
- **THEN** packaging preflight fails without widening arbitrary URI admission

#### Scenario: Compiled page references are complete
- **WHEN** all bundled page scripts/styles exist within the original size and name bounds
- **THEN** their exact filenames and package hashes are retained
- **AND** WebKit execution, original GTK/frame/reveal/closure and recovery gates remain separate

### Requirement: Bind private captured-image evidence to the current native projection

The system SHALL implement EARS CONTROL-037 without granting physical reveal
authority to image reports or offscreen WebKit snapshots.

#### Scenario: A pure renderer reports its loaded image
- **WHEN** original popup context and acknowledged native projection are current
- **THEN** native validates the original native-issued URI and bounded image dimensions
- **AND** a private snapshot retains the original projection, epoch and navigation

#### Scenario: A projection changes while a snapshot is pending
- **WHEN** its asynchronous callback has a stale view, epoch, navigation or projection
- **THEN** its pixel observation is rejected before accepted evidence is written
- **AND** original policy, physical resources and journals remain under their original authorities

#### Scenario: An independent oracle decodes actual offscreen preview pixels
- **WHEN** exact source colors and foreign-content exclusion pass
- **THEN** that bounded rendered-image evidence is retained
- **AND** physical frame/concealment/reveal and recovery/full release gates remain open

### Requirement: Bind private GTK paint and output-region evidence to original native custody

The system SHALL implement EARS CONTROL-038 while preserving the closed curtain
and all original policy/native effect and closure authorities.

#### Scenario: A current native projection schedules a paint observation
- **WHEN** native attaches its private observer to the original popup frame clock
- **THEN** at most one callback retains the original popup/view and projection scope
- **AND** supersession, invalidation, uncertainty and shutdown release that observer

#### Scenario: A stale paint callback runs
- **WHEN** its original view, popup, epoch, navigation, publication, lease or projection differs
- **THEN** it produces no accepted geometry/paint observation or reveal authority

#### Scenario: Native observes the current GTK paint phase
- **WHEN** all original object and current projection guards pass
- **THEN** native records actual GDK geometry, opacity and GTK frame counter
- **AND** that phase remains distinct from compositor and hardware presentation

#### Scenario: A closed-curtain output region is reviewed
- **GIVEN** a current actual source image and independently decoded private output region
- **WHEN** the same oracle also detects an actual unsafe-curtain variant
- **THEN** only that bounded region observation may be qualified
- **AND** ongoing transition concealment, physical reveal and recovery remain open

### Requirement: Retain an actual delayed WebKit result through original invalidation

The system SHALL implement EARS CONTROL-039 as an explicit private QA stimulus
without changing normal policy/native effects, deadlines or closure gates.

#### Scenario: A real snapshot completion is deliberately delayed
- **WHEN** the one-shot controlled QA stimulus receives the original WebKit result
- **THEN** one retained slot holds its actual result/view/completion scope
- **AND** no finish, accepted artifact, effect settlement or deadline renewal occurs

#### Scenario: Actual popup closure invalidates the retained projection
- **WHEN** the original native channel is invalidated
- **THEN** the same result is finished once and its stale scope is rejected
- **AND** its references drain without publishing stale pixels or erasing native obligations

#### Scenario: Normal shutdown encounters the retained observation
- **WHEN** native shutdown releases that actual result
- **THEN** the current-context guard and original strict native/policy close remain mandatory
- **AND** observation cleanup cannot certify outstanding effects or unknown recovery
# Requirement: Preserve the single persistent policy across normally retired native realms

The system SHALL implement EARS CONTROL-040 using original strict C/Bootstrap
closure and Native epoch issuance. Realm replacement SHALL preserve the same
Elm policy owner and permanent incarnation-retirement chronology.

#### Scenario: Native realm retirement still has outstanding custody
- **WHEN** policy/input/deferred/ticket/returned-event/confirmation/physical/journal duties remain
- **THEN** normal retirement and realm replacement are refused with that exact custody retained

#### Scenario: A normally closed native realm is reopened
- **GIVEN** original strict native closure and a later empty issued epoch on the same binding
- **WHEN** native rebinds the driver
- **THEN** the exact same persistent Elm policy transfers to the sole new driver
- **AND** only its drained old grant-bound transport is replaced

#### Scenario: A stale epoch or foreign binding requests replacement
- **WHEN** it differs from the original same-binding later Native grant
- **THEN** it is refused before policy processing and original policy custody remains unchanged

#### Scenario: A permanently retired window is replayed in a later realm
- **WHEN** original retired-window source facts enter the later envelope
- **THEN** the persistent retirement chronology refuses resurrection and new acquisition

#### Scenario: The GUI reopens its renderer
- **WHEN** the host opens a later native preview realm
- **THEN** the original fixed-grant renderer/context and strict object lifetime gates still apply
- **AND** actual GTK/WebKit qualification is required separately from C/JSC traces
# Requirement: Reopen the native GUI through the same policy and a fresh fixed-grant context

The system SHALL implement EARS CONTROL-041 using original Native retirement and
admission authority, preserving every outstanding duty and permanent policy fact.

#### Scenario: The user closes an admitted popup
- **WHEN** its original native presentation is invalidated
- **THEN** demand is quarantined and original custody drains through strict native retirement
- **AND** the same Elm policy remains alive for a later native realm

#### Scenario: A user reopens while the old realm drains
- **WHEN** the later popup intent already owns a lease/window/grab
- **THEN** it retains that original ownership while the old realm finishes
- **AND** a replacement renderer requires fresh DOM admission before a new preview factory opens

#### Scenario: The later context becomes admitted
- **WHEN** its original GTK/publication/lease and manager/view match
- **THEN** the later Native epoch rebinds the exact same policy and initializes its fixed grant once
- **AND** old context grants, receipts and callbacks remain inadmissible

#### Scenario: Native QA captures a later current preview
- **WHEN** its snapshot completes with the original epoch/view/navigation/projection still current
- **THEN** it publishes only a fresh monotonically numbered artifact
- **AND** private pixels and DOM/GTK observations grant no physical reveal authority

### Requirement: Original physical reader survives a later popup intent
The controlled host SHALL retain sticky original quarantine and all closing realm
obligations even if a later native popup is ready. Explicit QA may retain a real
original URI/GIO reader; it SHALL never manufacture a cleanup fact or reset grants.

#### Scenario: New intent while an old original reader is held
- GIVEN a current original preview image with a real retained native-authorized reader
- WHEN the popup closes and a later actual popup intent is configured
- THEN original held and fresh URI reads are revoked, old strict close remains blocked,
  and detachment/receipt producers continue against the closing realm's original scope

#### Scenario: One reader close and independent native settlement
- WHEN the private monotonic stimulus closes the actual original reader once
- THEN all original policy, physical, journal and confirmation gates still precede
  retirement and replacement, and no newer intent cancels old custody

#### Scenario: Retired renderer replacement inside the later popup
- GIVEN the old native realm is strictly closed and the later popup owns its GTK lease
- WHEN the host replaces the retired renderer child
- THEN that popup window/lease/grab persist, fresh DOM admission precedes a later
  fixed grant, and current images, chronology, original normal exits and cleanup qualify separately

### Requirement: Original async completion across a reopened renderer
The host SHALL retain original result/view/epoch/navigation/projection custody
until that result is consumed once, even when the old native realm strictly
closes and its renderer is replaced. Stale completion SHALL have no current
artifact, policy, grant, job settlement or reveal authority.

#### Scenario: Old real snapshot finishes after current new-realm receipt
- GIVEN one actual old WebKit result held across strict old native close
- WHEN the new same-policy epoch acknowledges its own current native projection
- THEN original finish executes once and original scope rejection accepts no old artifact
- AND the later current source image/snapshot preserves request chronology and
  original independent native teardown under unchanged deadlines

### Requirement: Error ownership follows original async scope
Stale original async errors SHALL have no failure authority in a later renderer
realm. Original finish SHALL consume its result once before scope disposition;
owned result/error cleanup SHALL preserve all Native custody and original gates.

#### Scenario: Canceled old snapshot arrives in new realm
- GIVEN an actual canceled WebKit result retained with its original old view
- WHEN the old native realm strictly closes and a current replacement acknowledges
  its later same-policy epoch projection
- THEN original finish reports its actual error once and old scope disposes it
- AND the current source image/new snapshot and strict normal close remain usable

#### Scenario: Current matching snapshot fails
- WHEN a current matching async result returns failure
- THEN original fail-closed reporting and retained Native custody remain in force
- AND stale-error disposal is not used to hide that current failure

### Requirement: Current renderer failure retains an ordered native drain
The host SHALL preserve the original failure outcome while keeping original
native custody and retirement progress alive. Concealment or process exit SHALL
NOT certify settlement. Unknown duties SHALL never be automatically replayed or
cleared to obtain closure; strict retirement remains the native authority.

#### Scenario: Current snapshot failure while a captured job is owned
- GIVEN a real matching-current WebKit cancellation and an original owned native job
- WHEN original fail-closed reporting begins
- THEN the renderer is concealed and receives no new work, while original native
  observations and receipts drive its existing duties to strict retirement
- AND the host exits with failure only after the original custody is actually drained
- AND the original observer deadline, single policy and native authority remain intact

#### Scenario: Current failure with uncertain native custody
- WHEN original native duties cannot be proved settled
- THEN uncertainty remains explicit and no normal closure or recovery is claimed
- AND no renderer disposal, reset, inferred process death or fabricated receipt settles those duties

### Requirement: Known renderer reload preserves policy and strict native retirement
Reloading an admitted renderer's trusted same URI SHALL preserve original
native custody and policy. Only original strict native retirement SHALL admit
a replacement renderer and later epoch; navigation or DOM reload SHALL never
certify native settlement or reset a grant, policy, counter, deadline or Unknown.

#### Scenario: Real same-popup WebKit reload with a known captured job
- GIVEN the original current source image and first real snapshot are captured
- WHEN the actual WebKit reload API causes original view navigation to advance
- THEN the host conceals/invalidate that renderer and quarantines the original realm
- AND original native receipts drive strict close before replacement in the same GTK popup/lease
- AND fresh DOM/fixed-grant admission precedes a later native epoch on the same policy/binding
- AND monotonic snapshot/nav chronology, current source pixels and final strict normal close qualify under the original deadline

#### Scenario: Unexpected URI or uncertain native duties at reload
- WHEN reload does not retain a trusted same URI or original native duties are uncertain
- THEN original fail-closed uncertainty remains explicit with no inferred settlement, grant reset or replay

### Requirement: Shared renderer termination preserves native custody before recovery
Actual shared renderer process termination SHALL retain its failure and original
native custody. Known preview duties SHALL drain through original native receipts
and strict close before GTK recovery/restart controls. Native uncertainty SHALL
prevent normal retirement/restart; process disappearance SHALL NOT infer settlement.

#### Scenario: Actual shared WebKit process termination after current capture
- GIVEN one original captured image and first actual snapshot with native duties known
- WHEN the actual WebKit terminate-process API delivers the original termination signal
- THEN renderer authority is invalidated and the original realm urgently quarantined
- AND original native receipts and independent physical/journal/confirmation gates close custody before GTK recovery controls
- AND failure remains failure with no policy/grant/navigation/snapshot/deadline reset or inferred settlement
- AND whole-host restart, outstanding window commands and durable Unknown qualify separately

#### Scenario: Uncertain native duties at shared process failure
- WHEN original native custody is uncertain at renderer termination
- THEN strict retirement and restart remain refused and Unknown is retained without automatic replay

### Requirement: Explicit whole-host restart preserves uncertain window commands
The host SHALL retain original durable window-command admission and Unknown
when a committed native effect loses its settlement receipt. An explicit native
Restart SHALL replace only the shell through its sealed supervisor. A fresh
binding SHALL carry the original pending record without automatic resubmission;
only a coherent current scene and a new explicit intent may admit another effect.

#### Scenario: Actual restore commits before its broker receipt is lost
- GIVEN a real pointer-driven committed minimize and a subsequent real restore
- WHEN the broker stops after native restore commit and before settlement/delivery
- THEN actual application pixels and keyboard focus show the restored window
- AND original exact keyed durable admission remains Pending while the GUI shows Unknown
- AND original deadlines and compositor/application identities remain unchanged

#### Scenario: Native Restart retains the original unknown intent
- GIVEN renderer failure with that original pending window admission
- WHEN the user selects the actual native Restart control
- THEN the original host exits with explicit restart code and the sealed supervisor starts a fresh host
- AND the same compositor lifetime and application incarnations persist
- AND the new binding carries the exact original record normalized to Unknown with no automatic replay
- AND a coherent scene precedes a new pointer command with advanced request/generation and current native state
- AND verified shell-cohort cleanup and independently waited helper exits remain required

#### Scenario: Reservation retirement retains historical outcome uncertainty
- WHEN a native binding-retirement proof and accepted post-proof reads release the original reservation
- THEN the ledger durably retains that original Unknown record and its retirement evidence
- AND capacity release does not certify an effect outcome or authorize replay
- AND a newer explicit command cannot rewrite the original historical Unknown

#### Scenario: Controlled preview recovery needs separate combined qualification
- GIVEN the main window-command restart scenario passes without an active controlled preview realm
- THEN combined preview retirement and window-command recovery remains unqualified
- AND no evidence from process disappearance substitutes for original native preview settlement

### Requirement: Combined preview retirement and window-command recovery
The shared host SHALL retain original known preview custody and the exact
uncertain window-command admission across broker and renderer failure. Native
Restart SHALL remain unavailable until strict original preview retirement;
an explicit new host SHALL recover the window Unknown without automatic replay.

#### Scenario: Held native preview reader blocks recovery after receipt loss
- GIVEN an actual pointer-admitted preview with captured source pixels and an original retained GIO reader
- AND actual popup close revokes that reader while native retirement stays blocked
- WHEN a real window command commits but loses its broker receipt and the shared renderer fails
- THEN window Unknown and original reader/policy/ticket/journal/confirmation custody remain distinct
- AND the original reader closes once before strict native empty custody and GTK recovery
- AND process death supplies no settlement proof or new grant authority

#### Scenario: Explicit new host preserves Unknown and captures through a fresh owner
- WHEN the user selects the real native Restart control after strict preview retirement
- THEN the same sealed supervisor starts a fresh host on the surviving compositor lifetime
- AND exact original window Unknown survives without replay before a coherent scene and advanced explicit intent
- AND original historical Unknown survives native reservation retirement and the newer effect
- AND new actual preview demand captures the same source through the fresh host's own native namespace
- AND independently observed source pixels, original clock, strict new preview retirement and verified cohort cleanup remain required
