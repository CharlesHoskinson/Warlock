# Durable Unknown reservation release

This isolated implementation separates immutable historical `Unknown` outcomes
from live target reservations. It does not submit native effects. The daemon,
Elm policy integration and combined native acceptance are still open.

The unchanged GUI521 C host admission producer and its header are copied exactly.
The Python grant endpoint is copied exactly from frozen599. The remaining adapter
modules are copied from521; the daemon still imports the original V5 store.
`retirement_ledger.py` is the new implementation, not production activation.

## Required behavior

* When a matching stored Unknown record has an authenticated Retired grant proof
  and two current accepted reads requested after that proof, the ledger shall
  persist the complete historical record, proof and independent read contexts
  before removing its exact durable host admission.
* When admission absence has been synchronized, the ledger shall persist the
  Released phase and removal of only that live key before returning a release.
* If any storage operation fails, the ledger shall refuse subsequent operations
  until explicit close and correction; it shall not acknowledge a release.
* When reopening a Prepared release, the ledger shall finish exact admission
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

`ledger-v6.json` retains the V5 fields, adds `v5SHA256` and bounded `releases`
(maximum64). Each release has a SHA256 identity over its record, nine-field native
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
each of eight barriers, injected storage failures, poison/refusal, restart,
matching latest, protocol2, idempotence, fresh explicit next admission, late exact
readmission, proof/read controls and unsafe files/predecessors.

Process interruption tests retain currently visible filesystem state. They do
not simulate power loss or prove device fsync implementation. No compositor is
launched, no native grant is authenticated by this CPU test, no frontend is
wired, and no full recovery or UI/UX gate is accepted from these results.
