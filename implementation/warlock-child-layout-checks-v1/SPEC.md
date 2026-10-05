# Explicit parent-layout model/native coupling

Select positionParentTest and stackingParentTest with exact match, export all
states and compare them to actual independently decoded native-v6 samples on
core-layout-v1/source-v3/AQ155. Pending actions preserve native context and applied
pixels; parent application advances native context and pixels. This finite model
covers one SHM child with parent-only stacking. It does not model general sibling
sequences, lifetime/destruction, layout memory budgets, fences/FIFO/presentation,
ordinary desktop effects or full release. Original native681/cache46 remain
separate required controls. Preserve all source identities and failures.
