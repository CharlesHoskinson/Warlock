# Warlock window system

[GitHub: CharlesHoskinson/Warlock](https://github.com/CharlesHoskinson/Warlock) · [Local repository entry and rename record](docs/warlock-repository/v1/README.md)

Warlock is an Elm-based Linux window-system project with an active integration
candidate and preserved source/evidence history. **Feature completion and release
acceptance remain open. A GitHub merge does not deploy the desktop.**

Start with the [current product](implementation/warlock/README.md),
[remaining implementation checklist](docs/warlock-roadmap/FEATURE-COMPLETION.md)
and [current workflow](docs/warlock-build-loop/v2/INSTRUCTIONS.md). The
[delivery ledger](docs/warlock-build-loop/v2/requirement-ledger.json) preserves
original scenario identities and bounded observations. Unadjudicated does not
mean unimplemented. The [October 3 handoff](docs/HANDOFF.md), historical
[requirements](window-behavior-spec/requirements.md) and
[status](window-behavior-spec/PARITY_STATUS.md) remain archival records.

Warlock is the name of the Elm-based window-system project. See the [brand identity](docs/warlock-brand/README.md), [design philosophy](docs/warlock-brand/PHILOSOPHY.md), and [research implementation plan](docs/elm-roadmap/research/20261005-design-adoption/WORKPLAN.md). Original archival names and evidence remain preserved.

The [design-language documentation](DesignLanguage/README.md) and
[browser catalog entrance](DesignLanguage/catalog/index.html) connect current
guidance, frozen widget specimens and the contributor plugin.

## Contents

| Directory | Contents |
| --- | --- |
| `implementation/warlock/` | Editable Elm/native GUI candidate, current feature documentation and bounded evidence |
| `DesignLanguage/` | Current design guidance, layered-window contracts and frozen browser specimens |
| `plugins/warlock-contributor/` | Shared contributor skill/checker and Claude Code, Codex and Grok packaging |
| `openspec/` | Original and adopted behavior specifications |
| `docs/warlock-build-loop/v2/` | Current implementation workflow, active slice and requirement ledger |
| `window-behavior-spec/` | Requirements, Quint models, source candidates, builds, provenance and status history |
| `window-integration-qa/` | QA harness, native collectors, reports, screenshots, failed runs and source reviews |
| `installed/home/` | Snapshot of the deployed scripts, Hyprland config, bar plugins, Files app and native modules |
| `installed/system/` | Selected installed compositor/shell binaries and root-owned Files operations |
| `src/` | Related compositor/plugin, Quickshell, Qt, accessibility and portal source trees |
| `evidence/` | Earlier QA reports/builds from the cache, surviving temporary prototypes and the user's focus-bug screenshot |
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

The original archive tracks regular artifacts, including selected generated
builds and failed-run evidence. New implementation work publishes source and
minimal auditable evidence; live profiles and disposable build caches stay local.
Embedded upstream `.git` directories are archived under
`provenance/upstream-git/` so source trees are ordinary tracked files rather than
uncommitted nested repositories. Runtime sockets/devices/FIFOs are described in
the inventory rather than recreated. OS packages and external dependencies
referenced by manifests remain system dependencies.

Git stores executable bits and symlink contents. The inventory additionally
records full modes, ownership and timestamps. File filters and newline conversion
are disabled for the snapshot; `tools/verify_snapshot.py` verifies indexed or
committed blobs against the inventory. See `provenance/verification.json` for the
initial verification.

The follow-up completeness audit is in `provenance/coverage-audit-v1/`.
Additional launcher integration, desktop entries/settings, native helper builds,
older cache evidence and temporary artifacts have separate immutable inventories
under `provenance/supplement-v1/` and `provenance/supplement-v2/`. Their hashes are
verified independently; the original snapshot inventory remains unchanged.

```bash
cd /home/hoskinson/omarchy-windows-parity
git log --oneline -1
git status --short
python3 -B tools/verify_snapshot.py --revision HEAD
```

## QA

Read [AGENTS.md](AGENTS.md) and the handoff before running tests. Native tests must
use the protected QA launcher and run serially. A passing model or CPU suite does
not establish native acceptance. Current evidence is recorded with source hashes
and explicit missing observations; historical check counts do not certify the
current candidate. The pin/MAX draft compiles but its native context interaction
failed when preview arrival moved a target between press and release.

## Contributing

Use the [contributor guide](CONTRIBUTING.md) and
[Warlock contributor plugin](plugins/warlock-contributor/README.md). It supplies
scenario scaffolding, ownership and evidence checks across Claude Code, Codex and
Grok. Explicit loop checks remain required; optional host hooks are advisory.
The plugin does not execute product builds or accept GUI/release behavior.

The repository is public on GitHub. Published development work and unfinished
drafts remain distinct from release acceptance and installed desktop behavior.
