# Typed durable reconciliation frame decoder v601

This isolated Elm module validates schema and correlates retirement evidence to
trusted, already accepted read identities. It is not wired into Desktop, Effects,
SurfaceController or native release admission. Existing public Binding, Effects,
ActionProjection, GeometryProjection, GeometrySizePolicy and UInt64 dependencies
are copied byte for byte from frozen v592. No desktop policy is reimplemented.

## Public contract

`decodeUnknown : Binding -> Json.Decode.Value -> Result String Frame` accepts an
exact protocol-3 host-reservation-unknown object with current binding and record.
The exact schema-2 record retains its **old binding**, full existing Effects.Intent,
effectProtocol 1 or 2 and historical Unknown status. Old intent lifetime/epoch must
match its old binding. Protocol 1 permits minimize/restore/activate; protocol 2
permits maximize/restore-geometry using the existing intent operation names.

`decodeReleased : Expected -> Json.Decode.Value -> Result String Frame` accepts an
exact protocol-3 host-reservation-released object with the same record and release.
Release contains id, proof and observation. The opaque ID is exactly 64 lowercase
hexadecimal characters; this module neither computes nor authenticates its digest.
The qualified binding-retirement proof has exactly nine fields: protocolVersion,
kind, retirementProtocol, operation, binding, requestId, queriedBinding, sequence,
grantState. Protocols are 3/1; operation is observe or retire; grantState is Retired.
Proof current binding and request ID match trusted Expected, and queriedBinding
matches the retained historical record binding. Old and current bindings differ
but share native lifetime authority. Unknown remains historical after release.

Expected must come from stored history plus the frontend's already accepted reads,
never from copying the untrusted release envelope. It carries currentBinding,
record, proofRequestId, actionRequestId, geometryRequestId, actionContext and
geometryContext explicitly. Each received read ID equals its own accepted ID;
each received context equals its own accepted context, including revision.
Both current observation contexts match current binding lifetime/epoch and share
output generation. Revisions, read request IDs, old effect request/generation,
retirement request and retirement sequence are separate numeric domains. No
cross-domain equality is required. Canonical nonzero UInt64 strings cover all
identity counters; booleans, JSON numeric counters and overflow are rejected.

## Integration ordering and limits

The upcoming v600 owner must retire each recovered old binding before fresh
frontend-requested action projection and geometry reads. Keep exact accepted
wire replies, IDs and contexts. Persist original Unknown record, retirement proof
and both observations; fsync admission retirement; deliver the accepted read
replies before emitting release. The Elm controller can then supply Expected
from accepted read state. No unsolicited snapshot IDs or rewritten counters.

This decoder produces values only: no Cmd, Sub, effects, replay, outcome invention,
deadline change, settlement, backend authentication or fsync assertion. A caller
must implement authoritative durable release separately. Unknown frames can retain
history from another native lifetime; release requires the qualified retirement
native scope. Native keyboard, accessibility, IME and real durable recovery remain
open and are not claimed by this CPU packet.

Strict object field checks occur after JSON parsing. Duplicate lexical JSON keys
must be rejected by the transport before JavaScript/Elm Value parsing collapses
them; these tests do not establish transport duplicate-key rejection.

## Evidence

The optimized compiled public worker checks 162 fixtures. It exercises exact
nested schema, unsupported protocols/status/operations, extra/missing fields,
foreign bindings, stale own-domain revisions/read IDs, independent accepted IDs,
noncanonical/boolean/numeric/overflow counters and malformed release IDs. Accepted
cases verify original intent, original binding and historical Unknown survive.

The positive release fixture is **synthetic normalization across campaigns**.
The captured v596 request-23 Retired proof is retained exactly. Original v573
Unknown request-12 frames are retained exactly via the v575 reproducer capture.
Only the test record's intent lifetime/epoch are normalized to that proof's old
binding; current observation contexts and accepted IDs are explicit synthetic
inputs. This is not a captured end-to-end release or durability certificate.

Five separately compiled deliberate mutations remove queried-binding, accepted
action-ID or accepted geometry-context guards, impose incorrect cross-domain
equality, or turn historical Unknown into Committed. Each must produce retained
counterexamples. The first mutation pass exposed a fixture alias between old
binding and queried binding; its failed report is preserved. JSON-isolated fixture
mutations correct that blind spot without changing production source. The initial
capture-extraction failure and pre-trim dependency snapshots are also preserved.

All proof commands run through the protected CPU qa_run.py launcher, with bounded
180-second compile subprocesses and 5-second worker timer. Commands, compiler
output, source/input SHA256 inventories, original frames, counterexamples and
versions are retained. Re-run qa/run.py and qa/mutations.py through that launcher;
new timestamped evidence must not overwrite frozen packet files.
