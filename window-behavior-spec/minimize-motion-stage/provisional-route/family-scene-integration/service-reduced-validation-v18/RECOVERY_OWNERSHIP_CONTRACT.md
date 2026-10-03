# Recovery ownership and write-ahead handoff

A recovery-capable native actor launch has three durable states: reserved actor
name, acquired exact directory, and gated renderer PID/start/material. The gate
opens only after the gated record is durable. Before that byte the child cannot
execute the renderer, create a Wayland surface, or deliver renderer callbacks.
An accepted receipt cannot be returned before the complete intent ledger and
all acquired resource ownership are durable. Actors without scenes and actors
retiring outside the manager list remain in the resource registry.

A restart holds the exclusive runtime lease. It validates the selected session,
full schema, accepted anchors/events/receipts, and all actor records before any
native endpoint. A live recorded PID is opened with pidfd, then its positive
start time, UID, actual executable device/inode, executable bytes/seals, exact
selected environment and (while gated) launch command plus renderer descriptor
material are checked. Signaling uses only that pidfd. A reused PID is already a
closed old lifetime and is never signaled. An unrelated process occupying the
same executable path is never discovered or selected. A live same-start PID
with changed material refuses recovery.

The launcher is a selected Python executable running a sealed, hashed handoff
script. The gated record includes that executable identity, exact argv and
sealed script/renderer FD identities. After the gate opens, exec preserves the
PID/start; executable material must be the exact sealed renderer. The child
always closes the gate before exec and does not inherit the runtime lock. Gate
EOF exits without renderer execution. A crash after durable gate recording may
be recovered in either the gated or executed phase.

Directory removal is allowed only after the exact renderer lifetime is gone,
and through the recorded private nonsymlink parent and directory device/inode.
All entries must be regular private UID-owned actor capture files; every file
identity is rechecked before unlink. Shared cache files are never actor cleanup
inputs. A replaced directory, unexpected file, live renderer, or incomplete
allocation record quarantines recovery and preserves the durable journal.
A crash between mkdir and its durable identity publication cannot authorize
removing the unrecorded directory: this narrow allocation gap refuses safely.
An absent reserved directory can close without deletion.

After old resources close, recovery preparation durably freezes the symbolic
endpoint for each exact latest family. Constant intent is never reinterpreted
from partially changed visibility. Before each guarded core operation, the
selected compositor proof, complete current native family, current geometry,
workspace/output fingerprint and latest receipt scope are re-observed. No old
source, callback, output generation or preview flag grants authority. Restore
orders ancestors before descendants and exact focus last. Idempotent repetition
following a recovery crash uses the durable prepared endpoint. Every result is
durable before another member. Cancellation is explicit and is not settlement.
The original intent/resource journal is replaced only after durable complete
outcomes; API bind/listen and new actor launch occur afterwards.

These source changes and offline tests do not prove native restart acceptance.
A fresh owned campaign must exercise gated launch, live renderer orphan,
partial family commit, unresolved anchored intent, changed outputs/family,
replacement resource refusal, and recovery interrupted by another restart.

## Runtime lease freshness

Before each durable reservation and recovery native phase, verify the acquired
runtime root device/inode, exact private nonsymlink lock inode, retained lock FD,
actual live owner PID/start/nonce/session and kernel lock exclusion. A copied
journal in a replacement directory or replacement lock file does not preserve
ledger authority. Explicit release/owner change revokes it. Recovery receives
this verification from the actual held RuntimeLease; a standalone pure plan or
constructor without that binding cannot authorize native cleanup/settlement.
