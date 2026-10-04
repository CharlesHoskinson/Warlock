# Qt250 source review

The held Qt250 fixture has no identified source blocker for a protected diagnostic attempt. This review does not qualify actual Qt modal routing, input, pixels or cleanup.

Current parentWidget ownership determines family retirement. Closing A preserves B and D after B moves to C; closing C retires that family. Reparent retires nested and popup roles locally before rebinding B, with deferred destruction explicitly journaled. QObject state connections disconnect before retirement; captured instance/widget guards prevent stale callback attribution. The event filter distinguishes QWindow delivery from QWidget propagation and preserves double-click events. Requested Qt modality and client-observed states are not compositor authority.

Resource identifiers and map generations must be joined to raw protocol epochs; neither queued drawing nor local normalexit proves presentation or native client retirement. Reparent and deleteLater require settled native observation before subsequent claims. Input event records alone do not authenticate an injection source. The private runtime probe establishes same-UID socket ownership on a separate connection; the outer host must retain actual process/socket/module guards. A private session bus and the reviewed successor to252 are required for activated-service teardown.

The real QtCore lifetime harness uses mocked QWidget/QWindow state; it qualifies local ownership and callback behavior only. All GTK and Qt native scenario gates remain open.
