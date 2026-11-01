# Warlock contributor

One shared offline Python checker and implementation skill, with thin Claude Code, Codex and Grok packaging. It helps contributors deliver actual GUI behavior against Warlock's original requirements. It cannot certify a physical/native/AT oracle or release acceptance. Linux, Python 3.9+ and Git in the repository are sufficient for checker use; product builds retain their existing protected QA tools.

From the repository root:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py doctor
python3 -B plugins/warlock-contributor/scripts/warlock.py status
python3 -B plugins/warlock-contributor/scripts/warlock.py remaining --summary
python3 -B plugins/warlock-contributor/scripts/warlock.py inspect --requirement ELM-UX-004
```

These commands inspect the repository without adopting the active work. Before implementation, follow `plan` → `preflight --slice-file` → `start --slice-file` below, selecting your own record. Bare `start --owner` resumes the selected `STATE.activeSlice`; use it only when you own that slice. Carry the same global `--record` through the loop. Then use `verify-plan`, implement, `record`, ending loop `check`, `report` and `review`. `self-test` is optional plugin regression testing after package changes, not a prerequisite for every GUI contribution.

## Scaffold and resume

For source entry points and the existing Elm/event/effect route, use the
[implementation map](references/implementation.md). Read only the rows relevant
to the selected behavior; it is not another mandatory full-suite checklist.

`remaining` returns a checklist from the original scenario ledger, including exact
given/when/then text, verification obligations and recorded missing observations.
Use `--requirement ID` to focus on a feature, repeat `--status failed` or other
statuses to filter, or use `--summary` for counts. Use `--markdown` for a readable
checklist and `--limit N --offset N` for bounded pages instead of loading the full
ledger into a planning conversation:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py remaining \
  --requirement ELM-UI-003 --markdown --limit 3
```

If you do not know the requirement IDs, `capabilities` lists exact original
capability names, their requirement IDs and recorded scenario counts. Filter
the checklist by one or more of those capabilities:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py capabilities
python3 -B plugins/warlock-contributor/scripts/warlock.py remaining \
  --capability elm-taskbar --markdown --limit 3
python3 -B plugins/warlock-contributor/scripts/warlock.py inspect \
  --requirement ELM-UI-008 --scenario menu-invocation
```

Repeated capability filters form a union; when requirement filters are also
present, the two sets intersect. Unknown or duplicate names fail instead of
silently returning an empty backlog. `inspect --scenario` narrows the original
and ledger scenario arrays together while retaining the requirement statement,
verification obligations and source pointers. It reports the original scenario
count and omitted count; it does not imply that the entire requirement was
inspected. Every selected requirement must have a matching scenario. Omitting
`--scenario` keeps the complete inspection. Both helpers are read-only and
return the ledger hash without selecting work or revalidating dispositions.

Pages follow ledger order after filtering. They retain total matching counts,
the number of omitted rows and a ledger hash; repeat the same filters and limit
with the reported `nextOffset` (`--offset` in Markdown). Compare hashes before
combining pages because a changed ledger can change their contents. JSON remains
the default, with complete original scenario objects and recorded rows. Markdown
retains given/when/then, verification, missing observations and recorded evidence
scope. An empty page does not mean the release is complete, and recorded accepted
rows never appear as checked boxes. `--summary` cannot be combined with pagination;
`--markdown` cannot be combined with global `--json`.

The default omits recorded
accepted scenarios. Counts describe recorded dispositions, not delivered features;
unadjudicated does not mean unimplemented, and this command does not revalidate
accepted evidence. The original 242/417 inventory is only part of the full release
scope. It never selects work or changes the ledger.

`doctor` checks local package files, manifest identity/version agreement,
plugin-relative skill/hook targets, reminder-hook structure and bounded timeouts,
Python/Git availability and the scratch ignore;
it reports which client executables are on PATH without launching or installing
them. It does not establish client trust, enabled hooks or product-toolchain
readiness. Missing client executables do not prevent direct checker use.

`self-test` explicitly runs the plugin's regression suite using temporary Git
fixtures. It returns a nonzero exit on failure, missing tests, zero discovered
tests or a five-minute timeout, and includes captured test output in its JSON
packet. Use it after changing the plugin or when checking a complete checkout;
ordinary GUI slices do not require it. It runs no product compiler or native GUI
campaign and installs no client plugin. Test fixtures do not modify participant
records, the real Git index or the delivery ledger. Review the repository test
code before executing it, as with any contributed code.

`plan` builds a slice from original IDs and scenarios and includes their unchanged
oracles and verification obligations. It does not choose the next feature, change
`STATE`, claim ownership or run QA. Use `--json` before the command to save the
start-compatible packet in ignored scratch:

```sh
mkdir -p .warlock-contributor
python3 -B plugins/warlock-contributor/scripts/warlock.py --json plan \
  --id launcher-search --requirement ELM-UI-005 --scenario search-no-match \
  --path src/Desktop.elm --path src/SurfaceRenderer.elm \
  --before 'No-match feedback is unreachable from keyboard search' \
  --after 'Keyboard search shows no-match feedback and retains the query' \
  --verify 'Changed Elm compile and replay; owned native keyboard journey' \
  > .warlock-contributor/search-plan.json
