# Private keyboard capability and focus loss

Fresh protocol7 derivative of146, using the existing same-UID exclusive
controller and private Weston fake keyboard. No installed or physical seat is
changed. Parent done receipts remain admission only.

Keyboard-capability0 shall require exactly one keyboard-device reference and
call owning weston_seat_release_keyboard without earlier key releases. The
real leave and capability events must reach the live child. Controller key
records remain until capability restoration; Weston retains its keys array
although it resets XKB state on removal. Keyboard-capability1 shall require
zero references, initialize the same private keyboard, then balance old parent
keys while keyboard focus remains null, before any new child keyboard binding.
No balancing release shall reach the lost child keyboard. Duplicate transitions
shall refuse. On controller destruction, a disabled held keyboard shall be
restored and balanced before control drops, for normal private-seat teardown.

Keyboard-focus0 shall require a live keyboard focused on the current pointer
surface and use owning weston_seat_set_keyboard_focus with null. It shall send
no earlier key release and remove no device/output. Keyboard-focus1 shall
require null keyboard focus and a current pointer surface. It shall focus that
surface through the owning API. Duplicate transitions shall refuse.

An owned physical key release may be admitted with null keyboard focus without
manufacturing focus. Unknown keys, unpaired ups and duplicate downs still refuse.
Other key requests retain146 focus-consistency gates. Controller and seat
destruction preserve the existing balancing/retirement rules.

Native acceptance shall retain6s observation limits, real GTK key recipients,
Core input/shortcut/modifier ledgers, exact owning tuple, live pointer/output and
child identities, restored real key/pointer delivery, and ordered normal cleanup.
Device disappearance alone cannot accept held-key cancellation.
