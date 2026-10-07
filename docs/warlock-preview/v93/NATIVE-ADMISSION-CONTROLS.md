Native admission control reservations

This amendment implements CONTROL-004 on the actual Coordinator/Broker admission
path, while its opt-in provider and WebKit integration remain separate gates.
No queue reservation creates a job, physical completion proof or Elm policy.

EARS CONTROL-007: BEFORE the first job is issued, the native endpoint SHALL enroll
its original receiver and assign its original epoch without inventing a subject
or borrowing an existing physical job. Later subject enrollment SHALL extend that
same receiver and SHALL NOT reset its epoch. An empty receiver SHALL authorize
no URI reads, terminal receipts or captures.

EARS CONTROL-008: BEFORE retaining a new native actor or calling the original
Coordinator/Broker job issuance operation, the native admission guard SHALL
reserve that actor's and job's cleanup credits under the original receiver grant.
Insufficient transport credits SHALL leave the original intent, job request floor,
physical reservation and native deadline unchanged. Exceptions after issuance
SHALL retain the pending control reservation for native reconciliation; the guard
SHALL NOT assume that an exception means no job was issued.

A conservative quota for one actual ImportedClients job is five distinct native
slots: one Acquire, one Cancel, one Release, and at most two terminal proof ACKs.
The actual imported producer admits one packet and calls producerComplete once.
Native Broker producerRefused/destroy produces at most two terminal proofs; a
terminal Cancel adds a cancellation proof only if it is absent. Offer/Fence are
not terminal ACKs. Repeated terminal delivery can emit unlimited identical Elm
ACKs; those must reuse a validated original slot, never consume a fresh quota.
The native one-packet condition is necessary: generic untrusted Offer events or
a different producer are not covered by this bound. The conservative five-slot
bound allows both proof ACKs even where Elm emits only the final correlated ACK.

An actor needs two distinct slots: exact RetireReady and its final retirement
processing ACK. Retries reuse original slots. Binding-wide Reconcile needs an
independent retained slot with native canonical correlation and exact-identity
coalescing; its implementation and unknown-outcome reconciliation remain open.

The planned upper capacity is 5 * 8 + 2 * (2 * subjectLimit) + 1. Eight is the
actual imported Broker record bound; the admission guard also caps retained job
control cohorts at eight even if physical record ACK precedes frontend transport
confirmation. Active native actors and retained completed journal rows may
coexist, each bounded by subjectLimit (at most256). The additional slot is for
binding reconciliation. This is a transport upper bound, not S02 timing/resource
acceptance. Actual admission must enforce these retained-cohort limits and must
not release quota until original physical/proof/actor and transport barriers
independently clear. Frontend staging, native typed-slot validation, canonical
reconciliation, renderer tickets and reload handling still require integration.

Executable evidence must show the actual Broker terminal proof bound, the
compiled Elm worst-case Acquire/Cancel/Release/ACK path and repeated ACK behavior,
receiver enrollment before admission, and transport refusal before physical job
issuance. Until those witnesses and integration pass, this document describes
the conservative reservation contract, not full provider acceptance.

EARS CONTROL-009: WHEN a retained original-receiver cleanup command references
the exact original job/token and the actual native packet is ready, the native
controlled decoder SHALL validate cleanup against that native packet even if a
delayed Offer still reports signaled:false. Renderer readiness flags SHALL NOT
create native readiness or bypass physical/proof barriers. The original command
bytes SHALL remain the ticket's immutable retry identity. Legacy strict decoding
and its original negative controls remain unchanged; activation of the controlled
path is a separate provider/WebKit gate.

Held GUI98 records the executable counterexample: actual optimized Elm emits a
Release for a late original Offer after Cancel, with signaled:false, and the
original decoder rejects it despite the actual native packet being ready. An
actual held URI reader prevents terminal proof before Release. This is coupled
CPU evidence with fixture bytes and synthetic source facts, not a deployed GUI
or genuine capture failure. Fresh GUI99 implements retained-path validation.

EARS CONTROL-010: WHEN native ImportedClients opts into cleanup reservations,
attachment SHALL require an empty original receiver and no prior intent, actor,
job or policy reset. The guard SHALL bind the exact owning Broker and permit
only one obligation manager for that issuer. Initial/new-stamp admission SHALL
reserve before advancing an intent or issuing a job. Resume SHALL first preserve
original mapping/export/backend/proof barriers and frontend delivery confirmation
for the old control job, then reserve before creating or advancing the new resume
intent. Receiverless legacy start/resume entry points SHALL be refused in the
controlled mode. Unknown issuance SHALL remain pending for reconciliation.

GUI100 wires this opt-in guard to the actual ImportedClients start/resume paths.
No C factory or WebKit code activates it yet. Controlled C ticket validation,
confirmed-command tombstones for old repeated ACKs, physical/actor quota release,
receiver replacement and renderer/native-ticket outbox remain required before
activation. Budget exhaustion must not rewrite an original cutoff or retry a
physical capture. Old fixed assertions remain separate and unchanged.

GUI100 is held with forty actual authenticated-socket admission controls,
fifteen selected Quint scenarios, twenty-three coupled native traces and191
comparisons, six compiled unsafe variants, the95-command full-host build and all
twelve original regression suites passing. This qualifies the opt-in C++ path;
the original C factories and shared-host WebKit flow remain unchanged.

EARS CONTROL-011: WHEN the original receiver proposes a job command, native SHALL
validate its actual job, packet or terminal proof before selecting the stable
native purpose slot and issuing a reserved immutable ticket. Exact retries SHALL
reuse original issuance even after the effect removes its Broker record. After
independent physical/proof settlement and original frontend confirmation permit
job-credit release, at most one confirmed predecessor per retained actor SHALL
remain. Exact predecessor retries SHALL report only already-delivered identity,
without another invocation grant or ordinal. Foreign receivers, changed bytes,
invented proof sequences and older unretained jobs SHALL NOT obtain a fabricated
delivered disposition. Unknown and unretained outcomes require separate native
reconciliation; transport confirmation never certifies effect success.

