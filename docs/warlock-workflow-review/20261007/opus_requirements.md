# opus_requirements review: traceability for the 242 original requirements, and the "zero completed" claim

## Verdict

"Zero EARS completed" is **true as bookkeeping but meaningless as a measure**. The process had no way to close a single requirement. And for at least the last 24h, the work did not trace back to the original requirements at all, so we can't tell whether it moved any of them forward.

## Severity-ranked findings

**F1 — Critical: the last 24h of work cites no original requirement.** I searched the whole packet for `ELM-XXX-NNN` IDs. They appear only in the requirements and openspec files, the workplans, and the 28-item in-progress list in `implementation-status.json:6-33`. There are **zero** ID references in:
- `git-24h.json`
- `source-deltas-94-143.json`
- all three `warlock-preview/v93/component-report-*.json`
- `v93/HANDOFF.md`, `NATIVE-ADMISSION-CONTROLS.md`, `OUTGOING-CONTROL-CONTRACT.md`
- `loop-state.json`, `FRP-ELM-WORKPLAN.md`, `BUILD-LOOP.md`, `INSTRUCTIONS.md`
- `implementation/elm-baseline-v5/` (live repo)

Commit titles use internal control vocabulary only: "retirement polling", "control tickets", "actor quotas", "receipt confirmation" (`git-24h.json:9…4422`). None of them names a user-visible behavior. **A full day of commits cannot be mapped to any original scenario.** That is the core failure, more than the empty list.

**F2 — Critical: the internal contract gets closed; the original one does not.**
- `openspec/changes/warlock-preview-actor-retirement/tasks.md`: **36 checked** boxes.
- `openspec/changes/elm-desktop-pivot/tasks.md`: 242 boxes, **0 checked**.
- `elm-release-closure/tasks.md:3`: "All checkboxes remain unchecked."

The agent invented a secondary CONTROL spec, completed it, and treated that as progress.

**F3 — High: the loop has no rule for closing an individual requirement.**
- `INSTRUCTIONS.md:5,40` and `BUILD-LOOP.md:83-95` only define completion of the whole release.
- Nothing defines when a single ID moves into `completedRequirementIds`.

So the empty list (`implementation-status.json:35`, repeated about 30 times in the per-lane entries from line 1328 on) is a structural result, not a measurement. The status file is also stale and points at a different lane: `activeSlice` is `elm-recovery-delivery-general-reviewed-v656` (line 3), while the 24h work happened in `warlock-preview-provider-v86…v143`.

**F4 — High: original acceptance is being over-gated in some places.** About 26 requirements (the ARC and native-bridge block) take as verification "Preserved scenario report with **native or bridge trace**" (requirements.json `verification` fields). That text allows a bridge trace. Withholding closure until full GUI release goes beyond the original contract. The opposite also holds: UI requirements need "Named native, keyboard and assistive-technology fixtures" (e.g. `requirements.json:4970`). Component or browser evidence must not close those.

**F5 — High: massive archival duplication per slice.** Each "Qualify" commit copies the whole tree:
- 519 product / 13,062 QA files (`git-24h.json:11-12`)
- 418 / 16,515 (`:3206-3207`)
- 405 / 10,955 (`:2776-2777`)

Each is followed by a "Record public…" commit touching 1–2 QA files. The ratio of QA files to behavior changes is absurd, and review stays unaffordable.

**F6 — Medium: honest negatives are buried.**
- `component-report-combined-restart-204-207.json:29`: `"originalRestoreTimingQualified": false`
- same file, line 92: "No native/hardware/full release acceptance."
- `baselineV5.nativeAcceptance:false` (`implementation-status.json:112`)

These are correct and should stay. But they appear only in component prose, not against the affected IDs (e.g. ELM-REN-*, ELM-QA-002).

## Measured facts

- 242 requirements. Owner, verifier, task ID and scenarios appear 968 times, which is exactly 4 × 242 (`requirements.json`), so every requirement has all four.
- 28 IDs are marked in progress; none are completed.
- 24h commits come in pairs: a qualify commit, then a record commit. I did not count pairs exactly beyond the excerpt I read.
- `Taskbar.elm:30-36` (v143) already has click policy: minimized → Restore, active → Minimize, otherwise Activate. It has no minimize focus-successor logic. A grep for "successor" found nothing in that file.

## Which requirements could be closed: what the evidence shows

| ID | Original obligation | Evidence | Disposition |
|---|---|---|---|
| ELM-REV-005 | Every requirement has owner, verifier, phase, task, scenario before admission | 968 = 4 × 242 fields, and 242 tasks in pivot `tasks.md` | **Can be closed now**, after one independent verifier pass |
| ELM-UI-003 (P0) | Freeze switcher MRU, wrap, zero/one, cancel, modal-family and retirement fallback | `docs/elm-roadmap/INTERACTION.md:27` freezes order (C,B,A; forward B then A,C,B; reverse starts A), zero/one, cancel. I didn't find modal-family representation or candidate-retirement fallback for the switcher; line 37 covers menus only. | **Partial.** Two missing clauses; close once they're written and reviewed. Note it isn't even in the in-progress list. |
| ELM-DEL-001 / REN-001 / REV-035 | Immutable ledger of 38/34/52 identities and original deadlines | baseline-v5 holds restore 38, faults 34, 52 held cases, and `protectedVerificationPassed:true` (`implementation-status.json:103-113`). The README keeps the two-second deadline (`elm-baseline-v5/README.md:19-20`). | **Unverified.** `ledger.json` contains "deadline" only once and cites no ELM IDs. Check that each case keeps its own deadline, then close. |
| ELM-QA-016 | Map every requirement to scenario, owner and verifier, **plus retained audit dispositions** | The mapping exists | Partial. Audit-disposition evidence is unverified, so don't close yet. |
| ELM-UI-013 | Freeze numeric accessibility thresholds | `INTERACTION.md:47`: "Numeric thresholds… remain pending" | **Correctly open.** |
| ELM-QA-002 | Map 38/34/52 cases to fresh Elm scenarios | No per-ID mapping found | Open |

