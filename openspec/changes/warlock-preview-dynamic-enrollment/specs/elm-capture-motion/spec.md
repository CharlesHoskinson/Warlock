## ADDED Requirements

### Requirement: WARLOCK-ENROLL-001 Original receiver admission

WHEN the trusted GTK owner enrolls another native preview subject, the system
SHALL validate the original receiver epoch and binding before scope query,
intent retention or job reservation, and SHALL update subject membership and
reserve any job in one native critical section while preserving existing
receiver entries and readers.

#### Scenario: WARLOCK-ENROLL-001 Receiver grows

Given an own enrolled receiver and native source, when another subject joins,
then the receiver epoch and existing membership remain unchanged and the new
own membership becomes visible atomically with native admission.

#### Scenario: WARLOCK-ENROLL-001 Reused popup refuses

Given a popup identity registered again with another epoch, when the former
owner tries to enroll, then it creates no new scope, retained intent or job.

### Requirement: WARLOCK-ENROLL-002 Original unissued intent

WHILE native work waits for physical capacity, the system SHALL retain its
original binding, incarnation, clock, publication, lease and deadline, SHALL
refuse identity changes or deadline renewal, and SHALL refuse issuance after
the original deadline even if physical capacity has returned.

#### Scenario: WARLOCK-ENROLL-002 Capacity returns in time

Given a waiting unissued intent, when original physical ownership retires and
capacity returns before its cutoff, then the admitted job uses the original
deadline and its own original request domain.

#### Scenario: WARLOCK-ENROLL-002 Capacity returns too late

Given an expired waiting intent, when capacity returns or retry supplies a new
cutoff, then no job or terminal proof is invented and the old cutoff persists.

### Requirement: WARLOCK-ENROLL-003 Local scheduling outcomes

WHEN dynamic native enrollment cannot issue a job because of capacity, expiry,
identity conflict or missing readiness, the system SHALL return typed local
scheduling feedback without fabricating a native Refused, evicting original
ownership or advancing an unissued actor's request floor.

#### Scenario: WARLOCK-ENROLL-003 Two items remain owned

Given two charged physical items, when a third subject requests enrollment,
then it receives Capacity with no job or terminal proof and both original
charges and journal records remain owned.

#### Scenario: WARLOCK-ENROLL-003 Duplicate enrollment

Given an already issued original job, when its identical subject and stamp are
enrolled again, then the result identifies retained work without replaying
capture or issuing another job.

### Requirement: WARLOCK-ENROLL-004 Original journal settlement

WHEN a newly enrolled subject has an actual terminal native proof, the system
SHALL deliver it only after explicit subject admission through the same owning
bootstrap and original journal, and SHALL retain physical retirement and exact
final ACK obligations for every old and new issued job.

#### Scenario: WARLOCK-ENROLL-004 Membership alone cannot settle

Given new pixel membership and a retained new terminal proof, when receipt
subject extension has not occurred, then neither delivery nor ACK is admitted
for that new subject.

#### Scenario: WARLOCK-ENROLL-004 Physical drain precedes settlement

Given actual imported mappings and held URI readers, when an entry is released,
then its backend, consumer, mapping and FD ownership retire before terminal
settlement, and its exact final ACK leaves other original jobs intact.
