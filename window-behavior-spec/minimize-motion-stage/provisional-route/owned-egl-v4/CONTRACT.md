# Owned Wayland GPU route and commit authority

This renderer owns a separate Wayland connection, layer surfaces, EGL context,
buffers and feedback proxies. It does not change compositor scheduling or use
Qt/QPA. Each immutable PNG is opened and hashed once, decoded once and uploaded
once. Every motion frame draws that texture on the GPU. The service remains the
only native window authority and must validate exact current stable ID/PID and
fresh family edges before acting on renderer acknowledgements.

## Submission and presentation

The rendered scene record contains immutable source digest, exact identity,
entire token, output generation, sequence, rectangle and progress. Feedback is
requested after GL drawing and before that surface's eglSwapBuffers. The record
is initially preparing and acquires commit authority only when this exact swap
returns EGL_TRUE. A callback observed before the return is deferred. GL errors,
failed swaps, feedback discard/timeout, surface destruction or output topology
changes cancel the route and retire all outstanding authority. No later commit
can revive those records. Protocol feedback belongs to this owned surface,
never to a borrowed Qt surface or an unrelated next commit.

Renderer-local submission sequence and accepted presentation timestamp increase
per output generation. The protocol's seq_hi/lo is a refresh counter (MSC), not
our content-submission number; zero is valid when no compatible counter exists.
Repeated nonzero MSC alone is not evidence of a duplicate content update: the
counter describes refresh cycles, whereas exact own feedback describes a commit.
We allow equal MSC with strictly newer local sequence and timestamp. Known
nonzero counters must not move backwards except natural uint64 wrap (forward
modular distance less than2^63); zero neither establishes nor resets this guard.
This modular consistency policy is conservative, not a protocol guarantee of
strict counter increments for every content update. Counter/clock state persists
across seeds on the same output generation and resets on generation replacement.
The primary protocol is installed stable/presentation-time.xml lines234–245;
GLX_OML_sync_control defines MSC per refresh, separately from per-window swaps. A bounded submission
ledger accepts delayed ordered feedback for an earlier submitted frame, while
rejecting duplicates or a frame older than the last actually presented frame.
Actual presented origins retain the exact scene record, not a freshly computed
clock position. Handover waits for at most one outstanding commit per output to
present before reserving its origin. All fragments share one monotonic progress
clock but use their own actual presented origins. An output generation change
cancels rather than clipping a stale route through the changed display.

## Provisional intent

A newer whole valid token may retarget the retained immutable source without
waiting for native family metadata. This is visual-only. Native readiness or
endpoint acknowledgements require explicit promotion of that exact token by
the service, plus matched actual presentation on every required output. Old
token feedback may update displayed origin if still the same source/identity;
it cannot grant current native authority. Cancel/close/reuse invalidates the
route immediately. New identities cannot inherit old source/presentation
records. Tokens with suffixes or trailing newline are invalid.

## Capability and test boundary

Layer surfaces have empty input regions, no keyboard interactivity and exclusive zone -1 (no reservation). The renderer does not bind a seat. It requires presentation,
layer-shell, viewporter, xdg-output and fractional-scale protocols; missing
capability fails before any native action. Only the reviewed Mesa26.2.2 token or exact source-backed Arch26.2.2-arch1.1 build token (end or whitespace metadata, never another numeric/development suffix) on the direct GPU backend is supported; the mapped gallium/Mesa-EGL material must match its pinned hash, pinned nonempty ELF build ID and same-domain PROCMAP_QUERY device/inode against the opened hashed fd probe. See DISTRO_MATERIAL_CONTRACT.md. software/swrast/llvmpipe/softpipe and Zink are rejected before source upload or readiness. Output geometry/generation is owned
and observed, not guessed from wl_output physical dimensions. PNG material
limitations remain those of the atlas provider (blurred decoration backdrop
fails; raw translucent client backdrop equivalence remains unproven).

The offline ledger tests prove authority/lifetime/order rules, not actual pixels
or cadence. A private native test must prove immutable pixel provenance,
successful-commit binding, discard/error/removal/close behavior and actual
presentation interval distribution before service integration or deployment.
