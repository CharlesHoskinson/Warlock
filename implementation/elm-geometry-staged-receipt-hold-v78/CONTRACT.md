# Staged geometry receipt-delivery fixture

QA-only derivative of frozen V63. The backend is the exact V74 captured V64 broker, pinned by component manifest9678ba49758ba4fd7688d1c0faed2a1fafef4b91e62be3d7dad23e830fb25b5a and V64 held manifest3aa379a0c7c694455d32f08c69d047b4ac0dd9200015d30b40e68593938b2161. All adapter siblings match; cached imports from other source paths refuse before transport. Production sources are unchanged.

The selected protocol2 operation is explicit: maximize (default preserving original45 tests) or restore-geometry (mandatory09 after scenario08's savedMAX). Only the selected incarnation/operation's actual Committed receipt is withheld AFTER native transport has returned. Post-close legacy projection and geometry facts pass immediately before submission and during delivery hold. Actual compositor event notifications and unrelated frames continue. No SIGSTOP, deferred facts, fabricated receipt, effect retry, or observed-state invention exists.

The wrapper CLI remains:

```
python3 -B qa/wrapper.py run --control-directory ABS --incarnation DECIMAL --config ABS_AUTHORITY_CONFIG --effect-operation restore-geometry
python3 -B qa/wrapper.py release --control-directory ABS
```

For the existing native host's two-argument broker launch, set `--backend` to the held absolute `qa/broker-entrypoint.py` and `--authority-config` to a canonical owned regular single-link0600 wrapper configuration:

```
{"authorityConfig":"ABS_ORIGINAL_NATIVE_CONFIG","controlDirectory":"ABS_PRIVATE_CONTROL","incarnation":"DECIMAL","effectOperation":"restore-geometry"}
```

The entrypoint accepts exactly these four keys and only closed geometry operations. It passes the original native configuration unchanged to the authenticated endpoint; it does not alter native identity or capabilities. Launch and release both require the unchanged protected QA scope. The root native runner owns processes, logs, private configuration and cleanup.

The control directory is canonical0700. Create an owned single-link0600 `gate.json` containing `{"action":"hold"}`. Gate inode/process PID+start/full binding+intent+protocol must remain unchanged. `held.json` contains the actual original receipt and wrapper identity; its appearance, not elapsed sleep, establishes that delivery is held. Release uses public `write_release()` or CLI, writes the same gate inode under exclusive nonblocking flock, and forwards the exact stored receipt once. Duplicate release, invalid/Unknown/nonmatching selected outcomes, malformed control, replacement or timeout fail closed. Matching reason text is bounded to256 UTF16 units with valid Unicode and no C0/C1 controls.

Keep the original native endpoint absolute3-second budget and original absolute6-second whole-scenario deadline. The inherited wrapper watchdog is at most5 seconds measured from receipt capture; it never extends the scenario and does not automatically release/retry. Unreleased EOF and watchdog failures unwind contexts, stop the watchdog, emit one host-disconnected and exit1. Successful release exits0. Full09 must assert the actual engine remains Pending/no replay while real native execution has already committed, notifications stay live, and the matching released receipt settles only its original operation. This does not prove native Pending execution, Unknown or storage recovery.

CPU qualification: unchanged V63 test45 plus staged30 cases. New cases exercise the actual V64 selector/strict endpoint validators and V78 wrapper CLI with explicitly synthetic transport, including preselection observations, postreceipt live event hint and postreceipt geometry facts before gate release. A first synthetic IO fixture failure is preserved: its mock os.read intercepted the private gate descriptor; corrected mocking applies only to stdin, preserving actual gate filesystem IO. CPU fixtures are separate from genuine native receipts/GTK/pixels acceptance. Native09, geometry/menu release and all roadmap gates remain open.
