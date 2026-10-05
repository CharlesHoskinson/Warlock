# Actual applied surface revision — additive native fact

- APPLY-01: WHEN the owning compositor applies any root or child surface state
  and texture, it SHALL advance that resource's native revision after application
  and before the synchronized-child notification suppression branch.
- APPLY-02: WHILE state is merely queued, its applied revision SHALL NOT advance
  from enqueue alone; an actual applied null attachment remains a new revision.
- APPLY-03: IF allocation, revision exhaustion or the bounded prototype registry
  cannot maintain a valid record, the native fact API SHALL return unavailable0,
  without inventing a successful capture or changing ordinary window policy.
- APPLY-04: WHEN a resource retires or the owning display is destroyed, its native
  revision records SHALL retire with that lifetime and SHALL NOT bind a reused
  resource address. Registry storage SHALL be owned by the display destroy hook.

Use a free API and a fresh owning core/plugin pair. No existing compositor class
layout/header is changed; only the actual Compositor.cpp translation unit changes.
The prototype65536 surface cap is bounded admission, not measured S02 acceptance.
One fresh core retains all205/470/450/89/73 archive members except that unit and
AQ155. No original native or full release gate is closed by compilation/model
checks. Validate actual synchronized/desynchronized child state and pixels next.
