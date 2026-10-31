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
