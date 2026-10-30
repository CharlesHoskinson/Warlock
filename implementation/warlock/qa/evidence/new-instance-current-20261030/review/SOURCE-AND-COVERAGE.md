# Bounded Apps → Actions → New instance review

Read-only source and retained evidence review. No QA/model/native execution, public edits or reopened window-Menu diagnostic. Graph-first navigation was partial; source pointers below are authoritative. Applied Quint review guidance for structural correspondence; runtime model checks were not rerun because root explicitly requested no QA.

## Original scope and actual route

Original ELM-UI-004 EARS requires explicit new-instance actions while ordinary activation does not launch duplicates; the primary-action scenarios alone do not discharge this extra EARS clause. Preserve application pin versus native always-on-top distinction. Existing native/keyboard/AT fixture requirements and frozen INTERACTION.md remain; no alternate requirement is created.

- Surface.elm77-86: newInstanceControl names `New instance` / `Open new instance of <name>`, uses current catalog identity, gates through Desktop.newInstanceAvailable and captures a Desktop.ViewStamp. Pending/Unknown have explicit disabled detail.
- Surface.elm102 adds the control to the application jump surface. Surface.elm301 exposes Actions for the first catalog search result in Apps. This is distinct from declared JumpList actions (`jump:action:*`). New instance ID is `control:new-instance:<catalog ID>`.
- Desktop.elm1064 OpenJumpList verifies current stamp, selection/prepare guards, binding and catalog membership; retires previous popup choices, opens jump state and requests actions. A pending read (`jumpExpected`) is distinct from a pending jump effect (`jumpList.pending`).
- Desktop.elm1378 newInstanceAvailable for jump requires matching jumpEntry and no pending jump effect, coherent/available shell, no choice/exhaustion/prepared menu, live catalog membership, no Launch Pending/Unknown, and Launch.select success. It intentionally need not wait for jumpExpected to clear: launch uses current application catalog, not jump-list service actions.
- Desktop.elm1299 NewInstance rechecks stamp and availability, obtains the current Launch.Selection, advances/closes Apps/jump and retires picker/menu choices, then delegates to Start. Desktop.elm1307 Start uses Launch.start and emits one application-launch intent plus its deadline when admitted; it does not dispatch an activate-window fallback.
- Launch.elm88 select captures host, reducer revision, catalog lifetime/generation and entry;112 start checks all these again, rejects Pending/Unknown, checks exact catalog intent and advances request once. Catalog refresh preserves Pending/Unknown (78); receive requires exact owner/intent (207); timeout preserves Unknown (243); disconnect retires host/catalog and converts pending to Unknown (257). Only explicit acknowledgeUnknown can clear the corresponding Unknown token (266).

No product defect was established in these inspected branches. No new model is warranted merely to exercise the unchanged route.

## Existing actual replay and model evidence

`qa/NewInstanceReplay.elm` is byte-identical to retained explicit-new-instance/final-build/NewInstanceReplay.elm (26e0442b…). Retained final-build/report.json SHA89e5fbaddb242bcc14ceb19b5147b9fde1991c54916d6a1d22bed45cd95ec3df records all19 actual compiled assertions true. Relevant assertions:

| Risk | Production replay coverage | Corresponding Quint named coverage |
| --- | --- | --- |
| Real explicit path | Labeled enabled control; pointer/keyboard resolve same typed action; one identity/generation-bound launch; popup closes; no window effect; jump control exists and launches/closes | windowMenuLaunchTest; applicationActionsLaunchTest |
| Stale selection | Stale Surface publication; old Desktop ViewStamp does not dispatch | staleViewAndIdentityTest; catalogReplacementRejectsOldSelectionTest |
| Duplicate | Pending reopened-menu dispatch cannot launch | pendingDuplicateTest |
| Unknown/no replay | Timeout-derived Unknown control disabled; cannot launch; refresh retains Unknown | unknownNeverReplaysTest |
| Catalog retirement | Removed catalog entry rejects previously captured message; ambiguous window menu has no launch control | removedCatalogIdentityTest; ambiguousWindowMenuTest |
| Ordinary activation/refusal | Ordinary primary emits activate window effect and zero launch; Refused does not automatically launch | ordinaryActivationNeverLaunchesTest; refusalHasNoFallbackLaunchTest |
| Other model-only coverage | No equivalent NewInstanceReplay assertion for stale receipt/unavailable sequence | staleReceiptTest; unavailableTest |

`qa/new-instance.qnt` and `_test.qnt` match retained copies (1b446657… /2c1b87e5…). Retained named log reports12 passing tests; sampled log reports1000 traces, seed0x134fe, TypeScript backend, no sampled violation. Four witnesses reached: windowMenuLaunch169, applicationActionsLaunch85, ordinaryWithoutLaunch364, unknownRetained127. These are retained bounded model observations, not a proof or new execution.

Correspondence is qualitative and small: Phase maps Launch status, Origin maps popup ownership, stamp models invalidation, generation/identity model catalog selection, launches/request model admitted intent, windowEffects separates ordinary primary. The single safety invariant (`launches==request`, nonnegative, Pending implies Closed) plus named traces does not establish all lifecycle or transport properties. Model ready abstracts several real guards; scalar request abstracts exact host/intent correlation; ordinaryPrimary abstracts real window decisions; timeout/rebind/explicit Unknown acknowledgement/output leases/UInt64 exhaustion/native GIO and AT are not modeled. State is grouped and enums are explicit; important witnesses are reachable in retained sampling. Do not claim a complete executable refinement relation.

## Precise remaining coverage

1. **Current source tuple:** historical final-build uses unchanged Surface/Launch/Catalog/replay/model but Desktop and SurfaceRenderer hashes differ from current source. Compile/run existing19 replay against the reviewed current frontend inputs; do not call old final-build a current-root result. Unchanged model evidence may be reused with explicit correspondence limits.
2. **Chosen jump route:** existing pointer/keyboard Surface.resolve assertion uses the window-menu-origin setup. Jump checks directly dispatch its message from OpenJumpList, not a full Apps→catalog→Actions→captured Surface action sequence. Add a bounded reachable positive for the actual jump route and same captured duplicate, stale publication/lease and retired catalog action through production dispatch. Never reopen stopped native Menu diagnostics to obtain these.
3. **Unknown and retirement sequencing:** existing replay synthesizes timeout state and directly replaces catalog fields for retirement. It does not drive Desktop incoming catalog correlation/generation replacement, disconnect/rebind, late matching/foreign outcomes after timeout or stale deadline on a later request. These are component/lifecycle gaps, not observed failures. For the selected work, preserve existing no-replay assertions and add only meaningful production-route sequences needed for its changed risk.
4. **Current native P/K/AT:** historical explicit-new-instance native recording has101 checks and three real bounded recorder executions plus stale desktop-file refusal; README explicitly leaves AT/independent acceptance/lifecycle schedules open. It does not prove current Apps→Actions pointer, physical keyboard and real exported AT activation. Require current coherent identity/publication/lease control, actual catalog ID/generation/GIO receipt and bounded real execution, no window-effect fallback, no ordinary-activation duplicate, and normal cleanup. Submitted is GIO submission, not app readiness. Native claim scope must match what is observed.

The retained old packet also contains application-actions-before-fix failure (real earlier utility-focus defect) and other historical fixture failures; preserve all of them. No source review or model count alone closes the UI004 explicit-New-instance EARS or its independent AT obligations.
