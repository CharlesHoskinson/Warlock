# Shared provider ownership

This full GUI519 derivative integrates the demand coordinator with the actual URI endpoint's physical Broker. It refines scheduling/ownership contracts ELM-ADOPT-022/027 and preserves ELM-ADOPT-006/009/010/028. The native provider and its policy inputs remain trusted API prerequisites; this is not a wire capability decoder.

WHEN the trusted provider configures demand, the URI endpoint SHALL pin one native lifetime, clock, positive interval and exact actual Broker limits, and SHALL reject configuration replacement.

WHEN demand admits a capture, the URI endpoint SHALL use the same native Broker reservation and exact job for storage, reads, consumer ownership, cleanup and final receipt acknowledgement.

WHEN a revoked demand retains an open URI reader, the endpoint SHALL deny further reads and preserve storage charge until read references drain and actual consumer completion permits physical destruction.

WHEN an admitted job has been physically retired and exactly terminal-acknowledged before the scheduler next polls, the coordinator SHALL clear the capture slot using the owning Broker's certified record removal; it SHALL retain the Broker's request floor and SHALL NOT treat elapsed time, stream closure or a frontend flag as retirement.

The coordinator owns a Broker only in standalone component mode. Integrated mode borrows the endpoint's Broker and cannot move or copy its reference. Shared storage outlives retained Readers. All integrated native scheduling/access remains serialized by the endpoint mutex.

The inherited Quint abstraction is unchanged. Ten selected scenarios, 300 invariant samples and 22 actual C++ replays cover its existing projected scope. A separate actual GIO stream fixture covers shared storage, exact lifecycle interleaving, revocation and physical drain. Fixture PNG signature bytes do not qualify native pixels, hardware or family fidelity. The full optimized Elm package and actual C/C++ host build are compiled; own provider process grant/bootstrap, actual capture and EARS/native release gates remain open.
