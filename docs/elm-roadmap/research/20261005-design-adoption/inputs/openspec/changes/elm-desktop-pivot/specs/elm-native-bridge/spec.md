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

#### Scenario: ELM-ARC-004 decoder-native-to-elm

- GIVEN an Elm decoder with a valid prior model
- WHEN malformed and unsupported-version native envelopes arrive
- THEN decoder records refusal, preserves the prior model and emits no effect intent

### Requirement: ELM-ARC-005

The Elm desktop SHALL attach request identity, compositor lifetime, frontend epoch, operation generation, window incarnation, output generation and expected native revision to window-effect intents.

#### Scenario: ELM-ARC-005 architecture-005

- GIVEN a known window and output
- WHEN an effect is requested
- THEN the serialized request contains the full authority tuple

### Requirement: ELM-ARC-006

IF an intent incarnation, authority epoch or expected dependency revision differs from current native authority, THEN the native authority SHALL refuse that request without mutation; reconciliation SHALL produce a new snapshot and never silently convert it into a commit.

#### Scenario: ELM-ARC-006 architecture-006

- GIVEN a closed and recreated window
- WHEN its old intent arrives
- THEN the new window remains unchanged

#### Scenario: ELM-ARC-006 stale-reconcile

- GIVEN a request refused on dependency revision mismatch
- WHEN reconciliation provides a current snapshot
- THEN the refused request remains terminal and a distinct freshly validated request is required for any later effect

### Requirement: ELM-ARC-007

The Elm desktop SHALL correlate each outcome with its request and represent Pending, Committed, Refused, Cancelled and Unknown as distinct states.

#### Scenario: ELM-ARC-007 architecture-007

- GIVEN a request whose connection drops
- WHEN its final effect cannot be proven
- THEN its state is Unknown rather than Committed

#### Scenario: ELM-ARC-007 receipt-pending

- GIVEN a request with unique identity and a fixture for Pending
- WHEN the fixture transition occurs
- THEN the correlated request has exactly state Pending and no other request changes

#### Scenario: ELM-ARC-007 receipt-committed

- GIVEN a request with unique identity and a fixture for Committed
- WHEN the fixture transition occurs
- THEN the correlated request has exactly state Committed and no other request changes

#### Scenario: ELM-ARC-007 receipt-refused

- GIVEN a request with unique identity and a fixture for Refused
- WHEN the fixture transition occurs
- THEN the correlated request has exactly state Refused and no other request changes

#### Scenario: ELM-ARC-007 receipt-cancelled

- GIVEN a request with unique identity and a fixture for Cancelled
- WHEN the fixture transition occurs
- THEN the correlated request has exactly state Cancelled and no other request changes

### Requirement: ELM-ARC-008

WHEN a dependent mutation is requested, the authority SHALL release it only after a correlated Committed prerequisite satisfies the same incarnation and generation; Pending, Refused, Cancelled and Unknown SHALL leave it withheld.

#### Scenario: ELM-ARC-008 architecture-008

- GIVEN restore followed by focus
- WHEN restore is still pending
- THEN focus is withheld until the required receipt

#### Scenario: ELM-ARC-008 prerequisite-Refused

- GIVEN restore is Refused for the requested incarnation/generation
- WHEN dependent focus is evaluated
- THEN focus remains withheld and no unrelated request receipt satisfies it

#### Scenario: ELM-ARC-008 prerequisite-Cancelled

- GIVEN restore is Cancelled for the requested incarnation/generation
- WHEN dependent focus is evaluated
- THEN focus remains withheld and no unrelated request receipt satisfies it

#### Scenario: ELM-ARC-008 prerequisite-Unknown

- GIVEN restore is Unknown for the requested incarnation/generation
- WHEN dependent focus is evaluated
- THEN focus remains withheld and no unrelated request receipt satisfies it

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

WHEN native effect admission executes, the authority SHALL validate cancellation, incarnation and dependency revisions in the same serialized critical section as its commit point; cancellation ordered before commit SHALL prevent mutation and retire that generation’s resources.

#### Scenario: ELM-ARC-012 architecture-012

- GIVEN a prepared restore
- WHEN Escape cancels before commit
- THEN restore is absent and owned helpers retire

#### Scenario: ELM-ARC-012 cancel-before-commit

- GIVEN prepared effect and cancellation compete at one native commit point
- WHEN cancellation is ordered first
- THEN no mutation occurs and only the cancelled generation resources retire

#### Scenario: ELM-ARC-012 commit-before-cancel

- GIVEN effect commits before native cancellation is ordered
- WHEN cancellation is processed afterward
- THEN the committed receipt is preserved, late cancellation does not claim rollback, and remaining resources retire

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

#### Scenario: ELM-ARC-015 queue-byte-limit

