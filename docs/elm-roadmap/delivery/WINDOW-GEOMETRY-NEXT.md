# Next native window operations

The current authenticated engine implements Minimize, unminimize Restore and
Activate. Existing menu vocabulary does not implement Maximize, Restore from
maximized, Close, persistent Pin or interactive Move/Size. Full right-click and
window-system acceptance remains open until those user flows are implemented.

The next concrete roundtrip is explicit Maximize and explicit restoration of
maximized geometry, preserving the existing meaning of unminimize Restore.
Minimizing a maximized window and restoring it must preserve maximization. Native
window incarnation, canonical root, effect context, capabilities and original
receipt keys remain authority; labels and paths cannot select a replacement.

The owning V89 native ABI already exposes Fullscreen::controller(),
getFullscreenModes(window), and setFullscreenMode(window,internal,client,
layoutAware). Its exact pairing is recorded in
implementation/elm-grab-safe-background-v89/qa/build-pair-manifest.json.
The setter returns void and can clear a competing workspace fullscreen window or
alter pinned state. An idempotent request must preflight all affected identities
and state, set an explicit target state rather than toggle, then read back the
actual native modes and dependencies before a committed receipt. Partial or
unproven results remain Unknown and cannot trigger automatic replay.

The owning default floating algorithm retains a full lastBox and can override
the generic size-only recentering fallback. Prove restoration on the actual
configured algorithm instead of assuming original position is always lost.
Authority-owned bounded placement records can make the expected native origin
explicit and support reviewed fallback policy; they must not overwrite correct
layout state. Internal/client MAX bookkeeping alone does not prove that the xdg
client received its maximized configure flag. The current fullscreen client-mode
setter only sends true fullscreen state, so explicit maximized configure handling
and actual client receipts are required before accepting the roundtrip. Records must be keyed
by native lifetime/incarnation and compatible workspace/output ownership, retire
with the target, survive supported minimize/maximize transitions, and never apply
to a replacement window. Externally maximized windows without a known origin need
an explicit supported restoration policy; do not invent an original rectangle.

The first implementation can enter through ordinary resizable floating roots,
with truthful eligibility facts and refusal for unimplemented interactions.
This is a phase, not the final acceptance boundary. Complete qualification must
cover tiled/grouped/modal/pinned and competing fullscreen behavior, fixed-size
clients, output/workarea changes, external client state transitions, maximized
minimize/restore, canonical root-only geometry policy, replacement/retirement,
client configure/render completion and representative user journeys.

Required implementation lanes:

- Native authority: versioned operation/capability handshake, explicit native
  state and eligibility facts, placement policy, guard/refusal matrix, exact
  request journal and outcome readback on the owning core/plugin tuple.
- Adapter: strict duplicate-free typed facts and projection, coherent observed
  window mode and eligibility, preserving legacy operations and scope checks.
- Elm: ActionProjection/Effects/NativeProvider/Provider/MenuBridge/ReceiptRouter/
  NativeOutcome changes through the shared allocator and original receipt keys.
- QA/model: review the new formal type sketch before model logic; preserve all
  original operation/menu/output scenarios and deadlines, run actual compiled
  controller/adapter checks and guard mutations, then protected serial native QA.

Native roundtrip evidence must compare pre-Max and post-Restore position/size,
work area, client/internal mode, focus and keyboard recipient, unaffected peers
and presented pixels. Opening/selecting allocates no operation; dispatch closes
the actual popup before exactly one command. Stale generation/revision/authority/
incarnation/capability refuses. Duplicate requests return the original outcome.
Unknown survives menu dismissal/reflow and blocks every competing family route.

Close additionally requires save/refusal-dialog handling: delivering a close
request is distinct from client retirement. Pin requires stacking/input and
persistence policy. Move/Size require an identity-bound interactive session with
Enter commit, Escape placement rollback and retirement abort. These obligations
remain in the complete roadmap; Maximize alone does not complete ELM-RC-006.
