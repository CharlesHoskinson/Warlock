# Haskell cancellation component

This page describes the Haskell port in `implementation/warlock/haskell/native-authority`.
It is separate from the [historical native cancellation route](cancellation-protocol.md).
Historical native results do not qualify this port. The current source is a
component under integration, not an installed window-system backend.

| Boundary | Current contract |
| --- | --- |
| Public module | `Warlock.Native.Cancellation` exposes an opaque owner and observational operations. Owner construction, provider results, commit permits and receipt constructors remain private. |
| Identity | Canonical protocol identities retain the peer/start/binding and full intent. A prepared ID and original deadline must match exactly. Constructing identity data grants no execution permission. |
| Admission | At most 64 active owner records. Busy, expiry, formatter failure and allocator exhaustion must not consume a prepared ID. |
| Cancellation | Semantic cancellation fences execution before encoding or retirement. Late cancellation preserves an existing terminal result. |
| Commit | A complete Unknown reply is retained before a synchronous trusted provider callback. The opaque permit carries the original deadline; the real provider still needs to check it freshly at the first mutation. |
| Execution evidence | Opaque execution metadata survives terminal reply publication. Provider doubles exercise this retention; they do not establish native execution or compensation. |
| Resource retirement | A close/retirement claim is attempted once. Uncertain outcomes remain retained; retrying a numeric descriptor is not recovery. |
| `TerminalTicket` | Private owner-selected immutable terminal snapshot. A decoded wire response or caller-created snapshot cannot mint it. |
| `TerminalReceipt` | A same-process observation of the exact owner and one-shot storage object. It requires retained entry/file/directory handles. It grants no native ACK authority. |
| `DurableReceipt` | The private type has no genuine issuer yet. The ACK path therefore remains unavailable; no test-only success issuer substitutes for it. |
| History | An in-memory post-ACK history overlay exists, but its positive ACK lifecycle cannot yet be exercised. Persistent generations, recovery and a real host-retirement witness are unfinished. |
| HostGuard | Retains the private namespace and actual writer-lock file, checks name/inode identity and uses kernel flock. Lifetime host-owner and namespace eligibility are separate unfinished joins. |
| SlotStore | Bounded relative scans/reads, exact-old atomic publication and exact unlink/directory sync, with retained FD/stream uncertainty. Its per-call gate does not replace whole-transaction ownership. |
| PairStore | Privately owns both stores; full inventories precede exact selection spend and Reserved → Pending → Submitted writes. Successful unlock and fresh view/D checks precede one queue insertion/claim. Returned work is data, not native execution or ACK authority. |

The storage primitive uses a held private directory, exclusive no-follow staging,
bounded full writes and readback, file fsync, no-replace rename and directory
fsync. It retains the final entry separately and compares its inode to the
original file. Directory UID/mode and regular-file UID/mode/link-count checks
reject invalid metadata. This is a one-record operation; fixed filenames do not
provide rotating generations or restart recovery. The preliminary WCAN1 encoding
is not a stable release format.

The source controls are split into `native-cancellation-controls` and
`durable-storage-controls` in the package's Cabal file. The latter requires an
explicit owned fixture directory argument. Root serializes both through the
[protected verification workflow](../how-to/verify-selected-change.md); do not
run competing compiler, model or filesystem campaigns.

The [package qualification record](../../../implementation/warlock/haskell/native-authority/qualification.json)
retains source hashes and exact report paths, including the staging-name
substitution failure and corrected run. Existing owner controls and real
owned-filesystem fault controls pass. These results do not establish hardware
power-loss durability, hostile same-UID immutability, native physical closure,
compositor OS-thread ownership, Elm integration or original-scenario acceptance.

The unchanged `native-cancellation.qnt` models cancellation ordering and retained
replies. `cancellation-durability.qnt` separately models host durability barriers.
Their symbolic clocks, mutation and durability inputs remain assumptions until
the implementation discharges them. See [why storage is insufficient for ACK](../explanation/cancellation-durability.md).

The guarded PairStore now passes thirteen independent component modes and an
original-validator check of actual persisted pair/Reserved bytes. Nineteen
legacy Pending data cases agree with the original validity/key rules, including
schema1 informational recovery; the active admissions folder explicitly still
requires schema2 Pending. Eight seeded12-step traces check filesystem/queue
counts through publication, duplicate/invalid/stale refusals and claims. These
checks use trusted fixture inputs and establish bounded component behavior.
They do not authenticate a host event or discharge the remaining integration gates.

Both `admissions-v1` and `cancellation-admissions-v1` are children of the lifetime
namespace. Existing legacy temporary/cache handling, real host-owner/current
namespace eligibility, genuine selection retirement, native dispatch and durable
terminal/ACK/recovery remain unfinished. Spent selections still accumulate up
to16; this is not acceptance of continuous64-active admission behavior.
