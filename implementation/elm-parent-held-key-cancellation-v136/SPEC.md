# Held keyboard cancellation before parent retirement

Fresh derivative of frozen AQ120. Public headers, class layout, owning Core89
ABI and all AQ120 exports shall remain unchanged. Pointer cancellation and
parent transport/output/poll/publication fences shall remain intact.

The backend shall keep an event-loop-owned private keyboard ledger with 768
bounded evdev key slots. It shall admit an in-range key transition only for a
current keyboard of a live parent backend. Duplicate downs and unpaired ups
shall emit nothing. Ledger mutation shall precede consumer callbacks.

When the parent transport fails, the backend shall fence parent work first,
then release each recorded held key while consumers still own their keyboard.
It shall clear the private key and modifier records before callbacks and retain
a strong keyboard snapshot until all cancellations finish. It shall emit no new
presses. It shall emit one zero modifier event for each keyboard with held keys
or a recorded nonzero modifier state. Repeated cancellation shall be silent.
Only after cancellation shall devices and outputs retire.

Late key/modifier callbacks from a failed parent or retired keyboard shall emit
nothing. Keyboard destruction shall erase its private ledger. Cancellation on
keyboard capability removal and ordinary focus leave is outside this slice.

Quint shall model one keyboard with two abstract key identities and cancellation
ordering. Actual C++ checks shall separately cover the 768-slot boundary,
modifier-only state, reentry and multiple strongly retained objects. These are
separate evidence; no model refinement or native acceptance follows from them.
Native acceptance requires the unchanged V135 recipient and Core key/modifier/
shortcut assertions, exact owning ABI tuple and normal protected cleanup.