GUI101 implements this purpose issuer in the actual opt-in ImportedClients path.
Validation precedes new issuance under the original Endpoint/Broker lock. Stable
slots are Acquire1, Cancel2, Release3 and the two actual terminal proof ACKs4/5.
The predecessor snapshot is allocated before the confirmed old quota is erased;
an allocation failure cannot advance admission. The predecessor remains bounded
by retained native actor ownership and is replaced only after the next job's
independent settlement. It carries no live bank ticket or native cleanup proof.
Controlled C factory, actual capture, actor/quota final release, reconciliation,
native-assigned renderer transport and WebKit activation remain required.

EARS CONTROL-012: WHEN the actual controlled actor retires, independent original
physical/proof/other-receiver barriers SHALL precede job-credit release, and
original old-control confirmation SHALL precede a fresh permanent native query.
The existing all-map transaction SHALL mark control actor retirement without a
new fallible post-commit operation. Native-issued dispatched readiness and an
exact currently invoking final ACK ticket SHALL guard their respective effects.
Actor credits SHALL remain until actual final processing and original frontend
confirmation both occur. Confirmed Unknown effects SHALL retain original native
journal/actor credits, refuse binding close and receive no effect reinvocation
from transport retry. Collection SHALL preserve all original issuance frontiers.

GUI102 implements these additional barriers in the actual opt-in aggregate
retirement path. The260-actor check uses an authenticated synthetic Native socket
and actual metadata actors, Coordinator/Broker, receiver, journal and C prefix.
It uses no real windows, captured FD, backend lock or compiled Elm/WebKit route;
it does not close the real native/Elm turnover or host shutdown release gate.
The strict completed-actor binding-close helper applies after permanent native
retirement and confirmation. Closing a presentation or detaching a binding with
live native windows requires a separate explicit native namespace-detachment
contract and must not infer permanent incarnation retirement. Controlled C
factory/routing, this live-binding detachment, reconciliation, renderer tickets
and WebKit activation remain required.

EARS CONTROL-013: WHEN native accepts exact retirement readiness, it SHALL retain
its immutable original bytes before publishing acceptance and SHALL use those
bytes during later native polling. Semantically equivalent JSON formatting SHALL
NOT replace an original issued ticket. Retained bytes SHALL remain bounded and
correlated with the original receiver/actor/observation; all physical/proof and
frontend-confirmation barriers still apply.

GUI103's original whitespace witness fails because the old journal reconstructed
readiness during polling, invalidating the exact native ticket. The failed
authenticated-socket fixture is retained. The fresh journal stores the accepted
raw readiness before setting its accepted flag and later copies that same wire.
The first fix compile exposed an uninitialized aggregate member under-Werror;
that failed compile is retained and the member now has an explicit empty default.

EARS CONTROL-014: WHEN the controlled C provider opens, it SHALL claim one native
preview namespace without a live legacy preview provider, enroll the actual
receiver before initial admission and derive its original endpoint epoch.
Reload SHALL retain the same owner rather than reset the old namespace. Legacy
raw C controls SHALL refuse controlled owners. The C dispatcher SHALL invoke only
native-issued original immutable tickets and preserve contiguous at-most-once
delivery under the actual receiver/binding/epoch. A returned delivery receipt
SHALL certify only dispatcher return; an Unknown outcome SHALL retain both that
receipt and original obligations. Live-binding detachment, actual native grant
retirement/reconciliation and renderer/WebKit activation remain separate gates.

GUI103 now provides an explicit controlled C factory and native purpose proposal,
dispatch, receipt and confirmation APIs. The actual Native transport records one
controlled namespace; live legacy C owners hold leases, and controlled opening
requires their absence. Raw imported commands, retirement controls and bootstrap
proof ACKs refuse the controlled namespace. The dispatcher validates the actual
creator thread, receiver, borrowed same Endpoint receipt capability, original
binding/epoch, native-owned exact ticket and contiguous prefix before invocation.
The exact latest returned ticket may echo its cached receipt after core exit;
receipt confirmation uses the original cached grant and cannot invoke effects.
An error after invocation records dispatcher return while retaining Unknown
obligations. The controlled empty/close path independently checks original actor
maps, journal, reservations and every issued ticket confirmation. It closes only
the completed-actor binding; live-window detachment remains open.

The actual controlled C fixture passes260 metadata actors/1041 uninterrupted
native tickets, including a nonfinal proof ACK handler refusal that retains the
Broker record, exact retries, confirmed predecessor suppression, raw bypass and
foreign/gap refusal, final ACK after C subject erasure, actor quota reclamation
only after final confirmation, and cached receipt/confirmation after actual
synthetic core normal exit. This is authenticated synthetic Native socket/C
bootstrap/Coordinator/Broker/journal evidence, with no real windows or capture.
The first C fixture incorrectly compared two calls to the advancing `next()`
allocator as equal. Its failed report is retained; the fresh fixture corrects
only the allocator arithmetic, with production source unchanged.

EARS CONTROL-015: BEFORE capture invocation, native SHALL retain the original
immutable request/binding/context/raw command/deadline. Capture or FD-transport
failure SHALL preserve that intent without acquisition replay or false cleanup.
Exact backend export ownership SHALL precede fallible local mapping/adoption.
Only actual Broker adoption SHALL publish its mapping pointer, including an
exception after transfer; refusal/pre-transfer exception SHALL publish no pointer.
Original native reconciliation and local-resource proofs remain mandatory.

