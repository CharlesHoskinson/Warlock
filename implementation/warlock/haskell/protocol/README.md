# Haskell protocol boundary

This package contains the checked protocol boundary and caller-retained framed
transport owner, supporting original ELM-ARC-004 and ELM-TEA-005. Production source is
Haskell; GUI behavior remains Elm. Historical C/legacy bridge acceptance does not
qualify this port. The stopped host-capture campaign is a separate record.

## Tutorial

The boundary must validate bounded bytes before decoding a versioned envelope,
record a refusal reason on rejection, and invoke no effect handler for rejected
input. A decoded envelope is data, not native authority. A valid positive route
must remain reachable so rejection tests cannot pass by disabling all work.

## How to verify

Use the root-serialized protected QA launcher for the strict package build,
negative and positive route fixtures, independent Quint/corpus correspondence,
and seeded properties. The strict offline library build, 20 named gate checks,
23 actual socket-pair owner controls and 256 lifecycle sequences of 24 actions
passed; 132 generated cases reached a live owner. The actual public Elm peer passed 15 refusal checks and three
preserved late-cancel properties with 1,000 fuzz cases each. These are component
results. [qualification.json](qualification.json) preserves the earlier protocol
wave; [transport-qualification.json](transport-qualification.json) records the new
owner composition, including failed compiler attempts and the targeted repair.

The installed GHC 9.6.7 SDK provides dynamic interfaces. Use
`cabal v2-build all --offline --enable-shared --disable-library-vanilla --enable-executable-dynamic`
and the same build-mode flags with `cabal v2-test all`. Root runs both through the
protected launcher with a private build/store. The failed default static-way
build is preserved; the SHA provider was not replaced.

## Reference

`Warlock.Protocol.StrictJson` provides opaque positive byte/depth bounds and a
strict UTF-8 JSON decoder. It rejects duplicate object keys, invalid UTF-8,
embedded NUL, malformed or trailing input, and exceeded bounds. Its constructors
produce JSON data, never authenticated session or compositor permission.

The parser preserves the qualified private `terra-4-v2` source behavior
(SHA-256 `6565ce760f12971333eef317029a2484ad0f37705b3e2135ea4e9e6c0328240b`);
only the obsolete uncompiled-proposal comment changed during integration. The
initial gate and fixed-SHA codec are integrated from the source-reviewed v17
packet. Root additionally forces bounded rejection history and state before MVar
publication, aligns nonnumeric-version rejection, and supplies a typed internal
envelope eliminator. Framed caller-owned transport is now integrated; peer
authentication and a live GUI connection remain incomplete. The
[handler model](formal/README.md) has bounded directed and sampled evidence,
including an explicit zero-random-Busy coverage gap.

## Explanation

ELM-ARC-004 also requires the Elm decoder to preserve its prior model and emit no
effect intent after malformed native input. Parser checks alone do not establish
that obligation, actual authenticated transport, native authority, or full
scenario/release acceptance. Keep those missing observations explicit.

The imported schema codec supports its recorded v1/v2 `version`/`kind`/`body`
envelopes. The coherent new Elm peer uses v2. The legacy desktop instead uses
`protocolVersion` and different fields; this package does not silently translate
that schema or establish a working legacy-desktop connection. The new Elm
refusal-diagnostic path is implemented and exercised as a reducer; its live
framed delivery connection still requires integration.

The public gate is opaque. The [transport reference](TRANSPORT.md) describes the
usable owner shell, explicit socket transfer, activation and retirement. Valid
schema/current binding admit a callback, not native permission. Peer authentication,
request deduplication, original effect deadlines and native-effect authorization
remain open. Transport tests do not establish those missing routes.

The [acquisition model qualification](formal/ACQUISITION.md) records 26 directed tests and 1,000 sampled traces of 30 steps, with source correspondence assumptions and remaining concurrent-return limits.

The separate [Haskell runtime](../runtime/README.md) now joins kernel sender credentials to current selected-session admission through `CredentialIngress` and a paired `CredentialGuard`. The generic protocol guard itself authenticates nobody. Its controlled real-child cases are source-bound component evidence; cross-user, persistent GUI and native-effect obligations remain open.
