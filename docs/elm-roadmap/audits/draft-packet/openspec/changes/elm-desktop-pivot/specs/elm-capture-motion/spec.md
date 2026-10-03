# elm-capture-motion

## ADDED Requirements

### Requirement: ELM-REN-001

The project SHALL preserve the original 38 restore-baseline, 34 fault/recovery and 52 drag/resize scenario identities and deadlines in a fresh acceptance ledger.

#### Scenario: ELM-REN-001 ren-001

- GIVEN an archived campaign
- WHEN a new derivative is inventoried
- THEN all original IDs, hashes and deadlines remain linked

### Requirement: ELM-REN-002

The native host SHALL own GPU buffers and expose opaque identity-bound frame leases to Elm without sending pixels in port JSON.

#### Scenario: ELM-REN-002 ren-002

- GIVEN a captured native frame
- WHEN Elm requests a preview
- THEN only bounded metadata and a lease key cross ports

### Requirement: ELM-REN-003

WHEN a capture source stops, the native renderer SHALL retain the last independently owned accepted frame until its lease is retired.

#### Scenario: ELM-REN-003 ren-003

- GIVEN an accepted retained frame
- WHEN the source context ends
- THEN the same frame remains drawable without live source ownership

### Requirement: ELM-REN-004

WHEN a window incarnation is replaced, the native host SHALL revoke its frame leases before accepting previews for the replacement.

#### Scenario: ELM-REN-004 ren-004

- GIVEN an old lease and reused window address
- WHEN the incarnation changes
- THEN old pixels cannot appear as the replacement window

### Requirement: ELM-REN-005

The native renderer SHALL associate motion samples and presentation receipts with one documented monotonic clock domain or an explicitly measured clock mapping.

#### Scenario: ELM-REN-005 ren-005

- GIVEN host and renderer clocks
- WHEN a motion receipt is recorded
- THEN its clock origin and correlation are explicit

### Requirement: ELM-REN-006

WHEN minimizing a window, the native authority SHALL preserve its normal workspace identity and restore geometry without moving it to a scratchpad.

#### Scenario: ELM-REN-006 ren-006

- GIVEN a normal workspace window
- WHEN minimize commits
- THEN workspace identity and restore geometry remain available

### Requirement: ELM-REN-007

WHEN restore motion begins, the native renderer SHALL use the accepted retained frame until an identity-matched live frame is ready for a continuous handoff.

#### Scenario: ELM-REN-007 ren-007

- GIVEN a minimized window with a retained lease
- WHEN restore starts
- THEN retained pixels bridge to the matching live frame

### Requirement: ELM-REN-008

The restore pipeline SHALL retain the original two-second deadline and its original start event across capture, retries, uploads and presentation checks.

#### Scenario: ELM-REN-008 ren-008

- GIVEN a restore with an original deadline
- WHEN a helper retries near expiry
- THEN the remaining budget is not renewed

### Requirement: ELM-REN-009

IF cancellation invalidates a motion generation, THEN the native authority SHALL reject further effects and retire only resources owned by that generation.

#### Scenario: ELM-REN-009 ren-009

- GIVEN a cancelled motion generation
- WHEN a delayed receipt arrives
- THEN no new native effect occurs and unrelated leases survive

### Requirement: ELM-REN-010

WHEN motion reverses between minimize and restore, the renderer SHALL start the new trajectory from the last presented geometry of the current transaction.

#### Scenario: ELM-REN-010 ren-010

- GIVEN motion is halfway presented
- WHEN the user reverses it
- THEN the new trajectory starts at the last presented geometry

### Requirement: ELM-REN-011

WHILE reduced motion is enabled, the native host SHALL complete the same minimize and restore state transitions without decorative motion.

#### Scenario: ELM-REN-011 ren-011

- GIVEN reduced motion is enabled
- WHEN restore commits
- THEN the final state matches the animated route without decorative motion

### Requirement: ELM-REN-012

The capture service SHALL enforce declared limits on outstanding frames, native pixels and helper processes and publish refusals rather than silently reuse stale pixels.

#### Scenario: ELM-REN-012 ren-012

- GIVEN the declared capture limit is reached
- WHEN another frame is requested
- THEN a refusal occurs without stale identity substitution

### Requirement: ELM-REN-013

WHEN a capture transaction ends, the native supervisor SHALL verify closure of owned helpers, callbacks, buffers and surfaces before reporting retirement complete.

#### Scenario: ELM-REN-013 ren-013

- GIVEN a capture owns a helper and frame
- WHEN the transaction retires
- THEN both exit and release evidence accompany completion

### Requirement: ELM-REN-014

The capture service SHALL label preview fidelity for client content, decorations and modal or popup extents according to independently verified native coverage.

#### Scenario: ELM-REN-014 ren-014

- GIVEN a decorated modal family
- WHEN a preview is produced
- THEN its recorded bounds match actual covered pixels

### Requirement: ELM-REN-019

WHEN an output scale, transform or generation changes, the native renderer SHALL invalidate incompatible frame geometry and rebuild presentation against current output truth.

#### Scenario: ELM-REN-019 ren-019

- GIVEN a preview spans mixed-scale outputs
- WHEN scale or rotation changes
- THEN stale output geometry is rejected and current pixels align

### Requirement: ELM-REN-021

WHERE 240 Hz hardware is available, WHILE motion is active, the native renderer SHALL sample motion in its native presentation loop and record cadence against a same-machine baseline.

#### Scenario: ELM-REN-021 ren-021

- GIVEN documented 240 Hz hardware and baseline exist
- WHEN motion workload runs
- THEN native cadence measurements and comparative budgets are published

### Requirement: ELM-REN-022

The release gate SHALL distinguish renderer receipts from independent presentation evidence and report latency, memory, wakeups and resource growth against the chosen host baseline.

#### Scenario: ELM-REN-022 ren-022

- GIVEN profiling is enabled
- WHEN results are evaluated
- THEN queue receipts are not counted as displayed-frame proof

