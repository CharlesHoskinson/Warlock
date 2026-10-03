# Omarchy Windows parity workspace

Local Git snapshot of the Windows 11 window-system work on this desktop.
**Full parity is incomplete. This snapshot does not deploy anything.**

Start with [the current handoff](docs/HANDOFF.md). It supplements the historical
[requirements](window-behavior-spec/requirements.md) and
[status](window-behavior-spec/PARITY_STATUS.md), which are preserved unchanged.

## Contents

| Directory | Contents |
| --- | --- |
| `window-behavior-spec/` | Requirements, Quint models, source candidates, builds, provenance and status history |
| `window-integration-qa/` | QA harness, native collectors, reports, screenshots, failed runs and source reviews |
| `installed/home/` | Snapshot of the deployed scripts, Hyprland config, bar plugins, Files app and native modules |
| `installed/system/` | Selected installed compositor/shell binaries and root-owned Files operations |
| `src/` | Related compositor/plugin, Quickshell, Qt, accessibility and portal source trees |
| `docs/crash-noise/` | Crash investigation and the five required QA launcher changes |
| `provenance/` | Source-to-repository mapping, SHA-256 inventory, original file modes and upstream Git metadata archives |
| `tools/` | Snapshot and integrity verification utilities |

The existing workspace remains at `/home/hoskinson/window-behavior-spec` and
`/home/hoskinson/window-integration-qa`. This repository is a separate snapshot;
new work in those directories does not automatically update it.

## Reproducibility and integrity

Historic evidence contains absolute paths, frozen file hashes, fixed deadlines
and compositor/plugin ABI identities. Those bytes and symlink targets are
preserved. Moving a checkout does not automatically make these native campaigns
portable; prepare and review a fresh derivative rather than rewriting old proof
packets or loading a plugin against a different compositor.

All regular artifacts are tracked, including generated builds and failed-run
evidence. Embedded upstream `.git` directories are archived under
`provenance/upstream-git/` so source trees are ordinary tracked files rather than
uncommitted nested repositories. Runtime sockets/devices/FIFOs are described in
the inventory rather than recreated. OS packages and external dependencies
referenced by manifests remain system dependencies.

Git stores executable bits and symlink contents. The inventory additionally
records full modes, ownership and timestamps. File filters and newline conversion
are disabled for the snapshot; `tools/verify_snapshot.py` verifies indexed or
committed blobs against the inventory. See `provenance/verification.json` for the
initial verification.

```bash
cd /home/hoskinson/omarchy-windows-parity
git log --oneline -1
git status --short
python3 -B tools/verify_snapshot.py --revision HEAD
```

## QA

Read [AGENTS.md](AGENTS.md) and the handoff before running tests. Native tests must
use the protected QA launcher and run serially. A passing model or CPU suite does
not establish native acceptance. The latest capture candidate passed 462 CPU
tests; its live restore baseline and recovery suite remain open.

No remote is configured. Nothing has been pushed or installed by this snapshot.
