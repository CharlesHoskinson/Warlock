# Paired plugin build evidence

Protected `qa_run.py` build completed successfully in 50.1 seconds. The five C++ translation units are byte-identical copies of `/home/hoskinson/src/hyprbars-dragend-initfix`; no plugin logic change. All copied C++/headers and build metadata are SHA-256 recorded.

Owner: `../native-core-v2` at commit `efb50993780079460b0cbed1363e2166a2de1d9f`, with the staged floating MAX Renderer.cpp patch verified by SHA-256. Candidate core `src/version.h`, generated protocol headers and exact source headers were used through a private `include/hyprland` mapping. Installed `/usr/include/hyprland` flags were removed, and all 710 compiler dependencies were resolved/hashed and checked for leaks or changes. Compiler binary/hash/version, exact commands and effective include directories are in `pair-build-report.json`.

Output: `hyprbars-maximized-stack-v1.so`, SHA-256 `51c97c4fff7de1eb389538c3c526297b80f546f8873a10d0fed09fc0f85ebd70`. Small root-consumable summary is `../plugin-build-report.json`.

Build used g++ with the existing O2/C++23/PIC settings. Existing narrowing-conversion warnings in barDeco.cpp were emitted; no source was changed to silence them. Compilation and linking establish build success, not safe initialization or functional acceptance. Plugin was not loaded by this build agent; root owns the private native smoke and final exact binary pairing. Current user desktop was not changed.
