# Direct xdg maximize/restore V28

The full Elm desktop, window-system and release gates remain open. V28 qualifies
one real floating xdg-shell client's explicit maximize/restore roundtrip on a
private owning core. It does not implement or qualify the Elm menu authority
operation, a new plugin pair, minimize/maximize composition or deployment.

The selected core SHA256 is
`be47f319ca67ec9294d2d6940909fc9b8c31841ff11cdfbd5b235593f27486c2`.
Three translation units change from the V7 archive; the other430 ordered members
remain byte-identical. The V13 minimized input guard is retained. Client desired
maximize requests are idempotent, the fullscreen controller sends the actual
maximized configure flag, and xdg mapping stops forcing a false maximized flag
merely to suppress client-side decorations. Native decoration negotiation remains
separate. Clients without that negotiation may legitimately draw their own frame.

Native evidence is
`implementation/elm-window-geometry-map-state-v28/core/qa/native-1791098384319585553/report.json`:
all35 checks and cleanup pass. Actual mapped core/AQ identities are checked.
The ordinary client is320x180 at83,61. Maximize fills the800x600 work area with
its configured one-pixel border: the client rectangle is798x598 at1,1. Repeated
maximize preserves that state. Restore and repeated restore recover the exact
ordinary rectangle. Five stages independently sample three interior pixels.
Configure-specific colours distinguish the selected buffers, with a collision
guard on the serial-derived colour. This is interior presentation evidence, not
proof of the complete decorated scene, hardware acceleration or frame cadence.

Each transition preserves one six-second absolute deadline across request,
correlated server sync callback, native/client observations and pixel decoding.
Request processing, configure acknowledgement, queued SHM commit and actual
captured pixels are distinct witnesses. A normal client exit and independently
observed native retirement precede private host cleanup. The main desktop was
not configured or activated.

Separate protected CPU evidence passes54 extracted window/controller callback
witnesses with three old-behavior mutants rejected, and453 mapping witnesses
with both forced-true and forced-false mutations rejected. Export closure retains
all13,404 ancestor defined exports;212 hashed link inputs reproduce the exact
ELF. Export preservation does not establish semantic plugin compatibility.

Failures remain preserved: the protected Python lacked Pillow before GUI launch;
the first native placement used legacy dispatch syntax in a Lua-configured core;
the next run exposed the forced maximized mapping flag. Fresh V28's first fixture
resized after moving, which shifted placement about its centre; the next fixture
used an incorrect border-free client-box oracle. Their original deadlines and
reports remain unchanged. Resize-before-move establishes the intended placement,
and the accepted fixture verifies its explicit native border policy.

V16 also retains the pure Elm geometry policy42 tests and placement-policy21
witnesses/13 rejected mutations, plus the type-only Quint sketch. Model approval
is still pending; there is no executed geometry model logic or safety proof.

Next: rebuild the authority against the exact owning core, add versioned geometry
facts/capabilities and bounded placement ownership, integrate the shared Elm
request/receipt path, and test actual menu user flows. Tiled/grouped/modal/pinned
windows, peer fullscreen effects, changed outputs/workareas, stale identities,
duplicate journals, Unknown recovery, maximized minimize/restore, Close/Pin/
Move/Size, AT/IME, measured budgets and coherent deployment/rollback remain open.
