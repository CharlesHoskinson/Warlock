# Haskell cancellation and prequeue components

This package is under integration. It is not an installed window-system backend,
a native provider or a complete durable journal. All original requirements and
native oracles remain mandatory. See [qualification.json](qualification.json)
for source-bound evidence, failures and remaining work.

## Implemented boundaries

| Component | Current behavior |
| --- | --- |
| Cancellation owner | Canonical full owner/intent/P/original-D identity;64 active slots; cancellation fences execution before encoding/retirement; complete Unknown fallback before a synchronous trusted callback; retained execution evidence and once-only retirement uncertainty. |
| Terminal storage | One-shot owned file/directory/final-entry storage. Final entry must match the held inode; receipt checks hold the same custody gate as retirement. TerminalReceipt is a same-process observation, not DurableReceipt or native ACK permission. WCAN1 remains preliminary, not a release disk format. |
| Selection | Trusted current-view claim binds scope/generation/publication/lease/control and exact Restore intent. Actual CLOCK_MONOTONIC acceptance fixes D=A+2s. Spending is once-only; stale/retired views cannot revive captures. Installing a claim does not authenticate GUI input. |
| HostGuard | Owns namespace/lock descriptors, private metadata and fixed-name inode; actual exclusive nonblocking flock, generation-scoped borrowed namespace, original async retention/unlock and once-only close. Writer ownership is distinct from lifetime host-owner eligibility. |
| LifetimeOwner | Host-side `host-owner.lock` stays exclusively held between writer critical sections. Namespace/held-file/fixed-name metadata joins and owning-thread custody are rechecked before publication/queue claim; cleanup claims close once and retains uncertainty. Adapter `writer.lock` remains separate. |
| SlotStore | Relative bounded read/scan/exact-old atomic publication and exact removal. Full writes/readback, file fsync, rename, directory fsync and final-entry checks;64 files/oneMiB, retained FD/DIR custody and uncertain close without numeric retry. Child directories are acquired into a preallocated owner before fallible validation. |
| PairStore | Allocates both stores privately and holds its actor gate plus HostGuard across full inventories, exact selection spend and Reserved → Pending → Submitted durable writes. Current view/D and successful unlock precede queue insertion; claim checks currentness again and consumes queued work once. Failures after spend retain phase and quarantine. |
| AdmissionShape | Informational legacy Pending decoder/key validation, including schema1. The active admissions folder independently requires schema2 Pending. Decoded data never grants enqueue, native execution or ACK. |

Both child folders are siblings in the lifetime namespace: `admissions-v1` and
`cancellation-admissions-v1`. The historical C `admission.directory` denotes
that lifetime namespace; `admission.entries` denotes the Pending child.

PairStore's full inventory checks precede spending or enqueue. SlotStore's
individual raw read is informational, not a substitute for that whole-directory
check. Storage shutdown preserves disk Pending/certificates and does not certify
native cancellation, physical effect retirement or ACK.

## Qualification scope

Protected checks retain the actual wrong-staging-inode RED and its correction,
compiler failures, the schema1 informational-decoding mismatch, and an ordinary
publication-failure stage regression. The latter was reproduced before correction:
failures after Reserved or Pending now preserve that confirmed stage while
quarantining the store and refusing enqueue. Current
bounded component results include:

- Owner/terminal storage controls, actual kernel lock contention and cleanup.
- SlotStore filesystem,64-file/oneMiB and uncertain-close/reused-FD controls.
- Child-acquisition faults and original SlotStore/selection regressions.
- Thirteen independently invoked PairStore modes, including stale view, expiry,
  foreign input, corrupt inventory and interrupted publication.
- Actual persisted pair/Reserved bytes checked by unchanged original validators.
- Nineteen legacy Pending validity/key cases, including snap/transfer and signed
  zero, checked against the unchanged original development oracle.
- Eight seeded12-step production-route traces with independent filesystem/queue
  counts. Observed27 positive,7 duplicate,19 invalid-control,23 stale and20 empty
  operations. These96 actions are bounded coverage, not exhaustive proof.
- Direct independent lifetime-owner controls for actual writer-independent contention,
  lock replacement, invalid metadata, owning-thread/reentrant refusal, interrupted
  acquisition and descriptor-number reuse after close uncertainty. Two pre-close
  failure cases deliberately retain uncertain descriptors until fixture process
  exit; their exit is not normal resource-retirement proof.
- A separate strict ordinary library build with development hooks disabled.

The manual `slotstore-test-hooks` flag defaults to False. Protected developer
fixtures explicitly enable it and link the same library unit; ordinary builds
keep the implementation modules and test constructors private. The Python
legacy oracle is development tooling, never a production dependency.

## Still required

Actual authenticated host/view integration and current namespace migration/marker/
predecessor eligibility are not established by
PairPhase.Available, a writer lock or returned queued-work data. They must be
joined before real dispatch. Lifetime host ownership is now integrated into
PairStore startup before the writer lock and checked again on publication/claim;
its bounded controls do not establish those separate eligibility conditions. The native event-thread/non-yielding provider must
freshly validate original D at the first mutation; Haskell ThreadId alone does
not prove compositor OS-thread ownership.

Spent selection entries currently accumulate up to16. Genuine handoff/retirement,
continuous64-active admission behavior, full legacy temporary/cache compatibility,
versioned journal generations and restart recovery remain unfinished. The native
owner has no genuine DurableReceipt issuer: real terminal retention, exact host
admission unlink/directory sync, durable AdmissionRetired/AckPending, native ACK
and persistent history must still be connected. No test manufactures that grant.

Provider/retire doubles, syscall-boundary hooks and abstract Quint models do not
prove native window mutation, compensation, physical closure, all syscall error
orders, hardware power loss, live Elm delivery or original/release acceptance.
