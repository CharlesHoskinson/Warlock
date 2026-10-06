## WARLOCK-RESUME-005 Exact terminal correlation
WHEN a terminal receipt arrives, the system SHALL acknowledge it only after
settling an exact known job or matching a retained exact terminal job and sequence.
### Scenario: future job proof
Given the prior job settled and the next job not registered, an early next-job
proof produces no ACK and cannot consume native ownership or advance Elm history.
### Scenario: exact replay
A repeated exact settled job and receipt sequence can repeat its ACK after a
delivery loss without recreating capture, changing the next request or inventing
ownership. Store one terminal tuple per lifecycle, retaining native journal and
floor authority.
### Scenario: altered replay
Changing the receipt sequence or full job identity cannot reuse terminal history.
