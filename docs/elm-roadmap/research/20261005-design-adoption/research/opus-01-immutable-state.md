# Research review opus-01-immutable-state: immutable state, deterministic updates, bounded history, journaling and model refinement

**Status:** independent first-round draft. Nothing here is consensus or acceptance. I only read the frozen inputs and browsed primary sources. I made no source, config or GUI changes and launched no agents.

## 1. Scope and frozen baseline

The inputs are the frozen snapshot listed in `source-manifest.json` (head `7acf7a7…`, 338 files). It frames the inventory as "Research inventory only; no native or full-release acceptance" (`source-manifest.json:1375`).

The Elm files I cite (`Main`, `Effects`, `OutputController`, `Shell`, `Replay`, `BatchReplay`) have identical hashes in v509 and v814, so each finding applies to both lanes. These stay unchanged:
- one controller with read-only bar/popup projections;
- native authority;
- 242 requirements / 417 scenarios;
- S01–S16 and the right-click amendment;
- the 13 native S09 preview scenarios;
- restore38 / recovery34;
- the original deadlines;
- the rule against replaying Unknown.

## 2. Current-design findings

The labels below separate three things: **[Impl]** is what the code does today, **[Obl]** is an obligation already in the requirements or workplan, and **[Gap]** is an acceptance gap.

**F1 [Impl] Pure, total transitions with errors that leave the model intact.**
- `Effects.apply` returns `(Model, Maybe effect, Maybe error)`, and every refusal returns the unchanged prior model (`inputs/implementation/elm-preview-shared-bridge-v509/src/Effects.elm:62-67`).
- `OutputController.update` and `register` are pure, and registration happens before the port (`inputs/implementation/elm-preview-shared-bridge-v509/src/OutputController.elm:87`, `:154-194`). `Main.update` composes them (`inputs/implementation/elm-preview-shared-bridge-v509/src/Main.elm:43-58`).
- `PreviewLifecycle` already treats native monotonic time as message data rather than reading a clock (`inputs/implementation/elm-preview-shared-bridge-v509/src/PreviewLifecycle.elm:216-228`, `:283-284`).
- This meets the core of ELM-TEA-002 (`inputs/docs/elm-roadmap/REQUIREMENTS.md:813`).

**F2 [Impl/Gap] The replay oracles see only part of the state.** There are three replay levels:
- `Replay.elm` serialises `Effects.encode` (`inputs/implementation/elm-preview-shared-bridge-v509/src/Replay.elm:18`). That encoder leaves out `unresolved`, `effectProtocol` and the observed context (`inputs/implementation/elm-preview-shared-bridge-v509/src/Effects.elm:155-164`). A defect that changes only the reserved Unknown set, which is capped at 64, would be invisible to it.
- `BatchReplay` builds its rows by hand (`inputs/implementation/elm-preview-shared-bridge-v509/src/BatchReplay.elm:96-99`).
- The v814 probe asserts selected fields over frames captured in an earlier lane (`inputs/implementation/elm-catalog-input-integrated-gui-v814/qa/run.py:9`, `:41-49`).

Only the W03 lane compares full state plus ordered commands against Quint ITF traces, and it uses declared nonce quotients (`inputs/docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.md:183-190`). ELM-QA-006 requires a replay diff covering "desired/pending/acknowledged state and emitted intent sequence" (`inputs/docs/elm-roadmap/REQUIREMENTS.md:2161-2165`). For the shared controller, that is still open.

**F3 [Gap] A replay can pass vacuously.**
- `BatchReplay` turns an undecodable corpus into `[]` (`inputs/implementation/elm-preview-shared-bridge-v509/src/BatchReplay.elm:26`).
- An unknown `kind` becomes `Nothing`, which still emits a row with no transition (`:54-55`).
- `Replay.elm` does report decode errors (`:21`), so the two harnesses behave differently.

