# Parent hit testing after layout and client commits V72–V78

V78 freezes the corrected parent hit-test implementation and four passing native
campaigns on the exact V74 owning tuple: 51 multi-output, 159 focus/capability,
195 cursor/stationary and 68 Elm-menu check executions. All pass normal ordered
cleanup. These 473 executions are bounded campaign counts, not 473 distinct
roadmap scenarios. No installed desktop was changed.

## Defect and correction

V53 creates two actual nested Aquamarine outputs and two independent GTK
recipients on one private 800×600 Weston parent output. Input reaches the second
output at its nonzero logical origin, including a scale-only change. A combined
mode/origin change then leaves the core cursor at the correct global point but
delivers no GTK buttons. V56 preserves that failure and demonstrates that an
additional physical motion crossing a logical pixel boundary restores input.
Parent wire events and GTK recipient wire logs establish that the parent owns
the correct output while child pointer focus has been cleared.

The pointer layout listener can run before later workspace listeners move the
window surfaces. An immediate hit test can therefore clear pointer focus using
the old window geometry. V57's deferred hit test repairs the moved-origin case,
but V59 fails the reverse resize: GTK commits its new surface after the layout
dispatch and its first deferred hit test. V66 adds a visible-window commit
notification, passing the stationary geometry cases. Its original menu campaign
then fails restored-window focus because ordinary commits trigger another
follow-mouse hit test. These intermediate binaries are not accepted release
tuples.

V72 limits the deferred work to an outstanding change in the owning parent
output's logical box. It routes the new point through the existing InputManager
and queues normal hit testing after the layout listeners complete. A visible
window commit can request another hit test only while that layout remains
pending. Settlement requires the committed window to own the actually focused
surface; a background window cannot settle the hovered window's pending input.
Ordinary commits after settlement schedule no hit test, preserving a window
restored through its context menu.

Queued work holds weak private state/window/device/output references and resolves
the current manager when it runs. It checks manager identity, live parent input
readiness, owning monitor eligibility and the currently applied logical box.
Superseding pointer sources clear the pending state. No stored old coordinate,
raw manager pointer or button event is queued by the new helper. Existing grabs,
focus policy and event routing remain in the normal InputManager path.

Only PointerManager.cpp.o and Window.cpp.o change relative to accepted V47;
the other 431 ordered archive payloads are byte-identical, including the monitor
reload fix. Window.cpp is derived from its actual V13 compiled ancestor and
retains the first-class minimized-window input guard. V62's attempt to use the
unchanged owning checkout fails its ancestry check before replacing the archive;
V66 and V72 bind the correct source/object ancestry. No existing public class
layout or vtable is changed. ParentPointerFocus.hpp adds the small free-function
interface used by the window commit hook. AQ V30 is unchanged.

## Iterative model and implementation evidence

V55 models serialized layout-listener/idle ordering. V63 adds the separate client
surface commit that native V59 exposed. V73 adds pending-layout settlement,
background commit ownership and preservation of later programmatic focus after
the original menu regression. Its explicit selector executes all 13 named
scenarios; a seeded invariant run checks 1,000 samples of up to 40 steps. Six
typechecked mutations are rejected. The first ordinary-commit mutation removed
only queue admission while retaining the callback guard and correctly did not
fail; the fresh model2 runner removes both protections for its negative control.
The earlier report remains unchanged.

V72's extracted scheduling and commit-notification bodies pass 29 typed C++
checks and reject five independently compiled mutations. Tests include weak
retirement, output/focus readiness, changed owner/monitor boxes, coalescing,
asynchronous client commits, background-owner refusal, normal commit refusal,
and an already queued task whose pending layout has been superseded. Its first
extractor mistakes a default argument's braces for the function body; the fresh
test3 runner fixes extraction and retains the failed report.

These are bounded scheduling/ownership abstractions with typed environment
mocks. They do not prove complete compositor refinement, native transport,
rendering, all popup/subsurface cases or physical multi-display behavior.

## Native tuple and campaigns

All campaigns use the shared native lock and unchanged protected launcher.
Receiving GTK recipients retain the original allocation/native-window join,
owned event-window assertions, physical button pairing, coordinate tolerance
and six-second observation deadlines.

- V75 multi-output: 51 checks pass. Two child output identities and independent
  real GTK recipients are observed. Stationary input survives scale, mode,
  positive origin changes and reverse resize. Moving/resizing the background
  output does not send it buttons or steal the owning output's cursor origin.
  Destroying the focused output preserves both clients, returns a real parent
  enter to the survivor, and permits fresh input to its selected GTK recipient.
- V76 original held/capability/full-cover campaign: 159 checks pass, retaining
  held-button balancing, actual pointer capability removal/restoration and both
  covered scale-change/stationary-reentry cycles.
- V77 original cursor/stationary campaign: 195 checks pass, retaining actual
  parent framebuffer cursor extent/hotspot/blank/movement captures and stationary
  input after geometry/scale changes.
- V77 original Elm menu: 68 checks pass, including restored-window state and
  focus, popup/effect receipts, geometry reflow and the current authority mapping.

V65 retains a background-fixture observation failure: its hidden parent surface
withholds callbacks and GTK allocation lags native layout. V69 uses validated
receipts plus the independent PID/address/window join for background button
isolation; receiving windows keep the full allocation join. It then correctly
observes one physical pair but fails a raw counter that also counts GTK's
type-5 double-click notification. V70/V75 require exactly one type-4 physical
press and one type-7 physical release, including rejection of extra physical
events at any coordinates. Raw counts and generated GTK notifications remain
archived. No physical extra press or widened deadline is accepted.

The owning tuple is core V72 build-1791104632059591332, SHA-256
1f29b73e2abb902b8c5680d15c2661c4b8c4cf776fa06d6a532e5bc971160378;
freshly compiled authority V74 build-1791104720913053327, SHA-256
f1bba468e10cf91ae276e0ca3f890cbdb9282819bd75dfb2871056cff7494f1e;
and unchanged AQ V30, SHA-256
1763ba3b38832b67ed70d9470661cdc18073ca0924f1ef962ffcbf61cf754ff5.
The plugin reproduces its previous binary hash; its fresh owning header closure,
pair descriptor and actual native mapping are independently verified.

V78 verifies current tuple hashes and mappings, model/helper results, source
inputs, native receipts and cleanup, retaining 11 failed reports and archiving
3,135 source/build/evidence files in its acceptance manifest. V71's prepared
freezer was never accepted because the original menu regression remained failed.
No failed report or earlier frozen acceptance was overwritten.

## Integration and remaining gates

Integrate the V72 pointer changes and its small visible-window commit hook into
the latest reviewed geometry/shared-shell source, preserving that lane's window
and monitor changes. Carry V47's monitor reload fix and V30's AQ bridge, rebuild
one coherent core/plugin tuple, then rerun the native campaigns. Do not replace
a newer geometry Window.cpp with this older complete ancestor file.

This qualifies two nested outputs on one fake parent output. Physical multiple
displays, rotation, zero-output/hotplug and parent transport loss remain open.
Queued AQ device publication/retirement and native parent configure-generation
fencing still need evidence. Hidden GTK allocation progress and broader popup,
subsurface, AT/IME and hardware behavior are not inferred from these passes.
Measured budgets/soak, original restore/recovery and user journeys, the complete
S01–S16/right-click/C00–C06 audit, reversible deployment and required activation
authorization remain open. The automatic goal remains active.
