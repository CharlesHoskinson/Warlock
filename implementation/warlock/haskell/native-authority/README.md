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

Receipt validation now holds the same nonblocking storage custody lease used by
retirement and persistence through its handle and owner checks. Concurrent close
cannot invalidate the handles between those checks. Nested validation returns
Busy; an asynchronous exception releases the gate. The observation is valid at
that check, not a transferable native ACK capability.

The private selection component now binds the exact Restore intent to the current
trusted view claim. It samples header-derived CLOCK_MONOTONIC and fixes D=A+2s;
spending cannot renew the deadline or revive a retired/replaced view's token.
Strict controls exercise real entropy/clock expiry, one-use spending, full-intent
mismatch and view ABA rejection. Fifteen actual encoded producer cases match the
unchanged legacy companion validator, storage-key hash and canonical JSON,
including Unicode. The legacy oracle runs only as development QA.

Installing a trusted view claim is not actual authenticated GUI input. The
selection registry still retains spent slots up to16; a genuine admission
handoff/retirement lifecycle is required before normal repeated operation and
original64 active-admission behavior can be claimed. PairBytes is encoding only,
not durable Reserved/Pending/Submitted publication or native ACK authority.

The private HostGuard now retains its namespace and actual fixed-name lock file,
verifies private metadata/name-to-inode identity and acquires flock exclusively.
A generation-scoped borrowed namespace is usable only in the owning thread while
the guard is held. Kernel-contention, nested/retirement Busy, original async
propagation/unlock, failed-operation quarantine, lock-name substitution and normal
once-only retirement controls pass. The guard protects storage coordination; it
is not native execution authority or the completed PairStore transaction.
