# Current production architecture

Warlock-authored production code uses Elm and Haskell only. All GUI elements
must be Elm. Haskell owns the backend and reviewed native/runtime integration.
Keep one policy authority for each decision. Generated Elm output and separately
inventoried system libraries are distinct from authored production source.
No Python runtime may ship. Development QA/formal tools remain separate.
Preserve original242 requirements/417 scenarios and all frozen evidence; ports
need their own source-bound acceptance. Use authenticated AgentBus, Scrapling for
online research, and the living LLM wiki for ideas, designs and verified outcomes.
The ten-agent design/interface campaign and Muse-supervised preparation loop
are explicitly authorized and armed in preparation mode. Preparation includes
architecture, interface/source development, tooling, workflow plugins, models and
meaningful fuzz/property checks needed for readiness. Root serializes protected
checks. Final product implementation and native acceptance campaigns remain gated
on independent readiness review under the user's existing conditional rearm
authorization. A preparation
receipt is not original-scenario or release acceptance. Respect future user pauses.

Root may run bounded isolated native capability trials needed to establish
readiness after reviewing the actual source, current provider/ABI, private runtime
and owned cleanup. Declare a dedicated original-scenario record and retain the
unchanged serial native launcher, safety guards and stop histories. This permits
neither main-desktop changes nor acceptance of unobserved original obligations.

# Working instructions

This is a local archival snapshot of an active Omarchy Windows parity workspace.
Read `docs/HANDOFF.md` first. Full parity is incomplete. Native acceptance,
CPU tests and Quint model results are separate claims.

- Preserve failed and accepted evidence, frozen inventories, original deadlines,
  scenario identities and source hashes. Existing versioned components are frozen.
  Develop incrementally in `implementation/warlock/`; Git records its revisions.
  Do not copy a whole source tree for each fix or evidence update.
- Every product implementation-loop continuation begins and ends with
  `python3 -B docs/warlock-build-loop/v2/loop.py check`. Use the shared
  [Warlock contributor plugin](plugins/warlock-contributor/README.md) to scaffold
  an original-scenario slice first. Its compliance result is not GUI acceptance.
- Original absolute paths are retained. Never load a plugin against a compositor
  whose owning ABI differs from the recorded pair.
- Native GUI campaigns run serially through the protected `qa_run.py` launcher;
  preserve the five changes in `docs/crash-noise/HANDOFF-codex-window-qa.md`.
- Follow `docs/warlock-build-loop/v2/INSTRUCTIONS.md` for the current Warlock
  GUI completion loop. This replaces the v1 scheduling, copying, reporting and
  per-iteration validation rules following the nine-reviewer October 7 AAR.
  Original requirements and applicable protected QA/ABI rules remain binding.
  `docs/warlock-build-loop/v2/STATE.json` and `requirement-ledger.json` are the
  current delivery records. Older integration records are historical lanes;
  preserve their owners' edits. New native GUI
  campaigns must use `python3 -B docs/warlock-build-loop/v2/loop.py native
  --runner /absolute/reviewed/runner.py`, which holds the shared native lock and
  invokes the unchanged protected launcher. CPU QA continues through `qa_run.py`.
- The additional Warlock design-language work follows
  `docs/warlock-build-loop/design-language-v1/INSTRUCTIONS.md` and
  `DesignLanguage/WORKPLAN.md`. Its exact five-reviewer consensus preserves the
  baseline, native gates and original preview meanings. Integrate catalog/design
  work into the active product slice; browser demonstrations never qualify
  native behavior or replace the single Elm policy authority.
- Do not edit `/usr/share/omarchy`. Read the installed Omarchy skill before
  changing desktop configuration; a snapshot is in `docs/skills/omarchy/`.
- Installed Files operation semantics are specified in Quint. Change that spec
  before modifying `scripts/ops.sh`, then run its model-based tests. Reinstall
  the root-owned copy after an accepted operation-script change.
- Omarchy shell caches plugin QML URLs. Put an edited plugin entry in a new
  subdirectory and update the manifest, then rescan plugins.
- No AI attribution in commits or PRs.

## Graph navigation and living journal

The user requested iterative Graphify navigation patterned after ProjectFenrir,
RTX 5080 acceleration, and a living LLM Wiki journal. On this host:

- Use `warlock-ctx q "question"`, `explain SYMBOL`, or `impact SYMBOL` before
  exploring a new implementation question. `hq "question"` uses CUDA embeddings
  to seed Graphify traversal. Default output is a conservative 1500-token estimate.
  Make at most two graph calls per question, then read at most three bounded
  source windows with `warlock-ctx show relative/path:LINE`.
