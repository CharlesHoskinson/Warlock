# Warlock after-action review — October 7, 2026

The failure was delivery management. I let an always-expandable preview safety backlog consume the implementation loop, repeatedly qualified and republished it, and failed to reconcile that work into original user scenarios. The engineering was real; the promised usable GUI did not follow. I should have changed course when the visible product stopped advancing.

All nine requested reviews are complete: three Grok 4.7, three Claude Opus 5.5 at high effort, and three GPT-6 Astra at high effort. Every reviewer had the exact 24-hour commit inventory, original requirements, actual source deltas, current evidence and read-only access to the entire repository. [The manifest](review-manifest.json) records model provenance and final-review hashes. The first Opus architecture invocation exhausted its turn limit; its failed output was retained, and the same requested model completed a bounded retry. No requested model was substituted.

## What the evidence establishes

- The snapshot interval is **2026-10-06 21:21:11 UTC through October 7 21:21:11 UTC**. It contains **90 commits, including 45 publication-record commits**. Path totals mostly count repeated archival copies and cannot measure unique authored work or features. [Exact inventory](inputs/git-24h.json).
- GUI137/139/141/143 contain genuine fixes for stale errors, current-error drain, known reload and shared WebKit process failure. The last two qualification publications changed no production C/Elm source and both reverified a 119-command build. [Actual deltas](inputs/source-deltas-94-143.json), [current combined report](inputs/docs/warlock-preview/v93/component-report-combined-restart-204-207.json).
- The controlled preview remains behind an opacity-0 curtain; the root preview remains ineligible. Physical reveal and the full release are unaccepted. Native202/203 retained real focus-precondition failures; successor fixtures explicitly did not qualify popup-dismissal focus restoration.
- The inspected integrated GUI lacks launcher query/search state and persisted catalog pins. Taskbar feedback is present in policy, but its bar status is visually hidden; generic recovery text masks important state distinctions.
- **My earlier “zero EARS completed” answer was unsupported.** The empty list belongs to an older integration lane. Corrected answer: zero original completions were recorded there; actual satisfied requirements need evidence adjudication. This review does not pretend an empty tracker proves absence of implementation.
- The roughly 7.9-million-token / 22.5-hour figure was a cumulative old-goal snapshot. **The last 24 hours' token usage and bill are unavailable.** It must not be presented as a measured daily cost.

## The nine reviews

| Reviewer | Principal finding / recommendation |
| --- | --- |
| [Grok product](grok_product.md) | Stop another uncertainty primitive; taskbar journeys and the known focus gap come first. |
| [Grok velocity](grok_velocity.md) | Copies, full rebuilds and receipt publications multiply cost without corresponding product change. |
| [Grok workflow](grok_workflow.md) | Internal CONTROL completion displaced original EARS; use one source candidate and scenario ledger. |
| [Opus architecture](opus_architecture.md) | Prototype fragmentation and unreconciled lineages prevent a coherent release. |
| [Opus requirements](opus_requirements.md) | Individual closure is undefined; honor the original evidence standard, including bridge evidence where permitted. |
| [Opus product](opus_product.md) | Demonstrate group selection/minimize/restore and a runnable isolated trial rather than invisible previews. |
| [Astra process](astra_process.md) | Add WIP=1, bounded no-progress triggers and proportional verification; fix focus and uncertain feedback. |
| [Astra code](astra_code.md) | Real lifecycle code exists; search and persistent launchers are concrete missing product capabilities. |
| [Astra delivery](astra_delivery.md) | Prioritize original user journeys and distinguish scenario, requirement, integration and release acceptance. |

They converge on the process failures, not an identical first-task order. Taskbar/focus, search and visible preview were competing priorities. I chose a small first repair to existing window-action feedback, then taskbar/focus and search, because it improves the current interaction without changing native effect authority or bypassing preview reveal.

## Root causes and decisions

**The work selector optimized for the next provable prerequisite.** “Smallest unblocked slice” always found another custody/error schedule. There was no requirement that the next interval finish a user journey. Safety was necessary; repeatedly choosing that subsystem over independent shell behavior was not.

