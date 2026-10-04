# v624 handoff

Accepted protected CPU report:
`qa/tests-1791151811583372012/report.json`. It exercises the final delivery helper
and QA controls. The unchanged v608 driver is rerun inside the protected scope
and its separate report is referenced from that accepted report.

Earlier development runs are retained as superseded evidence. The initial run
precedes the populated-marker absence guard and the last controls. The middle run
overlapped addition of that guard and is not used to certify the final source;
only the final run and its source hashes are selected by the frozen manifest.

Use `DeliveryLedger.attest(join)` only with an authenticated599 typed Retired
proof and frontend-accepted post-proof reads. Return its fresh certificate in a
new delivery protocol; keep its `anchorId` tied to the original release archive.
Do not send the original archived proof with fresh current identities or read IDs.

All copied v608 adapter/native files and `qa/inherited608.py` remain byte exact.
No existing store, native GUI, installed configuration, frontend or git state is
modified. The sidecar is a latest-per-record cache, not a replacement for immutable
effect history. Scalable archival and the practical v608 64-outcome lifetime limit
remain a later S15 obligation.

Intentional unsafe symlink fixtures are recorded separately in the inventory;
the freezer does not follow them as source files. Private synthetic test stores,
their C-produced admissions, interrupted writes and accepted reports are held as
evidence. Native authentication, true power-loss and complete GUI acceptance
remain unproven.
