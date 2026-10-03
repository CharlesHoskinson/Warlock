# Native surface draw-dispatch trace

A fresh native core derivative instruments surface draw dispatch after render-pass
simplification and surface texture/size/visible-region checks. Each composed frame
records monitor, nonwrapping serial, ordered surface dispatches and the actual
monitor-state commit result. Overflow, unfinished work and direct-scanout
invalidation cannot yield a usable trace. Monitor commit is not presentation
feedback. The trace does not change window/input policy or owning SDK class layout.

The authenticated authority exports render-trace-request on the existing bound
private protocol. Draws retain weak window references and main/popup roles. Window
incarnations are resolved at query time; draw-time identity binding, remap/reuse
reconciliation and dependency coherence remain UNQUALIFIED. Other surface roles,
transformed/offscreen passes, damage accumulation, masks, presentation callbacks,
all input routes and native overflow/direct-scanout tests also remain open. Limits
of 32 monitor slots and 1024 draws are prototype limits, not approved product budgets.
Canonical scene capability stays false. No paint list is inferred from vector order.

The ordinary private campaign passed its original 63 checks. A separate continuous
full-redraw diagnostic fixture passed 78 checks: the original behavior assertions
plus seven committed/complete trace checks, seven overlap draw-order checks and
minimized MAX exclusion from actual surface dispatch. Captured pixels and actual
pointer/keyboard behavior are retained. Full redraw is explicitly a diagnostic
configuration; it provides no production performance or power claim.

Observed order includes repeated floating-window main draws before and after the
MAX pass (and an additional pinned pass). For example peer-raised records Peer,
MAX, Peer at the overlap; pinned-peer records Peer, MAX, Peer, Peer. The last
qualifying dispatch matches the captured opaque fixture pixel. A unique window
vector would conceal this behavior. These findings must inform the canonical
surface/mask policy and redundant-pass evaluation before scene acceptance.

Typed Elm RenderTrace decodes diagnostic packets separately from Scene.Admitted,
keeps counters as strings, rejects malformed bounds/identity/completeness and
always emits canonicalScene=false. Its 22 executed checks include all 12 actual
native capture packets, eight malformed packets and two boundary/retirement checks.
Quint separately executed eight named recorder cases and 1000 sampled invariant
traces at 40 steps. That abstract model uses capacity2 and serial ceiling3 to reach
boundaries; it is not a native refinement proof or a 64-bit exhaustive proof.

All source, exact core/plugin ABI pairing, source dependencies, original deadlines,
compiler attempts and native packets are preserved. Nothing is installed on the
user's live desktop. Complete scene, UX/AT/IME/GPU and release gates remain open.
