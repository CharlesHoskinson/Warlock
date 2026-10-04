# Durable Unknown reservation release

This isolated implementation separates immutable historical `Unknown` outcomes
from live target reservations. It does not submit native effects. The daemon,
Elm policy integration and combined native acceptance are still open.

The unchanged GUI521 C host admission producer and its header are copied exactly.
The Python grant endpoint is copied exactly from frozen599. The remaining adapter
modules are copied from521; the daemon still imports the original V5 store.
`retirement_ledger.py` is the corrected608 implementation, not production activation.

## Required behavior

* When a matching stored Unknown record has an authenticated Retired grant proof
  and two current accepted reads requested after that proof, the ledger shall
  persist the complete historical record, proof and independent read contexts
  before removing its exact durable host admission.
* When admission absence has been synchronized, the ledger shall persist the
  Released phase and removal of only that live key before returning a release.
* If any storage operation fails, the ledger shall refuse subsequent operations
  until explicit close and correction; it shall not acknowledge a release.
* When reopening a Prepared release, the ledger shall reestablish journal-directory persistence before finishing exact admission
  retirement and both directory barriers before exposing the released target.
* When an exact released key is written again by the C host, synchronization shall
  remove it under the same host writer lock without resurrecting a live entry.
* If a different late admission from a retired scope appears, the ledger shall
  retain it as Unknown or fail closed on a target conflict. It shall not submit it
  or discard its history. Further reconciliation is required for that new key.
* When a target becomes unreserved, a new effect shall still require a fresh
  explicit C admission, a valid unretired binding and increasing allocations.
* The ledger shall preserve historical Unknown, all allocation watermarks and
  the immutable V5 predecessor; it shall not infer Committed or Refused from
  grant retirement, refreshed state or transport acceptance.

## Storage and trust boundary

`ledger-v6.json` retains the V5 fields, adds `v5SHA256`, bounded definitive `settlementHistory` and bounded `releases`
(each maximum64). Each release has a SHA256 identity over its record, nine-field native
proof and action/geometry observation, excluding the changing phase. Prepared
retains the exact Unknown in live entries; Released retains it only in history.
If latest points at that historical Unknown it is preserved exactly. V5 bytes,
older migration ancestry and source hashes must remain unchanged. Mixed older
producers fail closed.

Both storage writers share `host-writer.lock`; the broker also holds the existing
Journal writer lock. UID ownership,0600 regular single-link files,0700 nonsymlink
directories, bounded reads and duplicate JSON key rejection are inherited.
The write order is prepared-file fsync, rename, journal-directory fsync, exact
admission unlink, admission-directory fsync, final-file fsync, rename and
journal-directory fsync. A missing admission still requires the absence barrier.
Historical capacity exhaustion refuses work rather than deleting history.

`ObservationJoin` requires a599 RetirementProof and explicit post-construction
request IDs for each read domain. It rejects unsolicited, duplicate, mismatched
and foreign-binding reads. Output generations must agree. Read IDs, native
proof sequence and the two revisions are separate counters and may differ.
These Python DTOs are constructable by trusted code; structural validation is
not evidence of native authentication. The coordinator must receive the proof
through599 and accept fresh read replies through the owning authenticated native
endpoint, deliver the accepted replies to Elm, and then emit a release that601
can independently correlate. That coordinator is not implemented here.

## Verification limits

`qa/test.py` compiles and invokes the real unchanged C admission CLI and tests the
actual Python filesystem writes. It checks operation ordering, process exit at
each of nine boundaries (including the recovery root barrier), injected storage failures, poison/refusal, restart,
matching latest, protocol2, idempotence, fresh explicit next admission, late exact
readmission, proof/read controls and unsafe files/predecessors.

Process interruption tests retain currently visible filesystem state. They do
not simulate power loss or prove device fsync implementation. No compositor is
launched, no native grant is authenticated by this CPU test, no frontend is
wired, and no full recovery or UI/UX gate is accepted from these results.

## Reviewed corrections and additional controls

600 passed119 checks but independent review found historical/settled consistency,
marker type and migration-control gaps.603 passed158 after fixing those and
cleanup poisoning;604 passed228 with recovery-root persistence before unlink and
pre-call storage failures.606 passed234 with immutable same-record idempotence
and capacity-before-new-effect guards.608 passed248 with definitive-admission
absence fsync poisoning. Earlier sources and their reports remain preserved.

The unchanged V5 bytes can contain Pending, Unknown or definitive entries.608
durably normalizes recovered live Pending to Unknown under both locks while
preserving keys/counters and latest. Every migrated unresolved key needs a live,
released or exact definitive disposition; original definitive records and
watermarks cannot disappear. New saves retain previously archived histories and
never regress Released to Prepared. Definitive history stays after admission
cleanup and latest advances. Cross-set Unknown/definitive conflicts are refused.

A fresh valid proof/read join for an already released exact Unknown returns the
immutable FIRST historical release; consumers must classify that as historical
disposition and must never relabel its binding/read IDs for a fresh601 frame.
Recovery restores only live reservations, so archived releases do not create a
new unresolved operation on a clean frontend. Automatic handling of late
definitive C re-admission after its settlement was pruned is not accepted; it
fails closed against the retained definitive history. Different late old-scope
admissions still need their own bounded reconciliation.

The nine current interruption boundaries cover root recovery fsync, prepared
file fsync/rename/root fsync, unlink/admission-dir fsync and final file fsync/
rename/root fsync. Both after-call and before-call injected errors are checked;
restart ordering verifies root persistence before retiring or exposing history.
Temporary-cleanup failures and inherited definitive-absence fsync failures
poison snapshot/begin/release until explicit close/reopen.
