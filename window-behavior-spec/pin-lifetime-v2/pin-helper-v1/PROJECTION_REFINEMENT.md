# Typed completion projections

The retained projection counterexample reproduces two actual parser acceptances:
before.floating=null and before.pid=true with captured pid=1. Both are malformed
native snapshots. Full owner projections must preserve each captured field's
JSON type as well as its value. Both before/after floating and pinned fields
must be booleans; before floating may be either value because a successful pin
can float an initially tiled window. The final pinned state must be the exact
boolean inverse of its captured before state.

The new tagged-field Quint model distinguishes booleans from integers. Run it
before changing the corresponding parser guard. The original 30-test result
proves its recorded checks only; the exact failed source is separately retained.
