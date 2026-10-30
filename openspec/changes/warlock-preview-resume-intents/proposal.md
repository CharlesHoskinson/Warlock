# Retained preview resume intents

> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.

Resume currently lacks the original receiver guard, recalculates a deadline on
capacity retry, and expects every issued native job to be Started. Correct those
three behaviors through the existing native allocator and single Elm policy.
This additive contract retains the frozen 242/417 and separate right-click24/48.
It does not establish original S09 or full release acceptance.
