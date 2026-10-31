# Requirement admission

Whole original **ELM-REV-005 / requirement-ownership** is accepted on tested source `20df98fefb509ca935d34dc044d0e6664d17a45e`. This is administrative development-workflow acceptance, not a GUI feature or native/release verdict.

## Contract and enforcement

Before a contribution participant is admitted, every one of the original242 requirement rows must have an accountable owner role, a distinct independent verifier role, phase, task/task ID and named acceptance scenarios. The live [task list](../../../openspec/changes/elm-desktop-pivot/tasks.md) and [traceability table](../../elm-roadmap/TRACEABILITY.md) must form exact bijections with the [approved registry](../../elm-roadmap/requirements.json), with matching roles, phase/task, scenario counts and capability links.

The read-only `validate_registry_admission` in [the contributor checker](../../../plugins/warlock-contributor/scripts/warlock.py) runs in `context` after the existing frozen-registry/language and ledger guards. Missing, duplicate, foreign or inconsistent mappings fail before participant directories, locks or records are created. The check covers unselected requirements too. It supports the canonical optional-phase headings, checkbox state and escaped Markdown separators; unrelated prose is not an implementation mapping. Original registry, task and traceability bytes remain unchanged.

Role labels are structural assignments. This guard does not authenticate a human reviewer or accept any GUI/native oracle. Ordinary ownership and independent review still apply.

## Evidence and reproduction

The [canonical acceptance](../../warlock-build-loop/v2/registry-admission-acceptance-20261031.json), [independent review](../../warlock-build-loop/v2/registry-admission-review-20261031.json) and [retained evidence](../../../implementation/warlock/qa/evidence/registry-admission-20261031/report.json) preserve the actual failure and correction:

- The complete positive registry contains242 requirements and417 named scenarios. Both valid admission controls pass.
- The old checker admitted24 bad task/trace mappings and wrote participant artifacts, producing48 failed assertions. Registry-field changes already refused through the unchanged frozen-hash guard.
- The repaired checker passes the same35 transactions and213 assertions, refusing all33 invalid cases before artifact creation. Inotify and final artifact inventories cover transient and persistent participant writes.
- Eight seeded unselected-row variants use seed20261031. All197 plugin regression tests pass. Raw CLI outputs, hashes, source tuple and complete reports are retained in compressed evidence.

Root may reproduce the exact source-bound observation using the retained review packet:

```sh
python3 -B tools/qa_cpu.py \
  --review implementation/warlock/qa/evidence/registry-admission-20261031/cpu-review.json \
  --sha256 e1f3448d03491d0fbdd74ee16e3160459bfd8a5eca3602ca59fc31de33c593e8
```

The wrapper admits only the fixed registry runner and reviewed mode, retaining scope/core/private-runtime/serialization guards. A changed source or input requires a fresh reviewed packet; do not rewrite old evidence to make it appear current. The test mutates only disposable Git fixtures, with local hooks, signing and filter controls; no user configuration, production runtime or main desktop is changed.

The immutable tested commit contains the actual STATE/ledger inputs used by the run. Later acceptance metadata is a separate disposition batch. Native, Haskell-port, GUI/AT and release obligations remain open; all original deadlines and stopped histories remain binding.

Because STATE/ledger acceptance metadata is written after the tested source commit, the retained packet may intentionally refuse on the latest branch. It records the immutable experiment. A current rerun requires root to regenerate and review the complete input packet; preserving an old verdict never authorizes silently updating its recorded hashes.
