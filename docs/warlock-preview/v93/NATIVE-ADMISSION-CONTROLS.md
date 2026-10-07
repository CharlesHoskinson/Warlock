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
