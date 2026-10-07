# Ordered visual custody — bounded component qualification

Native creator-owned `WarlockVisualChannel` keeps a strong reference to its
attached native context, one pending visual snapshot and exact expected receipt.
Its renderer lease and visual sequence are separate monotonically increasing
UInt64 counters. They never issue or consume original native control ordinals.
Detach retains both floors; replacement requires detach then a new native lease.
Exhaustion refuses without resetting either counter.

The channel derives its domain and visual fields through the GUI118 read-only
getter. Offer invalidates earlier acceptance and issues a new visual sequence.
Retry copies the exact pending packet without invoking Elm or allocating another
sequence. Ack requires byte-exact latest receipt from the attached native context.
Retry, ack and current checks compare the snapshot with the same policy's latest
committed visual bytes; a changed/closed/uncertain cache removes visual custody.
Foreign threads/contexts and stale receipts refuse. Normal destruction requires
detachment and does not close a policy, settle an effect or retire resources.

`NativePreviewReceiver` holds only a validated projection, native grant, ordering
floor and concealment latch. It imports no window/lifecycle policy. A native
grant is fixed at initialization; incoming packets cannot establish or replace
authority. Older sequences and other domains/leases are ignored. Exact duplicates
repeat only the acceptance receipt. Conflicting same-sequence visual data or a
malformed current channel/projection conceals and latches uncertainty; a packet
cannot reset that instance. A recreated renderer needs a new native-issued grant.
The browser component compiles but no HTML/adapter/native host route activates it.

This component's receipt establishes pure receiver acceptance, not actual DOM or
frame application. GObject fixture identities do not qualify actual WebKit callback
authentication. Cache comparison establishes currency at that check, not ongoing
freshness or concealment between policy transitions and async WebKit evaluation.
The real host must physically conceal before policy changes/invalidation, bind
the actual WebKit instance and callback to its native lease, reject old async
completions, qualify DOM/frame application and original URI reader lifetime, then
reveal only with that full native barrier. No such host route is active yet.

Qualification passes67 actual C/JSC/pure receiver checks and33 native missing
destination/context/policy/receipt, absent/closed/destroyed custody boundaries.
Quint executes14 selected native custody scenarios and200 invariant samples;
26 traces compare451 observable states against actual sanitizer C/JSC with
normal fixture/policy teardown. Four compiled unsafe guard derivatives are
detected; the early-destroy variant also fails sanitizer ownership. Two separately
labeled seeded native counter builds preserve original exhaustion guards and
normal teardown. The pure receiver's maximum-sequence stress packet is explicitly
synthetic and is refused by native acceptance because native did not issue it.
The original native207 controls plus90 visual/74 getter comparisons still pass;
parent policy/getter/lifetime/backpressure/native issuer/physical/assets/adapters
stay byte-identical. Full115 commands retain112 and add two pure renderer builds
and native channel compilation/link. One new-header compile failure remains
with its exact original input snapshot. No original deadline or oracle is weakened.

Next: freeze/publication, current legacy native source requalification and actual
host integration with durable original input/ticket custody and bounded retry.
Uncertain worker/process recovery, delayed proposal outcome/order, actual native
captured FD/render/fence/readers, >256 native windows and all full release gates
remain open. Native130 remains the actual bounded legacy2518/278 baseline.
