# Corrected current recipe source review

Source-only READY for root's first protected build, using reviewed v2 lock d5049df9755a129992a8fa42a6f84be80bf66f3942fbcd8a42b2fa357939d723. No compiler, QA, imports of product code, native execution, or public writes by this reviewer.

The three requested fixes are present: locked source/project/cache/static bytes are copied and checked; exact compiler argv/cwd/environment, no timeout/error and false native/release flags are validated; command intent and partial output hashes survive handled failures. Recipe now records resolved Python executable SHA and version. Full interpreter libraries/dynamic runtime closure is explicitly outside the bounded frontend claim.

Read-only independent inventory: 98 Elm files plus elm.json = 99 source inputs, 16 static assets, 100 staged cache inputs, 111 held manifest files, 229 total input hashes. Actual cache has 101 files, including the intentionally omitted transient lock. Every held file and every v2 input hash matches; actual source set equals locked set. v1 remains preserved/unrun.

The negative source/cache scenarios alter reviewed lock metadata and exercise exact-lock rejection. They do not alter actual source/cache files, so describe this coverage precisely. Output/static/log scenarios actually mutate bytes. No claim of randomized fuzzing, complete input mutation coverage, whole-release reproducibility, or original DEL003 acceptance follows.

The postcompile staged cache checks are conservative: if the held compiler rewrites registry.dat/artifacts.dat, that will be an actual retained failure to analyze, not grounds to relax cache checks before observing it. No further blocking source issue found in the bounded delta review.
