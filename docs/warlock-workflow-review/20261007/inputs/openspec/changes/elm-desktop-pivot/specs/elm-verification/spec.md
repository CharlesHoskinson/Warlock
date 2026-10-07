# elm-verification

## ADDED Requirements

### Requirement: ELM-QA-001

The verification owner SHALL retain hash-bound original source inventories, proof packets, failures, scenario identities and deadlines unchanged and create reviewed derivatives for new evidence.

#### Scenario: ELM-QA-001 qa-001

- GIVEN an archived failure
- WHEN a derivative is created
- THEN the ancestor hash and failed verdict remain intact

### Requirement: ELM-QA-002

The verification owner SHALL map all original 38 restore-baseline, 34 fault/recovery and 52 drag/resize/reload cases to fresh Elm acceptance scenarios without removing cases or extending deadlines.

#### Scenario: ELM-QA-002 qa-002

- GIVEN the original inventories
- WHEN Elm scenarios are indexed
- THEN every original identity and deadline has a mapped scenario

### Requirement: ELM-QA-003

WHEN fault/recovery case 34 is executed, the protected runner SHALL enforce its original frozen deadline and time origin independently of campaign completion.

#### Scenario: ELM-QA-003 qa-003

- GIVEN the frozen case-34 contract
- WHEN completion arrives after its deadline
- THEN the case fails despite later successful cleanup

### Requirement: ELM-QA-004

WHEN a Quint campaign is reported, the formal verifier SHALL explicitly select every claimed scenario by exact name and retain selected names, execution results, seed and tool/model hashes.

#### Scenario: ELM-QA-004 qa-004

- GIVEN a model containing non-Test scenario names
- WHEN the named campaign runs
- THEN no skipped name is counted as executed

### Requirement: ELM-QA-005

The verification ledger SHALL distinguish formal, CPU, replay, fuzz, native, hardware and accessibility evidence and block substitution between these acceptance levels.

#### Scenario: ELM-QA-005 qa-005

- GIVEN a CPU-only passing report
- WHEN native acceptance is evaluated
- THEN the native gate remains open

### Requirement: ELM-QA-006

WHEN an Elm reducer changes, the policy verifier SHALL compare deterministic replay against frozen ordered native observations including identities, receipts and expected effects.

#### Scenario: ELM-QA-006 qa-006

- GIVEN a retained native trace
- WHEN the updated reducer replays it
- THEN state and intents satisfy the mapped oracle

### Requirement: ELM-QA-007

WHEN foreign protocol input is malformed, stale, duplicated or out of order, the native authority SHALL reject unsafe effects and the verifier SHALL retain a reproducible fault trace.

#### Scenario: ELM-QA-007 qa-007

- GIVEN a superseded window incarnation
- WHEN a delayed mutation is delivered
- THEN no replacement window receives the effect

### Requirement: ELM-QA-008

The formal verifier SHALL cover focus, modal families, pin/maximize, capture leases, cancellation, retirement and output generations with invariants and named transition scenarios.

#### Scenario: ELM-QA-008 qa-008

- GIVEN a cancelled capture generation
- WHEN a stale retirement arrives
- THEN the active generation retains its live lease

#### Scenario: ELM-QA-008 model-focus

- GIVEN a named model transition fixture for focus
- WHEN the fixture and its configured invariant checker execute
- THEN all focus invariants hold and exact transition and model hashes appear in the coverage ledger

#### Scenario: ELM-QA-008 model-modal-family

- GIVEN a named model transition fixture for modal-family
- WHEN the fixture and its configured invariant checker execute
- THEN all modal-family invariants hold and exact transition and model hashes appear in the coverage ledger

#### Scenario: ELM-QA-008 model-pin-maximize

- GIVEN a named model transition fixture for pin-maximize
- WHEN the fixture and its configured invariant checker execute
- THEN all pin-maximize invariants hold and exact transition and model hashes appear in the coverage ledger

