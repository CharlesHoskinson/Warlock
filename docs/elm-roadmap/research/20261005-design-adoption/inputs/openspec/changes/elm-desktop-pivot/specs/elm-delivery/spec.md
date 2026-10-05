# elm-delivery

## ADDED Requirements

### Requirement: ELM-DEL-001

The release plan SHALL preserve baseline source hashes, scenario identities, failures and original deadlines in an immutable migration ledger.

#### Scenario: ELM-DEL-001 delivery-001

- GIVEN an archived failed baseline
- WHEN migration mapping is generated
- THEN the original failure and deadline remain unchanged

### Requirement: ELM-DEL-002

The release plan SHALL assign an accountable role, dependencies, runnable deliverables and acceptance evidence to each outcome-driven build cycle and keep optional compositor work separately gated.

#### Scenario: ELM-DEL-002 delivery-002

- GIVEN an outcome-driven release plan
- WHEN cycle readiness and completion are reviewed
- THEN mandatory shell and optional compositor work have separate dependencies and gates, and progression depends on accepted results rather than elapsed time

### Requirement: ELM-DEL-003

The release builder SHALL pin compiler, Elm packages, test runner, JavaScript adapter, native dependencies and build-tool versions with source and artifact hashes.

#### Scenario: ELM-DEL-003 delivery-003

- GIVEN a candidate build
- WHEN its manifest is inspected
- THEN every build input resolves to a pinned hashed artifact

### Requirement: ELM-DEL-004

WHEN a release is rebuilt in two clean isolated environments, the builder SHALL produce identical distributable hashes or block release with the differing inputs recorded.

#### Scenario: ELM-DEL-004 delivery-004

- GIVEN a cached locked dependency set
- WHEN two clean builds run
- THEN distributable hashes match or release is blocked

### Requirement: ELM-DEL-005

The release package SHALL include an SBOM, upstream notices and a reviewed redistribution disposition for compiler, packages, host, native libraries and bundled assets.

#### Scenario: ELM-DEL-005 delivery-005

- GIVEN a candidate package
- WHEN redistribution review runs
- THEN all shipped components and applicable notices are accounted for

### Requirement: ELM-DEL-006

WHEN a host candidate is qualified, the host decision SHALL record compatible GTK and layer-shell major versions or Qt WebEngine initialization and transitive runtime dependencies.

#### Scenario: ELM-DEL-006 delivery-006

- GIVEN GTK and Qt candidate hosts
- WHEN host comparison runs
- THEN each candidate has an actual dependency and initialization report

### Requirement: ELM-DEL-007

The release package SHALL identify Arch Linux with Omarchy as the supported initial target and label other distributions unsupported until their dependency and native acceptance matrices pass.

#### Scenario: ELM-DEL-007 delivery-007

- GIVEN an unqualified Ubuntu environment
- WHEN support status is displayed
- THEN it is not advertised as qualified

### Requirement: ELM-DEL-009

WHEN a component migration is selected, the launcher SHALL activate only that qualified component and retain a selectable working predecessor for rollback.

#### Scenario: ELM-DEL-009 delivery-009

- GIVEN a qualified taskbar slice
- WHEN the feature selector changes
- THEN one taskbar owner runs and the predecessor remains selectable

### Requirement: ELM-DEL-016

WHEN a release is rolled back, the recovery tooling SHALL restore the preceding compatible settings copy without silently interpreting a newer schema.

#### Scenario: ELM-DEL-016 delivery-016

- GIVEN settings from a newer release
- WHEN rollback runs
- THEN the prior compatible copy is restored

### Requirement: ELM-DEL-018

WHEN a host or authority restarts, the supervisor SHALL invalidate old epochs and reconcile a fresh native snapshot before enabling new mutating requests.

#### Scenario: ELM-DEL-018 delivery-018

- GIVEN pending requests and retained frames
- WHEN a service restarts
- THEN old requests are invalid and new effects wait for reconciliation

### Requirement: ELM-DEL-019

WHEN an upgrade is interrupted, the activation tooling SHALL recover to one complete validated release tuple and preserve user settings and application drafts.

#### Scenario: ELM-DEL-019 delivery-019

- GIVEN an active old release
- WHEN activation is interrupted at each write boundary
- THEN a complete old or new tuple is selected with drafts preserved

