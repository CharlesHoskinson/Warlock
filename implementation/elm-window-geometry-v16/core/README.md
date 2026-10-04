# Explicit client maximize core qualification

This is a private, undeployed candidate. It does not yet implement the Elm
authority/menu Maximize or RestoreGeometry operation, and does not qualify the
complete desktop or release tuple.

The candidate retains V7's ordered 433-member archive, replacing only Window.cpp
and FullscreenController.cpp. The Window source is derived from the actual V13
minimize ancestor, preserving its native minimized input gate. The changes make
application set/unset maximized requests explicit and idempotent, and send the
actual xdg-shell maximized configure flag separately from fullscreen state.

`qa/callbacks-1791096460666628230/report.json` records 54 actual extracted callback
checks and three rejected old-behavior mutants. The first full build failed at
link because the owning relative inputs needed its build working directory;
`build-1791096576436035510` is retained. The fresh successful build is
`build-1791096651129914247/report.json`: 431 other archive members are unchanged.

`qa/closure-1791097255127497802/report.json` checks all 196 recorded compile
dependencies, selected source and policy headers, ancestor binary, candidate
binary and preservation of the ancestor's defined exported symbols. This is
source/interface evidence, not plugin execution or native ABI acceptance.
`candidate_host.py` revalidates selected build/closure and source/dependency
hashes before private launch, alongside the frozen AQ component closure.

`qa/link-closure-1791097509413004314/report.json` separately replays the exact
owning link with 212 hashed dependencies, producing an ELF byte-identical to
the selected candidate. It records the link tools and inputs; the private host
checks these hashes before launch. It does not change the selected binary.

The real xdg-shell client fixture is built in
`qa/client-build-1791097234964408082/report.json`. Its prior successful builds
remain separately scoped. A request-correlated wl_display_sync callback proves
server processing of preceding requests on that client connection. Local
`inspect` output proves no server processing. The eight-callback bound prevents
unbounded ownership; callbacks are destroyed on completion or teardown.
`qa/barrier-test-1791097534756588746/report.json` passes eight external lifecycle
oracles against actual extracted callbacks and rejects four unsafe mutations.
Its transport is mocked, so it provides no real-server or presentation proof.

Configure, acknowledgement, queued SHM commit, native geometry and actual
presentation are separate observations. The client fills each buffer with a
serial-derived colour; selected colours must be distinct because only the low
18 serial bits are represented. A queued commit does not establish displayed
pixels. Native retirement must be observed independently of normal client exit.

The real-client native campaign is being prepared. No native roundtrip result
is asserted here. It must retain the six-second observation deadlines, private
parent/child/source identity guards and ordered normal cleanup. Later integration
must rebuild and qualify the authority against its exact owning core, preserve
the original operation journal/deadline keys, expose truthful geometry facts,
and test the actual Elm user flow. Menu policy CPU checks and the separately
pending Quint model sketch approval do not substitute for these obligations.
