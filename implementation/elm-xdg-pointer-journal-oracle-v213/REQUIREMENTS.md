# Native pointer journal admission oracle

Source197 emits pointer-button records only for its owned wl_surface, with PID,
sequence, wl_fixed coordinates, floating local coordinates and button/state.
Validate a fresh press/release pair after a caller-owned sequence boundary,
canonical integers and consistent fixed/local coordinates, exact target button,
and expected surface-local point. Keep buffer scale separate from surface-local
pointer coordinates. This decoder does not inject pointer input or establish
hardware/physical-device acceptance. Caller must bind process start/incarnation,
real pointer injection route, observed compositor global point and screenshot
landmark inside original6s. Nonzero origin transform remains diagnostic175;
this module cannot enable capabilities or prove rendering/input agreement alone.