GUI104 records a bounded immutable native capture intent before effect invocation
and retains it across refusal, malformed completion and unavailable FD transport.
These three actual authenticated-socket cases preserve original Broker charge,
refuse capture replay and retain exact request bytes/context/deadline. Mapping
adoption now retains only actual Broker storage, including a receipt-allocation
exception after transfer. Four actual sealed-FD/Broker controls cover success,
refusal, pre-transfer allocation failure and post-transfer receipt allocation
failure; original local mapping/FD and terminal proof/ACK drain still apply.
Three unsafe native variants compile and fail original assertions. This retains
the information needed for reconciliation; it does not yet provide a native
backend cleanup-state protocol, settle Unknown captures, activate WebKit or
qualify real compositor capture or live-window binding detachment.

EARS CONTROL-016: Original native capture/export uncertainty SHALL be resolved by
authenticated exact request/subject/binding resource observation and scoped
idempotent cleanup, never acquisition replay. Export and producer obligations
remain independently observable under lock/revocation/expiry; another current
capture SHALL remain untouched. Producer lock barriers remain mandatory. Native
reply construction SHALL precede resource mutation, and a lost reply SHALL be
resolved by fresh observation. Backend zero cannot erase independent local FD,
mapping/readers, Broker proof, frontend processing or incarnation obligations.

GUI105 and owning-core16/plugin19 are fresh inactive sources for this protocol.
The fully qualified runtime remains GUI92/native128/core16/plugin18. GUI104 is
held at capture intent/adoption component scope (51+22 controls,14 capture
scenarios/66 traces/816 states/three variants, controlled C10190/260/1041 and full95).
The actual native resource engine and wire encoder, typed GUI decoder and
controlled C reconciliation path are implemented. Six actual authenticated
synthetic socket cases cover refusal/malformed capture/unavailable FD and lost
export/producer responses. Backend zero is checked before unoffered Broker
settlement; locked producers and malformed observations retain the original
charge. An issued ticket alone grants no cleanup. The final actors still need
actual permanent native incarnation facts, original proof ACK, final delivery
processing and independent control confirmation. These are CPU component
witnesses, not real compositor capture or imported-FD acceptance.

EARS CONTROL-017: Multiple original family Reconcile commands for one native
binding SHALL reuse one canonical native-issued reserved ticket. Only its
actual dispatch under the original native receiver and borrowed receipt
Endpoint SHALL quarantine that binding. Native polling SHALL re-observe and
settle original scoped resources without replaying acquisition; it SHALL
advance the fair entry cursor before a fallible operation, process at most one
original job and three resource operations per reconciliation poll, and retain
all independent local mapping/readers, terminal proof, actor and confirmation
barriers. Quarantine SHALL refuse new source admission and acquisition. Native
backend zero SHALL NOT be treated as permanent window incarnation retirement
or complete binding detachment. No measured UI performance acceptance follows
from the polling bound.

EARS CONTROL-018: Upon actual original binding reconciliation dispatch, the
single native quarantine state SHALL revoke existing and newly opened preview
URI read authorization immediately, before the first physical cleanup poll.
An existing reader SHALL retain its original storage reference until actual
close; permission denial SHALL NOT establish FD/mapping closure or final proof.
Native backend zero SHALL preserve original local mapping and charge while any
reader owns the buffer. A capture whose actual Broker adoption committed before
result allocation failed SHALL retain that exact mapping/packet, independently
complete its producer/reader/backend barriers and produce its actual Released
and Cancelled proofs, never fabricate an unadopted producer refusal.

Fresh GUI106 owns these actual SCM_RIGHTS/imported mapping/GIO-reader witnesses
and the original post-transfer allocator failure. Held GUI105/plugin19 remain
unchanged. Public72 is verified b4a72a5ce672dd05647c256ab5ef4b60aad5eddb
(10115 exact owned blobs); local source1387ee79b973310c060e68e20b6e2ec2ac0d9aa8
and receipt972f7a1f0c44da9fd6f28b1e0cfeb17f91cf2101. GUI106 is mutable and
inactive; no native compositor capture, WebKit or release qualification yet.

EARS CONTROL-019: When an original reconciliation purpose has been independently
confirmed, any exact reproposal for that binding SHALL return the same native
ticket bytes and ordinal with alreadyDelivered true, including after later job
or actor controls. A delivered but unconfirmed purpose SHALL remain eligible
for original receipt retry. Neither flag nor confirmation SHALL settle any
physical/backend/local/actor obligation or replay reconciliation or capture.

GUI106 fixes the binding purpose's confirmed-retry result. The first two coupled
local-resource fixture runs are retained: their teardown reproposed a confirmed
old purpose after final job ACK and encountered the original contiguous-prefix
rejection. The fresh fixture suppresses confirmed proposals, and the additional
trace tests exact reproposal after final ACK. No original ticket, prefix,
deadline or physical retirement guard is weakened.

Native129/core16/plugin19 with retained GUI92 legacy runtime is held at bounded
native qualification:2517 checks/278 normal exits/full cleanup,2459 original128
and2458 original126 fixed controls plus original allocator/expiry assertions.
The additive actual Core resource phase passes49 controls/11 scoped snapshots
and closes two imported sealed SCM_RIGHTS descriptors independently from backend
zero. Real private lock, original target/foreign binding/subject/transfer guards,
application-dropped ACK recovery and another current capture are exercised.
This does not claim kernel socket loss, native106 controlled factory/WebKit
activation, live-window binding detachment or full-release acceptance. Original
expired/revoked capture resource witnesses and current controlled integration
remain explicit work. Component/native evidence and source hashes stay separate.

