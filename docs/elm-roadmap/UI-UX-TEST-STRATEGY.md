# Replacement desktop UI/UX test strategy

Scope: the complete Elm desktop experience and its native window authority.
The user's replacement-GUI instruction supersedes Brave/Heroic-specific repair
work. Preserve historical failures as evidence; reproduce their general classes
with controlled windows. Representative real applications remain compatibility
coverage, without those two applications being special release gates.

This strategy implements the existing EARS/OpenSpec acceptance programme; it does
not mark a requirement complete. See `delivery/ui-ux-coverage.json` for every
requirement and original scenario, its work package and required evidence class.
All rows start planned. The frozen 242-requirement baseline remains unchanged.

## What a successful desktop means

A user can launch, find, switch, arrange, minimize, restore and close work without
losing data or wondering which window receives input. Every committed highlight,
preview, focused control and error reflects authoritative state. Cancellation
preserves the previous task. Failure leaves a reachable recovery path.

Elm owns the view and pure state transitions; native authority owns window effects,
seat focus and actual scene eligibility. Tests exercise both sides of that boundary.
The Elm message trace must agree with actual pixels, input recipients and native
receipts. A passing reducer or screenshot cannot establish this agreement alone.

## Evidence layers and cadence

| Layer | Execute | What it establishes |
| --- | --- | --- |
| Pure policy | On reducer/protocol changes: compiler, exact-name Quint scenarios, invariants, compiled Elm replay, property/fuzz tests with shrinking | State transitions, refusal and cancellation; no native or usability claim |
| Component | On view changes: DOM/control semantics, keyboard routes, theme fixtures and stale/pending/error states | Component behavior in the selected engine |
| Native integration | For each vertical slice: isolated compositor, authenticated authority, actual pointer/keyboard and client event logs | Surface lifetime, effects, pixels, seat input and recovery on the pinned tuple |
| Complete journeys | When connected features work: the journeys below from real launch through completion | Cross-surface consistency and task completion |
| Hardware and AT | Before host selection and release: actual GPU, displays, IME, Orca, braille where applicable | Capabilities the isolated fixture cannot establish |
| Human usability | Formative working slices and complete release candidate | Learnability, discoverability, comprehension and effort |
| Coherent release | One source/ABI tuple after fixes; repeat affected earlier gates | Integrated acceptance and reversible deployment |

Native campaigns are serial and use the protected QA launcher. Each fresh run
records source/build/driver hashes, applicability, case identity, input trace,
window incarnations, observed revisions, deadlines, results and ordered cleanup.
Retain failed packets and original deadlines. Repeat after a relevant change,
not merely to accumulate pass counts. Device and session fixtures must not alter
the user's desktop or drafts. Physical-device qualification is a separate gate.

## Complete journeys

Use deterministic content and known saved/unsaved state. Run pointer and keyboard
routes separately, then accessibility routes; do not substitute scripted dispatch
for user input. Record task completion, errors, recovery steps and time.

| Journey | Required outcomes and adversarial variant |
| --- | --- |
| Start work | Open launcher, search, launch, see correlated success and focus; delayed/no-result query and failed launch are understandable |
| Find running work | Taskbar groups and previews identify the right window; overflow remains reachable; stale/closed/reused identities cannot activate another window |
| Switch tasks | Forward/reverse switcher order matches policy; early modifier release commits once; Escape cancels; close/remap during selection is safe |
| Manage overlapping work | Raise/lower, maximize, pin and unpin obey policy; visible pixels, pointer recipient and keyboard recipient agree |
| Work with dialogs | Parent click redirects to the eligible modal and consumes the blocked click; nested modal chains work; independent same-process windows remain independent |
| Minimize and return | First-class minimize removes application paint/input eligibility, preserves taskbar entry and draft; restore commits eligible family and focus atomically; no scratchpad substitution |
| Arrange workspace | Snap chooser, drag, resize, Task View and workspace transfer preserve intended target; cancellation and output-generation changes refuse stale effects |
| Change displays | Move between unequal scale/transform outputs; unplug/replug during drag, popup, restore and switcher; work remains reachable |
| Use system surfaces | Menus, settings, notifications, volume/network/power adapters and Files reuse show accurate state and unavailable capabilities |
| Recover | Restart frontend/bridge, reject malformed messages, lose renderer/device or run out of capture budget; preserve applications and offer bounded recovery |
| End session | Dirty work is respected; lock/exclusive surfaces prevent shell input; recovery/rollback works without unintended logout |

## Canonical window and input matrix

Cover ordinary, maximized, fullscreen, pinned, minimized, unmapped, closing and
inactive-workspace windows; owner, child, nested modal, siblings, independent
same-process peer and malformed/cyclic families. Cover background/bottom/top/
overlay/exclusive layers and popup/transient lifetimes. Include application and
shell focus scopes, keyboard-only navigation, pointer press/hold/release, rapid
repetition and device disappearance.

