# Private native Qt toolkit plan

Stage only; no native process launched and no production changes. The accepted main Qt v2 manifest203 remains immutable. Fresh compiled fixture/source/CMake are byte-identical to v2.

Recovery's separate host stage is `/home/hoskinson/window-integration-qa/private-weston-host-v1`: a signed user-local Arch Weston15.0.1-3 headless GL host with a private Hyprland Wayland child. Its API/dependencies/renderer readiness are still under review. Qt requires host1600×1000 and private scale1, confirmed as supported planned launcher parameters; actual private monitor readiness must be asserted before fixture input.

`private_session.py` is an import-safe session module retaining the Qt v2 feature gates. All subprocesses and compositor commands take explicit private environments. `private_target.py` rejects shared main runtime/instance/socket/session handles, confines private HOME/state paths and checks actual socket identity. `main_observer.py` runs the accepted read-only complete main observation code in a separate worker with the captured original environment, preserving raw private snapshots. No main restoration dispatch exists.

The eventual orchestrator must capture main BEFORE host startup, create the reviewed host using1600×1000/scale1, call `run_session`, perform complete exact host cleanup, then compare main AFTER host shutdown under the original environment. This packet is not ready for native authorization until that orchestration, host source/dependency provenance, source freeze and exact command exist. Session modules alone cannot establish host preservation.

The production helper runs unchanged under the private environment, with one explicitly owned private motion daemon. No taskbar renderer is launched, so a successful bounded minimize/restore result describes native family fallback compatibility. It does not prove animation presentation.

No reader/audio/braille/physical-hardware claims. Root review and explicit native grant remain required before launch.
