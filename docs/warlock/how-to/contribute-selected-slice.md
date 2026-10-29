# Contribute a selected implementation slice

Use this guide when a concrete original behavior is agreed, you have ownership of the work and the product WIP slot is available. To learn the process without taking ownership, use [the first tutorial](../tutorials/first-contribution.md).

## Select and declare the work

1. Read `AGENTS.md`, the [loop](../../warlock-build-loop/v2/INSTRUCTIONS.md), selected `STATE.json`, the original requirement and its ledger row. Preserve unrelated dirty paths.
2. Choose one to three original IDs, exact scenario names, before/after behavior, source paths and smallest decisive verification. A supporting task names the observed blocker and original behavior it unblocks.
3. Use the contributor plugin's `plan`, `preflight --slice-file` and `start --slice-file`. The [canonical scaffold examples](../../../plugins/warlock-contributor/README.md#scaffold-and-resume) show the exact plan flags. Their search example is illustrative, not permission to reopen an accepted scenario or assert a current defect.

Use a new ignored plan/record path for new work. The global `--record` option precedes the plugin subcommand. For a reviewed plan that you own:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py   --record .warlock-contributor/your-slice.json   preflight --slice-file .warlock-contributor/your-plan.json
python3 -B plugins/warlock-contributor/scripts/warlock.py   --record .warlock-contributor/your-slice.json   start --owner your-name --slice-file .warlock-contributor/your-plan.json
python3 -B docs/warlock-build-loop/v2/loop.py   --record .warlock-contributor/your-slice.json check
```

Replace the example names with your actual agreed paths. Bare `start --owner` adopts current `STATE.activeSlice`; it is appropriate only when you own that selection. Do not use dirty-file adoption as permission to take another contributor's draft. Declare a genuinely discovered same-slice dependency with `extend` before editing it; select a new record for another behavior.

## Implement and verify

Work incrementally in `implementation/warlock/`. Keep original deadlines, no-replay, ABI identity, draft preservation and authority boundaries. For a refactor, declare preconditions/postconditions/invariants and what the extracted type or interface may not decide. Follow [contracts and fuzzing](../../warlock-build-loop/v2/FUZZING-CONTRACTS.md).

Use [the verification guide](verify-selected-change.md) to choose changed-target compilation, a production-route regression and a meaningful negative/lifecycle case. Root serializes protected execution in the active team workflow; source preparation does not authorize worker QA. Do not run an unrelated full suite just to accumulate check counts.

## Record, review and publish

Record the actual production change or original scenario verdict with immutable source/evidence references and missing observations. Do not promote intended verification or a favorable component result to native acceptance. Keep earlier failed and partial evidence.

Before publication, run the ending loop check with the same record and use the plugin's staged `review`, including owned support files. Inspect actual staged bytes, protect foreign work and publish the reviewed owned batch normally. Update README, documentation and wiki when behavior, setup, blockers or evidence scope changes. At two qualification-only iterations or 45 minutes without a production fix/original verdict, stop expanding that investigation and preserve the missing observation; do not reset the timer with metadata or publication.

Explicitly requested documentation/support work uses project-only checks before and after; it needs no fabricated GUI slice. That exception does not turn a product edit into documentation work.
