# Root model review and implementation correspondence

Reviewed frozen v2 source 677962afa6ff53346c4b033efcb7f89a9b8c3bfd98d1ad300715901ba859ddb2
and tests 582737d73c186e4b6a6a5b2346bb90beec02817262e878a84e9252f36d8ca575.
The rejected-v1-source folder retains the unexecuted fixture-composition error:
init -> existingUnsafe -> currentSchema combined two setups and violated the
overstrong twoLinkRecoverable claim. No v1 test result is fabricated. V2 separates
fixture choice, explicitly permits current-schema storage with an unrelated
unsafe backup, and limits two-link preservation to actual migration publication.
Original backup-before-activation property is unchanged.

Structural review: sum-type phases/outcomes, one grouped State, guarded transitions
and whole-State assignments avoid unassigned fields. Actions distinguish byte
identity, backup publication/file+directory sync, active publication and outcome.
originalBeforeActivation and savedAfterBarrier are substantive protocol claims.
Named positive witnesses reach every major route including successful upgrade,
existing backup, observational reads, current-schema save, failures and restarts.
Negative tests terminate at fail(); intentionally brokenActivate is excluded from
normal step and demonstrates the old backup-free activation defect.

Runtime: protected scope 59fdc3600e634ba0ba35e278246b6c9e,
invocation 858c955477144764bc8a421baf357700 exited 0. Both typechecks and one-step
initialization passed; all 29 named tests were positively selected separately
(each actual stdout says passed 1 test); five invariants each sampled 1000 traces
with max 30 steps and seed 20261030, no counterexample observed. Source/tool pins
were rechecked after execution. Full command/raw-output hashes are in model/report.json.

Correspondence: production Store 702f110e captures raw validated schema1 bytes;
CAS/no-op/proposal validation precede _preserve_legacy. New backup file sync,
exclusive hardlink publication, temporary unlink and directory sync precede
active file staging/sync/rename/directory sync. Existing exact private backup
requires file and directory sync. Actual hardlink interruption leaves old active
and original recoverable but refuses retry. Postrename syncerror is Unknown,
not false rollback. Actual process cuts corroborate visible-file/reopen behavior.

Limits: one cooperative locked writer, opaque byte classes and assumed POSIX
atomicity/sync behavior; no JSON enumeration, arbitrary edits/concurrency, hardware
power-loss or native/UI/release proof. Model source comments retain their original
proposal status; this report qualifies exact hashes, not a rewritten source claim.
The repeated rejection/read transitions are request observations; terminal traces
can end before maxsteps. Named route witnesses complement sampled safety and
prevent absence of successful reachability being mistaken for a safety result.
