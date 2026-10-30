# Receipt lifecycle independent source and evidence disposition

Decision: ACCEPTED for the original ELM-ARC-007 scenario `receipt-committed`, using the permitted compiled bridge fixture trace. This is not acceptance of whole ELM-ARC-007 or actual native delivery. Root should bind this disposition to the immutable source/evidence commit before recording scenario acceptance. This review reads source and retained artifacts only; the reviewer launched no compiler, model, replay or native QA.

The unchanged original oracle in docs/elm-roadmap/requirements.json says: given a request with unique identity and a fixture for Committed, when the fixture transition occurs, the correlated request has exactly state Committed and no other request changes. Its verification permits native OR bridge trace; requiring a new GUI trial would add an obligation absent from this fixture oracle. The retained successful production bridge trace and matching source/build receipts satisfy that bounded oracle.

## Demonstrated baseline and correction

The actual baseline entered through OutputController.Topology removal while a request was Pending, admitted the expected output-2 projection, then delivered the exact correlated Committed outcome. It left the current transaction Unknown while removing its unresolved/issued records. The full intent and effect protocol already identified the transaction; a changed observed output was therefore an incorrect additional settlement gate, not justified retention of uncertain evidence.

The sole product change in src/Effects.elm replaces the observed-authority-gated current-transaction update with `Maybe.map settled model.transaction`, plus its explanatory comment. `settled` retains full intent/protocol equality. Existing receipt-found, supported protocol and operation/protocol checks remain. Shell binding/issued correlation remains unchanged. The correction does not mutate the observed scene, issue a window effect, alter request/generation counters, settle a different current transaction or normalize unrelated reservations.

Baseline report: receipt-output-current-cpu-1793332444826191664/report.json, SHA256 e458fbb9242bc5888ccf85bc24eef6981bf1b48857831b3c4037853535bb8577.
Baseline data SHA256 d00e7ad6c5f0d788953d35a377c55b4a04c8bb8100cf99f3f6b083bc3bebbf4a.
Prior independent BASELINE-DISPOSITION.md remains unchanged, SHA256 37ec7bd07ef24eaf4bce87de5bddb2958442d828477baba69f128bc1d3b4a7de.

## Source, build and compile-failure history

Corrected Effects SHA256 80c574e8c564c28a1fb11f1f89bb5bfa7ac97a92474bbf027a737324bb2a82cd.
Frontend lock receipt-lifecycle-frontend-lock-root-v1.json SHA256 5f4f11fd1ea60de151083decbb6741b7f676aefce9ad7dd9bf1c72edee1ea7bf. Independent comparison with pin-scrollport-frontend-lock-root-v1.json finds exactly the Effects hash changed in inputs and sources; every other lock field is equal.
Fresh Main/Bar/Popup build passed: receipt-current-build-1793333212775066294/frontend/report.json SHA256 80ab7efec7eb9f7d5448cbf94260aa5f90b32e75f1b155294c2559c149475c11.

The first candidate replay compile failed solely on two Elm parameters named `result` shadowing the top-level `result`. Preserve receipt-output-candidate-cpu-1793333213881772070/report.json SHA256 83522fde4e927aea902d1b59fbbfa1e3e425ae3ae04f7aea0706e0c5547b80c2 and compile.stderr SHA256 f84813c09d5df72948860cbf3862169a9606fc8c00b0641dd9fe903de168ad28. Source review had not caught that compile defect. The subsequent fixture-only correction renames those parameters and their references to `outcome`; no assertion or product source changed. Reusing the still-current fresh three-root receipt for a replay-only rerun was appropriate; the driver validates that receipt before and after execution.

Final public ReceiptOutputLifecycleReplay.elm SHA256 f84ee49b10aee296e88155cb734be1f07c770ca00a890fb3d1d16d38d3212a3b.
Final receipt-sequences.cjs SHA256 c24a78d84381d62b9f78320881604a0398a95e348ff8da7f7fa06af53bcdc8d5.
Unchanged private run-candidate.py SHA256 199d8f46d7148ec131b4e007855a3513e0cb542ab7203312a8505f27c0bfcb68.

## Model correspondence and bounds

The corrected two-key model separates the current transaction, unresolved reservations and issued identities. Binding/protocol guards and exact opaque full keys represent production correlation. beginOld requires its original output; output change converts only the current Pending status to Unknown; exact receipt settlement is independent of observed output. Foreign/duplicate outcomes preserve other records. The broken-output-gated variant is retained as a deliberate witness, not admitted as the corrected transition.

The releaseOld action covers the explicitly restricted existing-issued, single-owner branch without preserveShared; it is not a model of the complete validated retirement/action/geometry proof protocol. No general recovery-release correctness follows from it.

Model source SHA256 ce5978f5e226ca40281bd6140861aa765d79c194620c63bb9c6b4af40256cdcb; tests SHA256 e27fcdde2317a2b799f886a35930cb54ac11e6e9602a4679bc9a13b257550722. Public copies correspond to the tested root-v2 packet. Model report receipt-lifecycle-model-1793332908328918863/report.json SHA256 83a7b9ebee3ab25e6f86de343a4e56c1c0184a367bf9436f6c79797f41915a28 records passing actual init/type checks, 12 explicitly selected named tests and five invariant campaigns of 1000 samples/20 steps, seed 20261030. This is bounded testing, not exhaustive proof or complete tool-dependency provenance.

## Actual final production-route result

Report receipt-output-candidate-cpu-1793333313793450484/report.json SHA256 2a667210050298c85af095bc61d0bdfe580750124ac36d77a5cb421e4932d807.
Raw receipt-output.json SHA256 97776dd3fe05a68f14805e589afbbc7720daf5e5271be8395466712459a3f1db.
Root protected scope qa-harness-69edd677a76d4a1098681adcf01288a3; invocation 98ca52f7aa3b4f8db7921100a14f789d. Actual compile and replay exit zero. Independently rehashed report output files and current recorded sources: no discrepancies.

The optimized worker uses actual OutputController, Desktop, TaskbarShell, Shell, NativeOutcome and Effects production modules with the existing OutputRetirementReplay fixture. It creates an actual captured Minimize request with full request/generation/incarnation/operation/context identity and an emitted window-effect, then drives incoming wire receipts through production decoding and correlation. The representative trace retains inputs and complete relevant state before/after.

All 200 fixed-route parameter cases pass 31 assertions, seed 1705492499, xorshift32. Variations change foreign counters and independent receipt-case ordering; these are not randomized event interleavings or a shrinking campaign. Same-authority, changed-output and disconnected exact Committed outcomes produce exactly Committed and remove only their own terminal reservations. In the distinct newer-request case, its Pending transaction, other unresolved/issued records and scene/counters remain unchanged while the old matching reservation is settled. Exact terminal duplicates and eleven malformed/foreign correlation variants preserve state and emit no additional window mutation. Refused and Unknown are supporting regressions; Unknown retains its reservation. The valid Unknown reconciliation record is exercised through the controller.

This establishes the selected original receipt-committed fixture oracle, including meaningful non-vacuous preservation of another live request. It does not claim actual compositor effect delivery, native ABI/runtime acceptance, all receipt states, Cancelled wire admission, arbitrary ordering completeness, complete proof-bearing recovery release, accessibility, release acceptance or whole ELM-ARC-007. No additional scenario acceptance is inferred automatically. Preserve the demonstrated baseline, model v1/corrected v2, first failed fixture compile and final successful run as distinct history.