EARS CONTROL-020: A controlled preview receiver realm SHALL obtain its epoch
from the original Native transport's monotonic namespace, before any subject/job
admission. That namespace SHALL survive endpoint replacement, consume failed
construction epochs without reuse, and refuse exhaustion before admission.
Only complete original physical/proof/actor/final-processing/control closure
SHALL release a published realm claim; unreported constructor rollback SHALL
release only that unpublished claim. A replacement SHALL retain the exact shared
Native binding/session/frontend and use a fresh epoch, rejecting every old
ticket before handler invocation. The transport SHALL never downgrade to legacy
preview ownership after entering controlled mode. These transport facts SHALL
NOT be treated as permanent window retirement or completed live-window detach.

The no-downgrade obligation includes a legacy admission already paused between
its namespace check and atomic claim. Controlled close must retain persistent
namespace state so a stale zero-state compare/exchange cannot cross that close.

GUI107 is held and inactive. Current111 replacement/exhaustion C controls,
36 actual threaded controls,16 selected Quint/28 coupled actual C traces/711
states, full95 and original current resource/capture/ticket/FD regressions pass.
Six failed reports and pre-race-fix passing evidence remain frozen separately.
Native129/public74 remains the actual GUI92/Core16/plugin19 bounded tuple,
2517 checks/278 normal exits; it does not qualify current107 controlled C/WebKit
activation. Full release, live-window detach, Bootstrap reattachment and typed
frontend realm delivery remain open. Publication75 is the next owned delivery.

EARS CONTROL-021: When a controlled C owner closes through its original owning
Bootstrap, native code SHALL validate that Bootstrap's exact transport,
Endpoint, receiver epoch, creator thread and empty borrowed receipt membership
before mutation. Every original physical/proof/actor/final-processing and
independent-confirmation close barrier SHALL still pass. Only after successful
native claim completion SHALL the Bootstrap release its borrowed delivery
before Endpoint destruction. Refused close or a foreign Bootstrap SHALL retain
the original handle and owner. A subsequent owner SHALL attach a fresh receipt
channel under its new native epoch without replacing the shared Native grant.
These local lifetime facts SHALL remain available after Core death, and SHALL
NOT certify live-window binding detachment or frontend processing.

EARS CONTROL-022: While a native application incarnation remains Active, the
preview provider SHALL support a distinct scoped binding-detachment transaction
under its original native receiver epoch. Only its canonical native-issued
reconciliation and detach-readiness controls SHALL authorize that transaction's
input; readiness SHALL NOT establish physical cleanup. Actual backend/export/
producer/local mapping/reader settlement, final terminal-proof acknowledgment,
receiver/Coordinator/Broker/intent/frame ownership and original control quotas
SHALL precede native aggregate removal. The provider SHALL mint a distinct typed
preview-binding-detached completion under that original epoch, retaining it
through exact frontend processing acknowledgment and independent confirmation
before strict Bootstrap-aware realm close. Permanent incarnation-retirement
facts and controls SHALL retain their existing semantics and SHALL NOT substitute
for scoped detachment, or receive a fabricated Retired state. A new realm SHALL
reenroll the same still-Active subject under fresh receiver/channel/opaque URI
identity on the unchanged Native session/frontend. Every old event, ticket,
completion and URI SHALL refuse against the new realm; no Unknown acquisition
or shared-host operation SHALL be replayed or reset.

CONTROL-022 scoped C path is implemented and CPU-qualified in inactive GUI109.
The exact actual C/SCM_RIGHTS/GIO/model/cohort/current build/regression scope and
four retained fixture failures are in GUI109/DETACHMENT-HANDOFF.md and
component-report109.json. Typed frontend realm wrappers, safe WebKit URI
lifetime/routing and actual controlled Core/Wayland qualification remain open.

EARS CONTROL-023: When a native WebKit preview route outlives a controlled
Endpoint or its receiver realm, each callback SHALL use a lifetime-safe native
read capability bound to the original Shared state, Endpoint lifetime, Native
binding, receiver identity and epoch. The capability SHALL reject retired,
replaced, foreign or destroyed owners before allocating a reader, including
when existing readers retain original storage. Endpoint destruction SHALL
revoke that lifetime under the same mutex as native reads; retaining a callback
SHALL NOT retain or fabricate application/producer authority. A stable native
router SHALL retain its original binding and monotonic realm frontier through
clear/rebind, refuse stale epochs and require its creator thread for mutation.
WebKit context callback ownership SHALL retain the router independently of the
C owner's reference and release it on context destruction. Existing URI nonce,
native time/privacy/source authorization, read limits and physical/proof/reader
cleanup barriers SHALL remain mandatory. These routing lifetime facts SHALL
NOT certify actual WebKit/Core capture or authorize replay of Unknown effects.

CONTROL-023 native read capability/stable reference-counted router/new WebKit
dispatcher are implemented and CPU-qualified, compiled but inactive in GUI110.
C66/four sealed mappings/three guard variants/model16/24/320/200 samples/full96
retaining original95/current resource and scoped-detachment regressions pass.
Two model fixture failures retained; actual WebKit callback registration/
controlled Core/Wayland-window/native renderer realm outbox remain open.

EARS CONTROL-024: When a controlled renderer transports a native-issued preview
ticket, it SHALL retain the exact original ticket bytes and Native binding,
receiver epoch and ordinal in a bounded contiguous queue. Native SHALL remain
the sole purpose-reservation and ordinal issuer. A dropped transmission or
delivery receipt SHALL retry the original oldest ticket without reserializing
its command or invoking a later ticket first. Changed bytes, foreign realms,
noncanonical counters, gaps and excess capacity SHALL refuse before altering
the transport frontier. A proposal's alreadyDelivered advisory SHALL NOT remove
a queued ticket. Only the trusted original native delivery receipt for that
head SHALL advance the observed receipt prefix. The renderer SHALL retain and
retry an independent exact confirmation prefix even after its data queue is
empty. Neither delivery nor independent confirmation SHALL assert physical or
Elm effect settlement, renew a deadline, reset the Native grant or replay an
Unknown effect. Synchronous receipts SHALL NOT recursively post the next data
ticket; the next bounded host poll SHALL supply progress. Renderer reload SHALL
recover the original native realm, retained tickets and confirmed prefix before
resuming controls; constructing an empty outbox SHALL NOT certify recovery.

