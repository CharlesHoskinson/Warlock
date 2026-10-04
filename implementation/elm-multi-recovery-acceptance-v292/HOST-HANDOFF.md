# Next production boundary: shared host admissions and ledger settlement

The current V268 shared host holds host-writer.lock continuously and replaces the
flat host-intent.json for each action. V291's ledger acquires that lock during
bootstrap and hash-binds legacy producer files. A running old host prevents
bootstrap; a later singleton write invalidates the ledger. This explicit refusal
must remain until the new handoff prevents lost unread admissions.

Implement in a fresh derivative of the accepted shared-output/recovery host,
retaining one authoritative Elm model/backend and scoped presentation views.
Use the new recovery store and geometry/context carrier through a reviewed merge;
do not replace the shared host with the singleton menu host. Keep the newer owning
core's Window behavior and qualify the parent hit-test changes on its actual ABI.

The handoff must preserve these behaviors:

1. Host admission persists every accepted full-key intent before forwarding or
   publishing Pending. Up to64 unresolved admissions survive a broker dying before
   reading input. Duplicate and65th admission cannot overwrite another record or
   authorize submission. Use an explicit new per-key/collection representation,
   canonical full keys and private/no-follow atomic storage.
2. Separate whole-host ownership from short storage critical sections. Only one
   host owns the instance/lifetime; broker bootstrap can take a bounded shared
   storage lock while the host is reconciling. Old persistent-lock producers refuse
   safely until explicitly retired. Do not weaken old-live-broker revocation gates.
3. Import host-unread admissions into informational Unknown during broker startup.
   A fresh explicitly dispatched intent remains distinguishable from a recovered
   duplicate. Journal every submission exactly once before native mutation.
4. Preserve exact definitive settlement while its corresponding admission remains.
   A lost host receipt must not resurrect a committed admission after unrelated
   later actions replace latest. Retain bounded correlated settlement tombstones
   or another reviewed proof of safe admission retirement. Removing an admission
   must be durable, and terminal duplicate receipts must be inert.
5. Use strictly validated broker settlement information to retire only the matching
   host key. Uncertainty, unrelated receipts and observed snapshots cannot retire
   an admission. Recovery/retirement metadata is informational, never a retry command.
6. Keep typed storage failure feedback, explicit reconnect, resource-retirement fixes,
   bounded stdio, source authentication, per-operation guards and ordered owned
   process cleanup. Preserve original deadlines and application drafts.
7. Validate real C/ledger cross-language key encoding, locks, write interruption,
   capacity and cold restart; compiled shared-controller storage/geometry/menu
   journeys; selected Quint models; then serialized native failures before read,
   after mutation and during settlement on one frozen source/ABI tuple.

The geometry lane's native popup destruction changed the authoritative legacy
revision and refused a menu Minimize. Integrate its reviewed staged-selection
refresh/revalidation fix rather than extending the native deadline or weakening
scope correlation. Old failure packets and original scenario identities remain.

This is an implementation boundary and acceptance checklist, not an accepted
native protocol or closed architecture gate. Finish the actual host/broker/Elm
roundtrip and fault matrix before marking production adoption complete.