#### Scenario: ELM-QA-008 model-capture-lease

- GIVEN a named model transition fixture for capture-lease
- WHEN the fixture and its configured invariant checker execute
- THEN all capture-lease invariants hold and exact transition and model hashes appear in the coverage ledger

#### Scenario: ELM-QA-008 model-cancellation

- GIVEN a named model transition fixture for cancellation
- WHEN the fixture and its configured invariant checker execute
- THEN all cancellation invariants hold and exact transition and model hashes appear in the coverage ledger

#### Scenario: ELM-QA-008 model-retirement

- GIVEN a named model transition fixture for retirement
- WHEN the fixture and its configured invariant checker execute
- THEN all retirement invariants hold and exact transition and model hashes appear in the coverage ledger

#### Scenario: ELM-QA-008 model-output-generation

- GIVEN a named model transition fixture for output-generation
- WHEN the fixture and its configured invariant checker execute
- THEN all output-generation invariants hold and exact transition and model hashes appear in the coverage ledger

### Requirement: ELM-QA-009

WHEN a native QA campaign starts, the protected launcher SHALL verify a live parent Wayland socket, a private UID-owned nonsymlink 0700 runtime directory and a dedicated QA scope with inherited core limit 1.

#### Scenario: ELM-QA-009 qa-009

- GIVEN an invalid runtime directory
- WHEN the campaign is requested
- THEN launch is refused before any client starts

### Requirement: ELM-QA-010

The QA owner SHALL serialize native GUI campaigns, disable Xwayland unless X11 is under test, prohibit DRM fallback and preserve all five crash-handoff protections.

#### Scenario: ELM-QA-010 qa-010

- GIVEN a live campaign owns the QA lease
- WHEN another campaign requests launch
- THEN it cannot start concurrently

#### Scenario: ELM-QA-010 x11-scope

- GIVEN a protected serial native campaign
- WHEN a campaign starts without an explicit X11 fixture
- THEN Xwayland is disabled in the launch receipt

#### Scenario: ELM-QA-010 no-drm-fallback

- GIVEN a protected serial native campaign
- WHEN the nested backend fails
- THEN the campaign fails without starting a DRM compositor

#### Scenario: ELM-QA-010 crash-protections

- GIVEN a protected serial native campaign
- WHEN a launch and teardown complete
- THEN each of the five handoff protections has an independent configuration and outcome receipt

### Requirement: ELM-QA-011

WHEN QA teardown begins, the runner SHALL stop owned clients and helpers, verify empty clients and unload modules before stopping nested compositor and private bus.

#### Scenario: ELM-QA-011 qa-011

- GIVEN owned helpers and loaded modules
- WHEN teardown begins
- THEN client/helper closure precedes compositor termination

### Requirement: ELM-QA-012

IF a process disappears without a recorded exit status, THEN the verifier SHALL mark process closure unproven rather than infer normal exit.

#### Scenario: ELM-QA-012 qa-012

- GIVEN a helper missing from process enumeration
- WHEN closure is assessed
- THEN normal exit is not accepted without its status

### Requirement: ELM-QA-013

The QA runner SHALL preserve user drafts and the main compositor session during research and acceptance campaigns.

#### Scenario: ELM-QA-013 qa-013

- GIVEN a user draft remains open
- WHEN isolated QA completes
- THEN its window and compositor lifetime are preserved

### Requirement: ELM-QA-014

WHEN a gate verdict is recorded, the verifier SHALL bind it to source/tool hashes, command, environment, ABI pair, deadlines, observations, closure receipts and reviewer disposition.

#### Scenario: ELM-QA-014 qa-014

- GIVEN a passing report lacking its ABI pair
- WHEN release qualification evaluates it
- THEN the gate remains unaccepted

### Requirement: ELM-QA-015

The release verifier SHALL qualify all mandatory gates against one coherent frozen source/runtime/ABI tuple and retain every failed attempt and rerun.