CONTROL-024 transport is implemented and CPU-qualified in inactive GUI111:
93 actual controlled C/Bootstrap/Native socket/Broker/native-issued JS roundtrip
checks across two same-Active-subject epochs;47 adversarial/full uint64/UTF8/
synchronous reentry controls;14 selected Quint/26 actual JS traces/463 state
comparisons/200 bounded samples/six executable guard variants. Three failed
roundtrip fixtures remain. Typed host routes, renderer reload recovery and
actual WebKit/Core activation remain open. The legacy host does not load this
new module. See GUI111/NATIVE-OUTBOX-HANDOFF.md for exact evidence scope.

EARS CONTROL-025: When a controlled renderer loses its JavaScript context, the
native owner SHALL retain the original realm and expose readonly bounded pages
of its independently confirmed, delivered and issued prefixes and exact native
tickets. Each page SHALL contain at most one original ticket and16384 bytes.
Recovery SHALL refuse foreign sender epochs, in-flight dispatch, invalid page
positions or changed captured prefixes before modifying any transport, purpose
or physical ownership. A new transport context SHALL validate complete,
contiguous, consistently bound pages before emitting data or confirmation. Its
first bounded host poll SHALL retry only the oldest original unconfirmed native
ticket. Recovery SHALL NOT issue an ordinal, replace a Native grant, refresh an
original deadline, settle an effect from delivery or replay Unknown. Recovering
a confirmed prefix SHALL remain distinct from having retained its past wire,
recovering the Elm policy model and qualifying an actual WebKit context reload.

CONTROL-025 code is implemented in inactive GUI112; current C129/JS recovery
and model24/36/498/200 samples/nine executable JS variants/full98/original four
resource regressions pass. Three compiled native guard variants and all four
current scoped-detachment regressions also pass. Actual typed host/WebKit/Core activation remains open.

EARS CONTROL-026: While a native controlled preview realm is enrolled, the single
Elm PreviewPresenter SHALL admit only exact envelopes for that original Native
binding and receiver epoch, and SHALL validate the same binding inside source,
catalog, lifecycle, metadata and retirement inputs before mutation. Bare legacy
inputs SHALL NOT enter a controlled policy. When that realm is quarantined,
Elm SHALL revoke display and demand immediately while retaining known jobs,
physical-resource obligations, cold metadata members and original request
counters. Binding reconciliation SHALL use the exact native canonical identity
before cleanup proposals; native SHALL issue every ticket and ordinal. When
the original scoped seed arrives, Elm SHALL match its binding, epoch, subject,
entry and request floor without inventing permanent Native retirement. Only
after the original lifecycle settles SHALL Elm emit terminal ACKs followed by
one distinct scoped readiness command. Only a contiguous final delivery that
exactly matches retained readiness and settlement SHALL remove that member.
An exact retained duplicate SHALL re-ACK transport only; changed facts and gaps
SHALL refuse. A greater receiver epoch SHALL require trusted native close of
the empty original realm and SHALL preserve permanent retirement chronology,
Native grant and unrelated shared-host state. Ordinary UI closure, transport
delivery, independent confirmation and JavaScript recovery SHALL NOT fabricate
that close or recover a missing Elm policy model.

CONTROL-026 is held in GUI113: current Elm44/native C+Elm+outbox175/two
Active-subject epochs on unchanged Native grant; Quint20/32/469/six compiled
variants; cold256/1549; original permanent45/native20+C34/model14/34/667;
full103 retains98. Eight failed attempts and earlier phase snapshots remain.
Actual controlled shared-host/WebKit/Core activation and full Elm recovery open.

EARS CONTROL-027: When the native owner receives an Elm preview proposal,
it SHALL validate the exact closed protocol/kind/Native binding/receiver epoch
envelope, creator thread, original popup and borrowed receipt capability before
issuing a native purpose ticket. Each ingress SHALL contain one original member
row and one original command within the unchanged4096-byte budget. Foreign,
malformed, oversized, empty or aggregate envelopes and renderer-assigned ordinal
fields SHALL refuse without consuming a native ordinal or changing original
job/resource obligations. The original native purpose guards SHALL remain
mandatory for every accepted command, and exact duplicate proposal retries
SHALL retain their original native ticket bytes and ordinal. Pure renderer
packetization SHALL validate the whole ordered policy output before returning
singleton wires and SHALL NOT allocate ordinals, settle an effect or mutate Elm
state. Actual Popup realm ports SHALL delegate to the existing PreviewPresenter
and SHALL NOT reconstruct a second preview policy. Compiling those ports SHALL
remain distinct from activating and qualifying real shared-host/WebKit routes.

Before activating that route, lost proposals before native issuance require an
explicit retained ingress/issued-ticket handoff. The post-issuance outbox cannot
recover a command that never reached native. Neither an emitted readiness flag
nor an empty native ticket inventory can certify that delivery. Transport-only
context recovery retains a still-existing Elm policy; actual WebKit context loss
requires separately qualified recovery of that policy and its outstanding work.

EARS CONTROL-028: While a controlled preview realm exists, its single immutable
Elm model SHALL retain every original ordered proposal intent before port
emission. When a proposal is lost before native issuance, a trusted same-domain
retry SHALL emit the oldest retained intents with unchanged identity, command
body, binding and receiver epoch. Only an exact native-owned issued-ticket fact
whose original wire matches the pending intent and both native domains SHALL
remove that intent. Foreign, malformed, changed-body, changed-inner-domain,
changed ordinal, empty, aggregate or unknown-purpose facts SHALL retain it.
Issuance SHALL NOT certify transport delivery, effect success, physical resource
settlement, terminal ACK, processing completion or independent confirmation.

