# CPU legacy fixture initial execution readiness

The exact frozen V19 guard refused one of64 CPU ungated launches with an empty
kernel environ/cmdline, same PID/start, stateD and incomplete mm fields. Original
guard and disposal source remain unchanged; that refusal is safe. Legacy producer
gate is written only AFTER process_factory returns, full verify_process succeeds
and durable owner callback returns. A CPU fixture-only factory can observe complete
initial execution before returning; it cannot release that gate or execute producer.

Legacy source has no positive readiness wait. Bound this fresh fixture observation
by ONE absolute2s deadline, below its existing3s renderer waits and using the
original2s failed-launch cleanup bound as a ceiling. Do not reset on partial reads.
No product timeout or lifecycle/native effect code changes. Keep original terminal
fixture assertions and ordinary modern owned-launch readiness unchanged.

Require current exact child PID/start/UID/live state; canonical launcher executable
full material, exact initial argv, selected initial environment and exact inherited
sealed handoff/producer descriptors. Observe the actual kernel data before and after
full verification. Empty initial environ or cmdline is pending observation only,
never authority. Every nonempty mismatch, malformed record, unknown/error, changed
lifetime/source/FD/executable or expired deadline refuses. A fresh complete witness
is required before returning; the unchanged gated_process verification must then
independently prove the entire ownership record and record it before release.

Failure is latched for that fixture setup. No caught mismatch may become ready on
a later matching observation. On failure, close/terminate/reap only the exact direct
Popen child created here; the original gate remains unreleased. Historical empty
kernel data cannot be reused as a successful observation. Formal proof precedes
fixture helper and inherited fixture changes. Native old-owner guards remain exact.

## Kernel gate phase before the selected initial witness

The first readiness fixture safely refused a nonempty environment mismatch during
startup. Do not treat preexec process data as selected initial interpreter data.
First require an actual current kernel syscall record for read syscall0, exact
inherited gateFD and bytecount1, matching sealed HANDOFF's sole gate read. Source
is this x86_64 CPU fixture. `running` or another well-formed startup syscall is
pending initial execution only; it cannot prove readiness or acquire authority.
Malformed/unknown/inaccessible kernel records or changed lifetime refuse. Only
AFTER this gate-phase witness sample the full exact selected environment, argv,
canonical launcher/source/FD/UID/lifetime. All nonempty mismatches at that phase
remain terminal. Observe exact gate-read phase again after the complete witness.
No producer gate release is performed by this helper. Preserve both earlier
fixture models/proofs and actual failures before refining this new phase.
