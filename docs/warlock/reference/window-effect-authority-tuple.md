# Window-effect authority tuple

This reference describes the existing Elm serialization boundary for original
**ELM-ARC-005**, scenario **architecture-005**. The complete original EARS and its sole scenario are accepted on immutable source `d3a57508ab7974e96e9a631bcd1f5b39b1f6d1d4`, using the original permitted bridge verification. It records no native execution or native acknowledgement.

## Original contract and records

The [original requirement register](../../elm-roadmap/requirements.json) requires:
“The Elm desktop SHALL attach request identity, compositor lifetime, frontend
epoch, operation generation, window incarnation, output generation and expected
native revision to window-effect intents.” Given a known window and output,
when an effect is requested, the serialized request contains the full authority
tuple. Its literal verification permits a preserved **native or bridge trace**,
with artifact hashes and matching scenario receipts.

The [canonical acceptance](../../warlock-build-loop/v2/authority-tuple-acceptance-20261031.json), [independent review](../../warlock-build-loop/v2/authority-tuple-review-20261031.json), [protected report and full compressed bridge trace](../../../implementation/warlock/qa/evidence/authority-tuple-20261031/report.json) and [delivery ledger](../../warlock-build-loop/v2/requirement-ledger.json) bind the verdict. UI007's separate source batch is published; its original native/AT acceptance remains partial.

## Seven fields on the wire

[Effects.elm](../../../implementation/warlock/src/Effects.elm) defines `Intent`
and the shared `encodeIntent` / `encodeContext` serializers. Paths below are
relative to the complete outgoing window-effect envelope.

| Original authority component | Elm value | JSON path |
| --- | --- | --- |
| Request identity | `intent.request` | `intent.request` |
| Compositor lifetime | `intent.context.lifetime` | `intent.context.lifetime` |
| Frontend epoch | `intent.context.epoch` | `intent.context.epoch` |
| Operation generation | `intent.generation` | `intent.generation` |
| Window incarnation | `intent.incarnation` | `intent.incarnation` |
| Output generation | `intent.context.output` | `intent.context.output` |
| Expected native revision | `intent.context.revision` | `intent.context.revision` |

Each value is a canonical decimal string through the opaque
[UInt64.Counter](../../../implementation/warlock/src/UInt64.elm), preserving
values above JavaScript's exact integer range through `18446744073709551615`.
Native identity boundaries reject zero; counter recovery permits zero watermarks.
Successful allocation takes the next request and operation-generation counters;
exhaustion emits no intent. Context comes from the admitted observation and the
incarnation from the admitted target. The outer binding and transport
`requestId` values do not replace any member of this tuple.

## Two effect protocols, ten operations

The outer shell envelope has `protocolVersion: 3`, `kind: "window-effect"`,
`effectProtocol`, `binding` and `intent`. Transport version 3 is distinct from
the two effect protocols below.

| Effect protocol | Constructors and serialized operation names | Construction route |
| --- | --- | --- |
| 1 | `Minimize` → `minimize`; `Restore` → `restore`; `Activate` → `activate` | `Shell.Act` → `Effects.apply` (`begin`) → `Effects.encodeIntent` |
| 2 | `Maximize` → `maximize`; `RestoreGeometry` → `restore-geometry`; `ExitFullscreen` → `exit-fullscreen`; `SnapPlacement` → `snap`; `TransferWorkspace` → `transfer-workspace`; `Pin` → `pin`; `Unpin` → `unpin` | `Shell.Act` → `Effects.beginGeometry` → `Effects.encodeIntent` |

[Shell.elm](../../../implementation/warlock/src/Shell.elm) checks the captured
observation stamp and availability before selecting either route, then wraps
the encoded intent in `Send`. Protocol 2 additionally requires current negotiated
geometry capability/facts and operation eligibility. Snap and transfer append
their typed `placement` or `transfer` payload without replacing the seven fields.
[UnsentOperation.encodeCommand](../../../implementation/warlock/src/UnsentOperation.elm)
uses the same intent serializer for the custody command envelope. A current
owning-route trace must establish controller-to-envelope correspondence rather
than testing the serializer alone.

## Evidence scope and remaining authority

The actual replay is `qa/AuthorityTupleReplay.elm`, compiled against the owning production controller route. The independent `qa/authority-tuple.cjs` oracle derives expectations from raw input frames and preallocation counters using BigInt. Eight reproducible input matrices exercise all ten operations and both effect protocols: 80 positive bridge/receipt cases and 232 negative cases pass 2,986 assertions. The compressed raw trace retains every case and matching scenario receipt, with compiler, development interpreter, compiled artifact and source hashes. The first fixture compiler-shadowing failure is retained; renaming two local parameters changed no product behavior or oracle.

Root verified all executed sources against regular Git blobs; the independent reviewer verified 109 participating source/support blobs on the immutable commit before accepting the entire original EARS. Existing behavior was requalified; this verdict is not a new GUI feature. No native core or plugin was loaded.

A matching simulated bridge scenario receipt is a bridge witness. It is not a
fabricated native ACK or evidence that a compositor applied a mutation. The
literal native-or-bridge option remains intact. This slice transfers no
acceptance to unintegrated `Protocol.Authority`, a Haskell runtime, deployment,
native GUI/AT behavior or the full release. Existing Unknown/no-replay guards,
original 242 requirements/417 scenarios, deadlines, failures and native gates
remain binding. No new model or production repair is implied by this reference.

## Reproduce the accepted bridge observation

On the recorded host/source tuple, root may use the exact retained [review packet](../../../implementation/warlock/qa/evidence/authority-tuple-20261031/cpu-review.json):

```sh
python3 -B tools/qa_cpu.py \
  --review implementation/warlock/qa/evidence/authority-tuple-20261031/cpu-review.json \
  --sha256 1ad1f06a30510c296fb62ff6b2f2f225ece7cd60538dcf38021e377f22eae8be
```

This fixed mode compiles the actual owning bridge fixture directly; unrelated unchanged GUI roots retain their source-bound qualification. The guard refuses any source/tool drift. A future change needs a newly reviewed packet and applicable requalification; do not change the retained packet to make old acceptance appear current. The compiler/cache and development interpreter hashes are in the report.