#### Scenario: ELM-QA-015 qa-015

- GIVEN individually passing reports from incompatible pairs
- WHEN the release ledger is built
- THEN the mixed tuple cannot qualify

### Requirement: ELM-QA-016

The planning verifier SHALL map every requirement to an OpenSpec scenario, phase, actionable task, owner and concrete verifier and retain audit findings with final dispositions.

#### Scenario: ELM-QA-016 qa-016

- GIVEN a requirement without a task
- WHEN planning validation runs
- THEN the missing link blocks plan acceptance

### Requirement: ELM-QA-017

The application verifier SHALL exercise representative native applications including maximized Brave, modal drafts and Files against visible order, hit order, focus, pin, minimize and restore assertions.

#### Scenario: ELM-QA-017 qa-modal-exception

- GIVEN Brave has a current eligible blocking modal and its owner is clicked
- WHEN native activation is processed
- THEN painting and hit traversal use one revision and focus follows the predeclared modal recipient while the draft remains open

#### Scenario: ELM-QA-017 qa-unrelated-window

- GIVEN Brave and an unrelated eligible opaque window overlap without input exceptions
- WHEN the top unrelated window is clicked
- THEN it receives the hit and focus on the same committed scene

### Requirement: ELM-QA-018

The native verifier SHALL qualify actual changed, unchanged, cancelled and stale popup/input routes before the fixed two-process, three-slot, twelve-helper reliability campaign.

#### Scenario: ELM-QA-018 qa-018

- GIVEN a stale popup transaction
- WHEN its receipt arrives
- THEN no stale focus effect occurs and the route is recorded

### Requirement: ELM-QA-019

The accessibility verifier SHALL qualify keyboard-only operation, focus announcements, audible and braille output, IME composition and reduced motion on the selected native host.

#### Scenario: ELM-QA-019 qa-019-keyboard

- GIVEN the selected host with no pointing device
- WHEN the required keyboard flow executes
- THEN all required controls are reachable and Escape returns focus without trapping navigation

#### Scenario: ELM-QA-019 qa-019-speech

- GIVEN the selected host with supported screen reader and audio output
- WHEN the required speech flow executes
- THEN control names/states and focus changes are audibly announced

#### Scenario: ELM-QA-019 qa-019-braille

- GIVEN the selected host with a supported braille display
- WHEN the required braille flow executes
- THEN focus changes and control labels are observed on actual braille output

#### Scenario: ELM-QA-019 qa-019-ime

- GIVEN the selected host with a preedit composition active while a popup opens/cancels
- WHEN the required ime flow executes
- THEN composition text/caret remain correct and commit/cancel produce no duplicate text

#### Scenario: ELM-QA-019 qa-019-reduced-motion

- GIVEN the selected host with reduced motion enabled
- WHEN the required reduced-motion flow executes
- THEN the final minimize/restore state and focus match the normal route without optional motion or stale capture actor

### Requirement: ELM-QA-020

The hardware verifier SHALL qualify scale, rotation, hotplug, output transfer and high-refresh motion on actual supported displays using native presentation feedback.

#### Scenario: ELM-QA-020 qa-020-scale

- GIVEN the supported physical configuration with two different fractional scales
- WHEN the scale workload executes
- THEN pixels and hit geometry match the active scale

#### Scenario: ELM-QA-020 qa-020-rotation

- GIVEN the supported physical configuration with an output rotated through supported transforms
- WHEN the rotation workload executes
- THEN rendered and input coordinates apply the same output transform

#### Scenario: ELM-QA-020 qa-020-hotplug

- GIVEN the supported physical configuration with a pending preview on an output
- WHEN the hotplug workload executes
- THEN removal retires the old output generation and reconnect reconciles current native membership

#### Scenario: ELM-QA-020 qa-020-transfer

- GIVEN the supported physical configuration with a preview and motion crossing output boundaries
- WHEN the transfer workload executes
- THEN frame, geometry and target eligibility match the destination generation

