# Additive EARS requirements

## WARLOCK-RESUME-001 Original receiver
WHEN a native preview resume is requested, the system SHALL validate the original
receiver binding and epoch under the admission mutex before native scope query,
intent mutation or job reservation.
### Scenario: receiver replaced
Given a retained job and replaced receiver, resume refuses without new query,
job, proof or request-floor advance; existing obligations remain owned.
### Scenario: creator thread
Given a resume from a foreign thread, the C bridge refuses without admission.

## WARLOCK-RESUME-002 Original cutoff
WHEN resume capacity is unavailable, the system SHALL retain the original
publication, lease, native identity and two-second cutoff across same-intent retries.
### Scenario: capacity returned
A same-intent retry uses the original cutoff after exact unrelated settlement.
### Scenario: expired retry
Capacity returning after that cutoff produces Expired with no new job or proof.
### Scenario: changed stamp
A pending intent refuses changed publication or lease without changing history.

## WARLOCK-RESUME-003 Issued rejection
WHEN the native Broker returns a real rejected issued job, the system SHALL
register its exact identity with Elm and retain its proof until exact final ACK.
### Scenario: rejected resume
Seed and request precede proof; Acquire performs no capture; wrong ACK preserves
the record, exact ACK settles only that job, and duplicate ACK cannot reset floor.

## WARLOCK-RESUME-004 Retirement
WHEN a source resumes, the system SHALL preserve old physical and journal
obligations until exact retirement and SHALL preserve monotonic request history.
### Scenario: retained proof
Old terminal proof blocks resume until its exact final ACK.
### Scenario: receiver loss cleanup
Receiver replacement cannot erase records or disable owned physical cleanup.
