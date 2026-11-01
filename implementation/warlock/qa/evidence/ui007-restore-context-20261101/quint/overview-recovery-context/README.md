# Overview recovery context model

This bounded Quint model covers origin intent/status, retained workspace presence, current transaction identity, focus selection/command count, repeated open, and mutation count. The source refinement points are `src/OverviewRecovery.elm`, `src/Desktop.elm`, and the corresponding production `Desktop.update` cases in `qa/TaskViewReplay.elm`. It is a separate bounded model, not proof that the native runtime or physical focus matches Elm.

Protected runner output: model and test typechecks pass; 8 named Quint tests pass, including deliberate repeated-open, missing-workspace and mismatched-refusal mutants. The simulation explored 5,000 traces up to 8 steps with seed `52012`; safety checks passed. The existing-workspace and vanished-workspace witnesses appeared in 271 and 1,091 traces. The mismatched-return witness was absent from the non-mutant simulation; the explicit mutant test demonstrates the forbidden state.

Model SHA-256: `fd817dd3430fcfb367fd3abf172a2c568f746371e4c8efae610ecafb04298e27`. Test SHA-256: `bca3bd6cdfe46455cb6e55536c02d6ae5368d9eb697d30c7ca1b7bf64db3fe4e`. Quint version and stdout, simulation output, source copies and checksums are retained alongside this file.
