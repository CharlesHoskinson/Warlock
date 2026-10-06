# Native intent succession

The existing trusted GTK bridge may request a successor only for an unissued
actor whose current intent expired on the actual native clock. Both publication
and lease must strictly increase; owner, incarnation and clock remain exact.
The successor receives a native cutoff within the original two-second bound.
Polling at the same stamp retains its cutoff. The ledger retains one immediate
predecessor per actor and a current monotonic stamp, bounded by the existing
actor limit. Older stamps cannot become current again. Broker request floors,
receipts, ownership and physical limits are never reset.

The dynamic full host uses the explicit API for unissued subjects. Existing
issued/resume APIs retain their original behavior. The same immutable Elm
presenter admits current seeds, sequences and effects. This change does not yet
retire old actors, advance expired resume intents, qualify ordinary eligible
capture, or establish full native/release acceptance.