python3 -B plugins/warlock-contributor/scripts/warlock.py start \
  --owner your-name --slice-file .warlock-contributor/search-plan.json
```

Choose source paths and before/after behavior from the actual defect; the example
is not a current defect verdict. Save each new plan under a new scratch name so
prior records remain available. A bare slice JSON still works with `start`.

Before creating a record, optionally preview the saved plan:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py preflight \
  --slice-file .warlock-contributor/search-plan.json
```

`preflight` checks the exact selected originals, source paths, prospective record
and its ignore rule. It lists selected dirty files separately from other drafts,
with current hashes, and allows absent source files for new implementation. It
writes no files, takes no ownership and runs no QA. An existing record fails with
guidance to resume it using `handoff` or choose an alternate global `--record`.
Selected dirty files produce an explicit ownership advisory: without a genuine
ownership assertion, `start` protects them as foreign drafts. A successful
preview does not reserve paths; `start` reads current state again.

Before a new record is created, `preflight` and `start` inspect indexed and
legacy participant records under `.warlock-contributor/` for the same exact
original requirement/scenario. `index-participants` freezes the discovered path,
immutable identity and full record-byte digest without editing participant
records. The index is refreshed after successful `start`, `record`, and `extend`
writes. Legacy nested records remain discoverable; new records must be direct
`.json` children. A move is reconciled only when old and new paths have a
one-to-one match on exact indexed record bytes. Identity-only legacy indexes
cannot prove mutable history and fail closed until their provenance is reviewed
and migrated explicitly. Inventory is limited to `.warlock-contributor/`; a
repository-wide census or historical backup review is needed before claiming
that no older participant record existed elsewhere. The 2026-11-01 checkout
census found 101 participant records under that root and no outside-root
signatures in the searched checkout; this is evidence about that checkout, not
all historical clones or backups.
If a prior matching record has reached its two-iteration or 45-minute stop,
preflight reports its path, digest, stop reason and original identity; `start`
refuses a fresh timer. Resume that record or select a different mandatory
scenario. Only a real meaningful-progress entry in that same existing record
clears its current stop; starting a fresh record cannot clear it. A missing,
corrupt, byte-changed, or identity-changed indexed record
blocks new starts because its scenario history cannot be reconstructed. Unrelated malformed
scratch JSON remains a warning after the index exists; before initial indexing,
unreadable JSON prevents claiming a complete inventory. The prior record is
never edited by the index operation. One `.records.lock` serializes all
participant writers, including starts and no-progress observations. This is
cooperative local coordination, not a defense against same-user writers that
ignore the lock.

For an existing checkout, create the ignored path index without rewriting
participant records:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py --json index-participants
```

The index covers participant records under `.warlock-contributor/`. New starts
outside that directory are refused so later starts share one inventoried root.
Do not treat an identity-only index from an older plugin version as verified
history: preserve it, collect old record and backup provenance, and review the
migration before establishing exact-byte bindings.

Both `preflight` and `start` reject a `planSchema=1` packet whose copied original
given/when/then or verification differs from the frozen selection. Regenerate a
plan after changing its selected scenarios. Bare slice files still work because
their originals come directly from the authoritative requirements. This is a
structural preview, not another mandatory gate for every slice.

`handoff` prints the participant owner, source revision/hashes, changes since the
last record, protected foreign paths, latest observation per scenario and its
missing obligations. It highlights stale evidence and no-progress warnings;
it writes nothing and never upgrades acceptance. Use it after compaction or when
another contributor resumes the slice, then read the referenced original ledger
and evidence. Global `--record` selects an alternate saved participant record.

`extend` adds source dependencies discovered while implementing the same selected
behavior. It retains the owner, original requirements/scenarios, start time,
iterations, failed evidence and progress timer. It does not change `STATE` or
select another feature. Declare dependencies before editing them:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py extend \
  --path src/Effects.elm \
  --reason 'The selected behavior needs its existing effect dispatch route'
```