### Requirement: ELM-DEL-020

The release SHALL provide an offline command-line recovery path that restores the preceding shell without a working Elm host or a main-compositor restart.

#### Scenario: ELM-DEL-020 delivery-020

- GIVEN a broken Elm host without network
- WHEN offline recovery runs
- THEN the previous shell returns without restarting the compositor

### Requirement: ELM-DEL-021

WHEN an owned session stops, the supervision SHALL stop clients and helpers, verify normal exits and retired resources, unload owned modules, and then stop its private compositor and bus.

#### Scenario: ELM-DEL-021 delivery-021

- GIVEN a private QA session
- WHEN teardown runs
- THEN closure receipts prove order and normal termination

### Requirement: ELM-DEL-022

IF a compositor and plugin ABI pair differs from the frozen accepted tuple, THEN the launcher SHALL refuse plugin loading and retain the working shell.

#### Scenario: ELM-DEL-022 delivery-022

- GIVEN a mismatched plugin/core pair
- WHEN activation is attempted
- THEN the plugin is not loaded

### Requirement: ELM-DEL-023

WHEN production activation is prepared, the release owner SHALL require one coherent source/runtime/ABI tuple with all mandatory native, model, CPU and user acceptance gates satisfied.

#### Scenario: ELM-DEL-023 delivery-023

- GIVEN partial CPU-only acceptance
- WHEN activation review runs
- THEN the release is blocked until missing native and user gates pass

### Requirement: ELM-DEL-024

The maintenance plan SHALL assign dependency-security triage, host-engine update cadence, regression owners and rollback responsibility for every supported release.

#### Scenario: ELM-DEL-024 delivery-024

- GIVEN a supported release
- WHEN a host security update is proposed
- THEN an owner reviews urgency and required requalification

#### Scenario: ELM-DEL-024 maintenance-fields

- GIVEN a release proposed for support
- WHEN the maintenance runbook is reviewed
- THEN security triage owner, numeric engine review interval, regression owner and rollback owner are all present with escalation contacts

#### Scenario: ELM-DEL-024 maintenance-overdue

- GIVEN the frozen engine review interval elapses without an assigned review
- WHEN maintenance status is evaluated
- THEN the overdue review is recorded and escalated to the declared accountable owner

### Requirement: ELM-DEL-025

WHEN the user acceptance session runs, the candidate SHALL preserve existing windows and drafts while demonstrating the named taskbar, focus, minimize, restore, pin, snap and keyboard flows.

#### Scenario: ELM-DEL-025 delivery-025

- GIVEN the user workspace with drafts
- WHEN acceptance flows execute
- THEN named flows pass and window/draft inventory remains intact

### Requirement: ELM-DEL-026

The host qualification SHALL identify the actual GPU adapter, driver, backend and hardware-acceleration status on each pinned host/driver tuple before claiming accelerated rendering.

#### Scenario: ELM-DEL-026 delivery-026

- GIVEN a candidate on target hardware
- WHEN render qualification runs
- THEN the report identifies adapter and actual acceleration status

### Requirement: ELM-DEL-027

IF hardware acceleration is unavailable or disabled, THEN the host SHALL report the active software fallback and qualify its performance independently without claiming GPU acceleration.

#### Scenario: ELM-DEL-027 delivery-027

- GIVEN hardware acceleration explicitly disabled
- WHEN the shell starts
- THEN fallback status is visible and its budget verdict is separate

### Requirement: ELM-DEL-028

WHERE WebGPU is enabled, the host SHALL require a qualified adapter and device, retain an accepted non-WebGPU rendering route, and invalidate GPU resources on device loss before recovery.

#### Scenario: ELM-DEL-028 delivery-028

- GIVEN an enabled qualified WebGPU route
- WHEN device loss occurs
- THEN stale resources retire and an accepted route restores presentation

### Requirement: ELM-REV-028

WHEN the machine resumes from suspend, the native host SHALL invalidate changed output and rendering generations, reconcile a fresh snapshot and refuse replay of pre-suspend mutating intents.

#### Scenario: ELM-REV-028 revision-028

- GIVEN a preview and mutating request are pending
- WHEN suspend/resume changes native output state
- THEN old generations cannot publish or mutate and a coherent current snapshot precedes new work

