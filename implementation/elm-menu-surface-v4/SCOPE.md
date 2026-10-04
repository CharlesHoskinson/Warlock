# Visible menus in one shared controller

Fresh derivative of the V98 choice-timeout desktop host and the frozen V3 menu
adapter. The bar and presentation-only popup use one SurfaceController. The
controller admits scoped context requests, publishes menu controls, renews the
lease for replacement menus, and forwards a selected window effect in the same
commit that closes the menu. Menu state and original receipt bindings survive
pending operations and frontend replacement.

The native input path pairs logical GTK secondary press/release events, cancels
movement beyond five CSS pixels and chording, consumes a receipt once, and
requires current source manager, publication, lease and admitted control. A
WebKit query checks both native points against the current DOM. Async completion
checks the event epoch and a 500ms age limit again. Keyboard context requests
require native Menu or Shift+F10 with excluded command modifiers and held-key
repeat rejection. The asset also excludes IME, prevented and untrusted events.
Menu navigation has a native key receipt and scoped reducer path. Tab moves
between the selected action and dismiss control; Enter on dismiss never executes
the selected action.

NativeProvider's registered provider and presentation output IDs are explicitly
one for this private single-output candidate. They are separate from the native
output generation. This is not full output identity or multi-output qualification.
Bar keyboard ownership remains unavailable under the existing NONE layer policy;
native keyboard tests use the grabbed popup. Pointer anchoring is native for bar
requests; popup-origin placement and complete workarea/scale handling remain
gates. Outside-click consumption does not establish delivery to an underlying app.

The source copied a tested V98 baseline. Parallel output/viewport derivatives
must be merged from their exact final source; this version does not overwrite
them. Preserve both lanes' failure packets, deadlines and original regression
identities when forming the coherent candidate and release tuple.