Use an actual new dependency for your slice; duplicate paths fail. For a file
already changed by you, repeat `--adopt-dirty implementation/warlock/EXACT_PATH`
and supply `--ownership-note`. This is an explicit ownership assertion, not a way
to take another contributor's draft. An overwritten protected file still fails,
and unrelated foreign paths stay protected. Paths outside the incremental product
and symlinks are refused. Record writes use the same lock and atomic replacement
as `start`/`record`.

Each extension retains the dependency's current hash (or absence) and the point
in the iteration history where it was added. Declaring an existing file does not
count as a production fix or reset the no-progress timer. Prior claims retain
their original source/evidence hashes and become historical for the expanded
source tuple; a fresh observation must include all declared sources. `handoff`
and `report` expose the extension history. For adopted edits, use
`verify-plan --selected` to consider verification of the newly declared bytes.
Choose a new record for another behavior rather than extending scope indefinitely.

For a source path already declared by the slice but lacking an explicit top-level ownership assertion,
`extend --path EXACT --adopt-dirty EXACT --ownership-note TEXT --reason TEXT`
can explicitly assert ownership of its exact latest recorded bytes (including a dependency extension or iteration binding). Run this separately from new
path extensions. Current bytes must equal the latest applicable source binding and, if the path
is captured as foreign, its protected foreign hash; the command cannot override unexplained drift. It appends an
`ownershipAdoptions` event with the exact source hash and prior/next custody and retains the prior custody in that event without
changing the slice, source baseline, start, iterations or progress. It does not
adopt the separate foreign model merely because that model was reconciled.

### Reviewed changes by a separate foreign owner

`reconcile-foreign` recognizes reviewed changes to paths already captured in
`foreignDirty`. It does not adopt files, edit the participant record, append an
iteration, reset a timer, accept evidence, or permit staging a foreign path.
Unknown new paths and unrelated drift still fail. `handoff` supplies the exact
`recordIdentitySha256` and sidecar location even when a changed foreign path makes
the check red.

Prepare a fresh exact owner census while the participant index is locked:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py --json owner-census
```

This writes a content-addressed ignored snapshot containing the participant
index bytes and every indexed record's exact bytes. It refuses an incomplete or
unindexed participant inventory, including unclassified JSON entries outside
the evidence directory. Prepare an untracked Git-ignored
`.warlock-contributor/` scratch JSON array containing one entry per changed foreign
path, with exactly `path`, `sourceRecordPath`, `ownerCensusSnapshot`,
`sourceRecordSnapshot`, `reviewFile`, and a nonempty `reason`. Include all
currently changed protected paths in one atomic batch;
partial batches do not write anything. Snapshot a genuinely owning participant
record under `.warlock-contributor/evidence/foreign-reconciliation-snapshots/`;
it must declare ownership and bind the new hash in its latest applicable source snapshot (base, chronological extensions and iterations). Historical claims or earlier source hashes cannot authorize a new transition. Retain an independent JSON review
under `.warlock-contributor/evidence/foreign-reconciliations/`, naming:

- `schema: 1`, `scope: "foreign-provenance-only"`, `scenarioAcceptance: false`,
  and `independent: true`;
- the exact `recordIdentitySha256`, `recordPath`, `path`, `previousSha256`,
  `currentSha256`, `sourceRecordPath`, `ownerCensusSnapshot`,
  `ownerCensusSnapshotSha256`, `sourceRecordSnapshot`,
  `sourceRecordSnapshotSha256`, `sourceOwner`, `reason`, and a `reviewer`
  distinct from both owners.

These are local reviewed provenance assertions, not authenticated identity or
product acceptance. Do not fabricate the owner snapshot or independent review.
Then invoke the reviewed repository copy:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py \
  --record .warlock-contributor/selected.json reconcile-foreign \
  --transition-file .warlock-contributor/transitions.json
```

