# Working instructions

This is a local archival snapshot of an active Omarchy Windows parity workspace.
Read `docs/HANDOFF.md` first. Full parity is incomplete. Native acceptance,
CPU tests and Quint model results are separate claims.

- Preserve failed and accepted evidence, frozen inventories, original deadlines,
  scenario identities and source hashes. Use fresh derivatives for changes.
- Original absolute paths are retained. Never load a plugin against a compositor
  whose owning ABI differs from the recorded pair.
- Native GUI campaigns run serially through the protected `qa_run.py` launcher;
  preserve the five changes in `docs/crash-noise/HANDOFF-codex-window-qa.md`.
- Follow `docs/warlock-build-loop/v1/INSTRUCTIONS.md` for the current Warlock
  GUI completion loop. It incorporates the inherited `docs/elm-roadmap/BUILD-LOOP.md`
  QA/coordination rules and the consensus research adoption and release contracts.
  Read the integration lane and latest per-thread checkpoints before choosing
  work; preserve concurrent workers' source paths and state. New native GUI
  campaigns must use `python3 -B implementation/elm-build-loop-v1/loop.py native
  --runner /absolute/reviewed/runner.py`, which holds the shared native lock and
  invokes the unchanged protected launcher. CPU QA continues through `qa_run.py`.
- The additional Warlock design-language work follows
  `docs/warlock-build-loop/design-language-v1/INSTRUCTIONS.md` and
  `DesignLanguage/WORKPLAN.md`. Its exact five-reviewer consensus preserves the
  baseline, native gates and original preview meanings. Implement the catalog
  in parallel with the native GUI work; browser demonstrations never qualify
  native behavior or replace the single Elm policy authority.
- Do not edit `/usr/share/omarchy`. Read the installed Omarchy skill before
  changing desktop configuration; a snapshot is in `docs/skills/omarchy/`.
- Installed Files operation semantics are specified in Quint. Change that spec
  before modifying `scripts/ops.sh`, then run its model-based tests. Reinstall
  the root-owned copy after an accepted operation-script change.
- Omarchy shell caches plugin QML URLs. Put an edited plugin entry in a new
  subdirectory and update the manifest, then rescan plugins.
- No AI attribution in commits or PRs.

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
