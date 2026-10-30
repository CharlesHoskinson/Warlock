# Build and runtime reference

Command review: October 30, 2026. Paths below are lookup facts, not a complete installation procedure. The candidate is not installed in the main Omarchy session.

| Item | Location / contract |
| --- | --- |
| Active product candidate | `implementation/warlock/` |
| Elm application | `implementation/warlock/elm.json`; pins `elm-version` 0.19.2 and existing package versions |
| Policy and coordination | `src/Main.elm`, `Desktop.elm`, `Shell.elm`, `OutputController.elm` and domain modules |
| Presentation roots | Bar/Popup and their rendering/protocol modules; inspect current imports before changing ownership |
| Native host integration | `native/shared-host.c` currently includes `native/host.c`; native mechanisms preserve scoped authority |
| Native/backend services | `adapter/` and native authority/plugin sources; exact recorded core/plugin/Aquamarine pair required |
| Static assets | `assets/`; generated Elm bytes and hand-written adapters have separate provenance |
| Packaging recipe | `adapter/release_builder.py`, `adapter/release_tuple.py`, [release instructions](../../../implementation/warlock/RELEASE.md) |
| Offline component profile | `adapter/recovery_profile.py`, [recovery contract](../../../implementation/warlock/RECOVERY.md) |
| Protected launchers | `window-integration-qa/qa_run.py`, `qa_launch.py`, and `docs/warlock-build-loop/v2/loop.py` |
| Original identities / dispositions | `docs/elm-roadmap/requirements.json` / `docs/warlock-build-loop/v2/requirement-ledger.json` |

## Offline contributor command lookup

From the repository root, these inspect rather than adopt the active slice:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py status
python3 -B plugins/warlock-contributor/scripts/warlock.py capabilities
python3 -B plugins/warlock-contributor/scripts/warlock.py remaining --summary
python3 -B plugins/warlock-contributor/scripts/warlock.py inspect   --requirement ELM-UI-020 --scenario first-use
```

For explicitly requested documentation/support changes, use `check --project-only` before and after. A structural pass is not evidence of product readiness. See the [plugin reference](../../../plugins/warlock-contributor/README.md) for exact planning, record and staged-review options.

## Current development host

The shared checkout is `/home/charles/Warlock`; the CPU protected launcher is `/home/charles/Warlock/window-integration-qa/qa_run.py`. Native artifact paths, compiler/package caches and private reports also depend on the development host. `warlock-ctx` indexes a selected source graph outside Git and uses RTX5080 CUDA embeddings; CPU AST/lexical/inferred graph results remain navigation only. Missing that local tool is not missing product implementation.

Web browsing/downloads use verified Scrapling 0.5 with fetchers/rag; `scrapling` and `scrapling-mcp` are installed on this host. Preserve existing primary downloads without unnecessary refetch. No `elm-test` installation or product test dependency is implied: current `elm.json` test-dependencies are empty, and selected production replay harnesses have their own pinned tools.

## Builds, installation and recovery limits

There is no documented one-command ready user installation. Build/capture/verify routines invoke compilers and require reviewed protected execution, local caches, exact consumed inputs and original ABI identity. Source changes can invalidate a lock or the relevance of a retained object; never rebaseline silently. Compliance/provenance and independent reproducibility gates remain separate.

Profile preparation can snapshot selected compatible preference stores and validate command descriptors. It does not demonstrate working full GUI rollback, recover arbitrary unsaved application drafts or repair a failed compositor. The actual managed-profile native trial fails early; direct first-use and renderer failures also remain. Treat `RELEASE.md` and `RECOVERY.md` commands as contracts with explicit readiness prerequisites, not permission to activate the user's session. See [current evidence status](status-and-evidence.md).


## Participant records and exit status

The CLI's global options precede the subcommand: `--repo`, `--record` and `--json`. `status`, `inspect`, `remaining`, `handoff`, `report` and `verify-plan` read data; they do not adopt work or execute the suggested QA. `plan` prints a proposal; `start`, `extend` and `record` write participant state and require actual ownership. `review` reads the existing staged bytes; it neither stages nor publishes them.

Both the contributor CLI and loop wrapper default to `.warlock-contributor/slice.json`. That file can be a stale historical record. `STATE.activeSlice` is the coordinator selection, while an explicit participant record can carry a selected-slice override. Ask for the actual owned participant path instead of guessing it from a default or changing historical state to make a command green. For a coordinator-provided path, replace `ACTUAL_RECORD.json` below:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py --repo "$PWD" \
  --record .warlock-contributor/ACTUAL_RECORD.json --json handoff
python3 -B docs/warlock-build-loop/v2/loop.py \
  --record .warlock-contributor/ACTUAL_RECORD.json check
```

`handoff` includes its effective `slice`, owner, source hashes, foreign paths, latest actual observation and progress warning. A structural `ok:true` with a stop warning still requires ending expansion of that investigation. A nonzero default `status` or `check` is not, by itself, proof that the explicit current record failed. Read its errors and use the intended record; preserve any genuine failure. Never use `start` to overwrite a record or turn a documentation task into source ownership.

For an explicitly requested documentation-only change, run the actual project check before and after:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py --repo "$PWD" \
  check --project-only
```

A no-participant warning is expected in that mode; `ok:true` checks repository structure only. It is not a product/native/AT or evidence-truth verdict. See [the first tutorial](../tutorials/first-contribution.md) for a runnable original-scenario inspection and [reading evidence](../how-to/read-recorded-evidence.md) for byte checks that execute no archived runner.
