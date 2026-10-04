# V665 admission authority refinement, before source implementation

Prototype API `commitAdmission(exactPendingJsonBytes)` and
`readAuthority(fullBinding)` uses the V630 schema2 full-record shape. Constructor
receives a positive canonical native lifetime from an assumed authenticated caller.
This prototype does not authenticate transport, call C or issue an effect.

EARS:

- AA-001: When committing a validated Pending admission, the store shall publish
  the exact full-origin event, live reservation, independently increasing request
  and generation maxima and per-origin completion quota reservation in one root.
- AA-002: If either positive canonical UInt64 replay domain is stale, malformed or
  exhausted, or an origin/target conflicts, the store shall refuse before write;
  publication generation/count shall never authorize replay.
- AA-003: When allocating an admission, the store shall durably charge actual
  publication plus worst-case three bounded completion publications before pages,
  and shall expose completion reservation only through the committed authority root.
- AA-004: While cold-open validation and fresh archive-directory fsync are
  incomplete, no positive authority lookup or admission success shall be exposed.
- AA-005: If a publication fails, the handle shall poison and recovery shall expose
  either the complete previous authority root or the complete published authority
  root, never an Admission without matching maxima and reservation.
- AA-006: The prototype shall conserve immutable full Admission bytes and reject
  malformed, foreign, incomplete and hash-invalid authority roots; it shall retain
  live≤64, scopes≤64, authority page≤16KiB and primitive cache≤64 bounds.

OpenSpec required scenarios: separate stale request and stale generation;
noncanonical/overflow/Boolean counters; changed full origin and same target
conflicts; duplicate never yields fresh admission; completion quota insufficient
before effect token; independent binding maxima; visible CURRENT rename process
exit then fresh root barrier; every before/after syscall failure conserves atomic
root; malformed authority closure/page counters/ref binding; actual short writes;
1026 terminal cycles are optional and not claimed without completion semantics.

Publication: durable conservative QUOTA charge → exact Admission and COW history
index plus typed authority page file fsync/rename → pages directory fsync → root
file fsync/rename/directory fsync → CURRENT file fsync/rename/root directory fsync.
One CURRENT selects all three facts. The authority page is not arbitrary archived
JSON; it contains validated full binding, separate maxima and references to exact
Pending events plus fixed reserved budgets. Cold-open checks current page and
all ≤64 live event references and direct predecessor authority conservation before
fresh root fsync. Historical replay indexes remain outside this bounded prototype.

Worst-case completion budget is three future publications, each conservatively
charged for one64KiB event, seventeen16KiB history-index pages, one16KiB authority
page, one16KiB root and4KiB overhead plus23 inode slots. No completion API consumes
this reservation yet. Quota is accounting, not filesystem preallocation; ENOSPC
still fails closed. Authority root never removes live admissions here.

The Quint model has one binding, two target origins and small bounded counters;
visible/durable authority tuples distinguish process crash from symbolic power
loss. It abstracts actual filesystem/name/hash/UInt64 validation. It does not prove
native authentication, paired locks, terminal semantics, retired scope or proof
sequence indexes, migration, full replay scaling, hardware power loss or S15.
