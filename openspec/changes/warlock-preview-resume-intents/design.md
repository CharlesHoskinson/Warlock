# Ownership and intent

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