For stacking cases, assert three distinct observations: presented pixel ownership,
pointer event recipient and actual client keyboard event recipient. Include a
negative oracle proving ineligible/blocked windows receive no events. Native focus
metadata alone is insufficient. Restore/motion cases require a canonical scene
revision and presentation/input receipts; sequential quiescent observations must
be labeled as such, rather than claimed atomic.

Press a blocked parent, retire its modal before release, and verify release does
not leak. Retire/recreate windows and input devices between press and release.
Inject workspace/output changes at the effect boundary. Open an exclusive surface
while a transaction is pending. Reuse addresses/PIDs with new incarnations.

Full cross-product testing is reserved for safety-critical identity, focus and
minimize boundaries. Use documented pairwise coverage elsewhere, plus targeted
three-way combinations for modal + maximize + pin and restore + output + scale.
Publish generated combinations and exclusions; an untested combination remains
untested even if adjacent cases pass.

## Visual, accessibility and internationalisation checks

Freeze supported theme, output scale, text scale and window-size matrices before
judging layout. Include light/dark/high-contrast, long labels, RTL, CJK, combining
characters and unavailable icons. Check clipping, readable contrast, focus rings,
overflow, target reachability, tooltip/menu placement and keyboard equivalents
for drag operations. Pixel comparisons use pinned fonts/engine/scale and narrowly
justified masks; semantic oracles decide dynamic content. Update goldens only after
reviewing the behavior change.

For Elm web content, use [WCAG 2.2](https://www.w3.org/TR/WCAG22/) AA criteria as
the accessibility target, including unobscured focus, target size and drag
alternatives. Desktop-native behavior also needs platform-specific tests; a web
checker does not prove desktop accessibility compliance.

Inspect the actual exported AT-SPI tree: names, roles, states, relationships,
actions and focus events. Then exercise taskbar, switcher, launcher, menus,
notifications and recovery through real Orca speech; test braille when its
requirement applies and record hardware/emulator distinction. Test magnification,
keyboard-only use, high contrast and reduced motion, following the practical
[GNOME accessibility guidance](https://developer.gnome.org/hig/guidelines/accessibility.html)
and [Orca testing guidance](https://orca.gnome.org/get-involved).
DOM semantics alone do not close the native accessibility gate.

Test actual IME preedit, candidate geometry, commit, cancel and focus transfer in
launcher/search/settings fields, including scale changes and popup lifetimes.
Verify preference changes mid-animation and reduced-motion operation without
losing feedback. Notifications must announce outcomes without stealing focus.

## Performance and graphics

Measure cold/warm launch, input-to-visible-response latency distributions, frame
cadence, capture/restore latency, idle CPU/GPU work, memory/VRAM, process/thread
counts and resource growth. Workloads include empty, typical and dense desktops,
large window families, long search results and repeated operation/soak sequences.
Report sample count, p50/p95/p99, misses, backend and workload; freeze numeric
budgets from the measured baseline under S02 before comparative acceptance.
Unknown budgets are open gates, not permission to pass by inspection.

Record hardware adapter/backend, submitted work, readback and displayed pixels
separately. WebGL hardware availability already observed is partial evidence.
WebGPU is not exposed by the current experimental WebKit host; any alternate host
must pass host, accessibility, IME, isolation and GPU gates before selection.
Exercise device loss, allocation refusal, renderer restart and bounded preview
budgets. Software fallback gets a separate result and visible capability status.

## Human usability protocol

Use task prompts with an observable end state, not instructions naming the right
control. Include new users of this desktop and experienced keyboard users, with
accessibility participants for the relevant workflows. Obtain consent for any
recording; minimise/redact captured application content. AI design reviews are
reviews, not participant evidence. Recruiting or contacting people requires
separate explicit instruction; absence of participants leaves this gate open.

For each formative round, record assistance, completion, wrong activations,
misunderstood state, cancellation/recovery and subjective ease after each task.
Select participant coverage and freeze task-specific success/error/effort criteria
before observing results. Release criteria require zero observed data-loss,
wrong-window destructive action, inaccessible essential journey or focus trap;
other thresholds remain an explicit S02 decision. Sample size and limitations
must accompany results; small formative studies cannot establish population-wide
claims. Fix findings and repeat affected journeys on the release candidate.

## Failure triage and release gates

P0: data loss, isolation breach, wrong-target destructive action or unusable
session. P1: essential journey blocked, incorrect paint/input/focus, inaccessible
essential controls or lost work on recovery. P2: usable workaround with substantial
friction or layout defect. P3: cosmetic. Open P0/P1 findings block release; lower
severity requires a recorded disposition, owner and user impact.

Every requirement retains its EARS statement and original OpenSpec scenario.
Attach bounded receipts to the coverage row; use planned/running/passed/failed/
blocked/not-applicable, with an applicability rationale for optional compositor
cases. No silent skips or aggregate pass count may hide missing scenarios.

Release requires all applicable scenario gates, hardware/AT evidence, measured
budgets, human usability evidence, coherent regression, source/ABI closure and
verified recovery artifacts. Prepare and review the concrete deployment/rollback
packet before any session activation requiring approval. Until then, the candidate
runs privately and the user's desktop remains unchanged.
