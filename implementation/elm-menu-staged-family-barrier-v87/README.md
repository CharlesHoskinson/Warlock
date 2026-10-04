V87 extends the existing MenuBridge family guard to inspect native unresolved
operations before reserving a staged selection. It checks Pending and Unknown
against the admitted native lifetime and every currently admitted member of
the canonical family. Protocol version, peer session, and frontend generation
do not release that barrier. Unrelated families and different native lifetimes
remain independent. When ownership facts are unavailable, unresolved native
operations prevent mutation admission.

The change leaves the allocator, full receipt keys, native dependency checks,
prepared timeout, and observation correlation unchanged. V69 remains held.
The old V85 failure is separately frozen: its original geometry scenario
`taskbar-origin Unknown prevents geometry namespace bypass` admitted a local
reservation and observation requests despite an unresolved native operation.

The copied V85 harness retains every original scenario name and final oracle.
Its traces add explicit post-close observations only at valid dispatch sites;
the menu and refresh observation counters account for those extra queries.
The original byte-exact traces still run and retain their old failures. The
successful equivalents cover menu 78, geometry 53, and refresh 21 scenarios.
Copied V71 traces cover 59 additional post-close cases and five compiled guard
mutants. The independent family worker invokes real typed Shell admission,
then supplies synthetic native outcomes; it does not seed or edit the ledger.

The native family check uses the current admitted ownership graph. A retired
child's former family cannot be reconstructed from the native intent alone;
historical ownership association is outside this change. No native execution,
GUI campaign, Quint logic, or complete desktop release is qualified here.
