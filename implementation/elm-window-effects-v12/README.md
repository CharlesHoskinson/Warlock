# Typed first-class window-effect transactions

Runnable pure Elm implementation of minimize/restore request correlation. This is
an intent/receipt boundary, not implemented native minimization or an accepted
production bridge protocol. The current read-only native host stays read-only.
The explicit experimental `window-effect` protocol 1 envelope must undergo native
boundary qualification before integration; it is not observation protocol 3.

An admitted scene plus context supplies compositor lifetime, frontend epoch,
output generation and expected native revision. Requests also carry monotonic
request identity, operation generation and native window incarnation, all encoded
as lossless uint64 strings. Elm emits only minimize/restore operations; workspace
or scratchpad parameters are rejected. Native authority remains responsible for
family identity, canonical scene publication, focus succession, captures, geometry,
actual input exclusions and mutation-time freshness checks.

The reducer retains one bounded transaction, with Pending, Committed, Refused,
Cancelled and Unknown states. A second pending request is refused. Receipts must
match the complete intent and a current authority lifetime/epoch/output; newer
observed scene revisions do not incorrectly invalidate an otherwise correlated
receipt. Pending or committed receipts never optimistically hide/show windows.
Only admitted native snapshots change the projected scene.

Disconnect changes pending to Unknown and disables new intents while retaining
historical observations. Exact same-revision snapshot resync is allowed only
while disconnected and with identical scene content. Rewinds and contradictory
same-revision scenes refuse. Resync does not recommit/retry an Unknown request;
a new user request gets a fresh identity/generation. Authority changes invalidate
pending operations. Unknown/native-minimized-null, malformed, locked or unmapped
targets emit no intent. Terminal receipts cannot rewrite another terminal result.

`src/Effects.elm` contains pure transitions; `src/Replay.elm` is a test worker,
not a product interface. `Scene.elm` derives from V6's admission implementation
with read-only revision/minimized/actionability accessors. Existing V6 is unchanged.

The protected runner compiles actual Elm, exercises fixed and deterministic
adversarial full-tuple fixtures, executes nine exact named Quint cases plus 1,000
sampled invariant runs, and replays actual action journals into compiled Elm.
The Quint model abstracts the complete authority tuple to one authority value;
separate compiled fixtures mutate each real tuple field. Replayed journals prove
this scoped abstraction, not arbitrary native/protocol equivalence. The runner
also compiles two unsafe variants and requires named independent test failures.
Keep parser/receipt-reporting failures and all earlier input closures intact.

Still open: authenticated native effect adapter and version negotiation, authority
request deduplication and cancellation intents, first-class minimized state,
atomic family focus/workspace/geometry/preview semantics, actual accessibility
feedback, performance bounds, exhaustive overflow/decoder fuzz with shrinking,
full host integration and original native acceptance campaigns. No whole EARS
requirement or build cycle is completed by this CPU proof.