#### Scenario: ELM-QA-020 qa-020-high-refresh

- GIVEN the supported physical configuration with the real 240 Hz output and frozen cadence budget
- WHEN the high-refresh workload executes
- THEN native presentation samples meet the frozen budget with recorded misses and no browser-frame inference

### Requirement: ELM-QA-027

WHERE compositor replacement is proposed, the feasibility verifier SHALL require isolated native Wayland/Xwayland application, input, output, capture, IME and accessibility evidence before a recorded go decision.

#### Scenario: ELM-QA-027 qa-027

- GIVEN an optional substrate prototype
- WHEN feasibility is reviewed
- THEN unsupported mandatory protocols and failed app cases remain explicit

### Requirement: ELM-QA-028

WHERE compositor implementation is authorized, the release verifier SHALL require equivalent mandatory shell parity and complete new native compatibility gates before that compositor replaces Hyprland.

#### Scenario: ELM-QA-028 qa-028

- GIVEN a replacement compositor has model passes
- WHEN replacement release is evaluated
- THEN native compatibility gates remain required

### Requirement: ELM-REV-005

The requirement registry SHALL assign each requirement an accountable owner role, independent verifier role, phase, task and named acceptance scenario before implementation admission.

#### Scenario: ELM-REV-005 requirement-ownership

- GIVEN all proposed requirement rows
- WHEN implementation admission is evaluated
- THEN every row has explicit role and verifier mapping and missing mappings block admission

### Requirement: ELM-REV-006

The final audit record SHALL bind reviewed documents, author-input JSON, primary corpus inventories and retained source/body hash roots to a mechanically verified supporting-evidence manifest.

#### Scenario: ELM-REV-006 audit-evidence-closure

- GIVEN a claimed corpus and author generation input
- WHEN the final supporting manifest is verified
- THEN all input/corpus references hash-match and excluded or failed acquisition scopes remain explicit

### Requirement: ELM-REV-029

The QA runner SHALL preserve the protected scope/core limit, verified nested parent socket, explicit X11 selection, authorized runtime/device access and client-before-compositor teardown controls from the frozen crash handoff.

#### Scenario: ELM-REV-029 revision-029

- GIVEN a private campaign with every frozen control recorded
- WHEN each missing-control preflight stimulus is supplied
- THEN each violation separately blocks launch or unsafe teardown under its named assertion

### Requirement: ELM-REV-030

The QA runner SHALL preserve the installed crash-watch override and the system grim and gnome-keyring builds during all planning, proof and acceptance work.

#### Scenario: ELM-REV-030 revision-030

- GIVEN protected system integrations are inventoried
- WHEN QA executes
- THEN their source/config identities remain unchanged

### Requirement: ELM-REV-035

The QA baseline SHALL freeze original restore baseline38, recovery34, drag/resize/reload52 and B12 through B24 scenario identities, oracles and original deadlines before claiming inherited native coverage.

#### Scenario: ELM-REV-035 inherited-coverage-frozen

- GIVEN original campaign scripts and partial reports
- WHEN the baseline coverage ledger is created
- THEN each original case has its source hash, deadline, oracle and unexecuted or observed verdict; missing definitions block inherited coverage claims

### Requirement: ELM-UI-021

The product verifier SHALL freeze representative usability tasks, participant profiles, assistance rules and measurable success thresholds before candidate evaluation, and SHALL block acceptance for failed or unobserved required outcomes.

#### Scenario: ELM-UI-021 usability-protocol

- GIVEN novice experienced keyboard and declared AT profiles
- WHEN restore switcher pin snap failure recovery and rollback discovery tasks run
- THEN success assistance errors recovery and completion measures are recorded against frozen thresholds

#### Scenario: ELM-UI-021 usability-failed

- GIVEN candidate fails a frozen threshold
- WHEN report is reviewed
- THEN failure remains recorded; changed thresholds require a new protocol and separately identified rerun

