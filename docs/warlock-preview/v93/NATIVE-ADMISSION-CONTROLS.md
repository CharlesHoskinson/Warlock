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
