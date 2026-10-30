# Ownership and intent

> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.

Each retained Frame owns at most one pending resume intent: original binding,
incarnation, clock, publication, strictly newer lease, and native cutoff. The
Frame's prior job anchors its request floor and physical/journal retirement.
The first available own observation fixes a two-second cutoff; repeated same
intent observes current availability without rewriting that cutoff. Changed
publication or lease conflicts with pending history, including expired history.
Distinct later unissued intent and bounded lifetime retirement require separate
explicit design; expiry cannot erase history or authorize replay.

Receiver validation and resume admission share Endpoint's original mutex.
Both dynamic and legacy C resume use their captured receiver epoch and creator
thread. Cancel, release, physical drain and terminal settlement keep existing
ownership paths; receiver loss cannot erase those obligations.

Typed local Capacity/Expired/Conflict/NotReady outcomes have no fabricated job
or proof. Every real Broker-owned issued job, including NativeRejected, replaces
the Frame only after old exact physical/journal retirement. Its seed/request is
registered in Elm before proof delivery; Acquire on a rejected Frame returns no
capture. Broker floors and receipt history remain authoritative.
