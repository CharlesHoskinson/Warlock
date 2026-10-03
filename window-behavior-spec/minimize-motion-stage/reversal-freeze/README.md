# Reversal freeze candidate

Status: staged only. Installed SHA793 controller and widget64 remain unchanged. Native Qt strict gate previously failed intermittently; this candidate still requires reviewed paired installation and native profiling before acceptance.

## Contract and implementation

`freeze_contract.qnt` was created before this implementation. It requires an exact captured identity reservation to hold the current visual rectangle before external preparation. Holding a snapshot has no native authority: latest token, mapped stable ID/PID and current identity are checked again for readiness, endpoint, watchdog, reduced motion and restart settlement. Timeout/reduction/reload model events explicitly supply a fresh observed identity; unvalidated or reused clients cannot be committed solely from a reservation.

Controller `request` reserves the exact already-pending caller identity and operation before client and modal-family queries, invalidating old callbacks immediately. `motionFreeze` stops the previous QML tween/readiness while its existing pixels stay visible. All freshly validated family routes are also held before any target/snapshot preparation. Older delayed family work cannot replace newer member intent. A reversal while the preceding request still prepares retains its actual visible ancestor image. Freeze acknowledgements carry source snapshot metadata; service accepts it only for the exact identity and its own existing token image chain, with matching native geometry before reuse. Visible native geometry and pin handling still belong to the unchanged core; whole-window capture/cache code is unchanged.

Taskbar `windowAction` holds the exact captured frame synchronously before spawning the helper. This provisional hold has a 1600ms failure timer. Accepted service reservations replace that timer; existing service watchdog/reduction/reload settle the latest intent and cancel the held visual. A failed freeze produces safe immediate native fallback after identity validation rather than an animation starting at an endpoint.

QML retains per-identity numeric epochs, rejects superseded begin/start/cancel, and ignores old session callbacks after daemon restart. A readiness callback from an image loading after it was paused cannot resume or replace the held pixels. Cancel/reduction act on the latest held token. Cancelled epochs and all retired service session prefixes remain remembered for each live exact identity, including minimized windows. Epochs are collected only after that identity closes/is reused and its overlay is gone. Begin/freeze also check the taskbar live identity mirror, so a late event after collection cannot recreate a closed window overlay.

Journal profile fields: `received`, `reserved`, `freezeSent`, `freezeAck`, `frozen` (actual QML current rectangle and route progress), `clientsStart`, `clientsDone`, `familyStart`, `familyDone`, `beginSent`, `beginAck`. Native driver records process issuance separately. `--require-freeze` requires equality between QML acknowledged frozen rectangle and the next route's `from`, plus freeze-before-query order; it retains the existing strictly interior reversal gate and pixel/identity continuity checks. Failure reports retain raw samples, diagnostics and pending/visual state at failure.

## Frozen offline verification

```bash
python3 ~/window-behavior-spec/minimize-motion-stage/reversal-freeze/check_offline.py
```

Runner freezes helper, tests and widget bytes, then checks source hashes stayed unchanged. `offline-report.json` records exact inputs and every command. It runs **76 unique Python tests**: accepted controller28, whole PNG13, new freeze12, actual core9, socket3, native observer11; **17 actual QML JavaScript scenarios**, three QML parsers, Bash syntax, and freeze contract **12 named scenarios / 2000 sampled traces**. Socket tests use private fake desktop/runtime and stop their daemon. Existing controller28 and PNG13 assertions are preserved.

After reviewed paired deployment, the same frozen test inputs can target installed sources:

```bash
python3 ~/window-behavior-spec/minimize-motion-stage/reversal-freeze/check_offline.py \
  --helpers ~/.local/bin \
  --widget ~/.config/omarchy/plugins/hoskinson.windows/widget_v65 \
  --report ~/window-behavior-spec/minimize-motion-stage/reversal-freeze/installed-offline-report.json
```

Root's existing installed-controller MBT can target this candidate with `MOTION_MBT_SOURCE` and `MOTION_MBT_REPORT`. Its existing 3030-state/13-event endpoint suite passed an earlier reservation candidate; rerun after reviewing final SHA.

## Coordinated native commands (not run here)

Only root or a coordinated GUI slot may run these. The wrapper creates disposable native fixtures, snapshots/restores original clients, cursor/focus, and reports cleanup. No other agent may use the GUI simultaneously.

```bash
python3 ~/window-behavior-spec/minimize-motion-stage/reversal-freeze/native_motion_fixture.py \
  --toolkit qt --require-freeze --reduced-motion-trial \
  --output ~/.cache/window-minimize-freeze-qt
```

Repeat for `--toolkit foot`, `gtk`, and `family`; relevant matrix variants add `--pin` or `--maximize`. Add `--capture-frames` for a separate screenshot replay after uninstrumented polling assertions. The driver never uses focus as a pass/fail oracle. Native screenshots still need decorated titlebar/border inspection; parsers and offline JS do not prove live Qt presentation, runtime alias wiring, or Orca behavior.

No native C++ changes or rebuild are needed; accepted v14 decorated snapshot bridge remains paired. Preserve V4 accessibility bridge imports/keyed models and `stateAll`/`stateForMonitor` diagnostics. Deploy to a fresh QML URL, not by overwriting a loaded plugin.
