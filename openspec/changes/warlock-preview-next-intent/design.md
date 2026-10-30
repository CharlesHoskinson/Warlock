# Native intent succession

> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.

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
