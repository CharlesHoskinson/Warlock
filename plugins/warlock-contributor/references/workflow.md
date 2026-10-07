# Protected execution and contribution scope

Use these commands from the repository root after inspecting the actual check/runner. The plugin never executes them itself.

CPU/browser compilation and QA:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /absolute/reviewed/check.py
```

Serialize native GUI campaigns through the existing loop:

```sh
python3 -B docs/warlock-build-loop/v2/loop.py native --runner /absolute/reviewed/runner.py
```

On another development machine, use its reviewed equivalent protected launcher and retain the same invariants; absence of a launcher is missing execution capability, never permission to bypass it. Preserve core limit 1, valid parent Wayland socket, private owned runtime, exact owning core/plugin ABI pair, no DRM/XWayland fallback, normal owned-helper cleanup, and the crash-noise protections referenced by v2 instructions. Actual activation uses the existing accepted-tuple/rollback authorization boundary.

The editable product candidate is `implementation/warlock/`; its ancestry is recorded in `ANCESTRY.json`. Frozen versions and evidence remain unchanged. `docs/elm-roadmap/requirements.json` preserves original EARS and scenario text; `openspec/changes/elm-desktop-pivot/specs/` holds matching capability contracts. The acceptance ledger at `docs/warlock-build-loop/v2/requirement-ledger.json` distinguishes implemented-unverified, partial, failed, blocked and accepted observations. Follow the active v2 instructions for ownership, exact source tuple and reviewer disposition.

Read `docs/warlock-workflow-review/20261007/AAR.md` for the failed qualification/copy/publication loop, and `docs/elm-roadmap/ROADMAP.md` for original product scope. Do not substitute this summary for the selected original requirement/scenario.
