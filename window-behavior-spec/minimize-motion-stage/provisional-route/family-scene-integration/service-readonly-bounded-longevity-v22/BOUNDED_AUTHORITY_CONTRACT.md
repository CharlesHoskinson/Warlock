# V22 bounded current-owner read authority (design only)

V21 source-ready f36282537be5978b479bc9ace61101e58fd1050a70e8ea15e5af064bed30ec6b
remains immutable. No V22 product runtime copy/change, deployment or native run.
This contract is sent for root review before implementation. Genuine unchanged
V21 measurements record history-dependent cost;640 does not prove long lifetime.

## Scope and authority boundary

Full authenticated segment and predecessor traversal remains mandatory before a
fresh service's first usable binding, before inherited recovery effects, and at
explicit full-history audit/normal closure. Validate every referenced body,
checksum, issuer, epoch, interval, serial coverage, old dataset, source, pointer,
directory and file identity exactly. No old schema/source migration or discovered
orphan authority. Existing native/Keeper/job uncertainty remains quarantine.

During the SAME authenticated service owner lifetime, new fixed read-only replies
come from new actual kernel connections, never historical rows. After full
validation, a sealed non-executable current-owner FD anchor captures exact owner
PID/start/lease nonce, root/lock/directory identities, session/socket/source and
executable bindings, full validated lineage tip/digest, and binding generation.
The anchor's actual FD number, inode/device, canonical memfd name, UID/mode/size,
full access/FD flags, required seals and no O_PATH/no executable mode must match
capture at every use. Sealed bytes are checked against the exact captured digest;
a different individually valid sealed FD is a replacement and refuses.

A bounded current-tip proof owns the exact FD of the latest immutable segment
and a sealed token for epoch/previous/current digest/publication. It reads the
entire latest bounded segment through that FD, verifies SHA/body/issuer/epoch and
exact named/descriptor metadata before/after. It never traverses older ancestors
on an ordinary new query. Active current rows remain bounded at512 and receive
every original fixed request, descriptor, peer, EOF, shape, lease/source,
absolute deadline and before/after durable publication check.

This is an explicit property boundary: a current-data proof does NOT assert all
historical files are currently intact. Changes to an unborrowed older segment
are refused at full-history verification, not silently asserted absent on each
fresh query. Its authenticated digest stays retained and no missing file is
reclaimed, normalized or used as current data. Root must review this boundary;
there is no implementation or weaker historical acceptance claim yet.

## Own append transition and overlapping operations

Only the exact current owner may append eligible closed/published/unreferenced
rows. It validates the currently owned predecessor tip, writes and fsyncs the
new immutable segment, confirms exact readback and source/owner/binding, then
publishes the new compact journal tip through the original durable writer.
Only after durable acknowledgment may memory rows leave and current tip FD/token
change. Pending/unpublished/held rows never leave. No historical traversal is
required to extend an already authenticated same-owner tip: every new segment
contains that exact predecessor pointer and chain digest. A process crash loses
this current-owner proof and forces full traversal before any new API/effect.

The stable owner binding never changes during own append. A live query borrows
its exact tip proof and keeps it until completion/refusal in finally. Authorized
append may advance the latest tip while that borrowed FD/token remains unchanged.
Confirmation validates the stable owner binding, the borrowed proof, current
latest proof, and exact still-current closed/published operation row. An arbitrary
replacement is not an authorized append and refuses, even if its FD/seals/body
are individually valid. Old tip FDs retire only when no live query borrows them.
At most512 live queries therefore bound retained tip FDs; newer history alone
cannot accumulate descriptor or memory working sets. Empty-tip proof has an
explicit first-generation role. No data anchor is an executable/native job.

Wrong owner/peer/source/tip/file/binding, malformed/partial/unknown state,
publication failure or missing/changed anchors latches refusal before bytes.
No later valid observation clears a failed connection/owner. Borrow release is
resource accounting, never completion or native settlement. Native atomics,
receipt/family membership, source-disposal and actor cancellation remain exact.

## Required tests and measurements

Formal valid-replacement tests must cover owner/root/source/binding FD identity,
flags/seals/no O_PATH/no execution, tip FD/material/epoch/digest, borrowed token,
partial durable publication and late confirmation. Authorized same-owner append
with a genuinely held query must remain possible without accepting arbitrary
replacement. Working work/FD bounds independent of historical length are source
properties, not physical latency guarantees. Histories must be actual kernel
connections, not synthetic row copies or disabled authority guards.

CPU tests will compare repeated-query cost across increasing real archive
lengths, including beyond512, under original per-query bounds; full startup
still validates all ancestors. Separate faults at segment creation, file/parent
fsync, readback, compact publication, FD/token adoption and release/crash must
retain full provenance. A fresh process must reject corruption of any ancestor,
never replay old data, and reconstruct a new binding only after full validation.
All V21 inherited proof/source/failure bytes and original native acceptance
oracles remain. Actor-ledger longevity/current-user cancel and actual native
baseline/restart acceptance require later independently reviewed integration.

## Model and kernel interpretation

The owner/sealed-token FD and regular archive FD are separate roles. Owner/token
FDs are O_RDWR plus CLOEXEC, NOEXEC_SEAL, mode0600 and the complete immutable seal
set (WRITE/GROW/SHRINK/SEAL/EXEC); regular segment FDs are O_RDONLY plus CLOEXEC
and the original no-follow/name/inode checks, with no memfd seals claim. Full
observed flags remain equality tokens; O_ACCMODE is separately consistent and
O_PATH refuses. NoEXEC means sealed mode without executable bits and no owned
executable alias; it does not claim Linux prevents all PROT_EXEC mappings solely
from this seal. A CPU-only design feasibility probe observed actual seal mask47,
refused write/truncate/chmod-to-execute with EPERM, and launched no native client.
Actual source must check aliases and exact descriptor metadata separately.

The two-slot model abstracts the existing512 active-row bound. It explicitly
retains durable diskTip separately from memory tip: publish-before-adopt crash
must use the exact durable tip only after full startup traversal. No new query
is admitted during publication/adoption, preserving the original reservation
serialization. The retained FD bound includes at most one new tip/token pair
being prepared in addition to latest and borrowed pairs. queryWork is a declared
bounded implementation obligation; it proves no physical deadline by itself.
