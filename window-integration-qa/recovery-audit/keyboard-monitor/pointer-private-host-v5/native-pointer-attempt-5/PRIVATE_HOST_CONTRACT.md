# Fresh full pointer/keyboard campaign on private GL host

Original Pointer V8c311 and SO af79 remain immutable. A fresh native candidate
changes the runtime authorization guard only: exact `/run/user/$UID/wqa/<4hex>`,
lowercase hex, owned nonsymlink0700 runtime AND wqa AND user-runtime directories,
explicit HYPR_A11Y_BRIDGE_PRIVATE=1, exact private bus socket owned by same UID.
Main /run/user/$UID, legacy/tmp, foreign UID, symlink or ambiguous suffix refuses.
All pointer owner-fence, XKB, grab, retirement and ABI logic stays identical.
Tests/model cover this authorization before code. Main load stays forbidden.

Run through shared qa_run dedicated QA scope→prlimit1:1 before all clients.
Owned host context provides private Weston→Hypr runtime/bus/display/signature;
the reviewed fixture parent env adds only HYPR_A11Y_BRIDGE_PRIVATE=1 to a COPY
of original main env. Original env stays separate for a read-only main observer.
No main display is ever a compositor parent; no main dispatch/input/restoration.

Host1280x800 with nested monitor scale1.25 must yield actual logical1024x640;
verify native dimensions/scale and CSD/popup mapped allocation before input.
Effective Lua disables Xwayland. Original popup/readiness/import/raw-double
oracles and telemetry remain. Full pointer campaign includes all real GTK/AX
signals/actual compat Orca navigation, owner/alias churn, unknown/multiwindow,
disable/toggle/outage and public reconnect. Follow with all accepted native
policy packet/Foot-byte cases and all official reader lifecycle/full-grab/restart
cases. Do not replace native evidence with host-capability success.

Private HOME/config/data/cache/state belong to owned runtime. Copy QA reader
profile into them; pass frozen actual ORCA_QA_READER_ROOT explicitly because
private HOME cannot locate the original signed prefix. Fresh reader/client/GTK
runtime guards use exact same shared helper and own bus; signed prefix untouched.
Native public protocol/capability/MouseReviewer semantics are unchanged.

Between phases, normal paired EOF/client quit comes before true PrepareUnload
and normal plugin unload. False quiescence remains failure; never force-unload
held callbacks. Foot/private AX stay alive until retirement/unload, then caller
stops its clients/AX; context stops nested Hypr then Weston then private bus.
Logs/config/bytes archive before removal. All PID/start/PGID descendants gone.
Main observer snapshots entire native session before/after with explicit original
environment and canonical full client set/state, monitor, hidden Files same
PID/start/public+UI state, a11y inode/connectivity, reader state, catalogs, plugins,
focus/cursor and devices. Any user main-state change is reported, never restored.

## V4 acceptance and user-awake observations

Before policy/plugin input, require exactly one complete bounded j/version reply
from the recorded compositor PID/UID, matching the same saved IPC socket inode,
owned path and exact commit. Verify the actual private Aquamarine4ed46 library
mapping. Actual startup and archived terminal logs must contain mandatory-Wayland
selection and configure/ACK handler markers, with no DRM/libseat fallback,
Wayland protocol error, parent transport failure or Broken pipe diagnostic.
Healthy graphics bootstrap alone does not satisfy this transport contract.

Original Files visibility is the actual captured value, whether open or hidden.
Preserve the same PID/start/instance/public/UI hashes and complete native client
set; do not require a historical hidden precondition. No main state is restored.
