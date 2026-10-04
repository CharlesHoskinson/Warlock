# Typed durable geometry intents: integration foundation

V275 extends the actual V268 recovery journal. Legacy schema-1 records remain
strictly readable and migrate unchanged under existing ownership rules. New
schema-2 records include an integer effectProtocol: protocol 1 accepts only
minimize/restore/activate, and protocol 2 only maximize/restore-geometry. Counter,
context/binding, status, ownership, capacity and namespace checks remain strict.
Receipt correlation includes the normalized protocol; a missing protocol remains
compatible only with protocol 1. A wrong protocol cannot settle Pending. Exact
host/broker correlation can suppress uncertainty across schema 1 and schema 2.
Protocol-1 informational recovery preserves the existing strict wire shape;
protocol-2 host-uncertain adds effectProtocol=2. Neither frame is a native command.

V275 passes 60 additional actual Python/filesystem checks, the unchanged inherited
19 abrupt-death/journal checks and 42 namespace/migration checks. V276 changes the
actual C host admission writer to emit schema 2 for both protocols and refuse
cross-protocol operations. Its strict compiler build and 47 C/Python filesystem
checks pass, including actual C records read by Python and geometry settlement.
The C/Python checks verify persistent representation and correlation, not native
geometry capability, eligibility, placement authority or displayed pixels.

V277 preserves a failed Quint parse: action functions omitted their return type.
V278 fixes that syntax in a fresh derivative and executes nine explicitly selected
named cases plus 1,000 invariant samples of up to 40 steps. This abstract model
covers receipt correlation, newer admissions, Unknown and no replay on reconnect;
it does not claim automatic refinement to C/Python/Elm or comprehensive architecture
verification. Its runner describes the actual limited contract.

No host program, geometry broker or Elm decoder is integrated or compiled by this
packet. The current accepted native GUI remains V268/V89. The new journal wire
requires a strict typed Elm geometry recovery decoder before production use.
Newer menu/core workers retain ownership of their paths and ABI pairs. Next:
compose the reviewed geometry broker with guarded begin/settle on both protocols,
carry typed storage failures and stale-action guard ordering into one Elm controller,
recover geometry Unknown into the shared allocator/transaction state, then run
original regression and fault/pixel/input cases on one coherent frozen tuple.
No requirement, sprint, release or deployment gate is completed here.

The three available UI/UX reviewers were resumed for read-only release audits.
Their conclusion is that the existing strategy covers the required behavior classes;
execution closure is the priority. See UI-UX-REVIEW.md. No native campaign or
installed/live desktop change occurred in this cycle.