That gives at least one requirement closable now (REV-005) and four that need small, cheap checks (UI-003, DEL-001, REN-001, REV-035). None of them needs a GUI campaign. **Do not** close any of the 28 in-progress runtime IDs on component evidence. GPU-002, for example, explicitly separates the kinds of evidence.

## Stop / Start / Retain

**Stop**
- Creating or completing internal CONTROL openspec changes (actor-retirement, outgoing-control) unless one is the minimum needed to satisfy a named original scenario.
- Whole-tree derivatives for single-module changes.
- Separate "Record public…" commits.
- Leading reports with counts (Quint samples, replay cases, file counts).

**Start**
- Every commit title and component report names ≥1 original `ELM-ID/scenario-name` and that scenario's original `then` clause.
- A per-requirement state field in a single **new** file, e.g. `docs/elm-roadmap/delivery/requirement-ledger.json`. States: `open → implemented → scenario-evidenced (per its own verification text) → native-accepted → release-accepted`.
- `completedRequirementIds` = scenario-evidenced and independently verified. Release acceptance stays a separate gate.
- Derivatives that copy only the changed module, plus a manifest referencing the unchanged held bytes by hash. Held evidence is never rewritten.

**Retain**
- The protected launcher and its single native lock (`BUILD-LOOP.md:60-72`).
- ABI tuple identity.
- Original deadlines (baseline README:19-20).
- Keeping Unknown separate from confirmed outcomes.
- Preserving the user's drafts and desktop.
- Honest `false` flags such as `originalRestoreTimingQualified`.

## Operating rules

1. **WIP = 1 product slice.** A slice has 1–3 original IDs and their named scenarios. Any CPU-only work running alongside it must reference the same IDs.
2. **Escalate validation in steps:** Elm unit/replay of the original scenario first, then a single isolated native run of the same scenario, then (only at release) journey/AT/perf. Quint/fuzz only when the slice changes a concurrency boundary, and justify it by ID.
3. **Integrate into one tuple** (the v143 lineage). No new `vNNN` lane unless the ABI changes.
4. **Report** = IDs moved between states, the behavior diff, and failures. No counts.
5. **Cost cap:** if a slice hasn't moved any ID's state after about 2h or 500k tokens, stop and re-plan in the open.

## First three product slices (original IDs)

**1. ELM-UI-001: minimize focus succession** (scenarios `focus-successor`, `focus-last`, `focus-unfocused`; `requirements.json:4968-4990`), paired with **ELM-REN-006** (preserve workspace and restore geometry; `:3328`).
- Code: `Taskbar.elm:31` already emits `Effects.Minimize`. Add native-authority successor selection using the committed MRU from `INTERACTION.md:27`. The exact native handler path is unverified, so locate it first.
- Verification:
  - 3 Elm/replay cases matching the scenario text.
  - 1 isolated native run checking that A receives no keyboard input and B is focused.
  - No Quint.

**2. ELM-UI-003, then a pure switcher order function.**
- Add the two missing clauses (modal-family representation, retirement fallback) to INTERACTION.md and get them reviewed. Close UI-003.
- Implement an Elm `switcherOrder` with tests for `switcher-order`, `switcher-cancel`, `switcher-zero-one` and `switcher-retire-arrive` (`:5050-5080`).
- `switcher-membership` stays open until native enumeration exists.

**3. ELM-LAY-003 + ELM-LAY-001/GNO-002: the restore round trip** (`:2304`, `:2358`, `:1596`).
- Minimized surfaces are excluded from paint and hit-testing. Restore makes the surface eligible again in one accepted transition and rejects old generations.
- Verification: one native paint/hit receipt for each case, reusing slice 1's fixture.

Together these take ELM-DEL-025's taskbar/focus/minimize/restore journey (`:1476`) to native evidence. Release acceptance stays separate.

## Risks

- Relabeling: closures must quote each requirement's own verification text, and the independent `verifierRole` must sign off.
- Ledger sprawl: the requirement ledger must stay one file with no copies.
- Native flakiness could tempt someone to loosen deadlines. Forbidden; keep the existing rule.

## Falsifiable success metrics (next 24h)

- ≥1 requirement in `completedRequirementIds` (REV-005), and ≥3 more after the cheap checks.
- 100% of new commits cite ≥1 original ID/scenario.
- Slice 1 reaches scenario-evidenced with ≤1 native campaign.
- QA files per commit fall by at least 10× from the 7–16k baseline.
- 0 new CONTROL openspec changes.

## Not verified by me

- Per-case deadlines inside `ledger.json`.
- Where native minimize is handled.
- Whether `elm-shared-observation-recovery-v121` carries ID traceability.
- The exact number of qualify/record pairs in the 24h window.