**F4 [Impl/Obl] Some events are derived from the model instead of recorded.**
- Deadlines come from JavaScript `Process.sleep` timers in the interpreter (`inputs/implementation/elm-preview-shared-bridge-v509/src/Main.elm:35-39`). That is already W05 (`inputs/docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.md:63`).
- Replay synthesises `choice-deadline` by reading the token out of the current model (`inputs/implementation/elm-preview-shared-bridge-v509/src/BatchReplay.elm:42`). The trace therefore depends on the state under test rather than on recorded inputs.

**F5 [Impl] There are three journal styles, and all of them store snapshots rather than event logs.**
1. **Native admission journal.** Per-entry files named by content hash, with fsync of the file and directory. Every write rescans the directory, capped at 64 (`inputs/implementation/elm-preview-shared-bridge-v509/native/host-journal.h:160-196`).
2. **Python intent journal.** A single record, replaced atomically (`inputs/implementation/elm-preview-shared-bridge-v509/adapter/recovery_journal.py:80-91`).
3. **Ledger-v4.** Rewrites the whole state on every transition, up to 524288 bytes, with 64 entries and 128 scopes. It is poisoned on storage failure and migrates through a `predecessorSHA256` chain (`inputs/implementation/elm-preview-shared-bridge-v509/adapter/durable_ledger.py:6-9`, `:45`, `:106-130`).

Storing state rather than events fits the "never an executable retry queue" rule (`:1`). Two problems remain:
- Per-binding-scope watermarks are never compacted within a lifetime (`:144-148`). That causes the sticky 128-scope exhaustion already tracked as W02/03-01 (`inputs/docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.json:341-346`).
- The cost of each transition (full rewrite plus two fsyncs) has not been measured against the budget contract.

**F6 [Impl] In-memory history is bounded, but not uniformly.**
- `unresolved` ≤64 (`inputs/implementation/elm-preview-shared-bridge-v509/src/Effects.elm:91`, `:122`) and topology views ≤64 (`inputs/implementation/elm-preview-shared-bridge-v509/src/OutputController.elm:95`).
- Batches are capped at 16. Each keeps its full wire text, up to 131072 bytes, so it can be compared exactly against the native certificate (`:31`, `:174`, `:192`, `:236`).
- The `PreviewLifecycle` lists (`known`, `cancelling`, `retiring`) are bounded only by protocol gating (`inputs/implementation/elm-preview-shared-bridge-v509/src/PreviewLifecycle.elm:26`, `:258`), not by an explicit cap.

**F7 [Impl/Obl] Journal privacy.** When the QA flag is set, `Inspection.packet` emits window titles and labels on every update (`inputs/implementation/elm-preview-shared-bridge-v509/src/Inspection.elm:22-32`, `inputs/implementation/elm-preview-shared-bridge-v509/src/Main.elm:58`). Any production journal or recorder must exclude these, per `inputs/docs/elm-roadmap/ARCHITECTURE.md:147` and `inputs/docs/elm-roadmap/ELM-PRACTICES.md:29`.

## 3. Source table (all retrieved 2026-10-05)

