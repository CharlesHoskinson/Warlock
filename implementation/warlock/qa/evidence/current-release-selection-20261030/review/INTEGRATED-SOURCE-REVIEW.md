# Integrated current-composition selection source review

SOURCE_READY for independent review and bounded consumption of the fresh composition capture. Read-only source review; no QA or public edits by reviewer. This is not package/host reproducibility or DEL004 acceptance.

Actual source hashes:

* implementation/warlock/adapter/release_tuple.py: 3267a1d3eca90d9dbcccc2f918ea71aafd96e0bba43f49705f7d3d845f330320
* implementation/warlock/adapter/current_native.py: 8bc7a0c1244192ea8c94f2388933eb056a0a8ad8888a1f879913e2c6d27fff69
* implementation/warlock/qa/check-release-repro.py: 356fb2bd7b5a601749478013a12075713ec11bc53266dfd59607a269533e0f87

Compared integrated release_tuple against the frozen Terra4 proposal and earlier review: both requested corrections are present. New reference.missingObservation retains absence of complete at-build core and Aquamarine source/tool/dependency provenance. The schema dispatch rejects nonobject JSON, then wraps the whole current-composition helper for RuntimeError/KeyError/TypeError into ValueError, including errors before its inner module-loading try. This preserves the release harness's caught failure route for those malformed-input classes. It does not claim exhaustive Python exception normalization.

The rest of the proposal remains the reviewed exact-kind branch with hash-pinned validator bytes, isolated current_build module binding restored afterward, same-byte JSON digest/decode, actual production composition validation, all inputs/resolutions/aliases and all19 asset guards. Historical derivative branch behavior remains intact.

CLI now checks regular-file status before hashing as well as paired flags, absolute path, lowercase SHA/content match and probe conflict. It records explicit selection and passes it to builder.capture; omitted selection keeps the legacy default. Root reports13 protected argument-bound checks passed; this source review has not independently inspected that raw report and makes no new test-execution claim.

current_native's explicitly approved release_tuple.py adapter delta keeps old sourceHistory and actual Git verification, separate adapterChanges and history-only delta, existing preflight rows and compiler overlap/full current adapter map. Any subsequent adapter source edit invalidates the new composition lock again. Old ba97 and all prior evidence remain immutable.

Fresh lock/input-map review remains required before selected consumption. Actual isolated build closure, byte-equal rebuilt host/all19 frontend assets and two distributable comparisons remain unobserved. Preserve failed logs and block release if those gates fail. Do not restart stopped native pin/top/New instance routes for this distinct delivery work.
