# Native recovery preserves the workspace after renderer failure

V167 killed the single related renderer and reached clean host/backend failure,
but its collector incorrectly accessed a title absent from authoritative facts.
V168 corrected that schema and exposed a real behavior failure: host exit removed
the48px bar reservation, moving tiled windows from y69/h510 to y21/h558. Both
failed packets and source hashes remain preserved. No frozen assertion is changed.

V169 quarantines script-message ingress at shutdown, closes the popup grab,
cancels/drains host I/O and closes the backend normally. After renderer failure,
it keeps existing native layer bars and replaces dead web views with trusted GTK
text and a Restart button. Geometry/workarea remains unchanged. Only the native
button requests exit3. Normal signals cancel recovery. The bar has no application
window-effect bridge. Output changes during recovery and keyboard-only/AT routes
are still open; this prototype is not a complete production recovery service.

V170 passes31 focused native checks: actual renderer SIGKILL while a popup is open,
backend normal exit, retained48px reservation, identical application incarnation/
geometry/minimize state, actual application keyboard recipient, native screenshot,
real pointer click on Restart, explicit exit3 and a fresh host/backend binding.
A coherent snapshot precedes effects; the old actual effect packet is refused
natively. Fresh activation reaches the intended application's keyboard controller.
The compositor PID/start and application connections survive throughout. The
reviewed fixture performs the fresh host launch; no production supervisor is
claimed. Actual restart may briefly release/reapply workarea reservation; only
failure-time and final geometry are asserted, not atomic restart presentation.

V171 also passes the complete137 native regression including all original91
assertions/helpers/deadlines, shared-controller popup/output/reflow/scale/rotation/
hotplug/replug and broker recovery, plus actual one-renderer observations. Actual
optimized Main/Bar/Popup/C build and11 host/4 surface groups pass. All29 Elm modules
still match frozen V145 (37+58+12 compiled checks and Quint10/1000 retained).

V173 recovery model passes six explicitly named scenarios and1000 invariant traces
of40 steps: quarantine, reservation, native-only restart, fresh snapshot/epoch,
retired epoch and stop cancellation. V172 parse failure is preserved. The model is
an abstract contract, not automatic C/Elm refinement; pending effects, time bounds,
actual pixels/AT and hotplug are independently unmodeled gates.

V166 separately qualifies related-renderer graphics:142 native includingoriginal91,
real shader/readback/native screenshot, Intel Mesa diagnostics, WebGPU unavailable.
That GPU packet uses V165 QA diagnostics; it is not the exact V169 source tuple.
Graphics, recovery and menus must converge on a reviewed release tuple. Full scene/
window operations, production recovery supervision, pending Unknown reconciliation,
zero-output/hotplug recovery, budgets/long-soak, AT/IME, physical displays/human UX,
C00 and release remain open. The installed desktop/configuration is unchanged.
