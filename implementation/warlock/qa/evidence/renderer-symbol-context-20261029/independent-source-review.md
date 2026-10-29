# Owned renderer symbols: independent source review

Verdict: no source blocker identified for a root-owned diagnostic trial. This is not a successful debugger run, a diagnosis, or original UI004 acceptance. Symbol availability, readable mappings and useful frames remain observations to establish in that trial; missing symbols, addresses or unreliable unwinding do not establish a cause.

Reviewed actual files under `taskbar-new-instance/diagnostics/ancestor-qualified-symbols-v1` (SHA-256):

- `entry.py`: 51b3c18d2ff19fcc9ec7667fe4ab7230b09e28190dcc9b58ba14f3de46be11b2
- `controller.py`: 8607fe91e57f499b0b9b6a1a48be20e125716c336105fad03b92bf2f9cd17f87
- `controller.gdb`: 2960a54bc584eccc87777e22065c46163b2dc714947fc4f644e0d64c2bde5668
- `diagnostic-runner.py`: 7bb724351897d2ce3726c8725f018c4d44f2bbf657de92dc20f417f0bf53f1b9
- Diffs reviewed: controller.py b4b357e4f78eb1b63788c39e341bc5e350f07af6d4c7e77cde72ac67e17dc094; controller.gdb 290d449b81cd1b0cdee8dd353ba80ab89833655ebe18b29be3fd80a5a2dd4a9b; runner b239906cb47bc2082fef21a61620facf4339a49e234f10e6d5b98d663c816f09.

The entry requires QA scope, checks pinned files and invokes pinned normal-user GDB with init and auto-loading disabled and debuginfod disabled. The controller retains UID, QA cgroup, start time, executable, unique owned host descendant, ancestor and live pidfd checks, rechecks after attach and before release, and sends stop/continue through pidfd. It checks the stopped `/proc/PID/exe` bytes and same-file identity against the pinned WebKit renderer before `file`, sets sysroot and solib paths under that owned process root, and enables library loading. This is a real symbol lookup attempt, not evidence that symbols or usable unwind information exist. No privilege or sandbox relaxation is present in the reviewed delta. Fatal captures retain signal forwarding, existing timeout and core-limit checks. Runner substitutions bind the previously reviewed fresh candidate SHA-256 9047be2e62947e68621b1bb7fa32403dd930b97cba444d67c82e501a1c4b311f; the original runner remains the behavioral source and its existing deadlines are not changed by the shown delta.

The bounded maps/build-ID receipts verify mapped-file device/inode before reading ELF GNU build IDs; deleted, mismatched or unreadable objects are marked unavailable. Build IDs do not prove debug-symbol completeness or that a resulting stack is correct. `preAttachMappings` in the result is a misleading name: it is captured **after attach and sharedlibrary**, before release; interpret as pre-release evidence. A maps bound, library setup, file access, or fixture attach deadline can stop the trial; report actual failure instead of inferring an outcome. The diagnostic deliberately pauses an instrumented private fixture and labels itself non-acceptance. The original native scenario requires its own actual uninstrumented evidence and review.

Source review only; no QA, GDB, native execution, or test was performed.
