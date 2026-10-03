# Private X11 Qt modal compatibility campaign

The accepted V9 Wayland nineteen callback/modal/family gates and ten host gates remain required. Only the Qt transport changes to xcb, with native xwayland identity required. One additional protocol gate requires the actual Qt process to map frozen libqxcb.so and Qt6XcbQpa. The exact V2 candidate remains private, production remains v18.

The isolated X11 adapter supplies an explicit compositor-chosen owned display and real private authority; no main display fallback is permitted. Actual cookie acceptance and missing-cookie refusal are required before Qt begins. Xwayland enabled and abstract sockets disabled only in this fresh campaign; all default frozen hosts remain disabled. See ../private-weston-x11-host-v1/CONTRACT.md for descriptor/parent/runtime/cleanup authority.

Private scale1 logical1600x1000, actual configured QWidget/layout extent, public callbacks, deepest child/native focus, strict .5 floating cursor readiness, peer independence, caption/body guards, destruction/lifetime and family min/restore remain unchanged. No global input or main restoration is performed. Main observations wrap the complete private host lifetime with eighteen strict preservation gates. Unknown descendants and non-normal client shutdown still fail.

Static loader closure and offline tests are preparation only. Native X11 behavior, actual owned authentication and server disconnect cleanup require one independently reviewed frozen native attempt.
