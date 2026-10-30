# Elm and Haskell ownership

Every Warlock GUI element belongs to Elm. Its pure update functions own visible
interaction state and describe requested effects. Haskell owns backend and
reviewed runtime integration. Each decision has one owner: moving a native
mechanism into Haskell must not introduce a second implementation of Elm's
window-action policy.

An interaction crosses more than a codec. A correlated request must retain its
session, original selection, full-width identities and original monotonic
deadline through admission, native execution, observation and durable terminal
acknowledgement. A historical result or read-only lookup cannot create fresh
permission, replay an attempt or renew a deadline. An uncertain delivery remains
uncertain until the owning boundary supplies the required evidence.

Opaque validated constructors and explicit errors constrain these transitions.
Strict raw-byte validation belongs before parsed values enter Elm. Codec
roundtrips, pure sequence properties and Quint models test different parts of
the contract; none establishes the identity of a real producer, native effect
ordering, physical input, accessibility or resource retirement by itself.

## Native integration remains a design gate

The current native candidate has recorded behavior tied to its original
compositor and source tuple. The replacement must preserve the original atomic
commit/cancellation and resource-retirement obligations. A command socket and
later state notifications have not established that contract. Reclassifying
Warlock-authored legacy native mechanisms as external dependencies would not
satisfy the new language requirement.

A Haskell host using an inventoried public compositor-library ABI is a possible
feasibility route. It remains a proposal until actual bindings, ownership,
callback ABI, event ordering and required compatibility are demonstrated.
Optional compositor feasibility does not remove mandatory Omarchy compatibility
or authorize switching the user's desktop.

## Preparation and implementation

The user authorized an active preparation loop to finish the architecture,
interfaces, dependencies, specifications, workflow plugin and proportional
verification. Muse checks its continuity and EARS fidelity every 20 minutes.
The final implementation loop requires a reviewed readiness checkpoint; a future
user pause still stops automatic continuation.

The [governed language revision](../../elm-roadmap/LANGUAGE-REVISION.md) changes
five implementation-language statements while retaining the frozen baseline,
all original scenario objects and every verification statement. No acceptance
automatically transfers to a new implementation. Use the
[completion workflow](../../warlock-build-loop/v2/INSTRUCTIONS.md) and its source-bound
records to distinguish preparation results, integrated behavior and acceptance.
