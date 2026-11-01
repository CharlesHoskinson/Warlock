# Desktop application stream

The current source integrates Elm Main with a bounded Haskell catalog/pin
backend. Protected executable and bridge checks pass. Complete original ARC003
and DEL011 are independently accepted on the [immutable source tuple](../../warlock-build-loop/v2/ui-backend-acceptance-20261101.json). This page asserts no native GUI or release acceptance. The
[shared contract](../../warlock-build-loop/v2/shared-desktop-contract-20261101.json)
records the reviewed schema and its provenance.

## Source and wire boundary

`implementation/warlock/src/Main.elm` exposes `incoming` and `surfaceCommits`.
Incoming values have exactly `bridgeProtocol`, `kind` and `payload`; the version
is 1. Trusted transport handlers supply the provenance discriminator. A web
payload cannot authenticate itself as a native event by naming that tag.

Outgoing values are complete `viewProtocol: 1`, `kind: "view-commit"` objects
with `projection`, `requests` and `focus`. Haskell validates every request and
binding before invoking the backend. An unsupported member refuses the entire
batch. Presentation-only commits have no domain operations. Projection and
focus data grant no native effects, and this backend emits no fabricated
presentation or admission acknowledgement.

| Trusted profile | Client limit | Server limit | Operations |
| --- | --- | --- | --- |
| Existing Native v1/v2 | 65,536 bytes | 65,536 bytes | Existing qualified schemas |
| Desktop application | 131,072-byte complete commit; at most 16 requests, each at most 8,192 bytes | 1,048,576-byte reply plus at most 128 gateway bytes | `catalog-request`, `taskbar-pins-write` |

Both profiles retain depth 16. Constructors select the profile before transport
use; payloads cannot select it. Kernel credential chunks remain at most 65,536
bytes. Existing absolute bootstrap and frame deadlines are preserved.

## Desktop inter-frame idle scheduling

The candidate desktop path calls
`receiveDesktopCredentialIngressAfterIdle` only after an authenticated frame has
been delivered. The retained owner waits for readability under its original
absolute session deadline D, then invokes the existing credentialed frame
receiver. Readiness consumes no payload or ancillary data and grants no trust.
The same channel read gate covers waiting and receiving; the ingress serial
covers delivery and dispatch. The owned leader watcher remains responsible for
observing exit and shutting the retained peer write direction.

The first receive and the Native profile keep their immediate five-second read
path. After desktop readiness, the absolute frame/admission deadline is the
smaller of receive-start plus five seconds and D. Header/body fragments renew
neither deadline. EOF, bad credentials, malformed data, retirement and expiry
remain failures; no heartbeat or synthetic domain request keeps the stream alive.
An already-admitted callback retains its existing drain contract: scheduling may
let its body start or finish after the admission deadline. That is separate from
admitting a new callback after the deadline or confirming cleanup.

The real-socket idle controls exercise kernel credentials with a same-process
fixture guard, including a known quiet interval above five seconds, seeded
fragmentation, stalled frames and original-D expiry. They do not authenticate a
held selected child. The selected-owner test's existing single catalog request
is in its fourth/final frame; the matching authenticated reply fences all four
frames before its controlled peer retires. HTTP204 alone is not consumption.
Current protected results and the actual VM outcome remain source-bound in the
canonical handoff; these contracts establish no native or release acceptance.

## Actual backend

The production executable is `warlock-ui-backend CONFIG`. Its Haskell
`loadBackendConfig` requires exactly `schema`, `binding`,
`deadlineMonotonicNs`, `ui`, `catalogRoots`, `pinsRoot` and `locale`. The trusted
startup image includes device/inode/size/hash/ancestor pins and startup arguments.
These paths and arguments are outside the web operation schema.

`Warlock.Backend.Catalog` scans real pinned desktop roots, preserves ordered
desktop identity precedence and refuses unsafe or incomplete traversal. A whole
reply that exceeds its count or byte bound becomes explicitly unavailable;
entries are never silently truncated. The entry bound is 2,048.

`Warlock.Backend.PinStore` uses fixed `taskbar.lock` and `taskbar.json` names in a
pinned private directory. The schema is 1. It requires private regular files,
single links, no-follow access, a nonblocking lock and revision CAS. `Saved`
follows file synchronization, atomic rename, directory synchronization and
readback. Uncertain publication yields `Unknown`; the owning conversation does
not replay that write. Pin identities are opaque, path-free names, validated
before domain I/O, and legitimate missing identities retain their order.

## Evidence boundary

ARC003 requires one incoming/outgoing stream, the recorded versioned schema and
matching intent/outcome bridge receipts with artifact hashes. DEL011 requires
both shell/unknown-method refusal and arbitrary-path refusal without operation
file I/O or command execution. All three original scenarios have independent
source-bound adjudication in the linked acceptance; decoder counts alone did not
close them.

The fixed QA route runs compiled Main against the actual production executable
and physical catalog/store files. Connected-host topology and native bootstrap
fixtures are explicitly labelled preconditions. Complete application commits
and actual replies cross the production transport unchanged. These checks are
separate from a rendered native desktop. Private HTTP/WebKit composition,
persistent UI lifecycle, native window authority, physical presentation/input,
AT/IME and release acceptance remain mandatory work.


## Presentation capacity

Applications retains the complete catalog and pin state. Normal presentation
shows eight body controls per page, with an explicit item range and total.
Search, close, refresh and recovery controls remain available. All application
and pin-management controls can be reached through page navigation.

An oversized presentation enters a disclosed compact mode with one body control
per page and an Applications/pin-count summary. The mode persists for the current
binding; query, refresh and reopening reset the page without regenerating the
oversized bar. Full names remain in the catalog, search and accessible names;
long visible action labels use an explicit, code-point-safe ellipsis.

The outgoing guard also applies to empty-request and unbound commits and checks
its own fallback. A locally omitted fresh pin write can leave Saving with a
truthful not-sent notice. An uncertain write retains its reservation and recovery
read. The existing7,023-check Elm campaign passes on this source; actual full
page traversal and worst-case metadata checks now pass:401complete frames, all
2,048entries,32full-length names and96pin-management actions.


A local cutoff for an exact, currently bound catalog/pin batch preserves existing
transport state so the next deliberate valid action can proceed. It still
settles only the omitted fresh proposal. Native, mixed, foreign, unbound and
genuine queue/scope refusals keep their existing handling. The owning-route
regression retained a32-case RED and passes the identical21-check oracle after
the fix, including Unknown with an allocated recovery read.
