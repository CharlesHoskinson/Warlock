# Haskell native cancellation owner — integration in progress

This component ports the existing cancellation owner to Haskell. It is not a
native provider or an accepted window-system implementation. Owner construction,
execution proof and ACK receipts remain private; no decoded wire status grants
native permission. The actual native event-thread adapter and real durable journal
issuer/post-ACK history are still missing, so no full/native/GUI acceptance follows.

The candidate retains full owner/intent/prepared-ID/deadline identity,64 slots,
cancel fencing, a complete Unknown fallback before a trusted synchronous callback,
terminal proof across encoding failure, and once-only generation-specific retirement
with uncertainty retained. Model and callback fixtures do not prove physical closure.

Root corrected the reviewed duplicate-publication path: query already publishes
and clears terminal proof, so commit must not publish a second time and return Busy.
Readonly key/ID views enable real formatter integration without exposing constructors.
The finite provider result is forced inside exception ownership; async faults retain
Unknown and propagate. The strict library build and actual source-control fixture passed under the protected launcher (see qualification.json). Provider callbacks are test doubles; this does not prove a native window mutation or physical closure.

See qualification.json for current evidence. The original native-cancellation.qnt
and all24 named tests remain unchanged, with their original resource/native premises.

The enhanced component run also passes controls for lazy provider-proof exceptions,
retained compensation evidence after reply publication, and original-deadline
carriage in the opaque permit. Native code must still check that deadline freshly
at the first mutation. Public snapshot accessors cannot forge a snapshot through
record updates. These are component guarantees, not native-provider acceptance.

The preliminary terminal storage path now passes real owned-directory component
controls. A reproduced staging-name substitution defect was fixed by retaining
and checking the final entry against the original inode; independent entry, file
and directory close ownership is retained. Fault controls cover actual syscall
boundaries, metadata rejection and synchronous/asynchronous exceptions.

`TerminalReceipt` observes only this process's owner and one-shot storage; it is
not `DurableReceipt` or native ACK authority. The WCAN1 representation is preliminary,
not a release disk format. Generation rotation, stable decoding/recovery, real host
admission retirement/AckPending and persistent history remain mandatory unfinished
work. The in-memory history overlay cannot yet exercise ACK because no genuine
DurableReceipt issuer exists. No test manufactures that authority.
