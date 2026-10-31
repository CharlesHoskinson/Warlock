# Controlled Haskell bootstrap and peer authentication

This package integrates held executable selection, selected-process custody,
credential-aware framing and current-session admission. Warlock-authored runtime
code is Haskell; GUI policy remains Elm. It is a controlled one-frame bootstrap,
not a persistent desktop server or a native effect authorization service.

## Tutorial: follow one approved request

Read `test/Main.hs` with `fixture-peer/Main.hs`. Root independently pins the actual
built child's path, device, inode, size and SHA256. The resolver validates the held
inode and issues an opaque executable lease. The process core inherits only the
owned endpoint. A current registration scopes the real Session, executable and
endpoint identity. Each consumed stream fragment supplies kernel sender
credentials. After checked decoding, the same scope rechecks final admission;
the callback enters subsequent policy validation. The fixture exchanges an
explicit ACK and observes normal exit and independent resource retirement.

## How to run the controlled checks

From the parent Haskell directory, build the relative `cabal.project` with tests
enabled using the repository's protected CPU launcher and strict offline toolchain.
The `credential-peer-child` executable and `current-session-oracles` test must
come from the same source-bound build. The test takes the child absolute path,
device, inode, size and SHA256; independently derive those values from that exact
binary. The test's original controls deadline is five seconds; do not renew it
between its child cases. Keep output and actual source/toolchain hashes.

The test stanza alone enables `WARLOCK_SCOPED_PEER_TESTING`. Build the production
library separately without that macro. It exposes no admission-race hook.
Source records and machine-local qualified runner receipts are in
[qualification.json](qualification.json). Follow root's protected QA workflow;
an arbitrary unprotected `cabal test` does not provide those containment records.

## Reference: ownership and observable outcomes

The only exposed module is `Warlock.Bootstrap`. `newCurrentSessions` creates one
trusted current-session authority; `newRegistration` creates an opaque lifetime.
`newBootstrapOwner` retains the process, executable, socket and registration
owners before acquisition. `runBootstrap` uses a caller-supplied absolute deadline.
`retireBootstrap` settles those independent owners or retains uncertainty.
Read-only `bootstrapAuthObservation`, `bootstrapCredentialTrace` and
`bootstrapSelectedPid` carry no signal right or authentication grant.

`CredentialGuard refusal` belongs to the protocol package. Its paired fragment
and rank-N admission operations are a control interface, not an authenticator.
The runtime closes both operations over one opaque Scope. Kernel PID/real UID,
held executable identity, selected endpoint, process observation, owning thread
and current registration all constrain admission. GID is retained diagnostically;
it is not an additional grant. Do not use JSON PID, socketpair creator credentials,
a cookie or a caller-provided UID as a substitute.

Credential traces retain at most 64 rows and are not complete audit logs. The
fixture rejects empty or truncated vectors and compares their PID/UID/GID to
independent real process facts. `AdmissionObserved` records an attempt, not success.

## Explanation: retirement and the tested race

Publishing a newer registration retires the previous Scope before exposing the
replacement. An old cleanup cannot revoke a newer registration. Fragment checks
do not create a durable grant. The exact-window test pauses after real final
authentication and before the finite Scope admission claim; replacing the session
there must refuse the old callback. The newer child must still be admitted after
old cleanup. Already admitted callbacks retain their normal drain contract.

The refusal fixture handles only exact ECONNRESET in explicitly expected-refusal
reads. Closing an endpoint with unread incoming bytes can reset the child; all
other I/O errors and positive ACK failures still fail the fixture. This is separate
from confirming socket, reader, process, transfer and executable retirement.

## Verified scope and remaining work

The recorded strict five-package/test build and all six controlled credential
cases passed. Eleven related suites passed on unchanged non-runtime sources.
Earlier compile and runtime failures are retained, including the original reset
failure and its exact-child reproduction. These checks establish neither a real
cross-user credential trace nor a native effect, persistent Elm connection,
GUI presentation, asynchronous teardown completeness or full ELM-DEL-010/release
acceptance. See the qualification record for the exact bounded source tuple.
