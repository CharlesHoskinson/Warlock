# Proposed Maximize/Restore transaction model

Types only; transition logic awaits explicit approval. The actor is one serialized
native authority owning shared windows, placement records and request journals.
API requests and native/client observations are inputs. This is a shared-state
model, so it does not use Choreo or model separate frontend transport actors.

Scope derives from RIGHT-CLICK ELM-RC-006 and WINDOW-GEOMETRY-NEXT: explicit
Maximize/RestoreGeometry, preserved-mode Minimize/RestoreMinimized, Activate and
separate ExitFullscreen; native lifetime/incarnation/root identity, affected
peers, bounded placement/journal ownership, original deadlines, duplicate
requests, Unknown outcomes and client/presentation correlation. Tiled/grouped/
transient, pinned and constrained windows remain represented; unsupported paths
must refuse, and partial prototype refusal cannot establish full acceptance.
Close and interactive Move/Size have separate future models/implementation gates.

Native mutation plus synchronous readback share one compositor step, without
inventing event-loop interleavings inside that callback. Request admission and
later client ACK/commit/presentation observations are separate. Native goal,
client configure serial and actually presented scene remain different facts.
Coordinate integers abstract logical placement; native tests must additionally
cover finite doubles, scale/borders and exact logical/visual boxes.

Planned safety properties: duplicate requests never mutate twice; stale/expired/
locked/ineligible requests preserve native state; Unknown blocks competing family
routes and cannot be replayed; matching original placements survive supported
minimize/maximize transitions but never attach to replacement windows; outcomes
cannot claim configuration/presentation from stale serial or scene; unrelated
peers and focus remain as the accepted operation policy specifies. Witnesses
will demonstrate actual maximize, exact restore, maximized minimize/restore,
refusal, Unknown and matching client completion.

Current API audit found two owning-core issues: requestsMaximize currently
ignores the requested boolean and toggles; client-mode MAX bookkeeping currently
does not send xdg maximized state. Default floating layout already retains full
lastBox; only its generic fallback recenters. Native implementation must fix or
qualify these facts rather than invent geometry behavior from sampled models.