The command takes the participant lock and atomically appends a hash-chained
sidecar. New event-schema-2 entries bind the source snapshot bytes to one exact
path and identity in the frozen, digest-checked participant index; the census
must still match the complete current inventory when the batch is appended.
Every selected/adopted path spelling in the census must be canonical, and any
stale or competing record claim makes ownership ambiguous and fails closed.
Earlier schema-1 events remain readable as legacy provenance and are not
retroactively upgraded to this stronger proof. Its lookup uses immutable participant fields; its full review identity
still binds the captured foreign/adopted custody. A retained custody baseline and
exact extension prefix must match current custody after replaying only explicitly
appended extension adoptions. Thus a later unrelated adoption keeps prior history
reachable, while arbitrary custody edits still fail closed. All historical snapshot/review hashes remain checked; only the latest
reviewed hash per path is compared with current bytes. A subsequent owner change
requires a new exact transition/review and retains the earlier event. Changing a
participant's identity or corrupting retained evidence fails closed. The original
`foreignDirty` pins, selected ownership, claims and STOP history remain intact.


`claim` prints a record-compatible observation packet with the selected original
oracle, verification obligations, current hashes for every declared source and
SHA-256 hashes of real evidence files. Supply the actual evidence scope,
disposition and missing observations. The observer is the participant owner;
this helper cannot scaffold `accepted` or appoint an independent reviewer.
It reads files without interpreting the evidence, running QA or changing records
and the ledger. For example, after producing a real component report:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py --json claim \
  --requirement ELM-UI-005 --scenario search-no-match \
  --evidence implementation/warlock/qa/evidence/your-report.json \
  --scope 'Observed typed replay only' --disposition partial \
  --missing 'Native keyboard, physical presentation and applicable AT remain open' \
  > .warlock-contributor/search-claim.json
python3 -B plugins/warlock-contributor/scripts/warlock.py record \
  --outcome scenario-verdict --summary 'Describe the actual observation' \
  --claim-file .warlock-contributor/search-claim.json
