# Prospective geometry conversion for ELM-RC-006

This fresh derivative refines V395: bounds may be intersected only within a
verified common coordinate space. Raw configure limits and effective layout
limits remain separate. No native capability is granted by this prototype.

- GC-001: The authority shall retain logical, visual, real-client and integer configure dimensions separately.
- GC-002: When projecting MAX, the authority shall round target boxes using the owning CBox implementation and subtract decoration reservations once from the selected visual box.
- GC-003: When projecting ordinary restoration, the authority shall use the rounded retained logical box without subtracting MAX decoration reservations.
- GC-004: While the XDG window-geometry origin is nonzero or conversion is unavailable, the authority shall refuse this initial conversion profile.
- GC-005: The authority shall compare raw client bounds against integer configure dimensions and effective layout bounds against real-client dimensions independently; zero raw maximum and DBL_MAX effective maximum mean unbounded.
- GC-006: If an input is nonfinite, malformed, outside positive signed-int configure range, contradictory or fixed on either axis, then the authority shall refuse without native mutation.
- GC-007: When monitor scale changes between valid positive scales, this Wayland conversion shall retain logical configure dimensions without multiplying by scale.
- GC-008: The production authority shall recheck conversion, bounds, scope and exact original before mutation and after callback; post-mutation disagreement shall remain Unknown until reconciled.

## OpenSpec scenarios

Given workarea800x552 with reserved extents4/6/8/10, MAX has real/configure size788x536; restoring logical320x180 has configure320x180. Given raw maximum790x540 the decorated MAX fits, while raw maximum780x540 refuses. Given minimum108x42 and zero maximum the GTK size gate fits. Given effective real width788.25 and integer configure width788, a raw minimum788.1 refuses independently of a fitting layout lower bound. Given a nonzero or negative XDG geometry origin, this profile refuses instead of combining conventions. Given scale1 or2, configure dimensions stay unchanged. Given reserves consuming the workarea, NaN, infinity, contradictory intervals or one fixed axis, no prospective operation is produced.

This bounded zero-origin profile requires source/ABI review, negotiated geometry
version2, strict Python/Elm consumers and actual decorated GTK configure/ACK/RGB
acceptance before integration. Nonzero-origin support remains an explicit gap.

GC-009: If raw and layout limits jointly leave at most one positive integer configure dimension on either axis, then this profile shall refuse resizing. Convert layout limits to configure space before this test; do not intersect unconverted boxes. Layout lower bound maps to floor(lower), raw lower to ceil(lower), and both finite upper bounds map to floor(upper). Retain separate real-dimension checks afterward. Signed-int range remains mandatory.

Given raw minimum128/unbounded maximum and layout minimum1/maximum128, then configure width128 is the only permitted width and MAX refuses. Given raw maximum128 and layout minimum128/unbounded maximum, it also refuses. Given a fractional layout interval128.1–128.9, all integer configure widths are128 and resizing refuses. Given layout maximum129 with raw minimum128, both128and129 are possible and the target may pass.
