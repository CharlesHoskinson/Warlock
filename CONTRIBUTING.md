# Contributing to Warlock

Use the [Warlock contributor plugin](plugins/warlock-contributor/README.md) for Claude Code, Codex or Grok. Its shared offline checker also works without an AI client. Read repository `AGENTS.md`, the [current loop contract](docs/warlock-build-loop/v2/INSTRUCTIONS.md) and the [AAR](docs/warlock-workflow-review/20261007/AAR.md) before product work. Original EARS and OpenSpecs determine behavior; a plugin pass is structural compliance, never GUI acceptance.

From the repository root:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py status
python3 -B plugins/warlock-contributor/scripts/warlock.py remaining --summary
python3 -B plugins/warlock-contributor/scripts/warlock.py start --owner your-name
python3 -B docs/warlock-build-loop/v2/loop.py check
```

The default scaffold uses the selected slice in `STATE.json`. For another task, supply a small JSON slice through `start --slice-file`: 1–3 original requirement IDs, exact scenario names, before/after behavior, candidate source paths and decisive verification. Preserve the old record and use a different `--record` when moving slices. Declare all files you intend to edit before work. Resumed drafts require explicit per-path `--adopt-dirty` and an ownership note; other contributors' dirty files remain protected. Scratch records are ignored.

Implement in `implementation/warlock/`, integrating with its actual model/update/view and narrow native authority. Read only applicable architecture/design-language/FRP and OpenSpec constraints. Preserve original deadlines, Unknown/no-replay, ABI pairing and drafts. Build changed targets and run the decisive behavior plus relevant negative/lifecycle case. Native campaigns use `docs/warlock-build-loop/v2/loop.py native --runner /absolute/runner.py`; it checks the contribution first and afterward, then delegates to the unchanged serialized protected native coordinator. CPU QA retains the original `qa_run.py` launcher.

Use the plugin's `verify-plan` to suggest proportional protected checks for source changes since the last record, or `verify-plan --selected` before edits. It executes nothing; inspect the runner and tuple before use, and choose checks for explicit unmapped/support files. Native candidates do not replace the original oracle or AT/IME obligations. Required loop checks expose structured no-progress elapsed time and trigger reasons so the next continuation can act on the AAR limits.

Record observed source changes or exact scenario verdicts through the plugin's `record` command. State what a user can do, what actually failed and which physical/native/keyboard/AT/IME obligations remain. Update the original ledger only when the original oracle is satisfied and independently reviewed. Publication, check counts and administrative closures are not GUI features. At two qualification-only iterations or 45 minutes without a production fix/original verdict, record the missing observation and choose another mandatory product slice.

Use `remaining --requirement <original-ID>` for the recorded scenario checklist, and `handoff` to resume an owned slice. Before committing, `review` compares staged files with current source and evidence; add owned support files with `--include`. It catches foreign drafts and partial staging without changing the index or certifying GUI behavior. See [the plugin guide](plugins/warlock-contributor/README.md#review-a-contribution) for scope and limitations.

The [implementation map](plugins/warlock-contributor/references/implementation.md) identifies existing source entry points. Use `report --markdown` for a delivery note from the participant record: it separates intended and observed behavior, retains evidence scope and missing obligations, and identifies uncommitted paths. Review the evidence before publishing; this command writes nothing and stale observations return nonzero.

Documentation, plugin development and other explicitly requested supporting work use proportional validation; use `python3 -B plugins/warlock-contributor/scripts/warlock.py check --project-only` before and after; they do not require a fabricated GUI completion. The optional CI template checks frozen original identities and archival-path changes, then runs the cheap plugin policy tests. It does not run GUI sessions or certify a release.
