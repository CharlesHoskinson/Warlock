# Atomic modal-family reservation candidate

Offline stage; root owns installation and native replay. Parent accepted143e stage remains unchanged.
Controller SHA256: `83609014a0a860c5d1e6228c8a8aa64799e5df9e35365e95d75daee1c12a653a`. Wrapper, core and widget65 unchanged.

## Counterexample and contract

`counterexample-report.json`: all three new reservation assertions failed against143e before implementation. A fresh family query can return the owner minimized; its earlier restore may finish before later reservation. Using that snapshot for an already-minimized skip loses the latest owner intent. Per-peer freeze IPC also allowed older callbacks before all peers were reserved.

`family_commit_order.qnt` first specifies current exact identities and endpoint decisions under the callback lock, then atomic whole-family reservation before any peer freeze/preparation. Four named scenarios and2000 randomized samples. Existing fresh relation/provenance contract remains intact.

## Changes

- Read mapped clients once under the controller lock after the native family query; reject the entire new scope if any captured exact member identity is missing/reused.
- Create all member reservations under the same lock; slow peer freeze/preparation follows. Fresh workspace/no-op decisions cannot be invalidated by older endpoint callbacks between peers.
- Profile every accepted member's identity, token, decision, current workspace/pin/rectangle.
- Bounded128-event diagnostic ledger records plan/commit/cleanup attempts and outcomes. Commit records include one extra read-only exact-client query after each native operation. No renderer/widget/native geometry changes.
- Cancel current/frozen pixels first, deduplicate token+identity, then stale tokens. Keep phase `cleaning` pending until every bounded cancellation attempt finishes, recording acknowledgements/errors. This distinguishes native settlement from cleanup completion; cancellation remains best effort after IPC failure.
- Fresh copied native driver captures the diagnostic ledger before fixture cleanup on both pass and fail. No focus oracle and no weakened interior/geometry gates.

## Offline acceptance

```bash
python3 ~/window-behavior-spec/minimize-motion-stage/family-reservation/check_offline.py
```

105 Python:28 controller+13 snapshot+12 freeze+9 core+3 socket+11 observer+15 scope+6 reservation+8 corrected fixture.17 actual QML,3 QML parsers and Python/Bash syntax. Freeze12/family8/commit4 named scenarios and2000 samples per model.

After reviewed helper installation, same runner accepts `--helpers ~/.local/bin --widget ~/.config/omarchy/plugins/hoskinson.windows/widget_v65 --report .../installed-offline-report.json`.

## Coordinated native replay (root only)

```bash
python3 ~/window-behavior-spec/minimize-motion-stage/family-reservation/native_motion_fixture.py --toolkit family --pin --require-freeze --reduced-motion-trial --output ~/.cache/window-minimize-family-reservation-native
```

Inspect `familyPlan` and `serviceDiagnostics.events` for each member token/current endpoint, commitDone native workspace/pin, cancellationStart/Done/Failed and cleanupDone. Existing failed native evidence stays in window-minimize-family-native-143e.
