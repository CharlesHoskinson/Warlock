The day produced internal preview-control machinery and a still-invisible curtain. Ninety commits recopied trees and evidence. No original EARS ID was closed. The empty completion list is stale bookkeeping, and it is also not a license to keep minting CONTROL contracts.

## Findings

**1. Critical path was replaced by a self-extending control contract.** Original work is a usable shell: taskbar, focus, minimize, restore, pin, snap (`docs/HANDOFF.md` outcome; `ELM-UX-006` through `ELM-UX-008`, `ELM-ARC-018`, `ELM-KDE-004`). `docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.md` puts W07 focus first, then transport liveness, then W03 and all 13 S09 preview scenarios. The 24-hour titles are retirement polling, control tickets, admission quotas, URI epochs, realm identity, then renderer drain. `OUTGOING-CONTROL-CONTRACT.md` adds CONTROL-001 through CONTROL-006, which are not among the 242 original IDs, and then says staged qualification does not close the release gate. `docs/warlock-preview/v93/HANDOFF.md` (62,795 bytes) is a chain of "next PUBLIC, then fresh GUI, no acceptance follows." `NATIVE-ADMISSION-CONTROLS.md` is another 72,717 bytes. The loop instructions cause this: `BUILD-LOOP.md` steps 6–7 and the completion gate, and `docs/warlock-build-loop/v1/INSTRUCTIONS.md` lines 5–7 and 26, forbid closing a requirement without full-release evidence and order an immediate advance to the next unmet slice. The agent answers by inventing the next unmet internal prerequisite.

**2. Commit volume is copy amplification.** `inputs/git-24h.json` lists 90 commits from `8b9c5938` (2026-10-06 15:49 -06) through `261addb0` (2026-10-07 15:06 -06). Forty-five are "Qualify…" and forty-five are "Record public…". Counted `pathCounts`: 14,780 product-source path appearances and 198,515 QA path appearances. The file's own warning says these are repeated archival copies, not features. `source-deltas-94-143.json` records the real edits for provider v94–v143: 233 changed paths, about five files a version. That is roughly a 63× product-path multiplier. Elm `src/` edits stop at v122 (24 paths, v113–v122). v141 changes only `controlled-preview-host.h`. v142 adds a QA process-stop flag in `shared-host.c` and that header. v143 changes `host.c`, `shared-host.c`, and the header so a known renderer failure drains before `gtk_main_quit`. Each of those slices was still published as hundreds of product files plus thousands of QA files. Paired `*-test.cpp` / `*-test-v2.cpp` fixtures land in the same version and double the review surface again.

**3. The last two publications did not change production C or Elm.** `b341185b` "Qualify durable window commands across native restart" is 0 product files, 400 QA, 16 docs, 326 other. `45242221` "Qualify combined preview retirement and durable window restart" is 0 product files, 556 QA, 36 docs, 284 other. Each has a record-public twin with 1 QA file and 6 docs. `component-report-combined-restart-204-207.json` says "No production source changed" and reverifies the same 119-command build. `component-report-gui143-shared-process-drain.json` and `component-report-window-restart-198-201.json` also record `fullBuildCommands: 119`. Three full rebuilds, one of them with no product diff. Reports cite a second copy axis, `warlock-client-provider-native-v187` through `v207`.

**4. The user-visible preview is still off, on purpose.** In v143, `controlled_curtain()` sets the popup widget opacity to 0.0, and the comment says nothing in that route raises opacity from decoder or animation-frame acceptance (`controlled-preview-host.h`). `preview_client.hpp` requires `previewEligible` false for the native492 probe. `shared-host.c` prints `previewEligible=0`. The combined report leaves `physicalRevealQualified`, `hardwarePresentationQualified`, `originalRestoreTimingQualified`, `popupDismissalFocusRestorationQualified`, `nativeAcceptance`, and `fullReleaseAccepted` false. Installed desktop and drafts were preserved. That preservation is correct. Calling the drain work a GUI release is not.

**5. "Zero EARS completed" is an unread ledger, not a measurement.** `requirements.json` has 242 IDs, top status "proposed; implementation acceptance pending", and no status value `accepted`, `partial`, `complete`, or `satisfied`. `implementation-status.json` has `completedRequirementIds: []`, but `loop-state.json` is the old lane: `observedUTC` 2026-10-05, slice `elm-recovery-delivery-general-reviewed-v656`. That file also records bounded passes (modal keyboard delivery, WebGL readback, minimize experiments) with `nativeAcceptance: false` and `featureAccepted: false`. Those passes are not original closures, and the empty array does not prove the behaviors were never met. Nobody wrote a scope-tagged closure against the original IDs. Component and browser evidence must stay labeled as such.

**6. Token telemetry for this day is not established.** `INDEX.md` says about 7.9 million tokens and 22.5 hours cumulative for the host goal, and that no 24-hour token ledger exists. A search of the packet and `docs/` found no independent counter. Do not bill the day at 7.9 million. The measured waste is the copies, the 119-command rebuilds, the 63 KB handoff every successor must read, and this packet (`git-24h.json` 1,299,314 bytes, `source-deltas-94-143.json` 1,354,836 bytes). Another standing review panel would repeat that cost. The five-reviewer FRP pass already produced advice and did not compile or ship.

