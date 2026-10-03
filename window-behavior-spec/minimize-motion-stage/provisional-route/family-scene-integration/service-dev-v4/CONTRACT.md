# Family scene integration contract (before implementation)

Production remains helper6d9/widget65 with native V18. The owned-EGL v2 packet
is a frozen single-window producer and is not changed by this integration work.
This contract is the next service/renderer boundary; no native code is installed.

## One composite family scene

One renderer connection owns the family scene, one immutable texture per exact
member identity, and one output surface per generation. Each output commit has
one immutable scene record containing the entire ordered member identity/token/
digest/rectangle list. It uses a single progress sample for that rendering batch.
The feedback authority proves that exact composite scene's successful own swap,
not separate per-member CLI roundtrips or a later frame with different membership.

Each member route retains its native rectangle, decorated atlas rectangle,
captured pixels/insets, actual taskbar icon destination, and source digest.
Cross-output fragments clip the shared global geometry to actual output logical
bounds. Each output's reversal origin is its last actually presented composite
scene. Each member's geometry is derived from that output's recorded rectangle;
no clock-derived undisplayed position replaces the recorded origin.

## Early visual intent, late native authority

A captured same-identity action reserves a new scene epoch under the controller
lock before external metadata calls. All members of the last accepted exact
family scene lose old native authority atomically. That retained membership is
permission to move already displayed pixels only. The renderer starts the visual
reversal immediately using the retained atlas/icon endpoints and per-output
presented origins; it does not wait for family enrichment or new PNG capture.

A newly accepted third intent supersedes the second scene atomically, including
all held or displayed members. It reuses the currently displayed immutable
textures. Old metadata, ready, endpoint, focus-follow and cleanup callbacks cannot
commit native state or destroy the newer scene. Every asynchronous callback
carries the full scene epoch and exact identity vector.

Fresh client/native coverage and scoped parent-edge validation, as established
by the installed family planner, are still required before promotion. Partial
coverage, lookup failure and malformed selected edges never redefine a captured
family to a singleton. Explicit current detachment may produce a new smaller
validated scope; the transition must first present the exact replacement scope.
Newly attached members require new immutable captures and an atomic displayed
scene handoff while old pixels continue moving. PID equality is never a family
relation. A missing/reused identity cancels its old pixels and prevents promotion;
the captured family operation fails or is revalidated completely.

## Native commits and completion

The controller alone commits native minimize/restore/focus/pin-follow. It checks
fresh exact identities, latest accepted family epoch and reduced-motion policy
under its callback lock, then records each member's result. Minimize hides native
members only after the complete current scene was actually presented on every
required output. Restore switches the stored destination before expansion while
native members remain minimized; native geometry is never rescaled or moved by
the renderer. Native restore/show and family focus occur only at the validated
latest complete endpoint. Overlay removal follows successful native handover;
cleanup completion is distinct from native settlement and includes renderer ACK.

Reduced motion, output removal/reconfiguration, feedback discard/timeout, swap
failure, source close/reuse, service EOF or reload retires scene authority and
removes all its input-free surfaces. Settlement revalidates the latest accepted
native intent; an unvalidated provisional request cannot acquire authority merely
because it timed out. Renderer failures never leave a permanent frozen frame.

## Required implementation and evidence

The next renderer protocol must add immutable `members[]` scene records and
atomic scene epoch commands. A thread-safe service transport replaces per-peer
blocking QML IPC. Existing acceptance/completion semantics, backend opt-out,
family provenance, atomic reservations and idempotent stop remain unchanged.
Tests must include fresh family coverage, close/reuse of each member, third intent
while metadata blocks, mixed pin bits, output generations, stale callbacks and
exact original native geometry. Private native tests must measure actual composite
presentation timestamps through metadata delay and verify decorated pixels and
real taskbar endpoints. The single-window v2 native fixture does not prove this
family contract or production continuous motion.

## Reservation ownership before destination effects

A metadata worker returning a complete observation has no permission to switch
outputs/desktops. The controller reacquires its reservation lock, verifies that
its scene object is still current, then performs the entire destination selection
transaction under that same lock. A newer accepted reservation prohibits *all*
destination effects from the obsolete worker, even if its observation was valid
when collected. Post-effect ownership checks do not satisfy this rule.

A same captured identity may supersede its initial pending request while the
first family observation is blocked and members are not yet populated. It uses
the prior requested exact identity for routing only; no unknown family members
acquire native authority or textures from that reservation.

## Request during visual cleanup

After native handover has queued cancellation, a new request cannot retarget that
retiring renderer scene. It may reuse persistent exact-identity atlas caches, but
must prepare fresh output surfaces/generations and seed a new complete scene.
The old cancellation ACK can release only old source files that are absent from
the newer scene, and has no permission to settle or delete the newer request.

## Capture lease ownership

Every successful member capture remains in a local lease until the complete
current scene transfers that exact source list into its record. Partial capture,
output preparation failure, fresh family/geometry rejection or supersession
releases all locally leased member PNGs. This includes failures after every
capture has succeeded but before record assignment. A released older lease
cannot delete files transferred into the newer scene. Persistent exact-identity
full atlas caches are distinct from these temporary epoch PNGs.

## Callback observations do not block visual supersession

A presentation callback collects its fresh native family observation outside the
reservation lock. A new input can reserve and queue its retained-scene reversal
while that lookup waits. The callback then reacquires the lock and checks the
same scene object, exact epoch/vector, sources and policy before any native effect.
An obsolete observation never minimizes, restores, starts, follows focus or
switches a desktop. Only the actual per-member native commit transaction holds
the reservation lock; endpoint metadata lookup cannot freeze new visual input.

## Transport drain and native callback dispatch

The stdout reader drains and validates producer events independently of native
operations. A separate serialized callback worker processes only transaction
events through a bounded queue; stale queued epochs are rechecked by the
controller. A blocked family/native lookup cannot stop presentation/event drain
or the producer's output pipe. Queue exhaustion, malformed output, unexpected
EOF or write failure truthfully fails the actor, removes its surfaces, and
schedules native settlement separately. Failed shutdown is never reported as a
normal accepted exit. A normal close requires callback dispatch to finish within
the stated bound, not merely a renderer process exit.

## Multiple families and global reservation authority

Each exact captured ID/PID receives a globally ordered request receipt. Known
native family members route to their existing actor; PID equality has no routing
meaning. If two unknown peers create separate actors before enrichment, only a
complete fresh native graph may reconcile them. A family claim succeeds only
when no exact member has a newer accepted receipt. It atomically revokes all
older overlapping actors before destination, readiness or native commit effects.
An old queued callback or obsolete enrichment cannot reclaim those members.

The registry and each controller use the same reservation lock, including the
complete native effect transaction. Allocating a new receipt cannot interleave
between peers' native commits. Fresh metadata and captures run outside that lock.
Retiring an overlapping visual actor queues exact-token cancellation and retains
its temporary files until its own acknowledgement or confirmed process failure;
retirement confers no native settlement authority. Cleanup cannot delete current
sources. Family mappings survive normal minimize cleanup so the same actor's
persistent exact-identity cached snapshot remains available for hidden restore.

Membership/geometry replacement and an authoritative desktop-context provider
remain separate required work. The manager cannot turn caller-supplied context
into proof of current native desktop/output identity.
