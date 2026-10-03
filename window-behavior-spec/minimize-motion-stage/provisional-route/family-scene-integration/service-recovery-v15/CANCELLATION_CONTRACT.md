# Recovery V15: durable cancellation discharge

Frozen Recovery V14 and all prior failures remain immutable. Requirements permit
recovery to discharge an accepted intent without endpoint settlement when its
exact original family no longer exists or is incompatible. Cancellation is an
explicit durable outcome, not a successful minimize/restore, toggle, or waiver.

## Authority and classification

The exclusive acquired RuntimeLease must freshly verify the selected runtime
root inode, lock inode, current process PID/start, owner nonce/session and actual
flock exclusion. Cancellation is startup-only: its owner socket is still null.
The selected compositor guard and exact on-disk journal must remain current.
The original receipt, captured identity, complete old scope, symbolic direction,
and any already prepared endpoint/original anchor observations and returned
member results are preserved. Every old scope member must still be owned by this
exact receipt. A newer owner, conflicting direction or malformed provenance
quarantines; cancellation cannot claim a newer intent.

Old renderer presentation authority and old helper/keeper groups must be proven
terminal through the existing authenticated lifetime/provenance mechanism.
An unfinished native-export or native-effect is uncertain even with empty
kernel groups. It always quarantines before retirement, observation or disposal.
A durable helper-closure archive preserves exact old ownership/jobs and matching
terminal results; later read-only query keepers do not overwrite that evidence.

Two complete fresh client/context observations classify every original member:
`present`, `absent`, `reused` (same address, different stableId/PID), or `unmapped`.
They record actual current identity, geometry, workspace, pin and monitor, and
read-only exact native family/focus for each surviving mapped original member.
Output context, complete client projections and native family/focus must agree
across both observations. Malformed, unstable, unknown or failed observations
quarantine. Stable absence/reuse/unmapping, a changed previously observed whole
family, or a changed prepared restore focus permits cancellation. For pending
unobserved families normal V14 expansion stays available only when all original
members remain exact/mapped; missing old members are not silently discarded.
No catch of arbitrary ValueError grants cancellation authority.

## Durable ordering and restart

1. Authenticate current lease/session/journal and complete old keeper/job closure.
2. Retire exact renderer lifetime; durably mark actor resource `retired` with
   `oldLifetimeGone=true`, retaining source directory and its immutable identity.
3. Observe twice and explicitly prepare a cancellation with the preserved intent,
   reason, current complete observations, fresh lease and helper/resource proofs.
4. Fsync the `cancelled` non-settlement acknowledgment before source disposal.
5. Dispose only exact proven actor directories with old callback authority gone.
6. Complete and expose startup API only after every resource and query helper is
   terminal; retain cancellation in recovery history, distinct from settlement.

A persistence fault before step 4 retains sources. A fault after acknowledgment
retains unresolved state; restart proves current lease/session/helpers/resources
and repeats the guarded observations before resuming disposal. An acknowledged
cancellation remains cancellation even if its original obstruction disappears.
Neither survivors nor replacement windows receive native writes. Prior returned
native results remain recorded; an unknown native return continues quarantine.
Fresh observations are separate from the original acknowledgment, so stale
partial proofs cannot authorize source disposal or API exposure.

## Boundaries

The new formal model binds receipt, lifetime, runtime root/lock/session/owner and
observation epoch tokens. Kernel/CPU tests use real RuntimeLease/JournalStore and
keeper closure with a deterministic read-only desktop. They are not native
recovery acceptance. Original baseline, endpoint, cache, reversal, focus, raster,
main-preservation and lifecycle oracles remain required in a root-owned native
campaign. No installed or main configuration is changed.

## Cancellation ingress still open

This derivative handles definite stale/closed/incompatible-family recovery
outcomes. It does not implement explicit user cancellation of a still-compatible
current receipt, interruption or reduced-motion stop ingress. Those need their
own authenticated current-receipt API and live actor ownership protocol. No
compatible family or user request is implicitly treated as canceled here;
full parity cancellation acceptance remains open even after this derivative.
