# Framed transport owner

## Reference

`Warlock.Protocol.Ingress` exposes an opaque `IngressOwner`. `ingressBinding`
validates three canonical, nonzero counters for lifetime, session and frontend.
These are correlation data supplied by the caller; they do not authenticate a
peer or grant native authority.

1. Call `newIngressOwner` and retain its socket-free handle before offering a
   socket. Constructor failure owns no socket.
2. Call `transferSocket` from one exclusive offering caller. Before its masked
   publication the caller owns the socket; afterward the retained owner owns it.
   Inspect `accepted` on that already-held owner if interruption makes the return
   uncertain. A refused additional socket remains caller-owned. A shared,
   concurrent multi-offer protocol is outside this contract.
3. Call `activateIngress` without supplying another socket. Only successful flag
   configuration and channel construction publish `OwnerLive`. Setup failure and
   independent close failure remain visible through the retained owner.
4. Use `receiveIngress`, `enqueueIngress` and `sendIngress` only on a live owner.
   Checked callbacks execute outside the gate lock. Rejected or inactive work
   cannot grant authority. The current implementation provides caller-owned
   framed delivery, not an authenticated production GUI connection.
5. Call `retireIngress` through the owner. During setup it records retirement and
   defers close until setup releases its use. It blocks new admissions and keeps
   gate drainage distinct from endpoint closure. Do not independently close an
   accepted socket, retry an ambiguous raw descriptor, or infer closure from a
   returned exception or a retired gate.

`OwnerStatus` reports phase, accepted transfer, gate status, endpoint state and
setup/close diagnostics. It is a concurrent observation across separate cells,
not a native retirement certificate or one atomic system snapshot. An empty
owner has no endpoint. `EndpointUncertain` retains custody and never starts a
second physical close. An interrupted close that was not yet claimed can still
be attempted later; that is distinct from retrying uncertain closure.

`retainedIngressFrames` exposes queued bytes for inspection after retirement.
It grants no permission to replay. There is one ordinary slot and one reserved
control slot. Framing retains its 65,536-byte body limit and absolute five-second
read deadline, carried unchanged into gate admission. These transport deadlines
do not establish the original native effect deadline or bound callback runtime.
`SocketFlags.hsc` derives flag constants from the target headers and preserves
unrelated descriptor/status bits. It provides neither socket custody nor peer
identity. The raw channel constructor and test hooks remain package-internal;
the obsolete pre-publication adoption API has been removed.

## How to verify this component

Root serializes verification through the repository's protected CPU QA launcher.
The current host's GHC 9.6.7 SDK supplies dynamic interfaces, so builds use
`--offline --enable-shared --disable-library-vanilla --enable-executable-dynamic`
with private Cabal build/store directories. Run the boundary, ingress-controls
and owner-sequences suites. `ingress-controls` receives the absolute fixture
folder through `--test-options`; the root evidence records the exact commands.

The actual public composition passed 20 boundary checks, 23 owner controls and
256 reproducible sequences of 24 actions (seed 20261031, 132 live-positive cases).
Controls exercise real socket pairs, split/coalesced frames, the checked v2
server route, reserved control capacity, retained queued bytes, setup/close
failure facts and asynchronous handoff/retirement. Injected close faults test
source error handling; they do not prove every kernel close failure mode.

The first build exposed a five-field pattern for the six-field owner constructor.
After correction, the production build and boundary/owner suites passed; the
aggregate remained red because the new sequence fixture had a layout parse error.
The repaired sequence suite passed separately, rechecking hashes for all prior
inputs except that fixture. Both failed reports are preserved. No failed report
has been relabeled as passing. Test-only syntax repairs changed no owner policy.

## Explanation and remaining work

A pre-retained owner repairs an acquisition gap that returning `Either Channel`
cannot solve: cancellation can arrive before a returned channel is stored, while
cleanup is uncertain. Explicit transfer makes custody observable independently
of call return. Setup leases prevent retirement from closing a socket still in
flag configuration. Short finite state publications are protected; socket IO,
handlers and close actions run outside those state locks.

This supports ELM-TEA-005's validated Haskell transport and ELM-DEL-021's resource
retirement obligation. It accepts neither whole original scenario. Pinned Elm
replay, peer/launcher authentication, native authority and effects, full session
teardown, remaining framing/deadline faults, GUI/input/AT/IME, resource budgets,
complete reproducible packaging and reversible deployment remain open. The
legacy desktop schema remains different; there is no lossy adapter or claim of
a connected new GUI. Stopped decoder/capture histories remain unchanged.
