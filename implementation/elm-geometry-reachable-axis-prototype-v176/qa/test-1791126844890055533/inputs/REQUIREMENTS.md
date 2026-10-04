# Bounded IEEE reachable-axis prototype

Requirements precede implementation. Experimental CPU-only algorithm, not approved formal logic or a native policy change.

1. Given an explicit consecutive integer rounded-dimension domain [first,last], finite nonnegative summed reserved extents, raw configure limits and layout real limits, return exact first/last admitted dimensions and configure values using double subtraction followed by floor.
2. Validate bounds before search; zero raw maximum is unbounded. Preserve existing per-source fixed/malformed refusal. Real size must be positive and <=INT_MAX, configure >=1; raw constraints apply configure and layout constraints apply real.
3. Use monotonic lower/upper predicates and bounded binary search. Do not replace floating subtraction with n-ceil(reserved). Preserve IEEE cancellation cases.
4. Compare returned endpoints and configure variability against independently enumerated actual owning ProspectiveGeometry::project calls on bounded domains, both MAX and ordinary Restore. Include fractional reservation, raw/layout contradictions, singleton intervals, wide/tiny maxima and boundary cancellation.
5. Explicit domain is a precondition, not a claim that all dimensions are physically reachable under a fixed native output/position/rounding transform. Caller must independently establish that domain. In particular edge-aware CBox rounding may yield INT_MAX+1 pre-reservation dimensions; permit explicit domain endpoint INT_MAX+1 but still enforce final real/configure capacity.
6. Keep402/407/161 and installed desktop unchanged. No native acceptance, model acceptance, policy adoption or release acceptance. Preserve failures in separate run directories.
