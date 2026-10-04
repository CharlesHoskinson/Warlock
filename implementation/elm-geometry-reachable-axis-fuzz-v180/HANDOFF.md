# Precision/search stress experiment

Protected test-1791127402239224556 passed20001 deterministic cases (seed176179), comparing solver endpoints against actual402project enumeration over explicit short integer domains near both small dimensions and signed-int capacity. Cases vary finite fractional/tiny/large reservations, raw configure limits, real layout limits and MAX/ordinary conversion. No solver changes from held176.

Protected controls-1791127449254286919 compiled and rejected four unsafe solvers: dropped raw minimum, dropped layout maximum, stalled lower binary search, and replaced IEEE subtraction with n-ceil(reservation). The stalled control was terminated by its explicit five-second CPU subprocess timeout; no native deadline was changed.

Failed179 reports remain preserved. Their fixture generated reservation=-0.25 in one ordinary-restore case, outside the declared nonnegative domain; actual402 rightly refused while one-axis ordinary solver used reservation0. Fresh180 clamps generated reservation to nonnegative. Original enumeration oracle and solver are unchanged; no expected assertion weakened. Both failure snapshots retain exact inputs.

This strengthens experimental CPU evidence for caller-provided consecutive rounded domains. It does not derive the complete native reachable domain, confer permissions, change409/410, run model logic or establish native/release acceptance. Independent181 review pending. Original08/09/10, nonzero-origin rendering/input, full roadmap and deployment remain open.
