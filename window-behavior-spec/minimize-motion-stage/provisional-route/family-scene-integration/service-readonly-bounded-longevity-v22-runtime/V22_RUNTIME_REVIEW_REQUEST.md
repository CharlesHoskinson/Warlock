# V22 bounded current-owner read-only source review

Isolated source packet. No native/client/GUI launch, deployment, live configuration change or acceptance of the original native baseline.

## Authority scope

The approved design is retained byte/mode-exact in `reviewed-design-v22/`, and the external design handoff remains immutable. The new `CurrentReadWitness` is only a fresh read-data witness. It is never historical integrity, native effect, Keeper/job/actor closure, cancellation or recovery settlement authority.

Construction still invokes the original full-chain `authority()` before creating an owned current proof. Explicit `audit_history()`, inherited recovery validators and normal `assert_closed()` traverse the entire chain. Mutating an older unborrowed segment can leave fresh query bytes usable under this narrow scope; full audit, normal close and restart refuse it. Latest or borrowed segment corruption refuses fresh bytes.

## Exact inherited changes

Only `readonly_ipc.py` and one function in `test_readonly_longevity.py` differ from the 131 inherited top-level sources. Every other inherited file and all inherited modes remain exact. Public `authority`, historical validators and original `_checked_active` remain text-exact. Native/effect/recovery consumers and their guards remain byte-exact.

`closure_tools/source-inverse-final.json` and the two exact diffs expose every inherited delta. The whole original query body, rotation body, constructor and query reference wrapper are recovered through explicit inverses. The sole fixture retarget forwards `borrow` to `_current_authority`, preserving its original blocked late-result timing, all assertions and all deadlines; its full-file inverse is byte-exact.

## New source and fields

- `readonly_current.py`: sealed noexec-data owner/tip tokens; exact root/archive/lease descriptors; latest regular segment descriptor; typed current witness; bounded live borrower slots; adoption only after durable tip publication; eventual owned FD retirement.
- Issuer adds exactly `currentSource`, the current helper's complete material. Full retained-row validation checks it and removes it before the original strict validator projection.
- Owner token: role, generation, complete issuer, exact root/directory/lease FD material, original predecessor, and `startupFullValidated=True`. It does not assert ancestors remain unchanged forever.
- Tip token: role, generation, issuer digest, exact epoch/pointer/previous, archived count, and actual regular file FD material. Tip metadata is captured independently of mutable Python FD wrappers.
- Witness: issuer digest, generation and exact owner/latest/borrowed descriptor identities and token digests. No historical/native/settlement field.
- Current snapshot remains the original nine-field version2 layout. Exact integer version/serial/epoch, literal false fault, exact field set, original strict pointer schema and canonical typed binding equality are required before connection. Bool/float numeric aliases are refused.

## Runtime ordering and limits

Each ordinary query retains the original absolute timeout, owned raw Unix connection/peer guards, full JSON/EOF/schema validation, durable connection registration/closure/confirmation and no retry. Begin reserves a bounded query proof slot before any new connection. Current queries validate bounded active rows and one latest bounded segment; held queries additionally validate their borrowed old tip. Own append keeps borrowed old descriptors live. Durable compact-tip record precedes adoption and row reclamation; failed publication/adoption quarantines with no usable response. Normal close refuses a pending append or live borrower and performs full audit before retiring data descriptors.

At most512 live query slots bound borrowed descriptor pairs plus latest/preparing pairs and fixed current anchors. No archive-depth term is introduced into the steady-state fresh proof. Full startup/audit/normal-close work deliberately remains proportional to retained history.

## Evidence

- Reviewed design:52 named tests, two2000×100 runs before implementation.
- Normal-close refinement:8 named/2000×100 before the append closure guard.
- Typed snapshot refinement:10 named/2000×100 before correcting the actual `epoch=False` counterexample;15 named/2000×100 with explicit typed historical source projection before correcting the actual float-size source counterexample.
- Final inherited refresh:388 Python tests,383 named Quint scenarios,33 models×2000×100 plus a separate bounded valid-path2000 run; exact runtime sources remained unchanged during the proof.
- Four actual closure-tool file/mode tests: nested ancestral manifest inclusion, exact own descriptor exclusion, declared mode replacement refusal, exclusive descriptor publication.
- Actual query histories: inherited genuine640 queries with automatic512-row capacity; separate1031 real peer requests over0..1024 archived rows with proactive64-row archival cadence, original1s query and actual1s maintenance deadlines. No synthetic rows, runtime budget overrides or replay data.
- Measurement overlapped the full CPU suite. The retained first typed point medians at0/64/128/256/512/768/1024 archived rows were57.943/123.496/100.220/96.414/91.897/99.643/122.377ms; largest1024 point163.026ms. Final-source timing is recorded separately in `v22-source-typed-history-measurement-final.json`. Process descriptors were11 before any segment and12 thereafter, with one unborrowed tip generation and zero borrowers after queries. Full audit/normal close passed.

These are bounded CPU/kernel/source results. They do not establish arbitrary history lengths, controlled cross-version speedup, physical frame cadence or native parity.

## Retained failures and remaining obligations

The packet preserves the initial full376/368/32 proof, the intermediate386/378/33 full proof and both earlier measurements, original three inherited instrumentation/diagnostic failures, actual unregistered borrower FD-bound counterexample and preimages, actual bool-epoch returned-bytes counterexample and preimages, actual float-size historical source projection counterexample and preimages, the one wrong nlink fixture-index failure and inverse checker whitespace mistake. Final corrections do not widen original assertions, timing or authority.

Independent review and root source freeze/pairing are pending. Original38 native baseline/fault acceptance, current-user cancellation ingress, actor-ledger longevity, reduction/preview/actor integration and later deployment remain separate obligations. Root alone may launch native campaigns.
