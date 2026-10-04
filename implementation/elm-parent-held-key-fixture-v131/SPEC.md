# Private held-key connection-loss fixture

This fresh protocol6 derivative of fixture113 admits only Linux KEY_A=30 and
KEY_LEFTSHIFT=42 on the existing isolated Weston fake keyboard. It retains all
pointer protocol requests and exact private-runtime, UID, exclusive-controller,
PID/start, unique-peer and focused-surface gates. Parent admission is separate
from GTK delivery.

When a key request is admitted, the fixture shall reject duplicate downs,
unpaired ups, unknown keys and invalid states. It shall use owning notify_key
with STATE_UPDATE_AUTOMATIC. It shall focus only the already focused private
pointer surface; it shall reject another keyboard focus while keys are held.

When disconnect-held-key-child is requested, the fixture shall require a
nonempty exact owned key mask (A=1, left Shift=2), no held pointer buttons,
the exact focused keyboard and pointer peer, and the same live process start.
It shall destroy that one child connection before balancing the parent keys.
It shall not send an earlier key release, signal a process or touch the main
desktop. Ordinary and held-pointer disconnects shall refuse held keys.

On controller destruction, the fixture shall balance all owned keys and buttons
while their devices remain live. At seat destruction it shall only forget the
retired records. Old fixture113 and all old evidence remain unchanged.

The native oracle shall retain the six-second observation deadline and prove
actual GTK key presses before the fault, no physical key releases before it,
Core key and keybind ledgers, device/output/poll retirement, no later stale
delivery and normal ordered cleanup. A missing cancellation is a failed result;
device disappearance alone cannot accept recovery.
