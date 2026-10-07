CONTROL-021 adds borrowed receipt ownership to the CONTROL-020 lifecycle model.
Seventeen named scenarios are explicitly selected. The actual compiled replay
uses the original native Bootstrap and its ReceiptDelivery for every owner,
then the strict Bootstrap-aware C close. After every event it compares native
active claim, actual Bootstrap attached state, receiver grant epoch, job/actor/
proof counts, terminal state, C empty predicate and operation outcome. Protocol
history `through` and `phase` remain excluded from native comparison. A separate
actual native peer/Bootstrap exercises foreign-owner refusal at full readiness.

Original C physical, terminal-proof, actor, final-processing and independent
confirmation guards remain before release. The Bootstrap preflight validates
exact Native pointer, creator thread, Endpoint, receiver epoch, empty receipt
membership, empty receiver entries, zero readers/records/actors/charge. It does
not supply another resource oracle or advance native policy. Only after original
control quota closure and Native claim completion does it release the borrowed
delivery before Endpoint deletion. Refused close leaves it available to drain.

The native bindings remain unchanged across owners. Lookup/polling after close
must refuse safely; subsequent actual C ownership attaches a fresh channel under
its greater native epoch. Model mutants separately retain the borrowed receipt,
reset receiver epochs, or complete a claim before strict close. The receipt
retention witness compares its actual attached state after close and performs
normal owned teardown without dereferencing the destroyed Endpoint.

The standalone C witness also stops the original authenticated synthetic native
peer after settlement and before strict close. Local ownership validation does
not issue a fresh Native hello/binding query, so complete closure remains
possible after that peer exits. This is a CPU/native-socket witness; actual
Wayland Core qualification remains separate. These actor routes still require
permanent incarnation retirement and do not implement live-window detachment.
Renderer outbox, frontend realm scoping, current controlled Core/WebKit and all
original full release gates remain open.
