# elm-native-bridge

## ADDED Requirements

### Requirement: ELM-ARC-003

The Elm desktop SHALL expose one incoming event stream and one outgoing intent stream with versioned, discriminated envelopes.

#### Scenario: ELM-ARC-003 architecture-003

- GIVEN a connected host
- WHEN an intent and its outcome cross the bridge
- THEN both conform to the recorded schema

### Requirement: ELM-ARC-004

IF an envelope is malformed or has an unsupported protocol version, THEN the Elm desktop SHALL reject it without a native effect and record the rejection reason.

#### Scenario: ELM-ARC-004 architecture-004

- GIVEN an invalid envelope
- WHEN the host receives it
- THEN no compositor action occurs and a reason is recorded

### Requirement: ELM-ARC-005

The Elm desktop SHALL attach request identity, compositor lifetime, frontend epoch, operation generation, window incarnation, output generation and expected native revision to window-effect intents.

#### Scenario: ELM-ARC-005 architecture-005

- GIVEN a known window and output
- WHEN an effect is requested
- THEN the serialized request contains the full authority tuple

### Requirement: ELM-ARC-006

IF an intent identity or expected revision differs from current native authority, THEN the Elm desktop SHALL refuse the intent before mutation.

#### Scenario: ELM-ARC-006 architecture-006

- GIVEN a closed and recreated window
- WHEN its old intent arrives
- THEN the new window remains unchanged

### Requirement: ELM-ARC-007

The Elm desktop SHALL correlate each outcome with its request and represent Pending, Committed, Refused, Cancelled and Unknown as distinct states.

#### Scenario: ELM-ARC-007 architecture-007

- GIVEN a request whose connection drops
- WHEN its final effect cannot be proven
- THEN its state is Unknown rather than Committed

### Requirement: ELM-ARC-008

WHEN a dependent effect is requested, the Elm desktop SHALL dispatch it only after the prerequisite receipt satisfies its declared precondition.

#### Scenario: ELM-ARC-008 architecture-008

- GIVEN restore followed by focus
- WHEN restore is still pending
- THEN focus is withheld until the required receipt

### Requirement: ELM-ARC-009

WHEN a duplicate request is received within a frontend epoch, the Elm desktop SHALL return the existing request disposition without executing the effect again.

#### Scenario: ELM-ARC-009 architecture-009

- GIVEN a committed request
- WHEN the same request arrives twice
- THEN only one mutation is recorded

### Requirement: ELM-ARC-010

WHEN a snapshot is installed, the Elm desktop SHALL apply only ordered events after its native sequence watermark and request reconciliation on a sequence gap.

#### Scenario: ELM-ARC-010 architecture-010

- GIVEN a snapshot at sequence 10
- WHEN events 9 and 12 arrive
- THEN 9 is discarded and the gap before 12 triggers reconciliation

### Requirement: ELM-ARC-011

The Elm desktop SHALL capture modifier press, repeat, release and Escape in native order with chord generation and ordinal before frontend readiness.

#### Scenario: ELM-ARC-011 architecture-011

- GIVEN the webview is starting
- WHEN Alt is released before readiness
- THEN the ready view receives the release in its original chord order

### Requirement: ELM-ARC-012

WHEN cancellation reaches native authority before an effect commits, the Elm desktop SHALL prevent that effect and retire its request-owned resources.

#### Scenario: ELM-ARC-012 architecture-012

- GIVEN a prepared restore
- WHEN Escape cancels before commit
- THEN restore is absent and owned helpers retire

### Requirement: ELM-ARC-013

The Elm desktop SHALL retain each original acceptance deadline through retries, queueing, reconciliation and frontend restart.

#### Scenario: ELM-ARC-013 architecture-013

- GIVEN a request nearing its original deadline
- WHEN the renderer restarts
- THEN the deadline remains unchanged

### Requirement: ELM-ARC-014

IF an effect outcome is Unknown, THEN the Elm desktop SHALL reconcile native state before permitting a retry of that effect.

#### Scenario: ELM-ARC-014 architecture-014

- GIVEN an acknowledgement was lost
- WHEN the user retries
- THEN native truth is read before another mutation

### Requirement: ELM-ARC-015

The Elm desktop SHALL enforce configured byte and item bounds on bridge queues, coalesce replaceable observations, and reject new effect work explicitly when admission fails.

#### Scenario: ELM-ARC-015 architecture-015

- GIVEN queues at configured capacity
- WHEN new observations and effects arrive
- THEN memory remains bounded and effect refusal is explicit

### Requirement: ELM-ARC-016

The Elm desktop SHALL reserve bounded control capacity for cancellation, receipts and retirement independently of preview work.

#### Scenario: ELM-ARC-016 architecture-016

- GIVEN the preview queue is saturated
- WHEN cancellation arrives
- THEN it uses reserved control capacity and is processed

### Requirement: ELM-ARC-017

The Elm desktop SHALL use one canonical owner for cross-output snap, pin and switcher transactions and send read-only projections to display views.

#### Scenario: ELM-ARC-017 architecture-017

- GIVEN two display views
- WHEN both propose actions on one window
- THEN one authority serializes the transaction

### Requirement: ELM-ARC-018

The Elm desktop SHALL resolve modal-family focus, input blockers, stacking and hit testing from native authority rather than DOM state.

#### Scenario: ELM-ARC-018 architecture-018

- GIVEN a draft modal overlaps a maximized window
- WHEN a user clicks a visible native region
- THEN the native family policy determines focus and hit order

### Requirement: ELM-ARC-019

The Elm desktop SHALL transport preview identifiers and revisions through ports while native components retain pixel buffers and verify source-stop lifetime.

#### Scenario: ELM-ARC-019 architecture-019

- GIVEN a retained minimized preview
- WHEN its source stops
- THEN the valid retained frame remains available without JSON pixels

### Requirement: ELM-ARC-020

The Elm desktop SHALL distinguish native effect receipts from native frame-presentation receipts and keep motion sampling and buffer retirement under native ownership.

#### Scenario: ELM-ARC-020 architecture-020

- GIVEN a motion effect accepted by authority
- WHEN the DOM animation callback fires
- THEN presentation is unproven until the native receipt

### Requirement: ELM-ARC-025

IF a compositor plugin does not match its recorded owning compositor ABI tuple, THEN the Elm desktop SHALL refuse plugin loading.

#### Scenario: ELM-ARC-025 architecture-025

- GIVEN a mismatched plugin build
- WHEN the shell starts
- THEN the plugin is not loaded and the mismatch is reported

### Requirement: ELM-ARC-028

WHERE native compositor replacement is selected, the Elm desktop SHALL require a separate feasibility record covering Wayland protocols, Xwayland, seats, outputs, rendering, IME, capture security and application compatibility before implementation admission.

#### Scenario: ELM-ARC-028 architecture-028

- GIVEN shell parity accepted
- WHEN compositor replacement is proposed
- THEN a separate scope and feasibility gate controls admission

### Requirement: ELM-ARC-029

WHERE native compositor replacement is implemented, the Elm desktop SHALL pass its declared compatibility matrix in nested and hardware sessions with sacrificial applications before any main-session activation.

#### Scenario: ELM-ARC-029 architecture-029

- GIVEN an optional native compositor candidate
- WHEN activation is considered
- THEN nested and hardware evidence precedes main-session use

