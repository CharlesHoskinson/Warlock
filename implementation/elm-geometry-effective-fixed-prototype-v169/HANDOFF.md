# Experimental fixed-axis profile guard

This isolated prototype follows `spec/REQUIREMENTS.md`, written before code. It changes only a fresh copy of V402 ProspectiveGeometry.hpp: one configure-interval helper and an either-axis guard before projection. V402/V406, all original oracles, native ABI, primary source and Quint logic remain unchanged. This is a proposed profile correction requiring independent/formal review, not native or broad policy acceptance.

The guard treats raw bounds as constraints on integer configure `floor(real)` and layout bounds as constraints on real dimensions. Effective integer lower is max(1,ceil(rawMin),floor(layoutMin)); upper is min(INT_MAX,rawMax0?INT_MAX:floor(rawMax),floor(layoutMax)). Either-axis empty/singleton intervals refuse. Existing source-invalid/source-fixed checks and separate raw/configure and layout/real applicability checks remain intact. No geometry clamp, native mutation, operation allocation, Unknown change or effect retry is added.

Protected report `qa/experiment-1791125795904400760/report.json` passes:

- The **unchanged original1710 fixture** against both the original402 helper and this experimental helper. Compatibility has no failing original cases; this alone does not prove the proposed policy complete.
- **34 independently named cases**: cross-source fixed widths/heights both directions, empty and two-value intersections, fractional real-versus-configure constraints, tiny raw maximum1–4/default minimum, source-invalid/fixed preservation, GTK108x42, asymmetric decorated MAX, ordinary restore, INT_MAX boundaries and huge finite lower bounds without integer overflow.
- **Four unsafe controls rejected**: removed guard; allowed singleton; ceil instead of floor layout minimum; raw upper applied directly to real size. The first two admit the effective fixed counterexample, and the latter two incorrectly reject valid real129.75/configure129 with possible configure interval128..129.

The original402 helper and captured406 helper hash identically; the V168 counterexample stays preserved. Real paired Hyprutils headers/library are verified against pair90 compiler/link capture. Generated sources, original fixture, binary runs and dependency/runtime inventories are captured. No native producer/consumer, wire negotiation, saved-state migration, callback, client ACK, pixels or shared08/09/10 acceptance is established. Fractional raw fixtures are mathematical characterization inputs; this prototype does not authorize them in a wire protocol whose raw hints are integer typed. Nonzero XDG-origin conversion remains unsupported.

Independent review and V161 approval/model alignment remain gates before adoption. Full release acceptance remains false.
