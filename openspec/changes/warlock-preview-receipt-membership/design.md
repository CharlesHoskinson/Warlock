# One receiver and one retained journal

Endpoint.nativeView serializes receiver lookup, epoch validation and broker inspection under the same existing native mutex. ReceiptDelivery records immutable entry/incarnation correlations. extendSubjects reads actual current native view membership and scopes, validates the entire union in a temporary map, then commits it. A frontend provides no subject list, scope, binding or epoch.

Existing subjects remain admitted for their original jobs even when source facts advance. Extension refuses any changed old incarnation, foreign native binding, wrong lifetime, duplicate incarnation, removed old membership, closed/reused receiver or capacity violation without partially admitting a valid prefix. Refusal does not destroy allocations or consume receipts.

pending and acknowledge validate the same receiver epoch atomically with journal access. New subjects cannot deliver or acknowledge until explicitly admitted. Receipt delivery repeats original terminal proofs; only the exact original final ACK removes a broker record. Stream closure, native consumer completion, physical destruction and terminal ACK remain distinct obligations, with original jobs, clocks, deadlines and request floors retained.

Qualification: full optimized GUI build, actual ASAN/UBSAN GIO ownership tests and explicitly selected coupled Quint traces. Then owning core/plugin native multi-entry growth and integrated ordinary eligible capture. Native101 qualified previous GUI54 and cannot qualify this source.