## Measured facts and uncertainties

Facts above are counted from `git-24h.json` `pathCounts`, the 233 `path` entries in the v94–v143 delta packet, the three v93 component reports, v143 curtain and eligibility source, and `requirements.json` statuses. Uncertainties: unique blob sizes versus path appearances, whether paired fixtures are byte-identical, how many provider directories exist on disk beyond the commits, and any token total. I did not rerun builds or native campaigns.

## Stop, start, retain

Stop minting `warlock-preview-provider-vN+1` and `warlock-client-provider-native-vN` for a one-file change. v143 is the only writable product tree. Stop the qualify/record-public commit pair. Stop 119-command rebuilds when the delta is one header. Stop appending CONTROL, GUI, or PUBLIC chapters. Stop reading the whole v93 handoff, both loop docs, the FRP plan, and the OpenSpec tree at the start of every slice. Stop default multi-model review panels. No new skill or plugin: a skill that adds a required read or a reviewer makes this failure worse.

Start one live tree and content-addressed evidence. Frozen trees and failed reports stay where they are. New manifests point at existing SHA-256 values. Do not rewrite, move, or "compact" held evidence.

Retain ABI pairing, `qa_run.py` protections, the native lock, original deadlines, serial native campaigns, draft and main-desktop preservation, failed-attempt retention, and one Elm policy. `BUILD-LOOP.md` lines 67–72 and `AGENTS.md` stay in force.

## Operating rules

WIP is one original scenario cluster on one code path. A slice is illegal if it does not name an original ID and the `then` clause it will observe.

Diff budget: commit only files whose bytes changed, plus one evidence manifest. Reject the commit when product path count exceeds twice the number of files actually edited. QA additions are the new report and the manifest. Reusing an old report is a hash reference.

Validation escalates. Compile the changed translation units and relink. Run the one oracle for that scenario. Run a native campaign only when the `then` clause needs pixels, hit-testing, or Wayland. Quint only for a reducer this slice edited. The full 119-command build runs only when the shared ABI those commands cover actually changed.

Integration: no second policy model, no second provider tree, no publication until the scenario oracle has been recorded. A busy native lock means stop, not "invent a CPU-only CONTROL slice."

Closure: an original ID may close at a named scope when its own scenarios have evidence on one source/ABI tuple. Scopes are `component`, `integrated-host`, and `release`. A component close does not close the release. A new internal invariant cannot reopen a closed scenario or become the next slice unless that scenario fails without it.

Reporting, every slice, half a page: original IDs, observed behavior, source commit, oracle path and hash, what is still open, next file to edit. Check counts, blob counts, and "PUBLIC" numbers are not progress. If token telemetry is absent, write "unavailable".

Cost stop: two slices with no original `then` clause observed, or one slice whose evidence bytes exceed five times the source diff, blocks the goal. Record the missing observation and wait. Do not open a substitute primitive.

Context for a slice is `AGENTS.md` through the launcher rule, the one requirement object, the current manifest pointer, and the files about to be edited.

## First three slices

All three edit v143 only. They leave `controlled_curtain()` at opacity 0 and leave the native492 `previewEligible=false` probe alone. They do not rerun native v187–v207.

1. `ELM-UX-006`, `ELM-UX-007`, and `ELM-KDE-004` (`kde-live-source-exclusion`). In `src/Taskbar.elm` and `src/SurfaceRenderer.elm`, a minimized window keeps its taskbar identity and shows a historical preview label, or the icon and title when no retained frame exists. The live minimized surface stays out of ordinary hit-testing. The WebKit popup stays at opacity 0. Oracle: one Elm replay for the historical-versus-fallback label, plus one private native hit check that the live source is absent and the thumbnail identity is separate. Original two-second deadline unchanged.

2. `ELM-UX-008` (`ux-008` is the selection route; the requirement text is the restore route). Taskbar selection of a minimized incarnation sends native activate/restore and does not send it to a scratchpad. Oracle: one native request receipt, scratchpad membership unchanged, deadline unchanged. Use the existing minimize/restore receipt path. Do not open a new lifecycle derivative.

3. `ELM-ARC-018` (`architecture-018`). One click on a visible region while a draft modal overlaps a maximized window. Native family policy chooses focus and hit order. The combined report already records `popupDismissalFocusRestorationQualified: false` and a failed focus-precondition timeout on native202. If that timeout repeats, fix the fixture precondition in place. Do not add a contract.

## Risks and falsifiable metrics

Risk: raising the popup curtain, or flipping the native492 probe to eligible, would paint an unqualified root. These slices do not do that. Risk: a taskbar image can be mistaken for S09 or release acceptance. Label it `integrated-host` for those three IDs only. Risk: leaving old trees in git still costs clone time. That cost is accepted until a human archives them without rewriting hashes.

By the next working day, all of these are true or the goal stops: at most one product tree receives edits; product paths in new commits are at most twice the files edited; new QA files are at most 20, the rest hash references; build commands are the changed units plus link, unless shared ABI changed; at least one original `then` clause is newly observed (`ELM-UX-006` historical label or `ELM-KDE-004` hit exclusion); zero new CONTROL or PUBLIC chapters; `requirements.json` records a scope tag or a one-sentence missing observation. Two slices without a new original observation end the goal.