- After each code/model wave, run `warlock-ctx update`, then `warlock-ctx eval`
  before the integration gate. Check `stats` and stale warnings. Graph artifacts
  live outside this checkout at `~/.local/share/warlock-graph/graphify-out/`.
  Serialize updates. A retrieval smoke pass is not a correctness proof.
- Source beats the graph. Verify pointers and use bounded `rg` when extraction
  is missing or partial. Elm/Quint declarations are explicitly lexical; C/C++
  macro extraction may be partial. Never compress edit targets, Quint models
  or original requirement registers. GPU embeddings do not make AST parsing GPU based.
- Maintain `~/wiki/topics/warlock/`: append meaningful decisions, failures,
  verified outcomes and ideas to `log.md`; preserve immutable `raw/notes/`
  observations and refresh linked status/articles/indexes. Validate with
  `~/.local/share/llm-wiki/scripts/llm-wiki lint ~/wiki/topics/warlock --json`.
  Distinguish proposed ideas, implementation, bounded checks and original
  acceptance. Store neither credentials nor full conversation transcripts.

## Muse EARS regulation and continuity

Charles appointed Muse as regulator, with an independent user timer checking every
20 minutes. The machine-local runtime is
`/home/charles/.local/state/warlock-team/20261028/muse-supervision/`;
`regulator.py status` reports actual state. Read its three `review-*.md` reports
and `REGULATOR.md` when continuing work. Preserve original 242 requirements,
417 scenarios, literal oracles, whole-EARS obligations and all stopped histories.
Select a real implementation or original-acceptance action; documentation, model
counts, audits and timers do not reset production progress or accept GUI behavior.

With Codex collaboration tools, `send_message` queues information but does not
activate an idle or completed agent. Use `followup_task` to resume that agent's
coordination turn. Confirm actual source-worker launch receipts and live handles;
queued assignments are not running jobs. Resume external persistent threads only
after their prior process and terminal log have been revalidated.

Muse uses its own authenticated `muse-regulator` AgentBus identity. Scheduled
continuations target this exact root thread through `codex queue`, preserving
terminal input drafts. The initial UI test separately verified physical Enter
and exact-root nonce acknowledgement; it did not replace the Codex process.
On a `MUSE_REGULATOR_RESTART` message, acknowledge its exact nonce using the
documented helper before continuing actual EARS work. Do not restart live workers
or interpret silence as a terminal process. If the user explicitly pauses/stops
the goal, disarm the regulator as well; its timer must not override the user.

## Research and contract testing

- User standing instruction: use Scrapling for all web browsing and downloads. The installed CLI is `scrapling`; use captured source material and primary references. If a required fetch is unavailable, report the actual limitation rather than silently changing tools. Do not copy full copyrighted papers into the repository.
- User standing instruction: include fuzzing and Elm-style design by contract in development/refactoring. Follow `docs/warlock-build-loop/v2/FUZZING-CONTRACTS.md`: validated opaque types, explicit errors and invariants, production-route property/sequence tests, reproducible seeds and retained counterexamples, protected proportional QA. Preserve original scenario obligations and Quint correspondence.

## Privileged operations

Use the user's graphical askpass mode, not plain sudo or a request that the user
run the command manually:

```bash
SUDO_ASKPASS=$HOME/.local/bin/sudo-askpass sudo -A <command>
```

Allow time for the popup. If the user cancels, stop instead of repeatedly prompting.

## GitHub

The `github` remote currently points to `https://github.com/CharlesHoskinson/Warlock.git`. The repository is named Warlock. `/home/hoskinson/Warlock` points to the original source root to preserve frozen paths and live workers. Honor existing publication authorization and preserve concurrent workers when publishing.
For authorized GitHub operations, use `gh` (logged in as CharlesHoskinson) and
HTTPS Git URLs. Never print, copy or store its token. Do not rerun authentication
setup. Git identity is `charles hoskinson <charles.hoskinson@gmail.com>`.

## Snapshot format

All source/build/evidence files are captured, including generated artifacts.
Nested upstream `.git` metadata is archived separately. Runtime special files
are recorded only. Full modes, ownership, timestamps and SHA-256 hashes are in
`provenance/snapshot.jsonl`. Disable Git filters and newline conversion when
updating this archive; the initial repository uses `.git/info/attributes` for
byte preservation. The repository root is private (0700).
