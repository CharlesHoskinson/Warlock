# Service V14 recovery candidate

Fresh derivative of frozen Service V13. No installed file was changed. Toolkit
V5/V21, Service V12/V13, renderer V10 and all retained native failures/acceptance
remain immutable. This packet is source/offline ready; native restart and full
Windows parity are unaccepted.

## Product changes

- Every durable reservation and restart phase rechecks acquired runtime root/lock
  inodes, retained FD exclusion and exact owner PID/start/nonce/session.
- Actual manager snapshots include full accepted direction, exact pending actor,
  actor directory/renderer ownership, and helper keeper/job ownership.
- Every selected renderer/helper waits in a private confined group behind a gate.
  Sealed source and kernel lifetime descriptors are journaled before release.
- Keeper authenticates actual kernel sender PID/UID and retains exact group
  pidfds after leaders exit. Service death closes those groups before a durable
  root/nonce/lifetime-bound terminal proof can authorize cleanup.
- Restart rejects incomplete/legacy provenance before resource mutation. It
  proves old helper closure, closes exact actor resources, then prepares a
  durable constant endpoint from the original accepted symbolic direction.
- Each native member write rechecks selected session, complete fresh family,
  current geometry/workspace/output and exact latest receipt. Returned results
  and final observed endpoints are durable before API listening.
- Native export/effect failure or timeout stays uncertain. Missing closure,
  unexpected files, replaced directories, changed/closed families and unfinished
  native calls quarantine. Explicit cancellation discharge remains unimplemented.

## Headless evidence

Tests exercise actual SCM credentials, sealed descriptors, inherited seccomp,
retained group signaling after leader reaping, keeper EOF cleanup, source
replacement, actual GNU timeout expiry, original timeout counterexample, real
NativeFactory gates/receipt journal/normal CPU retirement, and real JournalStore
restart after partial member effects. CPU fixtures have no Wayland/GL/native API.

The Bash adapter preserves original `$0` and literal argv; source introspection
using BASH_SOURCE refuses. The Python adapter preserves original source path,
argv and import directory. The inherited timeout function uses foreground mode
and preserves deadline/kill-after/arguments; surviving descendants still refuse
normal helper completion. No native replies, sources or pixels are fabricated.

## Required root review and native campaign

A fresh collector must register the actual gated keeper and exact isolated job
lifetimes from durable ownership, not assume every descendant inherits the
harness PGID. It must bind real service/default renderer/native helper sources,
all transitive bytes/modes/links, normal baseline and original strict reversal
oracles. Then exercise crashes while gated, presenting, after native returned
member results, and during another recovery. Unfinished native callback jobs
must demonstrate quarantine; they cannot count as settled recovery.

Accepted V13 responsiveness is inherited, but new gate/journal overhead has no
native latency acceptance. No C1 trajectory, physical cadence, native restart,
real frontend preview or deployment acceptance is added here.