```

Use the requirement/scenario from your own selected slice and replace the example
evidence path with the report you actually produced. `record` rechecks the packet
against the originals and current evidence/source hashes; editing an oracle or
changing a report after scaffolding fails. Existing bare claim arrays remain
supported. Partial and blocked observations require `--missing`; acceptance needs
the separate external review and source tuple described in the contract.

For an externally reviewed `accepted` claim, `sourceTuple.sourceRevision` must
be the full commit hash containing every source in `sourceHashes`. The checker
compares each hash with its regular Git file blob without checking out files or
changing the index. A branch, `HEAD`, abbreviated hash, absent file, symlink or
older commit with different bytes fails. Staging a draft alone is insufficient;
retain a partial observation until the tested source is committed and reviewed.
The independent reviewer's disposition must also be `accepted`, with no missing
observations and retained evidence. Historical observations keep their original
commit and remain explicitly noncurrent after relevant source changes. This
does not verify evidence contents, reviewer honesty, native/AT behavior or the
actual core/plugin/toolchain tuple.

`start` uses `STATE.activeSlice`; it does not select the next feature. The default local record is `.warlock-contributor/slice.json`; Git must ignore `.warlock-contributor/` before `start` (this repository supplies the ignore). On a new development checkout add that narrow ignore. New `--record` paths must be direct `.json` children such as `.warlock-contributor/worker.json`; indexed legacy nested records can still be resumed. Run `index-participants` once to inventory the existing paths before beginning work. Record updates are serialized with a POSIX lock and written atomically. Global `--repo`, `--record`, and `--json` precede the subcommand. For resumed own drafts, explicitly list each declared dirty path with repeatable `start --adopt-dirty <path>` and supply `--ownership-note`; undeclared and unadopted foreign drafts stay protected. See `--help` and [contract.json](references/contract.json). Zero exit means structural compliance; 1 is a structural policy violation and 2 invalid/unavailable inputs. Explicit loop checks and repository contributor instructions remain required even when no host hook runs.

## Choose proportional verification

`verify-plan` suggests existing protected checks for declared source changes since
this participant's last record. It prints runner hashes, argument arrays and
quoted commands, keeping compilation and serial native candidates separate.
No changed source means no default rerun. Use `verify-plan --selected` to plan
before editing. Global `--record` carries through to suggested native commands.

The map covers existing feedback, search, persistent catalog pins (ELM-UX-004), Task View, popup and owning-core
routes. A SeatManager change suggests the single-unit core build followed by the
owning-header authority build. Unmapped product files and supporting changes stay
explicit so a contributor can choose their proportional checks. Missing runners
have no executable command; a missing protected launcher requires a reviewed
local equivalent. Inspect the runner, arguments, source tuple and prerequisites
before using a suggestion. This command executes nothing; candidate native modes
are not complete original-scenario coverage. AT/IME, hardware and other original
verification obligations remain in the observation packet.

For ELM-UX-006/`ux-006`, the affected preview presenter, projection and taskbar
sources suggest `check-search.py --preview-states`. The plan uses the repository's
`window-integration-qa/qa_run.py` and supplies that directory on `PYTHONPATH` for
the current protected launcher imports. The original isolated native recording
remains a separate required observation; `unplannedOriginalObservations` names
it explicitly, and the planner does not suggest the historical native wrapper.
A passing CPU replay is not UX-006 or release acceptance.

Handwritten surface adapters, `shell.css`, `SurfaceController.elm` and `Popup.elm`
use the shell/view routes. UI-008 `overflow-first-last` suggests the existing
`--dense-taskbar` modes; `overflow-resize` suggests `--popup-reflow`, including
changed host/surface units. Shared targets retain all triggering source paths
without duplicate runs. Menu invocation suggests `--pinned-menus`.
Preview transport changes remain explicit unmapped product
work so the contributor can inspect their authority/lifecycle obligations.

Always-on-top/MAX (ELM-UX-016) is not mapped by `verify-plan`. Taskbar application pins, running-pin context menus and always-on-top are distinct behaviors. For UX-016, explicitly choose `qa/check-search.py --pin-max` through the protected CPU launcher and `qa/native-pin-max.py` with no arguments through `loop.py native`; inspect their prerequisites and exact core/plugin pair first. A suggestion or a passing compile does not complete the original native overlap/hit-target scenario.

## Design language contributions

The [design contribution guide](../../DesignLanguage/CONTRIBUTING.md) and [current browser catalog entrance](../../DesignLanguage/catalog/index.html) explain how the plugin supports product design and documentation. Apply the three token tiers, stable preview/control geometry, observed checked semantics, non-color cues and explicit focus/announcement ownership in the runnable product. Current inset-focus, provisional palette and effects-off/transparency gaps remain implementation work; preserve the voted EARS rather than rewriting them to match defects.

Catalog v6 is a frozen earlier closure, not current product coverage. Update current guidance or a fresh specimen after implementing the behavior. Independent documentation/catalog work uses `check --project-only` and proportional link/browser checks. Product design changes retain the original scenario slice and protected native obligations. Neither catalog checks nor this plugin can close a native gate.

Checks and delivery packets also include `progress`: consecutive iterations
without meaningful progress, elapsed seconds since the recorded baseline, trigger
reasons and an explicit next action. At two iterations or 45 minutes, end expansion
of that investigation and select another bounded mandatory slice. This remains an
advisory about contributor records; it does not measure feature delivery or block
independent work on other scenarios. Cross-record start continuity and the
participant index prevent hiding the trigger by creating another record for the
same exact original scenario. The
required loop checks expose these fields on every continuation.

New iterations use progress policy 6: each original requirement/scenario/disposition
counts once across the record. Rewording scope or missing observations, changing
the observer, regenerating reports, or alternating previously recorded
dispositions does not restart the timer. Actual authored source changes still
count through `production-fix`. Historical policies 1–5 keep their original
interpretation; a new iteration compares its disposition against all prior
observations. These checks detect record consistency, not whether a new verdict
is true. Retain real source/evidence hashes and review the original oracle.

## Local development and installation

Claude Code can load the source directly without installing:

```sh
claude --plugin-dir ./plugins/warlock-contributor
claude plugin validate ./plugins/warlock-contributor
```

For a reviewed marketplace installation, use `/plugin marketplace add .` and `/plugin install warlock-contributor@warlock` in Claude Code.

Invoke `/warlock-contributor:warlock-contribute`. Grok reads Claude-compatible plugins and skills; use its documented local install command after reviewing the package:

```sh
grok plugin validate ./plugins/warlock-contributor
grok plugin install ./plugins/warlock-contributor
```

Use `/skills` to inspect/invoke `warlock-contribute`, and `/hooks` to inspect loaded hooks. Do not bypass trust. Local install is a user configuration change; these instructions do not perform it.

Codex uses `.codex-plugin/plugin.json` and shared `skills/`. This repository includes `.agents/plugins/marketplace.json`, exposing `./plugins/warlock-contributor`. Register the repository marketplace with `codex plugin marketplace add .`, then install through the desktop Plugins Directory. The official packaging page documents marketplace shape and cache refresh. This repository's contributor instructions also permit reading the skill and invoking the CLI directly without installation. No fabricated Codex validate command or universal CLI hook activation is assumed.

Installed plugins may be cached copies; prefer the repository checker with explicit `--repo` for contributions. A cached checker whose bytes differ from the repository checker reports an error; refresh the installed package and inspect its skill/manifest before use. Merely seeing this source folder does not prove it is enabled. No installation, trust decision, global configuration change, remote service, secret or new dependency is performed by checker commands.

## Hook scope and limits

Claude's default `hooks/hooks.json` and Codex's explicit `hooks/codex.json` run a read-only checker at SessionStart (including resume/compaction when supplied by the host) and UserPromptSubmit. They add a concise reminder at session start or when a prompt check needs attention for recognized Warlock repositories. They never block prompts/tools/Stop or write contribution records; correction loops and unrelated work remain usable. The checker subprocess has a five-second timeout inside a ten-second host hook; both are advisory, so explicit checks must still run. They do not inspect transcripts or execute builds.

Grok uses the Claude-compatible manifest but has different semantics: passive event stdout is ignored. The adapter detects Grok's documented environment and returns immediately; its passive hook cannot deliver context. Explicit loop calls still run the checker. The shared skill and mandatory repository loop carry the instruction to call it. There is no Grok blocking tool hook.

Codex bundled hooks require manual desktop installation and review/trust of the current hook definitions; enabled is not trusted. Support on other Codex surfaces must be verified, and hooks are not eligible for the public directory. Cross-client discovery/validation does not prove live hook execution or GUI acceptance.

## Verified host contracts

Checked October 7, 2026 against primary documentation and installed CLI help:

- [OpenAI packaging](https://developers.openai.com/plugins/build/plugins): compatibility manifest, relative skill/hook paths, manually installed desktop hooks and plugin-root variables.
- [Codex hooks](https://learn.chatgpt.com/docs/hooks): SessionStart/UserPromptSubmit JSON additional context and trust rules.
- [Claude plugin reference](https://code.claude.com/docs/en/plugins-reference) and [hooks reference](https://code.claude.com/docs/en/hooks): default hook discovery, plugin paths and lifecycle context.
- [Grok plugins](https://docs.x.ai/build/features/skills-plugins-marketplaces) and [hooks](https://docs.x.ai/build/features/hooks): Claude compatibility, camelCase event input, GROK environment and passive stdout limitation.

See [the six-agent review and dispositions](../../docs/warlock-workflow-review/contributor-plugin-20261007/consensus.md), [the implementation skill](skills/warlock-contribute/SKILL.md) and [protected execution](references/workflow.md) for contributor work. Host manifests describe loading only; the v2 delivery contract and original EARS/OpenSpecs determine the product work.

## Review a contribution

After staging an explicitly owned contribution, `review` combines the participant
handoff with a read-only check of staged contents. Declared source and recorded
evidence are in scope; use repeatable `--include REPO_FILE` for owned supporting
documentation or other support files. Explicit includes cannot override protected
foreign drafts or permit archival implementation changes. All staged files must
be resolved regular files whose bytes match the working copy. This catches a
partially staged source or a report edited after staging. It neither stages nor
commits files, runs checks, pushes, nor establishes ownership or oracle truth.
An empty index produces an advisory; missing records and mismatches fail.

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py review \
  --include docs/your-owned-observation.md
```

