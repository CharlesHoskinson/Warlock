# Optional cancellation store: evidence and limits

The new RecoveryStore(cancellation=True) uses a V7 envelope over frozen V6 and
retains the existing delivery sidecar. The daemon still selects the legacy store.
There is no C/Elm lifecycle routing or consumer for host-cancellation-recovery.
Original ARC007/008/012/013 and release acceptance are not established here.

The final repository-owned protected runner exercises seven case groups against
actual current Python store code, private temporary files and strict native
response doubles. Recorded results: 36 base checks, 9 typed restart checks,
23 positive provenance/corruption checks, 99 checks across nine syscall faults,
239 capacity checks across 26 strict terminal reason/status pairs and exact funded
byte boundaries. Two additional groups compare ordinary legacy restart and
refuse the two missing-attempt provenance cases; their exact observations are
retained rather than folded into a fabricated aggregate count.

Actual errors tested: zero-progress writes, file fsync, close, replace, envelope
directory fsync, exact admission unlink, admissions-directory fsync, final
retirement save and ACK-permission save. Failures poison the open instance;
explicit reopen retains unresolved custody or reestablishes certificate barriers
and repairs exact retirement, with no native ACK/replay. Capacity tests exercise
maximum native counter widths, every finite strict terminal pair, exact funded
admission, one-byte-under refusal and an unrelated legacy write unable to spend
reserved terminal credit. All 64 retained slots, arbitrary compaction, actual
hardware ENOSPC and hostile same-UID mutation are not qualified.

Preserved RED controls: V4 reopened ordinary legacy Pending as Pending while the
old V6 reopened Unknown. The fix normalizes only V7 legacy custody and preserves
typed Pending keys/evidence. Private V5 accepted correlated Prepared/Committed
response doubles without durable attempt markers; the corrected live and disk
validators require prepare for native evidence and commit for Committed.
Native-certified Cancelled after prepare remains valid without a local Cancel
marker. These are conditional store-boundary defects, not observed daemon/native
window mutations. Exact rejected inputs are reconstructible from retained diffs
and current source hashes; complete original private packets remain local.

The unchanged reduced model 4990608d/tests 8fd71aaf actually passes 24 explicitly
selected named tests, two typechecks/init and nine sampled invariants, each
1000 traces/max 30 steps/seed 20261030. It models two targets and split persistence
barriers, not actual JSON/list/hash/locking/64capacity/native transport or
physical Escape. No exhaustive implementation, power-loss or whole-system proof.

Current store SHA 31316524 and helper SHA ad23d4e7 differ from independently
reviewed d42f464e/1e5ca372 only in module docstrings; AST equality excluding those
headers is checked. Final protected public source execution is retained in store/.
The source/protocol reviews retain their scope, including missing real consumers.
Prior qualification stops are preserved: actual integrated source progress
followed independent DEL015 completion, not an administrative timer reset.

Diataxis: new store QA how-to, updated protocol/status reference and ownership
explanation; source-navigation tutorial remains unaffected because its read-only
learning exercise and contribution commands do not change. Links and actual
commands are checked separately. No main-session deployment or compositor restart.
