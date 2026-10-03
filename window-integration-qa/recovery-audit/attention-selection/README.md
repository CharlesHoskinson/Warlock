# Attention observer compositor selection recovery

Status: installed and running after guarded restart. Fixed source SHA256 `b544917f44fcc4786fcc0b4eca922bbc4c3df00b9b4b1f92a220d4c6fcb10b5e`; new daemon PID 2850234, parent 1468, verified main compositor signature. Six installed-source selection tests and the installed EOF/reconnect/focus regression pass. All seven native state preservation checks plus selected-signature client query match pass. Runtime attention was unchanged across restart; main app indicator cache, original windows, focus/cursor, outputs, catalog and accessibility socket were preserved. Comparison slot released. See `deployment-report.json` for before/after snapshots, backup paths and rollback.

## Reproduced defect

The installed helper safely honors an explicit `HYPRLAND_INSTANCE_SIGNATURE`. Without that environment value, it picks the newest socket by mtime while later `hyprctl` calls retain their independent default target. A newer nested compositor can therefore supply urgency that is validated against a different compositor's window at the same address. Startup also clears an existing cached attention state before resolving ambiguity.

`live-mismatch-reproduction.json` records this behavior from the actual installed daemon subprocess with isolated Unix sockets and mocked compositor queries: the nested stream produces a false main-window urgency entry for PID 42. No native compositor, main runtime, GUI app, or live daemon is used by this reproduction.

## Formal contract and candidate

`attention_target.qnt` defines instance selection before persistence: an explicit session target is authoritative, an unknown target resolves only when `hyprctl instances -j` identifies exactly one valid signature, and ambiguity/no target leaves cached state unchanged. Selected stream and query targets remain identical; adding/removing other instances cannot retarget an existing observer.

The staged helper resolves the target before creating its lock or saving state, writes a uniquely resolved signature into its own process environment for subsequent queries, and reconnects only to that target. An explicit unavailable target waits and never chooses another socket. Unknown/invalid selection exits 2 with a concise error. Normal explicit-target startup/cache clearing and EOF/focus cleanup retain their established behavior.

`source.diff` is the exact candidate change. No shared helper other than this staged copy is modified. The existing recovery fixture now accepts `ATTENTION_HELPER` as an optional path override, while its default remains the installed helper used by root's central QA.

## Evidence

- Six Quint scenarios pass; 2,000 samples with up to 100 steps find no invariant violation. Ten traces retained under `traces/`.
- Six tests launch the actual candidate subprocess and isolated sockets: unique implicit selection/query environment, ambiguous selection preserving cache and avoiding locks/connections, no instance, malformed unique signature, explicit target preference over newer sockets, and explicit unavailable target refusing fallback.
- Existing actual-daemon EOF/reconnect/fresh-identity/focus regression passes against the candidate.
- `stage-report.json` records evidence and exact live/candidate hashes.

```bash
quint test attention_target_test.qnt --verbosity 1
quint run attention_target.qnt --invariant allProps --max-steps 100 --max-samples 2000 --seed 20261001 --verbosity 1
python3 test_target_selection.py
ATTENTION_HELPER="$PWD/hypr-taskbar-attention" python3 ../test_attention_recovery.py
```

## Integration boundary

Root approved deployment after copying and typechecking the formal models centrally. Installation was atomic with the existing executable backed up as `hypr-taskbar-attention.before-instance-selection`. The exact old PID/start tick/session signature was rechecked, then only that process was terminated through its pidfd. `guarded_restart.py --execute` launched the installed helper through the supported `hyprctl eval 'hl.exec_cmd(...)'` route. Runtime state was backed up as `attention-runtime.before-instance-selection.json`. No compositor, app, accessibility service, window geometry, focus, cursor or input command was changed by the restart. Root reports full central QA exit 0 against the installed source.

Main compositor shutdown/restart, physical cable hotplug, physical destination visibility, and additional independent application publisher compatibility remain open. The actual private nested restart and native physical-plus-headless drag evidence do not claim those physical boundaries.
