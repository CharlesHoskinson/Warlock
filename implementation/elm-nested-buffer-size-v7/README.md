# Nested buffer size guard V7

This fresh Aquamarine derivative preserves the private nested lifecycle candidate
and unchanged public headers. `upstream.json` captures all parent source hashes
and the failed V6 resize/scaling campaign. No installed library is replaced.

Actual `CWaylandOutput::commit` now rejects invalid pixel dimensions and a buffer
whose dimensions disagree with the pending mode before swapchain reconfiguration,
wl_buffer import, pending-release mutation, frame submission, or attachment.
The production helper accepts only finite positive integral dimensions fitting
signed protocol dimensions. Its compiled tests cover growth, shrink, mismatched
axes, non-finite and invalid values. Source-order assertions supplement those
checks; they do not establish native parent delivery or error recovery.

The companion owning-core derivative is `elm-native-buffer-size-v7`. It must be
qualified with a rebuilt plugin on the exact owning source/ABI pair. The V6
failed native campaign remains failed, including its original reset deadline.

## Remaining presentation contract

A child output mode of 960x640 does not fit the fixed 800x600 fullscreen parent
surface. Inner monitor scale=2 changes inner client buffers, not the parent AQ
surface. Guarding buffer/mode agreement cannot fix this separate protocol error.
A subsequent derivative needs explicit parent viewport mapping and corresponding
input normalization, or an explicit unsupported-mode rejection. Larger child
modes must not be silently declared accepted from an easier fixture.

The preferred mapping preserves child render dimensions and scales the full
buffer to the latest acknowledged parent logical dimensions through wp_viewport.
The committed destination, not source pixel dimensions, must normalize parent
pointer coordinates. Configure staging, ACK, idle callbacks and commit ordering
need a generation guard so superseded configure work cannot restore old sizes.
Zero-size parent suggestions need an explicit policy; no staged size may be used
before ACK. Viewporter capability fallback, output destruction and transport
failure must retain the existing private lifecycle gates.

Acceptance requires actual shrink/grow/shrink presentation, exact native input
recipients after scaling, no parent protocol errors, recovery after refused stale
buffers, original scenario identities/deadlines and ordered protected cleanup.
No native, rotation, multi-output, accessibility or release acceptance is claimed.

## Independent integration review findings

The existing AQ `test()` still returns true unconditionally; a follow-up must
share mode/buffer and parent presentation preflight with `commit()`. This V7
change only protects commit mutation. It does not assert successful presentation.

The owning compositor currently drops AQ absolute-motion output identity when
constructing its input event. A normalized parent coordinate therefore maps over
the whole child monitor layout unless a bound output exists. Single-output
mapping does not establish multi-output routing; preserve the output identity
through the owning input path before global multi-monitor qualification.

The nested seat currently supplies keyboard and pointer only. Touch, relative
pointer, tablet and gestures remain unsupported in this backend. Its separate
cursor surface is unscaled and uses a raw hotspot, so whole-output viewport
scaling also needs a reviewed cursor/hotspot policy. Scroll deltas stay actions,
not absolute coordinates. Input during the transition between ACK and a new
presentation must use committed mapping or be explicitly fenced.