| ID | Source (type, year) | Link | Supporting claim (verified) | Limitation |
|---|---|---|---|---|
| A1 | Czaplicki & Chong, *Asynchronous FRP for GUIs*, PLDI 2013 (academic) | [pdf](https://people.seas.harvard.edu/~chong/pubs/pldi13-elm.pdf) | §3.1: "events are globally ordered, and signal computation is synchronous"; `foldp` folds over current and previous values. §3.2: signals-of-signals are ruled out because computing the current value "would require saving all history … from the beginning of execution." | Describes historical Signal Elm. I use only the ordered-fold and bounded-history rationale; Signals are **not** proposed. |
| A2 | Okasaki, *Purely Functional Data Structures*, CMU-CS-96-177, 1996 (thesis) | [pdf](https://www.cs.cmu.edu/~rwh/students/okasaki.pdf) | Abstract: persistence means "old versions … are available for further processing"; "traditional methods of amortization break down" under persistence. | Elm is strict. The thesis says nothing about WebKit heap behaviour. |
| A3 | Abadi & Lamport, *The Existence of Refinement Mappings*, DEC SRC, 14 Aug 1988 | [pdf](https://lamport.azurewebsites.net/pubs/abadi-existence.pdf) | A refinement mapping maps lower-level states and steps to higher-level ones. Adding auxiliary (history/prophecy) variables guarantees one exists under reasonable assumptions. | It is an existence theorem and offers no tooling. |
| A4 | Davis, Hirschhorn & Schvimer, *eXtreme Modelling in Practice*, PVLDB 13(9) 2020 | [arXiv](https://arxiv.org/abs/2006.00915) | Trace checking was abandoned after 10 weeks (§4.2). One violation at step 4 left 2,683 steps unchecked. Post-processing "might mask a harmful transcription bug" (§4.2.2). It is "only practical if the specification is written with MBTC in mind" (§4.2.3). Model-based test generation was "highly successful." | Multithreaded database. A single-threaded Elm reducer avoids its snapshot-consistency problem. |
| A5 | Cirstea, Kuppe, Loillier & Merz, *Validating Traces of Distributed Programs Against TLA+ Specifications*, 2024 | [arXiv](https://arxiv.org/abs/2404.16075) | Traces can contain only updates to a subset of variables. Validation becomes constrained model checking. Discrepancies were found in every case studied. | Java/TLC rather than Quint. It is validation, not proof. |
| A6 | Overeem et al., *Empirical Characterization of Event Sourced Systems…*, JSS 178, 2021 | [arXiv](https://arxiv.org/abs/2104.01146) | Five challenges: event system evolution, learning curve, lack of technology, rebuilding projections and **data privacy**. Tactics include versioned events, upcasting and copy-and-transform. | Interview study of server systems. |
| O1 | elm/browser `Debugger/History.elm` (code, master) | [src](https://raw.githubusercontent.com/elm/browser/master/src/Debugger/History.elm) | `maxSnapshotSize = 31`. A snapshot stores the model plus a message array, and past models are rebuilt by replaying from the nearest snapshot. The snapshot array has no bound. | Not pinned; developer tool only. |
| O2 | elm/core 1.0.5 `Array.elm` / `Dict.elm` | [Array](https://raw.githubusercontent.com/elm/core/1.0.5/src/Array.elm), [Dict](https://raw.githubusercontent.com/elm/core/1.0.5/src/Dict.elm) | Array is a tree with branching factor 32 and a tail. Dict is a red-black tree with O(log n) operations. | Not checked against the pinned compiler's package set. Sharing is not measured. |
| O3 | Redux Style Guide (docs) | [docs](https://redux.js.org/style-guide/) | Reducers "must not … generate random values (`Date.now()`…)", because time travel calls them "many times with earlier actions". Non-serialisable state breaks DevTools. Model actions as events. | JavaScript library; advisory only. |
| O4 | Immer Patches (docs) | [docs](https://immerjs.github.io/immer/patches/) | Patches let you "replay changes on a slightly different state tree". They are not guaranteed minimal and must be applied to an equal base. | Based on mutable proxies. |
| O5 | Apache Kafka 4.3 Design: Log Compaction | [docs](https://kafka.apache.org/43/design/design/) | Retains "at least the last known value for each message key". Tombstones are kept for `delete.retention.ms`. "Compaction will never re-order messages." Offsets never change. | Tombstone removal is time-based, which is not acceptable for authority records. |
| O6 | Quint docs and Apalache ADR-015 ITF | [Quint](https://quint.sh/docs/checking-properties), [ITF](https://apalache-mc.org/docs/adr/015adr-trace.html) | Simulation is bounded by `--max-samples`/`--max-steps`. Apalache gives "incomplete verification results"; TLC enumerates states. ITF encodes integers as `{"#bigint":"num"}` and disallows JSON numbers. | Tool documentation. |
| O7 | elm-program-test `ProgramTest.elm` (code) | [src](https://raw.githubusercontent.com/avh4/elm-program-test/main/src/ProgramTest.elm) | `Cmd` cannot be inspected, so programs define an `effect` type and use `withSimulatedEffects : (effect -> SimulatedEffect msg)`. | Test library; no native oracle. |

## 4. Adoption proposals, in priority order (all drafts)

### OPUS01-IMM-1: Total canonical state observation with an explicit abstraction function

- **Reason:** F2. A partial observation function is a refinement mapping that nobody has declared (A3). A4's warning about transcription bugs hidden in post-processing applies directly to hand-built rows.
- **Classification:** refinement of ELM-TEA-002 and ELM-QA-006, and of W04 ("byte-identical differential replay", `inputs/docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.md:62`). It reuses the W03/402 quotient precedent. It is not new behaviour.
- **Requirement (EARS):** WHEN a replay or refinement oracle compares compiled reducer behaviour, the verifier SHALL observe a total canonical encoding of every controller Model field and the ordered effects. It SHALL compare them only through a versioned abstraction function whose quotiented fields are explicitly enumerated and reviewed.
- **Implementation choices (non-normative):**
  - A hand-written encoder per module, plus a review rule that fails when a record field is neither encoded nor quotiented.
  - Optionally, a per-step digest for long soak runs.
- **Alternatives:**
  - Keep spot assertions. Rejected: the escaped mutants 401/406 show the risk.
  - Use a non-optimized debug-build dump. It is not the release artifact; I did not verify whether `--optimize` forbids `Debug`.
  - Digest only. It loses diagnostics.
- **Costs:** encoder upkeep on every Model change; larger traces; nonce quotients.
- **Incremental fit:** start with `Effects` and `OutputController` against the existing BatchReplay corpus. No wire change.
- **Validation:** separately compiled mutants that change only fields outside the current observations must be detected. Examples: dropping an Unknown from `unresolved` (`inputs/implementation/elm-preview-shared-bridge-v509/src/Effects.elm:211-212`), changing `effectProtocol`, changing `highest`. The field-coverage report must show zero undeclared fields.
- **Scenarios:**
  - GIVEN the v509 Effects reducer and a mutant that removes one Unknown entry while leaving `transaction` unchanged, WHEN the replay corpus runs, THEN the diff names `unresolved` and the run fails.
  - GIVEN a new Model field that is neither encoded nor in the quotient manifest, WHEN coverage runs, THEN verification fails closed.
  - *(Race/negative)* GIVEN two traces that differ only in an opaque token nonce, WHEN they are compared, THEN they are equal under the declared quotient. Any difference in lifetime, session, frontend or incarnation makes them unequal.

### OPUS01-IMM-2: Replay corpora that cannot pass vacuously

- **Reason:** F3. A4 shows how partial coverage can masquerade as success, and O6 limits what bounded sampling can claim.
- **Classification:** refinement of ELM-QA-006 and ELM-QA-007 (`inputs/docs/elm-roadmap/REQUIREMENTS.md:2171`). It applies the exact-name rule of ELM-QA-004 to replay events.
- **Requirement (EARS):** IF a replay input fails harness decoding, has an unrecognised kind, or the executed event count differs from the corpus manifest, THEN the replay verifier SHALL fail the run, record the event index and reason, and SHALL NOT report state or effect agreement.
- **Distinction:**
  - A *reducer refusal* is a legitimate typed outcome and is counted separately; the 557 inactive-slot rejections are the precedent (`inputs/docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.md:106-107`).
  - A *harness* decode failure is fatal.
- **Alternatives:** schema-validate in Python only. Rejected because the compiled harness can still drop input.
- **Cost:** low.
- **Incremental fit:** one manifest per corpus (hash, count, kinds).
- **Validation:** truncated JSON, a renamed kind and a manifest count that does not match all fail. Legitimate refusals still pass with a nonzero refusal count.
- **Scenarios:**
  - GIVEN a corpus whose fifth event has kind `topolgy`, WHEN BatchReplay runs, THEN the run fails at index 5 and no agreement is reported.
  - GIVEN a stale disposition the reducer refuses, WHEN replayed, THEN the run passes and records one typed refusal with the state unchanged.
  - GIVEN a manifest listing 1,509 steps, WHEN 1,508 execute, THEN the run fails.

### OPUS01-IMM-3: Keyed compaction semantics for the durable unresolved/floor ledger

- **Reason:** F5. O5 offers a keyed-retention pattern (latest value per key, tombstones, order preserved, offsets immutable). Retiring a tombstone must be driven by the authority, not by time. A6's evolution tactics match the existing v3→v4 copy-and-transform chain.
- **Classification:** refinement of W02 (02-08, 03-01) and ELM-UI-007 (`inputs/docs/elm-roadmap/REQUIREMENTS.md:1745`). It **must coordinate with the existing 670/675/693 work, which is not in the frozen inputs**, and may duplicate it.
- **Requirement (EARS):** WHEN the durable ledger records a settlement or a scope retirement, the ledger SHALL:
  - retain the latest record per key;
  - retain monotone allocation floors for every binding scope the native authority has not certified as retired;
  - never remove a Pending or Unknown record;
  - compact a scope only after an authority-certified retirement with no unresolved entry under that scope.
- **Implementation choices:**
  - A schema-v5 copy-and-transform with a `predecessorSHA256` link.
  - Keep the existing temp-file, fsync and rename sequence.
  - Retirement evidence follows the `binding-retirement` proof shape (`inputs/implementation/elm-catalog-input-integrated-gui-v814/qa/run.py:14`).
- **Alternatives:**
  - Time-based tombstones (O5's `delete.retention.ms`). Rejected because they could revive an ID.
  - An append-only event log. Rejected because it adds replay surface the shell does not need.
  - Simply raising the cap. Rejected because exhaustion becomes sticky later instead.
- **Costs:** a migration, and a dependency on an authority certificate.
- **Validation:**
  - A soak that rotates more binding scopes than the current cap, each with certified retirement, completes without exhaustion.
  - A mutant that compacts an uncertified scope is detected.
  - Crash injection at each fsync point leaves either the old state or the new state valid.
  - Measure bytes written and fsyncs per transition against `budgets.json` (ELM-QA-021/023, `inputs/docs/elm-roadmap/REQUIREMENTS.md:1521-1545`). **No new number is proposed; freezing these budgets is a prerequisite task.**
- **Scenarios:**
  - GIVEN scope S with only settled records and a certified retirement of S, WHEN compaction runs, THEN S's floor becomes a retired tombstone and a new request under S is refused.
  - GIVEN scope S without a certificate, WHEN compaction runs, THEN S's floor is unchanged.
  - *(Race)* GIVEN a retirement certificate arriving while S holds a Pending intent, WHEN compaction is attempted, THEN it is refused, the Pending entry is kept (or becomes Unknown on disconnect), and nothing is replayed.

### OPUS01-IMM-4: Environment inputs, including time, are recorded messages

- **Reason:** F4. O3 forbids reading time inside reducers. A1 bases determinism on a globally ordered fold of events. O7 requires inspectable effects in order to simulate them.
- **Classification:**
  - Duplicate of W05 for native deadline semantics (`inputs/docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.md:63`).
  - Refinement of ELM-QA-006 for one point: replay must not derive inputs from the state under test.
- **Requirement (EARS):** The controller SHALL receive every expiry and clock observation that changes the Model as a typed message carrying its native clock identity and value. The replay journal SHALL record that message rather than reconstructing it from Model state.
- **Implementation choices:**
  - The JavaScript timer is only a wake hint, and native deadlines remain authoritative.
  - **Native safety is not moved into JavaScript.**
- **Alternatives:** keep model-derived synthetic events. Rejected because they hide token-selection bugs.
- **Cost:** a protocol migration, already scheduled under W05.
- **Validation:** replaying the recorded messages reproduces the model digest (IMM-1). A mutant that selects the wrong token under derivation is detected.
- **Scenarios:**
  - GIVEN a prepared token with native deadline D, WHEN the frontend stalls past D and then receives a native expiry stamped C≥D, THEN live and replayed runs reach identical models.
  - GIVEN a JavaScript wake that fires before the native clock reaches D, WHEN it is processed, THEN no expiry transition occurs.
  - GIVEN an exact late Committed receipt after expiry, WHEN it is processed, THEN it is reconciled per W05 and never re-emitted.

### OPUS01-IMM-5: A bounded, sanitised diagnostic flight recorder (deferred)

- **Reason:** ELM-QA-007 needs reproducible fault traces. O1 shows the snapshot-plus-messages design but with no bound. Persistence (A2) keeps retaining snapshots cheap, except that batches pin up to 16 wire strings (F6). Privacy is one of A6's five challenges (F7).
- **Classification:** new diagnostic behaviour. Status is **deferred** until the budget contract is frozen.
- **Requirement (EARS):** WHILE the shell runs, the controller SHALL retain at most the budget-frozen number of recent sanitised typed messages and periodic Model snapshots. It SHALL export them only on reconciliation failure, on exhaustion, or on an explicit diagnostic request. It SHALL NOT forward recorded content as native intents.
- **Implementation choice:** hold the recorder in a pure Elm wrapper Model, not in the JavaScript adapter.
- **Alternatives:** ship the Elm debugger. Rejected: its history is unbounded and not sanitised.
- **Costs:** heap and CPU. The measurement task is retained heap per snapshot inside WebKit, measured under ELM-QA-023.
- **Validation:**
  - A canary title or text never appears in an export.
  - Replaying the exported snapshot plus messages reproduces the exported final digest.
  - The bound holds across the soak.
- **Scenarios:**
  - GIVEN a window titled with a canary string, WHEN an export is triggered, THEN the canary is absent.
  - GIVEN an export requested during processing, WHEN it completes, THEN it reflects a whole-update boundary.
  - GIVEN a recorder at its bound, WHEN new messages arrive, THEN the oldest segment is dropped and no intent is emitted.

## 5. Rejected and deferred alternatives

- **Full frontend event sourcing or rebuilding state at startup:** rejected. It conflicts with "fresh snapshot; never replay old mutations" (`inputs/docs/elm-roadmap/ARCHITECTURE.md:277`) and with the Unknown rule.
- **Undo or time travel over native effects:** rejected. A user reversal is a new operation (`inputs/docs/elm-roadmap/ARCHITECTURE.md:217`).
- **Immer-style delta projections:** deferred. They require base agreement (O4), which is new protocol state, and should wait for budget measurements.
- **Replacing exact batch-text comparison with a digest:** deferred. Exact comparison authenticates the registered batch (01-01).
- **Replacing bounded Lists (≤64) with Dict, or adding `Html.Lazy`:** deferred until profiling shows a need (`inputs/docs/elm-roadmap/ELM-PRACTICES.md:19`).
- **Full-scale trace checking on the native multiprocess side:** deferred. A4 reports its cost. Prefer model-based test generation, as the Quint ITF lanes already do.

## 6. Research unknowns

- Whether 670/675/693 already compacts the ledger.
- Whether the pinned compiler (`elm@0.19.2-0`, `inputs/implementation/elm-catalog-input-integrated-gui-v814/qa/run.py:35`) and its package set match elm/core 1.0.5.
- Actual retained heap and fsync latency on the target filesystem.
- Whether the native admission journal's per-write directory rescan matters within budget.
- Whether a cheap total encoding is feasible for opaque types under `--optimize`.

## 7. Consensus note

These are one reviewer's independent drafts. Any overlap with the other nine reviews should be recorded as convergence rather than unanimity. Votes and dissent belong to the second-round candidate matrix.