The native-facing pending queue SHALL respect its original granted capacity.
If one accepted policy transition exceeds its free slots, Elm SHALL retain the
remaining original transition output in a bounded deferred batch, preserve
original order and hold back further ordinary policy inputs until retry admits it.
Trusted quarantine SHALL bypass that ordinary input block, immediately revoke
display/demand and retain its own bounded safety batch behind older original
intents while preserving known jobs. Repeated quarantine SHALL NOT append another
safety batch; the existing policy closing flag remains authoritative. The
pending queue plus one ordinary and one quarantine batch SHALL remain bounded
to3195 intents, with each original transition at most1065 rows. Neither a full
queue nor an emitted readiness flag SHALL
discard cleanup or permit realm close/replacement. A batch exceeding the original
1065-row or4096-byte singleton limits SHALL refuse atomically before committing
the candidate policy. Real host activation requires durable input backpressure,
native-owned issued facts, retained original tickets before dispatch and an
explicit bounded retry schedule. Compiled Popup and synthetic peer tests SHALL
remain distinct from that host qualification and full Elm context recovery.

EARS CONTROL-029: While the retained preview policy exists, its native owner
SHALL retain one compiled immutable Elm worker, its original creator thread,
private JavaScriptCore context, private scheduling context and exact input/output
custody independently of recreated renderer transport contexts. The native API
SHALL expose no mutable JavaScript value or context and SHALL issue no native
ticket, dispatch no effect and infer no physical settlement. The existing single
PreviewPresenter SHALL remain the only window/lifecycle policy. Activating a
native-owned policy requires a renderer projection without another policy instance.

When an input arrives on a foreign thread or fails the bounded closed native
input union, the owner SHALL refuse before policy invocation and retain the
original state. While ordinary output is deferred, ordinary native/presentation/
legacy inputs SHALL return explicit WOULD_BLOCK before invocation; the caller
SHALL retain each original refused input until admission. Trusted quarantine and
exact original issued/retry facts SHALL remain admissible through that block.
This API refusal SHALL NOT imply real host input storage or retry qualification.

When original processing lacks exactly one bounded valid output, has a runtime
exception, leaves scheduling work unsettled or exceeds the original three-second
asynchronous replay limit, the owner SHALL classify processing as Unknown rather
than safe refusal, successful execution or authority to reset the native grant.
Private native timers SHALL execute the held Elm port tasks without pumping the
desktop default context. Constructor failure before any grant SHALL release its
unpublished resources; this SHALL NOT qualify recovery of an uncertain live policy.

When normal destruction is requested, the owner SHALL require the original
creator thread, no uncertain/inflight processing, empty policy membership and
ingress, no deferred output or pending native timers, and the original trusted
closed notification for a controlled realm. Empty rendering or native inventory
alone SHALL NOT authorize destruction. This Elm notification SHALL remain
separate from original native physical/processing/independent-confirmation gates.
Recreated transport-context evidence SHALL NOT qualify actual WebKit reload,
JavaScriptCore/process-loss recovery, captured resources or full release acceptance.

EARS CONTROL-030: While the native-owned single Elm preview policy produces
display data, its visual projection SHALL share the original lifecycle status,
drawable authorization, metadata concealment, presentation-stamp and enabled-row
decisions with the existing popup view. Its lifecycle transitions, known jobs,
resource ownership, proposal retention and native issuance/settlement rules SHALL
remain unchanged. A renderer SHALL receive typed visual data rather than another
window/lifecycle model, original jobs, pending effects or diagnostic metadata.

When a visual projection is decoded, the decoder SHALL require its original
native binding/receiver epoch, closed protocol/field union and exactly the original
ordered popup identities. It SHALL preserve the original popup2051/bar259 limits
and lossless UInt64 strings. Only nonzero original 64-character lowercase opaque
tokens SHALL form fixed preview/icon URIs. Live/historical shapes SHALL contain
the original drawable token/fidelity without fallback title/icon metadata;
loading/unavailable shapes SHALL contain no frame/fidelity. Hidden/fallback/local
states SHALL remain distinct closed variants. Text SHALL preserve the original
1024-byte preview-label bound and render as text without arbitrary HTML/URI fields.

When the original preview policy conceals a locked, quarantined or detached
preview, the visual projection SHALL omit its concealed preview metadata and
drawable token while leaving Unknown, known jobs and physical retirement intact.
Concealment of surface controls and the full desktop SHALL retain their separate
original presentation-policy gates; this preview DTO SHALL NOT invent those proofs.

When a pure renderer decoder or projection helper is qualified, that evidence
SHALL NOT establish actual DOM/WebKit rendering, URI capability reads, native
pixels, delivery ordering, resource budgets or full release acceptance. Before
activation, native host custody SHALL deliver only the current typed visual
projection through an authenticated original-domain channel with explicit
ordering/reload/concealment barriers, preserving the single policy authority.

EARS CONTROL-031: When the original native creator requests the current visual
projection of an open controlled policy, the owner SHALL return a separately
allocated copy of only the six typed visual fields from the latest successfully
processed output. This read SHALL invoke no JavaScript, mutate no model, emit no
command and allocate no native ordinal. Caller mutation or disposal of a copy
SHALL leave the original private cache and every subsequent copy unchanged.

When the caller is foreign, the output destination is missing, or authority is
absent, closed, inflight or uncertain, the owner SHALL refuse with no projection.
The caller SHALL conceal on refusal. While ordinary input is refused before
processing by WOULD_BLOCK, the read SHALL retain the exact last committed visual
projection, including its original quarantine concealment; it SHALL NOT imply
that refused input was processed or release pending jobs, proposals or custody.

