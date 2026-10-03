# Fresh v6a guarded lifecycle attempt

The reviewed v6 source/library/runner/manifest are unchanged. `native/plugin-v6a.cpp` contains only the requested startup timeout correction: capture `now` once after request allocation, reject `now>=deadline` while releasing the request, then subtract and clamp to a positive signed timeout in `[1,500]`. `native/v6-to-v6a.diff` shows the exact correction. The fresh exact-ABI library builds without warnings.

`native_probe_lifecycle_guarded.py` retains the reviewed lifecycle cases and reconnect adapter. It replaces presence-only original client preservation with canonical **exact full set equality**, including monitor. The helper `lifecycle_preservation.py` is an exact copy of the already accepted atlas `cross-output-design/nested_preservation.py`: full client projection, order-independent full output projection, and responsive original Files observations.

Before native launch the original Files process must be hidden and absent from native clients. Its public state, complete UI state, coherent ready migration status, exact PID, instance ID, and `/proc/PID/stat` process start are observed through bounded read-only IPC. After cleanup the same observations must match exactly; hidden status and absence from native clients must still hold. Public/UI states use canonical complete JSON SHA256, with no filtered fields. A failed or unresponsive IPC is a failed preservation gate.

All other original preservation gates remain. The runner now has 14 named restoration checks: the previous 12 strengthened checks, plus exact original hidden Files state and unchanged frozen dependencies. Exact catalog bytes remain backed up at 0600 and compared after natural cleanup; no catalog overwrite or historical restore is introduced.

The runner requires `--output` naming a new `native-lifecycle-attempt-*` directory directly under this stage. It refuses to overwrite an existing attempt. Before launch it verifies the root-reviewable guarded manifest, copies and hashes every dependency into that new 0700 directory, retains the manifest and exact command at 0600, and verifies the actual external Orca/profile/library sources. External sources are retained as 0600 reference copies. Artifacts are executed from the fresh copy; externally loaded signed reader files remain at their original paths and are checked again after the trial. Source stage files are checked again too.

Proposed exact command after review and a root GUI grant:

```
python3 /home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor/native_probe_lifecycle_guarded.py --execute --output /home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor/native-lifecycle-attempt-1
```

No native trial has run from this stage. There is no main plugin load path, main reader change, production packaging change, or PointerLocator integration in v6a.
