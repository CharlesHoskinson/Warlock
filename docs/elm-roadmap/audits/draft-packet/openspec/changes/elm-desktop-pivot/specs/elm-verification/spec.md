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

#### Scenario: ELM-QA-017 qa-017

- GIVEN maximized Brave overlaps a draft
- WHEN another visible window is clicked
- THEN painted order, hit target and focused identity agree

### Requirement: ELM-QA-018

The native verifier SHALL qualify actual changed, unchanged, cancelled and stale popup/input routes before the fixed two-process, three-slot, twelve-helper reliability campaign.

#### Scenario: ELM-QA-018 qa-018

- GIVEN a stale popup transaction
- WHEN its receipt arrives
- THEN no stale focus effect occurs and the route is recorded

### Requirement: ELM-QA-019

The accessibility verifier SHALL qualify keyboard-only operation, focus announcements, audible and braille output, IME composition and reduced motion on the selected native host.

#### Scenario: ELM-QA-019 qa-019

- GIVEN an active IME composition and screen reader
- WHEN a popup opens and is cancelled
- THEN composition and announced focus remain correct

### Requirement: ELM-QA-020

The hardware verifier SHALL qualify scale, rotation, hotplug, output transfer and high-refresh motion on actual supported displays using native presentation feedback.

#### Scenario: ELM-QA-020 qa-020

- GIVEN different output scales
- WHEN a preview transfers during motion
- THEN pixels, hit coordinates and generations match the destination

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