When a read-only copy passes bounded component checks, the system SHALL NOT treat
it as authenticated current delivery, a renderer lease, freshness, ordered
replacement, actual DOM/URI/physical acceptance or permission to reconstruct an
uncertain worker. Those host and renderer barriers SHALL remain required before
activation. Native issuance, independent confirmation and physical retirement
SHALL retain their original authorities and deadlines.

EARS CONTROL-032: When native attaches an original renderer context to visual
custody, the creator SHALL strongly retain that context and issue a fresh positive
renderer lease. Separate native visual sequence and lease counters SHALL remain
lossless UInt64, survive detach/reload within that channel and refuse exhaustion
without reset. Neither counter SHALL issue or consume a native control ordinal.

When an original attached context requests a snapshot or exact retry, custody
SHALL read only the original policy's committed visual projection. New snapshots
SHALL advance only the visual sequence and invalidate prior acceptance. Retry
SHALL preserve exact bytes/sequence. Before retry, exact receipt acceptance or
current acceptance is reported, custody SHALL require the same latest committed
visual bytes/domain; changed, absent, closed or uncertain authority SHALL clear
visual custody without settling policy, effects or resources. Foreign creators,
contexts and non-original receipts SHALL refuse.

While a pure renderer instance exists, its native domain/lease/floor SHALL be fixed
at initialization. Older snapshots and other domains/leases SHALL NOT revive
visuals. An exact duplicate SHALL repeat only its acceptance receipt. Malformed
current data or conflicting same-sequence visuals SHALL conceal and latch
uncertainty; packets SHALL NOT reset it or establish another lifecycle policy.

Before host activation, native SHALL bind actual WebKit callback identity to its
issued renderer lease, conceal physically before policy changes/invalidation,
reject stale async completions and qualify DOM/frame application and original
URI reader ownership before revealing. A pure acceptance receipt or cache
comparison SHALL NOT establish physical concealment, ongoing freshness, actual
WebKit authentication, native pixels, recovery or full release acceptance.

EARS CONTROL-033: When native creates a policy driver for an original controlled
owner, the creator SHALL verify the exact original grant against native's empty
issued, delivered and confirmed namespace. The owner SHALL have only one driver,
one persistent Elm lifecycle policy and one private transport outbox. A constructor
failure before policy admission SHALL release only its own contexts and registry
entry. Uncertain live admission SHALL retain opaque custody without reconstruction
or a native grant reset.

When a native event batch is admitted, the driver SHALL validate and stamp the
original source epoch/domain before JavaScript, then retain all typed wrapped
events atomically. Ordinary inputs SHALL be bounded by 1065 items and 16 MiB of
serialized wrapped bytes. While either bound or original policy backpressure
prevents processing, refusal SHALL retain the exact queued representation and
leave the producer responsible for unadmitted bytes; the host SHALL pause that
producer. Native urgent quarantine SHALL bypass ordinary input custody without
discarding queued inputs or known/Unknown jobs. Only successful invocation SHALL
remove its input. Process-owned memory SHALL NOT be treated as a process-loss
journal.

When native issues an original proposal ticket, the driver SHALL retain that
exact ticket before notifying the policy or allowing native dispatch. JavaScript
post/confirmation callbacks SHALL store bounded bytes only. A subsequent creator
step SHALL notify issuance before dispatching; native SHALL remain the sole
ordinal/effect authority. A returned data receipt SHALL retain original native
events before releasing transport custody. Confirmation SHALL be a separate
native step and SHALL NOT settle policy jobs or physical obligations. A ticket
without a returned receipt SHALL remain exact; retry SHALL NOT authorize another
handler invocation or infer success from disappearance.

When normal closure is requested, the driver SHALL refuse until ordinary inputs,
returned events, tickets, confirmations, policy membership, ingress and deferred
custody are empty, and original native physical/journal/confirmed gates permit
strict closure. An uncertain live driver SHALL refuse reset/replay/normal close.
Private diagnostics SHALL remain native/QA only. Before GUI activation, retained
native output bounds, producer scheduling, original delayed proposal outcomes,
actual WebKit identity/frame/concealment/URI and all original release gates SHALL
remain independently required; CPU driver checks SHALL NOT establish them.

EARS CONTROL-034: When the original native driver is about to dispatch a retained
ticket, it SHALL reserve one batch and 8192 returned wire bytes before invoking
any native effect. Under the held original producer contract, a dispatch SHALL
return at most two fixed typed frame events or one fixed journal completion;
UInt64 fields and the 64-character token SHALL retain their original encodings.
Normal returned custody SHALL be bounded by 3195 batches and 26173440 wire bytes.
Insufficient reservation SHALL report WOULD_BLOCK with the exact original ticket,
policy, queued inputs, outbox and native effect counters unchanged.

When original returned events are retained and the original policy's deferred
gate admits input, the driver SHALL process those events before dispatching more
output-producing work. Each successful action SHALL remove only its consumed
event; refusal SHALL retain it. Original issuance-notification and independent
confirmation priorities SHALL remain intact. Urgent native quarantine SHALL stay
available through output pressure and SHALL NOT discard held tickets, events or
known/Unknown physical obligations.

If an original producer violates its held output contract, the driver SHALL
retain its exact original outcome, ticket and receipt as live uncertainty before
refusing further normal work. It SHALL NOT truncate/drop that outcome, reset a
grant or claim normal bounded success. This exceptional recovery duty SHALL remain
separate from the normal custody bound and measured workload/RSS acceptance.

When maximum-field serializer checks, a labeled stricter compiled reservation
gate or first-ticket model traces pass, that evidence SHALL NOT imply actual
output queue exhaustion, full-workload progress, measured memory/performance,
actual paused host producer scheduling or native GUI acceptance. Those gates,
actual WebKit callback/frame/physical concealment/URI, uncertain live/process
recovery and original delayed proposal outcome obligations SHALL remain required.


