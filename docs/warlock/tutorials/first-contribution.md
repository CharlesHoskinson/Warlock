# Your first evidence-grounded contribution

This exercise teaches you to turn a requirement into a bounded source finding. You will inspect the first-use requirement and produce a short proposed contribution. You will not start a product record, claim someone else's selected work, run a GUI or modify the desktop.

You need a Warlock checkout, Python 3.9+ and Git for the offline contributor checker. Product compiler/native dependencies are separate.

## 1. Establish the workspace

From the checkout root, run:

```sh
git status --short
python3 -B plugins/warlock-contributor/scripts/warlock.py --repo "$PWD" --json status
```

Notice which files are already dirty. `status` is read-only, but may exit nonzero when its default participant record is stale; that is not permission to repair its historical pins. `activeSlice` reports STATE selection, while an explicitly selected participant can carry its own slice. Obtain the coordinator's exact record path and use the [record lookup reference](../reference/build-and-runtime.md#participant-records-and-exit-status) to identify the actual work owner. Keep other owners' files untouched. Read [CONTRIBUTING](../../../CONTRIBUTING.md) and [the loop](../../warlock-build-loop/v2/INSTRUCTIONS.md) before proposing work.

## 2. Read one original obligation

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py inspect   --requirement ELM-UI-020 --scenario first-use
python3 -B plugins/warlock-contributor/scripts/warlock.py remaining   --requirement ELM-UI-020 --markdown --limit 2
```

Find the original given/when/then, verification text and recorded missing observations. The exercise is about first-use: customized shortcuts and a qualified component, enablement and guidance dismissal, persistent mapping or explicit choice, available help and a working component. Offline recovery is a separate named scenario. A missing observation does not prove missing implementation.

Confirm that your inspection selected the intended original, without writing a plan or record. This uses Python's standard library, not `jq` or the product toolchain:

```sh
python3 - <<'PYTHON'
import json, subprocess, sys
packet = json.loads(subprocess.check_output([
    sys.executable, "-B", "plugins/warlock-contributor/scripts/warlock.py",
    "--repo", ".", "--json", "inspect", "--requirement", "ELM-UI-020",
    "--scenario", "first-use",
], text=True))
row, = packet["requirements"]
scenario, = row["original"]["scenarios"]
assert packet["ok"] and row["original"]["id"] == "ELM-UI-020"
assert scenario["name"] == "first-use"
print(row["original"]["id"], "/", scenario["name"])
print("Given:", scenario["given"])
print("When:", scenario["when"])
print("Then:", scenario["then"])
print("Recorded requirement accepted:", row["ledger"]["requirementAccepted"])
print("Other original scenarios omitted:", row["omittedScenarios"])
PYTHON
```

You should see `ELM-UI-020 / first-use`, customized shortcuts and a qualified component, enablement and guidance dismissal, then persistent mapping or explicit choice/help/component behavior. One other original scenario is omitted by this filter. The acceptance field is a live ledger value, not an assertion that this tutorial verifies the behavior. A wrong ID, missing scenario or failed command means stop and inspect the error; do not edit the frozen requirement to fit the exercise.

## 3. Compare a source fact with the obligation

Use [the navigation tutorial](source-navigation.md) to locate the settings/help and shortcut-preference routes. Read a small source window around the actual transition. Check whether the evidence refers to these same sources or to an older tuple. Do not infer a renderer cause from a generic error message.

Write a private note containing:

- The original ID and exact scenario name.
- One concrete source fact, with file/function and source hash or revision.
- What the existing evidence actually observes and what remains unobserved.
- A proposed smallest change or decisive observation; say explicitly if no defect is established.

For example, a fixture that opens Settings first does not establish desktop use before onboarding. A before-Settings Apps observation can address that gap without inventing a production bug or rerunning offline rollback.

## 4. Finish without taking ownership prematurely

Your result is a reviewable proposal, not an accepted feature. Share it with the current coordinator. When an implementation slice is agreed and the WIP slot is available, continue with [the selected-slice how-to](../how-to/contribute-selected-slice.md). Do not run bare `start --owner` merely to finish this exercise: it adopts the currently selected work.


## 5. Check the result of the exercise

You have finished when your note separates original obligation, actual source fact, recorded observation and remaining evidence. Follow one retained archive using [the evidence-reading guide](../how-to/read-recorded-evidence.md) before calling a proposed check decisive. Re-run `git status --short`: these inspection commands should not create product files or participant records. A concurrent owner's changes may appear; inspect them without overwriting them. This tutorial has not installed a compiler, run a model/native test, selected work or changed acceptance.
