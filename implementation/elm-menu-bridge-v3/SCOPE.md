# Shared window-authority menu bridge

Fresh derivative of Menu V2 and the shared desktop lane's V79 Shell/Effects
engine. The adapter must call that engine to allocate commands, register the
actual generated native tuple before forwarding, and retain the independent menu
receipt ledger through dismissal, frontend rebind and other window operations.
It must never allocate a parallel native intent sequence or infer application
state from receipt hints. Registration refusal prevents forwarding an unsent
command; it must not erase a previously forwarded pending operation.

NativeProvider derives only Restore/Minimize capabilities from an already
admitted Shell observation. It requires explicit registered provider and actual
presentation-output identities from its caller; the native context output field
is an output generation, never a substitute output identity. Provider publication
does not authenticate a connection or authorize its sender.

External fixtures must exercise actual attached/action-projection inputs,
engine-generated command IDs and native outcomes. Cover disabled and stale opens,
duplicate activation, a pending engine unrelated to the menu, native refusal,
Unknown followed by same-target rebind, and a delayed original receipt after
another window completes. Observations must change only from admitted projections.

This production adapter is the next integration seam, not a second desktop
controller. Shared bar/popup rendering, host gesture provenance, authenticated
callbacks and fresh native acceptance remain subsequent gates. All original
roadmap and right-click requirements remain in scope.
