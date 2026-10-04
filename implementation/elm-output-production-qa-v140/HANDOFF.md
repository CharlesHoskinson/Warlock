# Live output geometry and keyboard readiness

The V132 GTK/WebKit host and its V125 Elm controller now retire the native popup
wrapper on an owning monitor geometry change and request a fresh logical lease
from the primary Elm reducer. The presentation engine stays alive. A reused,
already-closed lease cannot accept the new presentation. Current native configure,
grab, presentation and keyboard-focus events must all precede DOM focus issuance.
The C comment referring to retention of the logical lease describes the failed
V123 approach; the actual V125/V132 code requests and publishes a fresh lease.

The production V140 campaign passes 127 native checks, retaining the original
91-check window campaign, unchanged helper AST, original check/wait ordering and
six-second observation deadline. It exercises resize with an open popup,
scale-two Wayland buffers, transform-one logical geometry, 48px bar reservation,
Escape, pointer reopening and owning output removal. On the rotated 960x640
scale-two output, the bar is 320 logical pixels wide and the popup configures at
(4,48,312,420), wholly within its 320x480 logical viewport. Both host/backend
processes exit normally and ordered cleanup passes.

Compiled production Elm matches V127's 70 controller/codec checks and 12
presenter checks, except its test-only SurfaceReplay observer. V132's native build
passes eight host groups and four surface groups. V134 explicitly executes eight
named Quint scenarios and 1,000 invariant samples of 40 steps. This is an abstract
architecture model, not automatic refinement of the C host.

## Failed experiments and fixture diagnosis

V120 keeps the oversized mapped popup after resize. V121/V122 attempts GTK
in-place resize, which the layer-popup interception does not reconfigure.
V123/V124 replaces the wrapper but reuses its retired lease, refusing render/input.
V125 makes the logical lease fresh. V130 also exposes a keyboard-readiness race;
V132 requires the scoped GTK focus-in event before issuing DOM focus.

V124/V126/V129/V133/V135/V137 request rotation after creating a 960x640 scale-two
surface beneath an 800x600 kiosk parent. The parent rejects this with xdg_wm_base
error 4 (geometry exceeds configured fullscreen bounds), and later rule application
cannot proceed. Preserve these failed packets. V136's read-only authenticated
monitor-rule diagnostic initially fails compilation on misleading indentation;
V138 fixes that in a fresh derivative. V137 observes declared/effective transform1
but active/observed transform0. Pointer frame wake in V135 does not fix it.

V139 provides a 1600x1000 private parent while preserving the original 800x600
child geometry and all scenario deadlines, then observes declared/effective/
active/actual transform1 and passes126 checks. V140 removes the diagnostic plugin,
uses the unchanged qualified V89 plugin/CoreV23 production tuple, and passes127
including absence of that Wayland geometry protocol error. This is a fixture
correction supported by failure logs, not a relaxed rotation assertion.

## Remaining gates

Two independently controlled private hosts are a bounded output fixture. They do
not implement the final single authoritative Elm controller across all presenters.
Connector identity/replug, fractional scale/all transforms, arbitrary workarea,
modal/fullscreen/lock/canonical scene, physical GPU/display/input qualification,
AT/IME, human usability, measured budgets, complete menu providers, C00 and release
remain open. No requirement, complete sprint or deployment is accepted here.
Review and integrate the newer V125/V132 reflow and focus gates with the parallel
menu-output lane without replacing either lane's reviewed policy changes.

Source, builds, failed evidence and the accepted production report are frozen in
`qa/slice-manifest.json`. Native campaigns used the coordinator and unchanged
protected launcher. The installed desktop and user's drafts were not modified.
