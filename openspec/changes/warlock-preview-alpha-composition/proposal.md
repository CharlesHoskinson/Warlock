# Native preview alpha composition

## Why
Opaque root-only shader comparisons miss borders, shadows and transparent margins. Native79 measured6912 mismatches because its oracle assumed black while the actual background remained#111111, and two measurement exit2 values stopped the final normal-exit verifier. Preserve that failed fixture; it proves no renderer defect or original terminal acceptance.

## What Changes
Require actual independent output-background evidence and every cropped pixel's source-over comparison. Valid pixel measurements return facts normally; the mandatory terminal assertion evaluates those facts after original assertions and physical cleanup. Native80 explicitly configures and independently verifies private black, restores#111111 before original final GUI controls, and passes84836 pixels for identity/tint programs with zero mismatches,2224 assertions/all1783 original identities/221 normal0 clean.

## Impact
No product policy, native ABI or FD3 schema change. Actual compiled PNG comparison, fixture background/source ownership and original clocks remain explicit. Half-alpha body, arbitrary backdrop/blur/privacy, general shaders and full release remain open.
