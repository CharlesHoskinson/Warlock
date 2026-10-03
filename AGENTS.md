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

This repository has no remote. Do not publish it without explicit authorization.
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
