The native owner activates `native-actor-retirement-channel` with its exact
binding after the Elm presenter has that binding through an admitted entry or
catalog, before any retirement observation or legacy completion is accepted.
Activation selects the retained protocol for that immutable presenter lifetime.
Repeating the same activation is inert; a different binding, late activation,
or replacement cannot reset its prefix. Legacy facts remain usable only in the
unactivated historical protocol. Once activated, bare final facts are refused.

`native-actor-retirement-delivery` contains exactly `kind`, `deliveryOrdinal`
and `fact`. The nested fact is a strict `native-actor-retired` object. Ordinals
are canonical positive uint64 strings, independent of all native proof IDs.
Only the next ordinal may remove its exact ready, physically confirmed actor
from Elm, and only after the existing settlement/correlation/frontier checks.
That same pure transition advances the compact processing prefix and emits
`retire-delivery-ack` with the original binding and ordinal on the existing
output port. It emits no extra physical cleanup or terminal proof acknowledgment.

A strictly decoded original-binding duplicate at or below the processing prefix
only repeats transport acknowledgment. Gaps, malformed fields, foreign binding,
premature completion, receiver replacement, legacy downgrade and uint64 exhaustion
do not advance the prefix. Native retains byte-identical final records and
checks the original WebView/receiver epoch; compact Elm history is not a payload
authentication mechanism or a license to substitute a different native record.
Original source seeds, cutoff monotonicity, live neighbors and settlement
obligations retain their existing behavior. The bounded native journal stays
nonempty through processing-ACK loss and refuses close until confirmation.

Qualification requires selected Quint scenarios, actual compiled Elm state and
ordered-command comparisons, separately compiled guard mutations, and a compiled
C/native/Elm round trip with lost final delivery and lost processing ACK. Real
WebKit routing, captured resources and continuing native window turnover remain
separate gates. This document adds no GUI release acceptance.
