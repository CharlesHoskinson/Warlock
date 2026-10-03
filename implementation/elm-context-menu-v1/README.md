# Elm window context menu — first implementation slice

This derivative connects a typed Elm menu reducer to the existing authenticated
native minimize/restore authority. It is a window-row menu in the experimental
WebKit shell. It does not install or replace the user's desktop shell.

The [right-click contract](../../docs/elm-roadmap/RIGHT-CLICK.md) remains the
acceptance target. This slice implements a subset: matching secondary-button
press/release, Context Menu and Shift+F10 opening, disabled-item navigation,
explicit activation, dismissal, native receipts, and stale identity rejection.
It does not complete any of the 24 requirements or 48 scenarios.

`Menu.elm` emits a typed command only after an enabled item is explicitly
activated against its exact menu and target binding. Opening and navigation
emit no command. Pending and unknown operations stay in a ledger across menu
dismissal and reopening. Late replies match the original operation identity.
The adapter preserves native uint64 identities as canonical decimal strings;
the UI does not treat a title or a DOM index as native authority.

`Main.elm` projects only Restore and Minimize, with enabled states from the
native snapshot. A dispatched command still passes the existing native
identity and context checks. The UI applies a receipt separately from the next
authoritative snapshot. The native host suppresses WebKit's built-in menu for
its own shell view.

Evidence is separated: `qa/replay.py` tests the compiled Elm reducer against
external fixtures; `qa/host_build.py` compiles the actual GUI and C host;
`qa/native.py` exercises the private compositor; `qa/model.py` checks the
approved Quint abstraction. Run all through the protected launcher described
in [qa/README.md](qa/README.md). Each attempt preserves its source hashes,
logs, and failures. Results and limitations are recorded in `HANDOFF.md`.

Remaining work includes a complete native system-menu authority (move, size,
maximize, graceful close), application/group and Files providers, nested menu
ownership, full pointer gesture policy, outside-click and focus lifecycle,
monitor-aware popup placement, accessibility and IME, scale and transform
qualification, resource limits, and combined release regression. Current popup
placement uses the shell's own layer rectangle and does not establish general
Wayland popup behavior.