- GIVEN a queue at its configured byte limit
- WHEN replaceable observations and new effect work arrive
- THEN only replaceable observations coalesce; admission refuses new effects explicitly and both bounds remain respected

#### Scenario: ELM-ARC-015 queue-item-limit

- GIVEN a queue at its configured item limit
- WHEN replaceable observations and new effect work arrive
- THEN only replaceable observations coalesce; admission refuses new effects explicitly and both bounds remain respected

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

#### Scenario: ELM-ARC-028 optional-feasibility-admission

- GIVEN P1/P2 evidence and a separate scope decision exist
- WHEN native-compositor feasibility is admitted
- THEN a separate protocol/security/output/application scope record is required without depending on completed P6 shell release

### Requirement: ELM-ARC-029

WHERE native compositor replacement is implemented, the Elm desktop SHALL pass its declared compatibility matrix in nested and hardware sessions with sacrificial applications before any main-session activation.

#### Scenario: ELM-ARC-029 architecture-029

- GIVEN an optional native compositor candidate
- WHEN activation is considered
- THEN nested and hardware evidence precedes main-session use

### Requirement: ELM-REV-001

WHEN stale global scene state delays a valid activation, the authority SHALL reconcile current dependencies and use a distinct freshly validated request to reach a terminal result by the original deadline without waiting for unrelated scene activity to stop.

#### Scenario: ELM-REV-001 activation-progress

- GIVEN stable eligible target A and continuously moving unrelated B
- WHEN A is activated from a stale global observation
- THEN the old request remains refused; a distinct fresh request with safe current dependencies commits A within the original deadline

#### Scenario: ELM-REV-001 activation-invalid-target

- GIVEN target A is destroyed or its family/eligibility changes
- WHEN a stale activation is reconciled
- THEN no effect targets a reused incarnation and a terminal refusal is recorded within the deadline

### Requirement: ELM-REV-007

The bridge SHALL encode authority identities, generations, revisions and absolute native deadlines as lossless schema-defined canonical strings and reject numeric JSON values for those fields.

#### Scenario: ELM-REV-007 revision-007

- GIVEN two native incarnations above 2^53 differ by one
- WHEN both traverse Elm/JS ports
- THEN their strings remain distinct and numeric representations are rejected

### Requirement: ELM-REV-008

WHEN an event sequence gap occurs, the frontend SHALL withhold later deltas and new effect admission until a coherent reconciliation snapshot establishes a fresh contiguous watermark.

#### Scenario: ELM-REV-008 revision-008

- GIVEN sequence11 destroys incarnationI and12 reuses its address
- WHEN 11 is missing and12 arrives
- THEN 12 is withheld and no effect can target the reused address before fresh snapshot reconciliation

### Requirement: ELM-REV-009

The bridge SHALL preserve native order for chord press, repeat, release, Escape, cancellation, effect receipts and retirement receipts; observation coalescing SHALL exclude those control events.

#### Scenario: ELM-REV-009 revision-009

- GIVEN the preview observation stream is saturated
- WHEN Alt release and cancellation are admitted
- THEN both control events retain order and neither is replaced by a later observation

### Requirement: ELM-REV-010

IF reserved control capacity cannot admit a cancellation or receipt, THEN the authority SHALL stop new effect admission, invalidate uncertain pending generations and supervise reconciliation without silently losing cancellation.

#### Scenario: ELM-REV-010 revision-010

- GIVEN preview and reserved control queues are full
- WHEN Escape cancellation arrives
- THEN no new mutation is admitted and pending authority is invalidated/reconciled without a silent cancel drop

### Requirement: ELM-REV-011

IF a request identity is expired, retired or outside its bounded deduplication window, THEN the authority SHALL refuse it without mutation and record an expired-identity outcome.

#### Scenario: ELM-REV-011 revision-011

- GIVEN a committed request is evicted from the retained result cache
- WHEN its identifier is submitted again
- THEN the identifier is refused rather than treated as a new effect

### Requirement: ELM-REV-012

The authority SHALL measure effect and restore deadlines in one documented native monotonic clock domain, preserving their time origin through queueing and restart without wall-clock reinterpretation.

#### Scenario: ELM-REV-012 revision-012

- GIVEN an operation has an original two-second native deadline
- WHEN wall time jumps and the renderer restarts
- THEN remaining native time does not reset or jump with wall time

### Requirement: ELM-REV-034

The protocol schema SHALL version capability negotiation, lossless identities, queue classes, byte and item bounds, admission refusals and control-event failure outcomes before bridge implementation admission.

#### Scenario: ELM-REV-034 protocol-schema-complete

- GIVEN the proposed schema and required field checklist
- WHEN implementation admission runs
- THEN every required field, queue class and refusal outcome has a decoder fixture; any omission blocks admission