Policy 6 counts selected Elm/Haskell source in the existing product roots and
Haskell `.hs`/`.hsc` files under `haskell/<package>/src/`. Test, formal, build,
generated and documentation subdirectories do not count. Cabal files, QA, models
and generated output remain support evidence. Historical policies 1–5 retain
exact validation and saved progress flags; there is no record migration or
retroactive timer reset. A source delta remains a self-attestation, not scenario,
native or release acceptance.

## What is enforced

The v2 product-loop wrapper requires a participant record before and after native execution; session hooks remain advisory. For explicitly requested documentation/plugin/support work, run the shared `check --project-only` directly before and after without inventing a GUI slice. The [CI template](references/warlock-contributions.yml) runs recordless `--json check` on a clean checkout and compares PR changes against the base revision; ignored local ownership records are not available to CI. Copy it to `.github/workflows/warlock-contributions.yml` to activate GitHub Actions when the publishing credential has `workflow` permission. The existing GitHub credential lacks that permission, so this package publishes the reviewed template rather than claiming live CI.

Local records are self-attested, not a tamper-proof audit or proof of independent review. The checker detects contradictions and stale/current evidence but cannot tell whether changed code improves behavior, whether a reviewer is honest, or whether pixels/AT match the original oracle. Work in separate Git worktrees when concurrent ownership is unclear. Record reports must describe observable behavior and unresolved obligations.

