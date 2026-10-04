# Recovery storage failure presentation

V248 adds a typed Elm RecoveryFailure variant for unavailable, full, busy,
unverified and unowned legacy recovery data. Only an exact versioned envelope and
known reason can change presentation. A failure detaches window controls, retains
any pending transaction as Unknown, and produces no native window effect. Subsequent
generic broker disconnection preserves the reason. Explicit Reconnect sends one
backend restart request; a fresh authenticated attachment clears the reason, while
a verified current snapshot retains Unknown without replaying the old action.
User-facing explanations give a correction step and remain ordinary escaped text
in Elm's existing status/live region. No paths, raw exceptions or storage bytes
enter the product presentation.

The broker classifies only guarded recovery operations. Journal open/migration,
uncertain-state read, durable begin and durable settlement failures get a bounded
reason before the existing disconnection. Native host admission failures withhold
the surface/effect batch before forwarding and show unavailable recovery data.
The host cancels its owned broker I/O and signals only that owned subprocess, so
an explicit retry can create a fresh broker once the old one has exited. It never
automatically retries or deletes a recovery record. Native admission validation
failures remain separate from write failures. The owning V89 core/plugin is
unchanged; V249 seals V248's actual ELF, compiled assets and broker in 20 files.

V248 passes the actual C/Elm build and its 20/27/30 inherited replay checks, 55
new compiled Elm failure/reconnect/malformed-envelope checks, 21 filesystem
classification checks, 22 compiled admission checks and 42 namespace/migration
checks. The filesystem tests exercise real held locks, malformed/public records
and ambiguous legacy ownership. ENOSPC, EDQUOT, EROFS, EACCES and EIO are explicitly
injected at fsync: these are CPU failure-path checks, not native disk exhaustion.
V251 executes eight named Quint cases and 1,000 samples up to 40 steps. This is an
abstract presentation/retry contract, not automatic C/Python/Elm refinement.

V250 preserves a failed native fixture oracle and successful cleanup. It compared
pre-shell application geometry with geometry after the shell's normal bar-space
reservation. V252 corrects that oracle in a fresh derivative: pre-shell identity
and minimized state are preserved; geometry is compared after the legitimate
reservation, across correction and same-host reconnect.

V252 passes 23 actual native checks for a malformed broker intent record: real Elm
bar repair text, declared broker failure exit, disabled effects, preserved corrupt
bytes, no auto retry for 500 ms, explicit real-pointer Reconnect, fresh native
binding in the same host, current-state reconciliation and a newly committed
minimize. The fixture archives its own bad record under a nonjournal filename to
simulate deliberate repair; product code never performs that archival/clearing.
V253 passes 22 actual native checks for a public host admission record: refusal
before forwarding Restore, unchanged durable previous record and minimized window,
declared owned-broker signal exit, access explanation, no auto retry on permission
correction, same-host explicit Reconnect and a newly committed Restore. Screenshots,
pointer exits, owner identities, zero residual cohorts and normal shell/session
teardown are retained for both accepted cases. Installed desktop and drafts are
unchanged.

These two native cases do not qualify every storage stage or failure class. Busy,
full and legacy-owner messages have compiled Elm/CPU evidence only. Admission
failures show a conservative unavailable reason; finer errno presentation remains
open. Initial attachment/host-lock failure, live settlement failure after a real
native commit, disk-full/readonly-device cases, stale interaction preservation of
failure text, legacy provisioning and accessibility/human acceptance require further
qualification. The original four interrupted plus normally settled recovery matrix
V247 is retained on V238, not newly qualified on changed V248. Rerun that matrix
and full coherent native regressions after the next source fixes. No whole
requirement, work package or release is completed.

Next: retain the failure explanation under stale scoped user interactions; qualify
busy/legacy and host-binding/settlement failure with actual native correction,
then rerun recovery and original integration campaigns. Global old-live-broker
revocation, original restore timing, updated geometry/menu/GPU/native91/137,
AT/IME, hotplug/zero output, physical-device/human UX, budgets/soak, C00 and release
remain open.