EARS CONTROL-035: While the QA-only controlled GTK/WebKit host is active, the
system SHALL create its native controlled owner and single persistent policy
only after original current GTK/publication/lease admission. Before that admission,
the renderer SHALL contain only validated presentation custody and surface actions,
with no preview lifecycle/window policy or native control ordinal allocator.

When the native visual channel issues a renderer grant, native SHALL initialize
the pure receiver once with that fixed grant. Later projection packets SHALL NOT
establish/reset a grant or initialize another receiver. Native SHALL bind callback
admission to the original manager/view and current navigation identity, epoch and
visual lease/sequence. Navigation uncertainty SHALL conceal and retain the original
live policy/native obligations without constructing a replacement policy.

When host input custody or the driver refuses ordinary input with WOULD_BLOCK,
the host SHALL retain the exact original producer bytes, continue draining original
driver work, and refrain from another producer poll until admission. New surface
commits SHALL reserve host presentation custody before native effects/admission;
preflight refusal SHALL preserve the original unsent-disposition contract.
Unexpected output-contract violations SHALL retain exact exceptional custody as
Unknown rather than discard bytes or claim normal bounded progress.

When original scoped C detachment removes the controlled subject mapping, the
host SHALL read the original native actor inventory before identity-dependent
polling or detachment seeding. The host SHALL stop those identity queries while
continuing original pending terminal, retirement and detachment delivery. Mapping
absence SHALL NOT settle Elm state, retained inputs, tickets, confirmations or
physical obligations, and SHALL NOT authorize resetting or closing the realm.

While DOM/frame/Wayland reveal acceptance remains unqualified, the controlled QA
route SHALL keep its native opacity curtain closed. A decoder/RAF receipt SHALL
NOT reopen that curtain or claim physical concealment/reveal qualification.
The actual WebKit context SHALL retain its own scoped URI router reference; only
native SHALL bind the original endpoint, receiver and epoch. Streams/transport
receipts SHALL NOT substitute for original physical/terminal/independent-confirmation
closure. Shutdown SHALL retain uncertain or undrained custody and report failure.
All actual frame/input/resource/recovery/full release gates SHALL remain required.


EARS CONTROL-036: When preparing the exact compiled GUI asset package, QA SHALL
verify every bundled HTML script and stylesheet reference is a closed local name,
exists as a regular nonsymlink file of the original permitted size, and belongs
to the actual owning scheme allowlist. The controlled page SHALL reference the
original compiled NativePreviewRenderer output, native-visual-renderer.js, and
the admission output native-preview-admission.js. A missing/misnamed referenced
asset SHALL fail preflight before actual controlled native admission. Passing
packaging SHALL NOT establish WebKit execution, actual frame/reveal, recovery or
native/full release acceptance; their original gates SHALL remain required.

EARS CONTROL-037: When the QA-only pure renderer reports a loaded preview image,
native SHALL require the original popup manager, active controlled driver and
current acknowledged native projection before admitting the original URI/size
observer and private WebKit snapshot. The snapshot attempt SHALL retain its
original projection bytes, native epoch and navigation identity. When the
asynchronous snapshot finishes, native SHALL check the original view and current
projection again before writing accepted pixel evidence. A stale observation
SHALL be consumed without settling or replaying a policy/native effect. Actual
image loading and independently decoded offscreen pixels SHALL remain distinct
from physical frame/concealment/reveal authority; the curtain SHALL remain closed.

EARS CONTROL-038: When recording a private native popup paint observation,
native SHALL retain the original popup/view/frame-clock objects, epoch,
navigation, publication, lease and projection for at most one pending callback.
Supersession, frame invalidation, uncertainty and shutdown SHALL cancel that
observer without altering policy/native effects or custody. The GTK after-paint
callback SHALL revalidate those original objects and current acknowledged native
projection before recording GDK geometry, actual opacity and GTK frame counter.
GTK after-paint and GDK geometry SHALL NOT certify compositor or hardware
presentation. A private output-region concealment claim SHALL require a current
actual source-image reference, checked native region, independent output pixels
and an actual unsafe-curtain control detected by the same oracle. That bounded
claim SHALL NOT certify ongoing transition concealment, physical reveal or recovery.

EARS CONTROL-039: When explicit private controlled QA delays a WebKit snapshot
completion, the host SHALL retain at most one actual original result, original
view and completion scope, and SHALL retain the existing pending disposition.
The one-shot stimulus SHALL NOT reset on ordinary input, finish early, fabricate
replacement pixels, alter policy/native effects or renew an original deadline.
After actual native projection invalidation or shutdown, the host SHALL finish
that same original result once, apply the existing current-context/projection
guards and release its references. Stale completion SHALL publish no accepted
pixel artifact or settlement. Original policy/input/ticket/physical/journal/
confirmation obligations and strict close SHALL remain independently mandatory.
This bounded actual-result probe SHALL NOT establish renderer reload, process
loss, uncertain effect recovery, physical reveal or complete stale-callback coverage.
# CONTROL-040: one policy across normally retired native realms

When the original native realm has drained every policy model, retained input,
deferred intent, native ticket, returned event, independent confirmation, physical
resource and retirement/detachment journal obligation, the host shall retire that
realm through its original strict C/Bootstrap close while retaining the same Elm
policy owner. While any such duty or unknown outcome remains, it shall refuse
normal realm replacement and retain the original custody.

When the original Native issues a later receiver epoch on the same binding after
that strict close, the driver shall admit only the exact empty issued namespace,
transfer the same persistent Elm policy, preserve permanent retirement history,
and create only a new grant-bound transport outbox. It shall reject stale epochs,
foreign bindings and replacement of an open realm before policy processing.
Reusing a renderer requires its separately qualified original-context lifecycle;
CPU/C/JSC traces do not qualify actual GTK/WebKit close/reopen or physical reveal.