## Prepare a delivery note

`report` produces a read-only packet from the selected participant record. Use
`--markdown` for a status update or pull-request body, or global `--json` for tools.
It includes the before/after intention, latest recorded result, selected source
changes, uncommitted paths, exact original oracles and verification obligations,
recorded evidence scope/hashes and missing observations. Planned verification is
labeled as planned; an intended result is never rendered as an observed result.

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py report --markdown
```

Read the evidence before publishing the note and edit the prose for the actual
contribution. The command does not post, commit, run QA, update the ledger or
establish acceptance. Source HEAD is accompanied by uncommitted path information;
a draft is not represented as a tested commit. Missing records fail. Stale evidence
returns a nonzero exit and retains the structural findings in the note. Historical
claims remain visible with their hashes marked noncurrent. `--markdown` and
`--json` are mutually exclusive. Use `review` separately for staged contents.


### Reconciliation filesystem boundary

Reads walk directory descriptors with `O_NOFOLLOW`; JSON and its digest come from
one regular-file descriptor, and detected in-place changes refuse the read.
Participant locks/reads and atomic writes use directory-relative operations.
Reconciliation holds the sidecar parent from reading its prior state through
validation and replacement, checking the prior sidecar digest before commit.
Creating an absent sidecar never overwrites a concurrently created entry.
A concurrent ancestor-to-symlink swap cannot redirect a read or replacement into
that symlink's target. If an already-open owned directory is renamed, the write
remains confined to that held directory object; a later check refuses the now
redirected pathname. This is object-bound I/O, not an immutable checkout or an
OS security boundary against a same-user process that independently overwrites
files or ignores advisory locks. Source/evidence hashes must still be rechecked
at the actual consuming gate; reconciliation never authorizes a native action.


Existing-sidecar concurrency limit: the prior digest comparison and subsequent
`renameat` replacement are separate kernel operations, not atomic compare-and-swap.
A same-user writer ignoring the participant lock can replace that final directory
entry between them; descriptor anchoring prevents pathname escape but cannot
preserve that competing version automatically. Treat this as a residual blocker
for any stronger claim of conflict-safe integration against uncooperative writers.
The current draft is not a secure integration certificate. An immutable,
no-replace generation protocol would be a separate reviewed change if that stronger
conflict contract is required; no silent weakening or automatic retry is permitted.


### Bootstrap with retained negative QA fixtures

An existing checkout may contain deliberately malformed storage fixtures, raw
symlinks, captured CLI output or handoff packets under `.warlock-contributor/`.
Keep their original paths and bytes. Initial indexing still refuses unknown or
ambiguous history; do not create an empty index or convert failures to warnings.

For independently audited **nonparticipant evidence only**, the fixed ignored
`.warlock-contributor/participant-bootstrap-classifications.json` can name exact
paths and fingerprints. Its schema has `schema: 1`, distinct `owner` and
`reviewer`, an `entries` object and a hash-bound `review` reference. Each entry
has `kind` (`file` or `symlink`), `fingerprint`, `reason` and `producer`. File
fingerprints are SHA-256 of exact bytes; link fingerprints are `symlink:` plus
SHA-256 of the raw link target, without dereferencing it. The independent review
binds the canonical schema/owner/reviewer/entries payload and explicitly uses
`scope: participant-inventory-bootstrap-only`, `scenarioAcceptance: false`,
`independent: true` and `disposition: accepted`. See the executable examples in
[`qa/test_bootstrap_classifications.py`](qa/test_bootstrap_classifications.py).

Genuine participants, possible history containing `startedUTC` or `iterations`,
indexed paths and control files cannot be excluded. Unknown corruption, changed
fixture fingerprints and missing or changed reviews still fail closed. The
resulting index binds the exact manifest bytes in its digest. This classifies
provenance; it neither adopts source drafts nor resets progress or accepts EARS.
Use `--json` and save command output beneath `.warlock-contributor/evidence/`
so captured status text is not confused with another participant record.
