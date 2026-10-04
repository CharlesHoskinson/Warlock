# Native floating MAX stacking correction — formatted v2

Fresh derivative of [v1](../maximized-stack-v1/README.md), preserving its source, build and native proof packets. Owning core remains `efb50993780079460b0cbed1363e2166a2de1d9f`. Only clang-format whitespace changed; whitespace-stripped whole Renderer.cpp equals v1. The full original-to-v2 patch and separate v1-to-v2 formatting patch are included. Exact owning style file hash, formatter version and range are recorded in `source-manifest.json`.

Candidate Renderer.cpp SHA-256: `b1d840d49e360ed45790ac5a4bad95e2a8420e5ee85438f6c476454ca0a1d244`.

Six source/model tests passed through `qa_run.py`, including original source/patch hashes and 192 stack/pin combinations. The modified range passes protected `clang-format --dry-run --Werror` with the owning core `.clang-format`. Root owns incremental native-core build, exact ABI pair review and serial private native rerun; this staging agent did not mutate the v1 core/build or run GUI actions.

Policy remains renderer-only: floating native MAX final-pass order follows stack; pinned exceptions retained; true fullscreen and tiled MAX unchanged; no input/alpha/allowedOver flags or return geometry altered. See v1 for source findings, remaining acceptance boundaries and controlled restart requirements.
