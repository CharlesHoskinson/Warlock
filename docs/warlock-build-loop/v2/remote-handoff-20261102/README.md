# Remote development handoff — November 2, 2026

This publication preserves the current working implementation and unfinished work. It is not native GUI or release acceptance. The accepted ledger remains **19/242 requirements and 42/417 scenarios**, tied to its historical source tuples. All original requirements, scenarios, deadlines and failed evidence remain.

## Current source

The committed working tree includes the beta Elm interface, state-derived subscriptions and scoped preview paint handling; website work; contributor ownership tooling; and Graphify/GPU navigation helpers. Runtime custody fixes were previously published in `6e6ad828c2ec5b86935fee918d9af72522039047`.

`UiHttp.elm` is still the original `a41b32a054031bf5f99cc920450cffe01ad82362729a4af1450b05aa99507172` version. The reviewed `sol-uihttp-effects-0535.patch` is archived, not applied. The runtime actors/retained-image issuance proposals are also drafts: do not assume the published backend uses the proposed persistent route.

## Verification

- Current MVP: six production roots and three official HTML documents compile; HTTP and feedback replays pass; all **639 standalone assertions pass**. See `verification/mvp-passed/`.
- Subscription component: all eight production roots and four debug workers compile. Its last runtime run fails `HttpBar must render sticky unconfirmed-delivery alert`. A source-reviewed QA text correction is archived as `elm-tests-tea004-stopped-alert-0650.patch`; it is not applied. Full HTTP wrapper model/effect descriptions and SiteMain inventory remain outstanding before whole ELM-TEA-004 acceptance.
- Workflow self-test: the first run failed two of 300 tests. Two fixture corrections were applied without changing production guards. The fresh protected rerun passed registry admission and the complete plugin suite. See `verification/workflow-repaired/`; the failed run remains in `verification/workflow-first-failed/`.
- The new GUI has **not** received a fresh Omarchy trial. The old guest binaries are stale. A future trial must rebuild from the immutable qualified Haskell tuple (223 inputs at `6e6ad828c`) plus matching current GUI artifacts, retain the original 28-second deadline, preserve the desktop, and report missing retired-cgroup inventory as unconfirmed cleanup.

## All unfinished engineering work

`engineering-work.tar.gz` contains the engineering source proposals, patch histories, Quint models, QA fixtures, research, provenance, and original participant records. `manifest.json` gives every included file's original relative path, byte count and SHA-256, plus the archive SHA-256 and exclusions.

Inspect it without overwriting a local checkout:

```sh
mkdir -p /tmp/warlock-remote-work
tar -xzf docs/warlock-build-loop/v2/remote-handoff-20261102/engineering-work.tar.gz -C /tmp/warlock-remote-work
ls /tmp/warlock-remote-work/.warlock-contributor/engine-pid1-drafts
```

Apply only the chosen patch after checking its documented preimages; do not bulk-apply incompatible successors. For example, the archive holds multiple versions of runtime custody proposals. Original contributor records and index snapshots preserve their start times and stop histories. Their host-local claims, foreign-source reconciliations and bootstrap classifications are not a fresh remote readiness certificate. Never reset the records or invent acceptance to resolve a tooling failure.

Private keys, passwords, live authentication state, model conversation transcripts, runtime broker inboxes and disposable caches are not published. The manifest records engineering candidates excluded from the archive. AgentBus credentials and machine-local SDK/model caches must be provisioned on the remote environment rather than copied through Git.

## Why the loop stalled

The goal was reported blocked at **07:10:09 UTC**. The last bounded worker logs ended by **07:20:27 UTC**; no workers were live at the 14:25 census. AgentBus health now passes all six checks, so no external service outage has been established.

The continuation checkpoint still claimed an active run after its test report had already failed. The launchers bounded individual turns, while the installed watchdog watched memory rather than useful work or goal liveness. There was no independent lead-wake mechanism to replace the manual resumption loop. Repairable internal test failures and ownership bookkeeping were left as a blocked goal instead of being resolved or handed off promptly.

The two failing workflow fixtures are now repaired and verified. Sanitized forensic findings, worker terminal receipts and a seven-test continuity-probe proposal are preserved under `engine-pid1-drafts/stall-forensics-20261102/` in the archive. **That probe is not installed and does not automatically resume a lead.** It must not be described as a functioning overnight supervisor. Recovery needs a singleton coordinator, explicit current run state, terminal-result-aware checkpoints and an actual independent lead-wake route; it must preserve authentication, ownership and QA gates.

## Next concrete work

1. Complete the UiHttp typed effect transition and exact full HTTP wrapper fixtures using the reviewed archived packets.
2. Finish the subscription runtime replay and retain both old failures and new source-bound results.
3. Rebuild the matching runtime and exercise the current GUI on Omarchy; inspect screenshots and real inputs.
4. Install and verify durable liveness supervision before arming another unattended run. Do not restart the local team simply because this handoff was cloned.
