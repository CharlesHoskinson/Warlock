# Stable surface publication

EARS: When pure desktop state changes but the complete native surface packet remains byte-equivalent at the current publication/lease, no lease transition is required, and no desktop effect is emitted, the controller shall retain publication/lease and store the updated desktop state.

EARS: When the surface packet changes in any field, or a desktop effect must be dispatched, the controller shall retain its existing publication and delivery behavior. Native proof and DOM callback guards shall remain unchanged.

OpenSpec: Given a closed bar and an admitted pointer proof, when only the internal presentation owner changes without changing its surface packet or emitting effects, then the actual compiled controller stores the new owner, emits no Publish, and the native proof remains scoped to its original publication.

OpenSpec: Changing a control identity, enabled state, status, mode or lease must produce a new publication and invalidate the old proof. A nonempty effect list must not be coalesced by this new rule. Existing applications-only SupersedeObservations behavior is preserved independently. Focus/epoch loss still invalidates a proof even with unchanged publication.

The model abstracts packet identity using status/target/enabled/mode/lease. Actual Elm compares the entire encoded Surface.packet. Model/compiled CPU checks are separate from native acceptance and cannot causally close504 by themselves.