**Immutable evidence became an immutable-development architecture.** Each fix copied a whole application, while qualification/publication became separate commit pairs. Git already supplies source history. Existing archives stay untouched; one candidate is materialized once, then edited incrementally. Unchanged toolchain/evidence bytes are referenced by hash, not recopied.

**Release acceptance swallowed individual acceptance.** The workflow defined the full finish line but not individual scenario verdicts. The replacement ledger preserves all 242 requirements / 417 scenarios and distinguishes unadjudicated, implemented-unverified, partial, failed, blocked and accepted. Full-release acceptance is separate. A native-required scenario still cannot close on browser evidence.

**Reporting rewarded activity.** Counts of versions, checks, files and publications hid missing behavior. Future reports lead with the original scenario, observable change and remaining observation. Administrative closures are explicitly separate from GUI features.

Not every reviewer recommendation was adopted. We reject automatic whole-goal blocking after two unsuccessful slices: the host tool's actual repeated-blocker rule applies, and independent product work continues. We reject editing frozen GUI143 in place; the new candidate preserves it. Several Elm programs do not alone prove duplicated authority, so a wholesale root-policy rewrite is not the first task. We reject automatic closure of UX-008 from workspace-1 evidence when its original fixture says workspace 2, and blanket closure of UI/UX requirements without the AT/native obligations they name. Commit percentages and arbitrary token caps would invite more proxy optimization; no new host token budget was invented.

## Installed solution

- [x] Nine independent evidence-based reviews and model provenance saved.
- [x] [v2 instructions](../../warlock-build-loop/v2/INSTRUCTIONS.md) installed through repository `AGENTS.md`; v1's scheduling/copying/validation sequence superseded.
- [x] One editable [integration candidate](../../../implementation/warlock/ANCESTRY.json), derived from held GUI143 once, with no copied QA/toolchain trees.
- [x] [Current state](../../warlock-build-loop/v2/STATE.json) and [original scenario ledger](../../warlock-build-loop/v2/requirement-ledger.json) installed without overwriting other workers' five dirty files.
- [x] WIP=1 product slice and one serialized native campaign; each slice names original IDs and before/after behavior.
- [x] Changed-target compilation and decisive checks first; broader regression only for a relevant boundary/failure or integration milestone.
- [x] Two qualification-only iterations / 45-minute no-progress trigger ends expansion of that investigation, without bypassing safety or discarding full scope.
- [x] First source task selected: visible and distinct Pending/Refused/Unknown feedback, **ELM-UI-007**. Its actual implementation result is recorded in [the first slice](../../warlock-build-loop/v2/FIRST-SLICE.md).
- [ ] Original native/AT verdicts, taskbar/focus journeys, pins, search, switcher/Task View, snap/output/drag, authorized visible previews, settings/notifications/Files/right-click, design-language/Omarchy integration and release qualification continue under the new loop.

The full release scope remains intact. AAR completion is not GUI release completion. Goal activation and its actual host status are recorded separately in `STATE.json`.

## Outside research and tools

The change to small, integrated behavior batches is supported by DORA's evidence on shortening feedback and reducing rework. Its WIP guidance specifically warns that invisible work and local optimization can conceal the real delivery bottleneck—an apt description of this loop. These findings support the scheduling changes; they do not replace repository evidence. [DORA small batches](https://dora.dev/capabilities/working-in-small-batches/), [DORA WIP limits](https://dora.dev/capabilities/wip-limits/).

OpenAI's Goals guidance describes an evidence-checked completion contract with explicit iteration policy and constraints. The new goal therefore names the whole GUI outcome, original evidence surface and the v2 iteration rules. A goal alone supplies no productivity discipline. [Using Goals in Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex).

One concrete skill recommendation is **Impeccable**, using its `audit`, `harden` and `clarify` commands on already-implemented widgets for accessibility, failure handling and understandable messages. It is secondary to product implementation; Warlock's frozen behavior and brand contracts override generic styling preferences. No installation is required for this first repair. Existing GitHub CLI, Quint and the installed browser tooling cover the immediate delivery work; no additional plugin or standing review council is recommended now. [Impeccable primary repository](https://github.com/pbakaus/impeccable).

Research used the available web tool. Scrapling was permitted, not required; it was not installed, and installing another scraper would not improve this audit.
