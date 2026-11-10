# Owned Wayland endpoint admission component

The new Haskell owner uses an explicitly selected compositor endpoint.
It validates held ancestor directories, socket metadata, process birth, peer credentials and executable identity.
One bound OS thread owns its connection, private queue and callback state.
Reads inherit the supplied deadline. The owner exposes observation data, not native window actions.

Source review found two retirement defects before adoption.
Libwayland can create a new proxy before its callback reaches the tracked map.
Retirement now requires a private empty-queue proof and no sticky connected fault before destruction.
A public read marks a connected fault before rethrowing, even when its caller catches the exception.
Unproven retirement returns retained ownership. It does not free uncertain callback resources.

| Protected observation | API baseline | Runtime R3 | Runtime R4 | Qualified R5 |
| --- | --- | --- | --- | --- |
| Compiler | Missing public source | Redundant import under strict warnings | Both targets linked | Both targets linked |
| Old allocation mode | Not run | Not run | PASS | PASS |
| New endpoint CPU mode | Not run | Not run | Threaded RTS required | PASS |
| GUI owner executed | No | No | No | No |

The import-only correction preserves strict warning flags.
Only the control test executable gains threaded RTS linkage.
The production GUI owner remains unchanged.
The separate endpoint mode performs metadata and file-descriptor IO before any compositor connection.
The existing pure allocation mode retains its exact command and output.
The collector accepts only the old suite or the exact ordered pair of fixed suites.
It derives the endpoint deadline from the parent, authorization and five-second cap.

The endpoint fixture contains 17 refusal cases, 32 literal seeds and expired retained-owner/reuse checks.
The final control program reaches its exact completion marker.
No separate per-case output telemetry or measured child deadline is claimed.
All six commands exit zero without forced cleanup.
Independent review matches 259 Haskell files, 11 support files, 272 managed inputs and both ELF identities.
The independent support probe also passes all 15 builder and 8 admission controls after the retained failing baseline.

This evidence qualifies compilation and pre-connect CPU behavior only.
It does not establish a connected observer, successful callbacks, peer authentication against a real compositor or normal native retirement.
The raw cleanupQualified false field remains unchanged.
Original UX024 still requires a useful real menu, physical traversal and eligible focus return.
All original 242 requirements, 417 scenarios and native bounds remain unchanged.
